import os
from apikey import apikey
import streamlit as st

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from io import StringIO
from typing import List, Union

from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate, StringPromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.agents import Tool


#############################################################################################################################################################
##### LLM set-up ############################################################################################################################################
os.environ['OPENAI_API_KEY'] = apikey
llm = OpenAI(temperature=0)


#############################################################################################################################################################
#############################################################################################################################################################

#############################################################################################################################################################
##### Session state variables ############################################################################################################################################
if 'biom_class' not in st.session_state:
    st.session_state['biom_class'] = 0

if 'list_of_ex' not in st.session_state:
    st.session_state['list_of_ex'] = 0

if 'narrowed1' not in st.session_state:
    st.session_state['narrowed1'] = 0

if 'narrowed2' not in st.session_state:
    st.session_state['narrowed2'] = 0

#############################################################################################################################################################
#############################################################################################################################################################

#############################################################################################################################################################
##### Document inputs into system ###########################################################################################################################

# 75 exercises generated by ChatGPT
ex_75_doc = open('exercises_75.txt','r')
ex_75 = ex_75_doc.read()

# Daily activities exercises generated by ChatGPT
all_DA_ex = open('daily_activityex_list.txt','r')
all_DA = all_DA_ex.read()

# Formated Patient Data: example of extracted and formatted patient data
example_form = open('patient_data_example.txt', 'r')
ex_format = example_form.read()

# Chart of Exercises: example chart of exercises
example = open('Example_for_ChatGPT_ PatientA.csv','r')
ex_chart_str = example.read()

# Information on Impact of Biometric Factors on Postural Stability Exercise Adjustment: lists ways that biometric factors affect body's adjustment to PS exercises
biometric_adj = open('bio_adjusting.txt','r')
bio_adj = biometric_adj.read()

# Information on Impact of Injuries on Postural Stability Exercise Adjustment: lists how different injuries to different parts of the body affect adjustment to PS exercises
injury_adj = open('injury_adjusting.txt','r')
inj_adj = injury_adj.read()

# Information on Which Exercises to Avoid for Each Injury
injury_avoid = open('inj_avoid.txt','r')
inj_avoid = injury_avoid.read()
#####################################################################################################################################################################
#############################################################################################################################################################


#############################################################################################################################################################
##### App Framework & Inputs ##############################################################################################################################################
st.title("Biometric Properties form")

# KMEANS INPUTS:
# data points of COP avg vel from literature
df = pd.read_csv('newCOP_from_matlab.csv', header=None)
x = df.values.flatten().tolist()

# initializing session state variable
if 'PSscore' not in st.session_state:  
    st.session_state['PSscore'] = 0

# form for the participant's COP avg velocity
with st.form('form1'):
    st.markdown('<p style="color:LightGreen; font-size: 20px;">Postural Stability score</p>',unsafe_allow_html=True)
    in_x = st.text_input("input individual's COP average velocity")
    submitted_1 = st.form_submit_button(label = "Submit")
    

# KMEANS FUNCTION
def classification_of_ind(x,in_x):
    y = [0]*len(x)

    # k-means implementation
    data = list(zip(x, y))
    kmeans = KMeans(n_clusters=3, init='k-means++', random_state=1)
    kmeans.fit(data)

    # find the cluster centers
    pos_of_c = kmeans.cluster_centers_ # numpy array version of cluster centers
    pos_of_c = sorted(pos_of_c[:, 0].tolist()) # pos_of_c = a list of the positions of the cluster centers

    # setting up a data point from user input
    data_pt = np.array([[in_x,0]])
    c_label = kmeans.predict(data_pt) # cluster_label = using predict function to classify in_x to a cluster 

    # Separating Clusters
    data_labels = kmeans.labels_
    data_labels_np = np.array([data_labels])

    c_1 = np.array([]) # cluster 1
    c_2 = np.array([]) # cluster 2
    c_3 = np.array([]) # cluster 3
    for i in range(len(data_labels)):
        if data_labels[i] == 2:
            c_3 = np.append(c_3, (x[i])) # if point is labeled 2, then append to 3rd cluster
        if data_labels[i] == 1:
            c_2 = np.append(c_2, (x[i])) # if point is labeled 1, then append to 2nd cluster
        else:
            c_1 = np.append(c_1, (x[i])) # if point is labeled 0, then append to 1st cluster

    c_1 = list(zip(c_1,[0]*len(c_1)))
    c_2 = list(zip(c_2,[0]*len(c_2)))
    c_3 = list(zip(c_3,[0]*len(c_3)))

    # Z-score threshold
    z_thresh = 2.5

    # Normalize Clusters
    norm_c1 = StandardScaler()
    norm_c1.fit(c_1)

    norm_c2 = StandardScaler()
    norm_c2.fit(c_2)

    norm_c3 = StandardScaler()
    norm_c3.fit(c_3)

    # Find Z-score of data point relative to which cluster it's in
    if c_label == 2:
        dp_zscore = norm_c3.transform(data_pt) # z-score of the data point
        dp_zscore = np.abs(dp_zscore[:,0].tolist())
    if c_label == 1:
        dp_zscore = norm_c2.transform(data_pt)
        dp_zscore = np.abs(dp_zscore[:,0].tolist())
    else:
        dp_zscore = norm_c1.transform(data_pt) # z-score of the data point
        dp_zscore = np.abs(dp_zscore[:,0].tolist())

    # Outlier test: results --> inclonclusive if data point is an outlier of its cluster
    if dp_zscore >= z_thresh:
        if c_label == 0:
            message = '**Very Weak** Postural Stability'
            return message
        if c_label == 1:
            message = '**Very Strong** Postural Stability'
            return message
        else:
            message = 'Normal Postural Stability'
            return message
    else:
        return c_label
    
