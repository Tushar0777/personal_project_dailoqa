import streamlit as st
from api.playbook_api import list_playbooks
from api.version_api import list_versions

def viewer_dashboard():
    token = st.session_state["token"]
    st.header("Viewer Dashboard")

    playbooks = list_playbooks(token)
    st.json(playbooks)

    pb = st.text_input("Playbook ID")
    if st.button("View Versions"):
        st.json(list_versions(token, pb))
