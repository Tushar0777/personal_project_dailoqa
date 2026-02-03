# frontend/app.py
import streamlit as st
import requests

BACKEND_URL = "http://localhost:8000"

st.title("📘 Playbook Manager")


resp = requests.get(f"{BACKEND_URL}/playbooks")
playbooks = resp.json()

playbook_ids = [p["playbook_id"] for p in playbooks]

selected = st.selectbox("Select a Playbook", playbook_ids)

if selected:
    pb = requests.get(f"{BACKEND_URL}/playbooks/{selected}").json()

    st.subheader(f"Latest Version: {pb['version']}")

    content = st.text_area(
        "Playbook Content",
        value=pb["content"],
        height=300
    )

    if st.button("Save as New Version"):
        res = requests.post(
            f"{BACKEND_URL}/playbooks/{selected}/versions",
            params={"content": content}
        )

        if res.status_code == 200:
            st.success("New version saved!")
        else:
            st.error("Failed to save version")