# KMEANS RESULTS
with st.expander('Grouping details'):
    st.write("The graph shows the k means clustered COP average velocities of 42 individuals from Kei Masani's 2014 study: 'Center of pressure velocity reflects body acceleration rather than body velocity during quiet standing'")
    st.image('grouped_COP.png')
    st.write("Link: https://www.sciencedirect.com/science/article/pii/S0966636213007030?via%3Dihub")
# the classification of the individual
if submitted_1:
    in_x = float(in_x)
    group = classification_of_ind(x,in_x)

    if group == 0:
        st.write("**Weak** Postural Stability")
        PS_score = 'weak postural stability'
    elif group == 1:
        st.write("**Strong** Postural Stability")
        PS_score = 'strong postural stability'
    elif group == 2:
        st.write("**Normal** Postural Stability")
        PS_score = 'normal postural stability'
    else:
        st.write(group)
        PS_score = group
    st.session_state['PSscore'] = PS_score


# Form for Patient Response + Biometric factors
with st.form("form2"):
    # patient response
    #pat_upload = st.file_uploader("Upload the patient's response form")
    pat_upload = st.session_state['injuries']
    # doctor's input (BIOMETRIC FACTOR DICTIONARY)
    age = st.text_input('Age')
    height = st.text_input('Height (cm)')
    body_fat = st.text_input('Body Fat Percentage')
    q_angle = st.text_input('Quadricep angle')

    submitted2 = st.form_submit_button("Submit")

biom_fact_dict = {'age': age,
                  'height': height,
                  'body_fat_percentage': body_fat,
                  'quadricep_angle': q_angle}  # the biom_factors

######################################################################################################################################################################
#############################################################################################################################################################


#############################################################################################################################################################
##### CHAINS #########################################################################################################################################################

