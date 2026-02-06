import streamlit as st
from components.auth import login_ui
from components.admin import admin_dashboard
from components.editor import editor_dashboard
from components.viewer import viewer_dashboard
from state.session import logout

st.set_page_config(page_title="RBAC Playbook UI", layout="wide")

if "token" not in st.session_state:
    login_ui()
else:
    st.sidebar.button("Logout", on_click=logout)

    role = st.session_state.get("role")

    if role == "ADMIN":
        admin_dashboard()
    elif role == "EDITOR":
        editor_dashboard()
    else:
        viewer_dashboard()

# PS D:\Local Disk (D)\Dailoqa(Intern)\30jan_project\version1\VERSION3> streamlit
#  run frontend/streamlit_app.py