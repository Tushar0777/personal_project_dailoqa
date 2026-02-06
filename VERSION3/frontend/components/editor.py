import streamlit as st
from api.playbook_api import list_playbooks
from api.version_api import create_version, delete_version, list_versions

def editor_dashboard():
    token = st.session_state["token"]
    st.header("Editor Dashboard")

    playbooks = list_playbooks(token)
    st.json(playbooks)

    pb = st.text_input("Playbook ID")
    content = st.text_area("Version Content")

    if st.button("Create Version"):
        st.success(create_version(token, pb, content))

    vid = st.text_input("Version ID")
    if st.button("Delete Version"):
        st.success(delete_version(token, pb, vid))

    if st.button("List Versions"):
        st.json(list_versions(token, pb))