if submitted2:
    ## CHAIN 1: Using information from the internet about classifying each biometric factor as weak, normal, or strong
    template1 = '''Based on the means and standard deviations for the gender group of the individual: {gender} and their biometric factors: age, height, body fat percentage, and Q angle,\
        classify the individual as:
        
        age: young (0-12), average (12-40), old (40-60), very old (60+);
        height: shorter than average, normal range, taller than average; 
        body fat percentage: obese or non-obese;
        Q angle: smaller than average, normal range, or larger than average;

        Here is the individual's information:
        biometric data: {biom_data}
        '''
    
    Biom_classification = PromptTemplate(
        input_variables = ['gender','biom_data'],
        template = template1)
    biom_class_chain = LLMChain(llm = llm, prompt = Biom_classification, verbose = True)
    biom_class = biom_class_chain.run(gender = st.session_state['gender'], biom_data = str(biom_fact_dict))
    st.session_state['biom_class'] = biom_class

    # st.write(biom_class)
    ## CHAIN 2: Daily exercises list
    template2 = '''This is a list of Daily activities (numerated 1 through 7) with corresponding exercises that can be done during the daily activities: {DA_list_all} \
        Instructions:
        Remove the daily activities and their corresponding exercises that are not included in this list: {daily_activities} and return the result.\
            Make sure to preserve everything else not deleted.'''

    DA_refiner = PromptTemplate(
        input_variables = ['DA_list_all','daily_activities'],
        template = template2)
    DA_refiner_chain = LLMChain(llm = llm, prompt = DA_refiner, verbose = True)
    DA_ex_list = DA_refiner_chain.run(DA_list_all = all_DA, daily_activities = st.session_state['daily_activities']) # list of all exercises for individual's specific daily activities


    ## CHAIN 3a: Narrows down based on Biometric Classifications
    template3a = '''You are a world-class physician. Right now, you are editing a list of personalized postural stability exercises for an individual given their biometric factors.
    
    Instructions:
    Starting out with this list of exercises for each daily activity, delete exercises from this list based on the postural stability score and classification of biometric data for the individual while preserving the other exercises in the list.
     Base your reasoning using a document about the impact of Biometric Factors on the adjustment to exercises. Return a result in the same format as the list of exercises for each daily activity.

    List of exercises for each daily activity: {DA_list_ex}

    The 2 data points:
    1. Postural Stability rating: {PS_rating}
    2. Classification of Biometric Factors of Individual: {Biometric_Factors_class}

    The information document:
    1. Information on Impact of Biometric Factors on Postural Stability Exercise Adjustment: {BF_on_PS_exercises}

    '''

    
    Narrow_Down1 = PromptTemplate(
        input_variables = ['DA_list_ex','PS_rating','Biometric_Factors_class','BF_on_PS_exercises'],
        template = template3a)
    narrow_down_chain1 = LLMChain(llm = llm, prompt = Narrow_Down1, verbose = True)
    narrowed_1 = narrow_down_chain1.run(DA_list_ex = DA_ex_list,PS_rating = st.session_state['PSscore'], Biometric_Factors_class = biom_class, 
                                        BF_on_PS_exercises = bio_adj)

    st.session_state['narrowed1'] = narrowed_1
    # st.write(narrowed_1)

    ## CHAIN 3: Narrows down further based on Past Injuries
    template3b = '''You are a world-class physician. Right now, you are editing a list of personalized postural stability exercises for an individual given their past injuries, and therefore bodily weak points.\
        
        Instructions:
        Starting out with this list of exercises for each daily activity, delete exercises from this list based on information about their past injuries.
        Base your reasoning using a document about the impact of particular injuries to different parts of the body on the adjustment to exercises, and another document about which exercises to avoid for specific injuries.\
              Return a result in the same format as the List of exercises for each daily activity. If there are no items to delete, then preserve and return the entire list. For example, if there are no past injuries, or if the injury rating is low, return the input.\
        
        List of exercises for each daily activity: {DA_list_ex}

        Information about individual's past injuries: {past_injuries}
        note: their injuries each has an injury rating, describing the current pain state of their injury. The injury rating ranges from 1-10 with 1 being no pain and 10 being extreme pain.

        Document with information about how particular injuries affect adjustment to exercises: {I_on_PS_exercises}
        Document with information about which exercises to avoid for specific injuries: {I_avoid_exercises}.
        
        Here should be your thought process: take the injury, and look at the injury's location.\
            Using the information provided about how an injury in particular locations of the body affect adjustment to exercises, and the information about certain exercises to avoid for particular injury locations,\
                assess which exercises to take off the list. Also use the injury pain rating to determine the severity of the injury, and the level to which they can still perform an exercise that targets that particular injury location.\
                    
        Example: [Plantar Fasciitis, 4] --> located in the foot --> look at how foot injuries can affect exercise adjustment and exercises to avoid due to injuries in the foot. Since the rating is 4, the individual can still do medium exercises that put strain on the foot, just not very hard exercises that put strain on the foot.
        '''
    if st.session_state['injuries']:
        Narrow_Down2 = PromptTemplate(
            input_variables = ['DA_list_ex','past_injuries','I_on_PS_exercises','I_avoid_exercises'],
            template = template3b)
        narrow_down_chain2 = LLMChain(llm = llm, prompt = Narrow_Down2, verbose = True)
        narrowed_2 = narrow_down_chain2.run(DA_list_ex = narrowed_1,past_injuries = pat_upload, I_on_PS_exercises = inj_adj, I_avoid_exercises = inj_avoid)

        st.session_state['narrowed2'] = narrowed_2

    # ## CHAIN 4: Fit exercises into schedule based on Daily Exercises: take list of exercises and group them based on which ones they can do during their daily activities
    # template4 = '''Here is a List of exercises for each daily activity: {exercises}\
    #     Instructions:\
    #     Create a weekly circuit by dividing the List of exercises for each daily activity out into 2 sets with {num_ex} exercises to do during each of their daily activities: {daily_acts}.\
        
    #     Here is a layout of the weekly circuit and an example of a set:\
    #         Weekly Circuit:\

    #         Week:\
    #         Set 1: Monday, Tuesday, Wednesday\
    #         Set 2: Thursday, Friday, Saturday\

    #         Example of formatting of a Set for 2 activities per Daily Activity:\
    #         Set 1:\
    #         Daily Activity 1: [List daily activity 1 here]\
    #         - exercise 1
    #         - exercise 2

    #         Daily Activity 2: [List daily activity 2 here]\
    #         - exercise 1
    #         - exercise 2

    #         Daily Activity 3: [List daily activity 3 here]\
    #         - exercise 1
    #         - exercise 2

    #         Daily Activity 4: [List daily activity 4 here]\
    #         - exercise 1
    #         - exercise 2
                
    #         Please return the organized list sets for a week (with their corresponding daily activities and exercises) for each week with proper spacing'''

    # Set_creator = PromptTemplate(
    #     input_variables = ['exercises','num_ex','daily_acts'],
    #     template = template4)
    # sets_chain = LLMChain(llm = llm, prompt = Set_creator, verbose = True)
    # weekly_sets = sets_chain.run(exercises = narrowed_2, num_ex = st.session_state['num_ex'], daily_acts = st.session_state['daily_activities'])

    # st.write(weekly_sets)

    # template4b = '''Evaluate these exercises within this schedule to make sure all of these exercises are fitting daily activity: {schedule}.\
    #     In other words, make sure the exercises can be done under the mobility constraints under each Daily activity: {daily_acts}.\
    #         Switch out exercises from this list of exercises if needed: {exercises}. Return the result with the same format as the schedule.'''
    # Set_evaluator = PromptTemplate(
    #     input_variables = ['schedule','daily_acts','exercises'],
    #     template = template4b)
    # set_eval_chain = LLMChain(llm = llm, prompt = Set_evaluator, verbose = True)
    # sets_new = set_eval_chain.run(schedule = sets, daily_acts = st.session_state['daily_activities'], exercises = narrowed_2)

    # st.write(sets_new)

