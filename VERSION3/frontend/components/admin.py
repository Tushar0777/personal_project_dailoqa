import streamlit as st
from api.user_api import create_user, assign_role
from api.playbook_api import create_playbook, list_playbooks, delete_playbook
from api.version_api import create_version, list_versions, delete_version
from api.user_api import list_users


import streamlit as st
from api.user_api import create_user, assign_role, list_users
from api.playbook_api import create_playbook, list_playbooks, delete_playbook
from api.version_api import create_version, list_versions
from components.viewer import viewer_dashboard

def show_success(message):
    st.success(f"✅ {message}")
    st.toast(message)


def admin_dashboard():
    token = st.session_state["token"]
    st.header("Admin Dashboard")

    # ---------- CREATE USER ----------
    with st.expander("Create User"):
        u = st.text_input("New Username", key="cu_u")
        p = st.text_input("Password", type="password", key="cu_p")

        if st.button("Create User", key="cu_btn"):
            if not u or not p:
                st.error("Username & password required")
            else:
                try:
                    res = create_user(token, u, p)
                    show_success(
                        f"User `{res['username']}` created with role VIEWER"
                    )
                    st.rerun()
                except Exception as e:
                    st.error(e)



    # ---------- PLAYBOOKS ----------
    with st.expander("Playbooks"):
        name = st.text_input("Playbook Name", key="pb_name")
        title = st.text_input("Title", key="pb_title")
        description = st.text_area("Description", key="pb_desc", height=100)

        if st.button("Create Playbook", key="pb_create"):
            if not name:
                st.error("Playbook name required")
            else:
                try:
                    create_playbook(token, name,title,description)
                    show_success(f"Playbook `{name}` created")
                    st.rerun()
                except Exception as e:
                    st.error(e)

        playbooks = list_playbooks(token)

        if playbooks:
            for p in playbooks:
                col1, col2 = st.columns([4, 1])
                # col1.write(p["name"])
                col1.write(
                    f"{p['name']}  "
                    f"(latest: {p.get('latest_version', 0)}, "
                    f"total: {p.get('total_versions', 0)})"
                )

                if col2.button("Delete", key=f"del_{p['name']}"):
                    delete_playbook(token, p["name"])
                    st.success("Deleted")
                    st.rerun()
        else:
            st.info("No playbooks found")

    # ---------- VERSIONS ----------

    # with st.expander("Versions"):
    #     playbooks = list_playbooks(token)

    #     if not playbooks:
    #         st.warning("Create a playbook first")
    #         return

    #     # pb_name = st.selectbox(
    #     #     "Select Playbook",
    #     #     [p["name"] for p in playbooks],
    #     #     key="ver_pb"
    #     # )
    #     pb_map = {pb["name"]: pb for pb in playbooks}
    #     pb_name = st.selectbox(
    #         "Select Playbook",
    #         list(pb_map.keys()),
    #         index=None,
    #         placeholder="Choose playbook"
    #     )

    #     if not pb_name:
    #         st.info("Select a playbook to create version")
    #         return
    #     selected_pb = pb_map[pb_name]
    #     st.markdown(
    #         f"""
    #         **Latest Version:** `{selected_pb.get("latest_version", 0)}`
            
    #         **Total Versions:** `{selected_pb.get("total_versions", 0)}`
    #         """
    #     )
    #     content = st.text_area("Version Content", key="ver_content")

    #     if st.button("Create Version", key="ver_create"):
    #         if not content:
    #             st.error("Version content required")
    #         else:
    #             try:
    #                 create_version(token, pb_name, content)
    #                 show_success(f"New version added to `{pb_name}`")
    #             except Exception as e:
    #                 st.error(e)

        # if st.button("List Versions", key="ver_list"):
        #     try:
        #         versions = list_versions(token, pb_name)
        #         st.subheader("Versions")
        #         st.json(versions)
        #     except Exception as e:
        #         st.error(e)

        # ye abhi abhi admin change jab total_version changes kare the tab change kara hai 
        # if playbooks:
        #     pb_name = st.selectbox(
        #         "Select Playbook",
        #         [p["name"] for p in playbooks],
        #         key="ver_playbook"
        #     )

    with st.expander("Versions"):
        playbooks = list_playbooks(token)

        if not playbooks:
            st.warning("Create a playbook first")
        else:
            pb_map = {pb["name"]: pb for pb in playbooks}

            pb_name = st.selectbox(
                "Select Playbook",
                list(pb_map.keys()),
                index=None,
                placeholder="Choose playbook"
            )

            if pb_name:
                selected_pb = pb_map[pb_name]

                st.markdown(
                    f"""
                    **Latest Version:** `{selected_pb.get("latest_version", 0)}`
                    
                    **Total Versions:** `{selected_pb.get("total_versions", 0)}`
                    """
                )

                content = st.text_area("Version Content", key="ver_content")

                if st.button("Create Version", key="ver_create"):
                    if not content.strip():
                        st.error("Version content required")
                    else:
                        try:
                            create_version(token, pb_name, content)
                            show_success(f"New version added to `{pb_name}`")
                            st.rerun()
                        except Exception as e:
                            st.error(e)
            else:
                st.info("Select a playbook to create version")

    
    # ---------- ASSIGN ROLE ----------

    with st.expander("Assign Role"):
        users_resp = list_users(token)
        users = users_resp.get("users", [])

        usernames = [u["username"] for u in users]

        selected_username = st.selectbox(
            "Select User",
            usernames,
            key="assign_role_user"
        )

        selected_role = st.selectbox(
            "Select Role",
            ["ADMIN", "EDITOR", "VIEWER"],
            key="assign_role_role"
        )

        if st.button("Assign Role"):
            try:
                resp = assign_role(token, selected_username, selected_role)

                if resp["status"] == "ROLE_ASSIGNED":
                    st.success(
                        f"✅ Role `{selected_role}` assigned to `{selected_username}`"
                    )

                elif resp["status"] == "ROLE_ALREADY_ASSIGNED":
                    st.warning(
                        f"⚠️ `{selected_username}` already has role `{selected_role}`"
                    )

                else:
                    st.info(resp)

            except Exception as e:
                st.error(f"❌ {e}")


    with st.expander("View Playbooks (Read Only)"):
            viewer_dashboard()
        



