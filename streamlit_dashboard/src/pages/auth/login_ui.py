import streamlit as st
from src.pages.auth.login_auth import authenticate

def show_login():
    st.subheader("Login to the Dashboard")
    
    # Create a form for the user to input their credentials
    with st.form(key='login_form'):
        username = st.text_input("Username")
        password = st.text_input("Password", type='password')
        submit_button = st.form_submit_button("Login")

    if submit_button:
        # Call the authenticate function with the provided credentials
        if authenticate(username, password):
            st.session_state.logged_in = True
            st.success("Logged in successfully!")
            # st.experimental_rerun()  # Reload the app to show the dashboard
        else:
            st.error("Invalid username or password. Please try again.")