#############################################################################################################################################################
##### CHAINS FOR POMODORO #########################################################################################################################################################

# ## CHAIN 1: Narrows down based on Biometric Classifications
# ptemplate1 = '''You are a world-class physician. Right now, you are editing a list of personalized postural stability exercises for an individual given their biometric factors.

# Instructions:
# Starting out with this list of exercises, delete exercises from this list based on the classification of biometric data for the individual while preserving the other exercises in the list.
#     Base your reasoning using a document about the impact of Biometric Factors on the adjustment to exercises. Return a result in the same format as the list of exercises.

# List of exercises for each daily activity: {exercises}

# The data point:
# Classification of Biometric Factors of Individual: {Biometric_Factors_class}

# The information document:
# Information on Impact of Biometric Factors on Postural Stability Exercise Adjustment: {BF_on_PS_exercises}

# '''


# Narrow_Down1 = PromptTemplate(
#     input_variables = ['exercises','Biometric_Factors_class','BF_on_PS_exercises'],
#     template = ptemplate1)
# narrow_down_chain1 = LLMChain(llm = llm, prompt = Narrow_Down1, verbose = True)
# narrowed_1 = narrow_down_chain1.run(exercises = ex_75, Biometric_Factors_class = st.session_state['biom_class'], 
#                                     BF_on_PS_exercises = bio_adj)

# # st.write(narrowed_1)

# ## CHAIN 2: Narrows down further based on Past Injuries
# ptemplate2 = '''You are a world-class physician. Right now, you are editing a list of personalized postural stability exercises for an individual given their past injuries, and therefore bodily weak points.\
    
#     Instructions:
#     Starting out with this list of exercises, delete exercises from this list based on information about their past injuries.
#     Base your reasoning using a document about the impact of particular injuries to different parts of the body on the adjustment to exercises, and another document about which exercises to avoid for specific injuries.\
#             Return a result in the same format as the List of exercises.\
    
#     List of exercises: {list_of_ex}

#     Information about individual's past injuries: {past_injuries}
#     note: their injuries each has an injury rating, describing the current pain state of their injury. The injury rating ranges from 1-10 with 1 being no pain and 10 being extreme pain.

#     Document with information about how particular injuries affect adjustment to exercises: {I_on_PS_exercises}
#     Document with information about which exercises to avoid for specific injuries: {I_avoid_exercises}'''

# Narrow_Down2 = PromptTemplate(
#     input_variables = ['list_of_ex','past_injuries','I_on_PS_exercises','I_avoid_exercises'],
#     template = ptemplate2)
# narrow_down_chain2 = LLMChain(llm = llm, prompt = Narrow_Down2, verbose = True)
# narrowed_2 = narrow_down_chain2.run(list_of_ex = narrowed_1,past_injuries = st.session_state['pat_info'], I_on_PS_exercises = inj_adj, I_avoid_exercises = inj_avoid)

# ## CHAIN 3: Turning narrowed_2 list into a list
# ptemplate3 = 'Here is a list of exercises: {list_of_ex} Please turn this list into a python list. Example: [exercise 1, exercise 2, ...]'

# ListFormat = PromptTemplate(
#     input_variables = ['list_of_ex'],
#     template = ptemplate3)
# list_chain = LLMChain(llm = llm, prompt = ListFormat, verbose = True)
# list_of_ex = list_chain.run(list_of_ex = narrowed_2)

# st.session_state['list_of_ex'] = list_of_ex
    