# def admin_dashboard():
#     token = st.session_state["token"]

#     st.header("Admin Dashboard")

#     # ---------- CREATE USER ----------
#     with st.expander("Create User"):
#         u = st.text_input("New Username", key="create_user_username")
#         p = st.text_input("Password", type="password", key="create_user_password")

#         if st.button("Create User", key="create_user_btn"):
#             if not u or not p:
#                 st.error("Username & password required")
#             else:
#                 st.success(create_user(token, u, p))
#                 st.session_state["create_user_username"] = ""
#                 st.session_state["create_user_password"] = ""

#     # ---------- ASSIGN ROLE ----------
#     with st.expander("Assign Role"):
#         u = st.text_input("Target Username", key="assign_role_username")
#         r = st.selectbox(
#             "Role",
#             ["ADMIN", "EDITOR", "VIEWER"],
#             key="assign_role_select"
#         )

#         if st.button("Assign", key="assign_role_btn"):
#             if not u:
#                 st.error("Username required")
#             else:
#                 st.success(assign_role(token, u, r))
#                 st.session_state["assign_role_username"] = ""

#     # ---------- PLAYBOOKS ----------
#     with st.expander("Playbooks"):
#         name = st.text_input("Playbook Name", key="playbook_name")

#         if st.button("Create Playbook", key="create_playbook_btn"):
#             st.success(create_playbook(token, name))

#         playbooks = list_playbooks(token)
#         for p in playbooks:
#             st.write(p["name"])
#             if st.button(f"Delete {p['name']}", key=f"del_{p['name']}"):
#                 delete_playbook(token, p["name"])
#                 st.success("Deleted")
#                 st.rerun()

        
#     with st.expander("Versions"):
#         pb = st.text_input("Playbook ID")
#         content = st.text_area("Version Content")
#         if st.button("Create Version"):
#             st.success(create_version(token, pb, content))

#         if st.button("List Versions"):
#             st.json(list_versions(token, pb))

