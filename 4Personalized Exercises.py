import streamlit as st

if st.session_state['injuries']:
    st.write(st.session_state['narrowed2'])
else:
    st.write(st.session_state['narrowed1'])