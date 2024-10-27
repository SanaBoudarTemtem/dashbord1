import streamlit as st
from src.pages.auth.login_ui import show_login
from src.pages.auth.login_auth import authenticate
from src.pages.dashboard_page import show_dashboard_page

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

def main():
    st.title("Temtemone Submissions Dashboard")

    # Show the appropriate content based on login status
    if st.session_state.logged_in:
        # Create a sidebar for navigation only if logged in
        st.sidebar.title("Navigation")
        st.sidebar.button("Logout", on_click=logout)
        
        # Show the dashboard when logged in
        show_dashboard_page()
    else:
        # Only show the login UI when not logged in
        show_login()  

def logout():
    st.session_state.logged_in = False
    st.success("You have been logged out.")

if __name__ == "__main__":
    main()
