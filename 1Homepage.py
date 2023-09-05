import streamlit as st

st.set_page_config(
    page_title = 'Multipage App',
    page_icon = 'home'
)

st.title("Welcome")
st.sidebar.success("Select a page above")

st.write('Hello, welcome to the Online Postural Stability Assessment and Exercise Generator!')

st.write("This program is meant to aid doctors and physicians in evaluating a patient's postural stability and giving them postural stability exercises that are personalized\
         to their body and their needs.")

st.write('''Here are the steps you should take:
        \n1. Get COP average velocity measured in a Biomechanics Lab
         \n2. Collect biometric information: height, body fat percentage, Q-angle, and more from a qualified physician
         \n3. Set up the patient's account with the patient using the 3rd page: 'Setting Up Account'
         \n4. The patient can generate their exercises based on the pain level of their injuries (if they exist) on the 4th page: 'Personalized Exercise Generator'
         ''')