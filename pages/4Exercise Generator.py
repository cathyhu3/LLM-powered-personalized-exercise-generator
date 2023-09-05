import os
from dotenv import load_dotenv

from langchain import OpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.vectorstores import Pinecone
from langchain.chains.question_answering import load_qa_chain

import pinecone

import streamlit as st
import database as db
import streamlit_authenticator as stauth

import yaml
from yaml.loader import SafeLoader

######### SESSION STATES/INITIALIZATIONS ###################################################################################################################################
if 'sub_inj' not in st.session_state:
    st.session_state['sub_inj'] = False

output_sets = []

#############################################################################################################################################################
##### LLM set-up ############################################################################################################################################
load_dotenv('.env')
APIKEY = os.getenv("OPENAI_KEY")
PINEKEY = os.getenv("PINECONE_KEY")

os.environ['OPENAI_API_KEY'] = APIKEY
PINE_KEY = os.getenv("PINECONE_KEY")
PINE_ENV = os.getenv("PINECONE_ENV")
llm = OpenAI(temperature=0)

#############################################################################################################################################################
###### User Authentication #################################################################################################################################################

with open('output.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

name, authentication_status, username = authenticator.login("Login",'main')

if authentication_status == False:
    st.error("Username/password is incorrect")

if authentication_status == None:
    st.warning("Please enter your username and password")

#############################################################################################################################################################
##### Data Connection ############################################################################################################################################
pinecone.init(
    api_key=PINE_KEY,
    environment=PINE_ENV)
index_n = "post-stab-info"
index = pinecone.Index(index_name=index_n)
qa = load_qa_chain(llm, chain_type="stuff")
embeddings = OpenAIEmbeddings(openai_api_key=APIKEY)
vectorstore = Pinecone.from_existing_index(index_name=index_n, embedding=embeddings)

#############################################################################################################################################################
#############################################################################################################################################################
col1, col2 = st.columns([3, 1])

if authentication_status:

    num_ex = db.get_num_ex(username)

    exlist = db.get_ex_list(username)

# Injury pain level form
    if db.get_injuries(username):
        injuries = db.get_injuries(username)
        list_inj = injuries.split(', ')
        ratings = db.get_ratings(username)
        with col1:
            if len(list_inj) == 1:
                st.write("Here is your current injury: " + injuries)
            else:
                st.write("Here are your current injuries: " + injuries)
            with st.form("form0"):
                st.header('Injury State Form')
                st.write("Has the pain level of your injury changed?")
                st.write("Rate them on a scale from 1-10 with the pain chart on the right")
                ratings = []
                for i in range(len(list_inj)):
                    ratings.append(st.number_input("Rate your " + list_inj[i], min_value=1, max_value=10, step=1))
                submitted0 = st.form_submit_button("Submit")
                if submitted0:
                    st.session_state['sub_inj'] = True
                    ratings = ', '.join(map(str, ratings))
                    db.update_user(username,{"ratings": ratings}) 
            
            with st.form("form1"):
                st.header('Add or delete Injuries')
                st.write("Add Injuries")
                added_inj = st.text_input("Enter new injuries using a comma and space between injuries \nex: Plantar Fasciitis, Ankle Sprain")
                rating_for_added = st.text_input("Enter your current pain level for your added injuries \nex: 7, 9")
                st.write("Delete Injuries")
                delete_inj = st.text_input("Input injuries you want to delete using a comma and space between injuries \nex: Plantar Fasciitis, Ankle Sprain")
                submitted1 = st.form_submit_button("Submit")
                if submitted1:
                    if added_inj:
                        db.add_inj(username, added_inj, rating_for_added) 
                    if delete_inj:
                        db.delete_inj(username, delete_inj)


        with col2:
            st.write('Welcome ' + name + '!')
            authenticator.logout('Logout', 'main')
            st.markdown("***Notes***")
            st.write('''Injury rating: rate on 1-10 scale based on this pain chart''')
            st.image('pain_scale.jpeg')
            with st.expander('Sources'):
                st.write('https://specialistshospitalshreveport.com/patient-resources/using-the-pain-scale/')


#############################################################################################################################################################
##### OPERATIONS ON INPUTS ##################################################################################################################################

# Creating output of injuries with their respective ratings
    if db.get_injuries(username):
        injuries = db.get_injuries(username)
        list_inj = injuries.split(', ')
        ratings = db.get_ratings(username)
        list_ratings = ratings.split(', ')
        inj_and_rates = []

        for i in range(len(list_inj)):
            inj_and_rates.append("injury: " + list_inj[i] + "rating: " + str(list_ratings[i]))

#############################################################################################################################################################
##### CHAINS ################################################################################################################################################
    if st.session_state['sub_inj']:
        # CHAIN 4: ask for advice based on injuries
        prompt4 = "Starting from this list of postural stability exercises: " + exlist + ", which exercises should I remove based on the patient's past injuries and their injury ratings,\
            information about exercises avoid for the different types of injuries, how injuries to different areas can affect postural stability, and the highest intensity Postural Stability exercises that puts stress on the injury area that the patient can safetly perform given their injury rating.\
                The patient's injurie(s) and injury rating(s): " + str(inj_and_rates)
        docs = vectorstore.similarity_search(prompt4)
        feedback1 = qa.run(input_documents=docs, question=prompt4)

        # CHAIN 5: Narrow down exercise list based on advice on Injuries
        prompt5 = "Starting from this list of postural stability exercises: " + exlist + ", remove exercises from this list based on this feedback: {feedback}. Return the list of the remaining exercises."

        Narrow1 = PromptTemplate(
            input_variables = ['feedback'],
            template = prompt5)
        narrow1_chain = LLMChain(llm=llm, prompt=Narrow1, verbose=True)
        narrow1 = narrow1_chain.run(feedback = feedback1)

        # CHAIN 6a: Divide list down into sets of n exercises (number of exercises user wants to do per day)

        prompt6a = "Starting from this list of exercises: {exercises}, divide this list into sets of " + num_ex + " by first randomizing the order of the exercises, then dividing them into sets of \
            " + num_ex + " exercises. Return the sets of the new exercises."

        sets_prompt = PromptTemplate(input_variables= ['exercises'], template = prompt6a)
        sets_chain = LLMChain(llm = llm, prompt = sets_prompt, verbose = True)
        sets = sets_chain.run(exercises = narrow1)

        # CHAIN 7a: Format the sets into a list that's more user-friendly
        prompt7a = "Format these sets of exercises by including line breaks between all of the sets. The sets: {sets}. Remember to include all of the exercises listed."

        format_prompt = PromptTemplate(input_variables = ['sets'], template = prompt7a)
        format_chain = LLMChain(llm = llm, prompt = format_prompt, verbose = True)
        formatted_sets = format_chain.run(sets = sets)
        st.write(formatted_sets)

        
    elif len(list_inj) == 0:
        # CHAIN 6b: Divide list down into sets of n exercises (number of exercises user wants to do per day)

        prompt6b = "Starting from this list of exercises: {exercises}, divide this list into sets of " + num_ex + " by first randomizing the order of the exercises, then dividing them into sets of \
            " + num_ex + " exercises. Return the sets of the new exercises."

        sets_prompt = PromptTemplate(input_variables = ['exercises'], template = prompt6b)
        sets_chain = LLMChain(llm = llm, prompt = sets_prompt, verbose = True)
        sets = sets_chain.run(exercises = exlist)

        # CHAIN 7b: Format the sets into a list that's more user-friendly
        prompt7b = "Format these sets of exercises by including line breaks between all of the sets. The sets: {sets}. Remember to include all of the exercises listed."

        format_prompt = PromptTemplate(input_variables = ['sets'], template = prompt7b)
        format_chain = LLMChain(llm = llm, prompt = format_prompt, verbose = True)
        formatted_sets = format_chain.run(sets = sets)
        st.write(formatted_sets)