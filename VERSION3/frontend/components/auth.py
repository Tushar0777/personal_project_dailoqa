import streamlit as st
from api.auth_api import login

def login_ui():
    st.title("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    # if st.button("Login"):
    #     try:
    #         res = login(username, password)
    #         st.session_state["token"] = res["access_token"]
    #         st.session_state["role"] = res["role"]
    #         st.success("Login successful")
    #         st.rerun()
    #     except Exception as e:
    #         st.error(str(e))
    if st.button("Login"):
        try:
            res = login(username, password)

            role = res["role"][0]   # 🔥 LIST → STRING

            st.session_state["token"] = res["access_token"]
            st.session_state["role"] = role

            st.success(f"Login successful as {role}")
            st.rerun()

        except Exception as e:
            st.error(str(e))
