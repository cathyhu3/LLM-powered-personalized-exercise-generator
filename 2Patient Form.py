import streamlit as st

col1, col2 = st.columns([3, 1])

with col1:
   with st.form('form0'):
    st.header("Patient Form")
    name = st.text_input('Name')

    email = st.text_input('Email')

    gender = st.radio('Gender',('Female','Male'))

    past_injuries = st.text_input('''List any of your past injuries and their injury rating **including type of injury and body location**
                                    \n\n\nInput in this format: [injury 1, injury rating 1], [injury 2, injury rating 2]
                                    \nex: [Plantar Fasciitis, 2], [Ankle Sprain, 4]''')
    
    daily_activitiesl = st.multiselect('Please select 4 Daily Activities',['Getting out of bed','Brushing teeth','Walking','Working at a sitting desk',\
                                                                           'Working at a standing desk','Watching TV','Waiting for food to cook/toast'],\
                                                                            max_selections=4)
    daily_activities = str(daily_activitiesl)

    num_of_ex_per_DA = st.radio('Preferred number of exercises per Daily Activity',('1','2','3'))

    submitted0 = st.form_submit_button('Submit')

with col2:
   st.markdown("***Notes***")
   st.write('''Injury rating: rate on 1-10 scale based on this pain chart''')
   st.image('pain_scale.jpeg')
   with st.expander('Sources'):
      st.write('https://specialistshospitalshreveport.com/patient-resources/using-the-pain-scale/')

# Session state variables for Patient Info and Email
if 'pat_info' not in st.session_state:  
    st.session_state['pat_info'] = 0

if 'injuries' not in st.session_state:
   st.session_state['injuries'] = 0

if 'email' not in st.session_state:
   st.session_state['email'] = 0

if 'gender' not in st.session_state:
   st.session_state['gender'] = 0

if 'num_ex' not in st.session_state:
   st.session_state['num_ex'] = 0

if 'daily_activites' not in st.session_state:
   st.session_state['daily_activities'] = 0

if submitted0:
   st.session_state['injuries'] = past_injuries
   st.session_state['email'] = email
   st.session_state['gender'] = gender
   st.session_state['num_ex'] = num_of_ex_per_DA
   st.session_state['daily_activities'] = daily_activities
   col1.success('Submitted Successfully!')
