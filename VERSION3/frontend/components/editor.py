import streamlit as st
from api.playbook_api import list_playbooks,create_playbook,delete_playbook
from api.version_api import create_version, delete_version, list_versions,update_version

# def editor_dashboard():
#     token = st.session_state["token"]
#     st.header("Editor Dashboard")

#     # playbooks = list_playbooks(token)
#     # st.json(playbooks)

#     pb = st.text_input("Playbook ID")
#     content = st.text_area("Version Content")

#     if st.button("Create Version"):
#         st.success(create_version(token, pb, content))

#     vid = st.text_input("Version ID")
#     if st.button("Delete Version"):
#         st.success(delete_version(token, pb, vid))

#     if st.button("List Versions"):
#         st.json(list_versions(token, pb))

# def show_success(message):
#     st.success(f"✅ {message}")
#     st.toast(message)

# def editor_dashboard():
#     token = st.session_state["token"]
#     st.header("Editor Dashboard")

#     with st.expander("Versions"):
#         # ----------------------------
#         # PLAYBOOK SELECTION
#         # ----------------------------
#         playbooks = list_playbooks(token)

#         if not playbooks:
#             st.warning("Create a playbook first")
#             return

#         pb_map = {pb["name"]: pb for pb in playbooks}

#         pb_name = st.selectbox(
#             "Select Playbook",
#             list(pb_map.keys()),
#             index=None,
#             placeholder="Choose playbook",
#             key="pb_select"
#         )

#         if not pb_name:
#             st.info("Select a playbook to manage versions")
#             return

#         selected_pb = pb_map[pb_name]

#         st.markdown(
#             f"""
#             **Latest Version:** `{selected_pb.get("latest_version", 0)}`
            
#             **Total Versions:** `{selected_pb.get("total_versions", 0)}`
#             """
#         )

#         # ----------------------------
#         # LIST VERSIONS (BACKEND CONTRACT SAFE)
#         # ----------------------------
#         resp = list_versions(token, pb_name)
#         versions = resp.get("versions", [])

#         if not versions:
#             st.warning("No versions found for this playbook")
#             return

#         # version -> full object
#         version_map = {v["version"]: v for v in versions}
#         version_numbers = sorted(version_map.keys())

#         # ----------------------------
#         # VERSION SELECTION
#         # ----------------------------
#         selected_version = st.selectbox(
#             "Select Version",
#             version_numbers,
#             index=len(version_numbers) - 1,
#             key="ver_select"
#         )

#         current_version = version_map[selected_version]
#         is_latest = selected_version == max(version_numbers)

#         # ----------------------------
#         # CONTENT EDITOR
#         # ----------------------------
#         content = st.text_area(
#             "Version Content",
#             value=current_version["content"],
#             height=300,
#             key="ver_content",
#             disabled=not is_latest  # old versions read-only
#         )

#         st.caption(
#             f"Created at: {current_version['created_at']} | "
#             f"Version: {selected_version}"
#         )

#         col1, col2 = st.columns(2)

#         # ----------------------------
#         # UPDATE CURRENT VERSION
#         # ----------------------------
#         with col1:
#             if st.button("Update Version", key="ver_update", disabled=not is_latest):
#                 if not content.strip():
#                     st.error("Version content required")
#                 else:
#                     try:
#                         update_version(
#                             token=token,
#                             playbook_name=pb_name,
#                             version=selected_version,
#                             content=content
#                         )
#                         show_success(f"Version `{selected_version}` updated")
#                         st.rerun()
#                     except Exception as e:
#                         st.error(e)

#         # ----------------------------
#         # CREATE NEW VERSION
#         # ----------------------------
#         with col2:
#             if st.button("Create New Version", key="ver_create"):
#                 if not content.strip():
#                     st.error("Version content required")
#                 else:
#                     try:
#                         create_version(
#                             token=token,
#                             playbook_name=pb_name,
#                             content=content
#                         )
#                         show_success(f"New version added to `{pb_name}`")
#                         st.rerun()
#                     except Exception as e:
#                         st.error(e)

# def editor_dashboard():
#     token = st.session_state["token"]
#     st.header("Editor Dashboard")

#     with st.expander("Versions"):
#         # ----------------------------
#         # PLAYBOOK SELECTION
#         # ----------------------------
#         playbooks = list_playbooks(token)

#         if not playbooks:
#             st.warning("Create a playbook first")
#             return

#         pb_map = {pb["name"]: pb for pb in playbooks}

#         pb_name = st.selectbox(
#             "Select Playbook",
#             list(pb_map.keys()),
#             index=None,
#             placeholder="Choose playbook",
#             key="pb_select"
#         )

#         if not pb_name:
#             st.info("Select a playbook to manage versions")
#             return

#         selected_pb = pb_map[pb_name]

#         st.markdown(
#             f"""
#             **Latest Version:** `{selected_pb.get("latest_version", 0)}`
            
#             **Total Versions:** `{selected_pb.get("total_versions", 0)}`
#             """
#         )

#         # ----------------------------
#         # LIST VERSIONS
#         # ----------------------------
#         resp = list_versions(token, pb_name)
#         versions = resp.get("versions", [])

#         # =====================================================
#         # CASE 1: NO VERSION EXISTS → ONLY CREATE FLOW
#         # =====================================================
#         if not versions:
#             st.info("No versions exist yet. Create the first version.")

#             content = st.text_area(
#                 "Version Content",
#                 key="ver_content",
#                 height=300
#             )

#             if st.button("Create Version", key="ver_create"):
#                 if not content.strip():
#                     st.error("Version content required")
#                 else:
#                     try:
#                         create_version(token, pb_name, content)
#                         show_success(f"First version created for `{pb_name}`")
#                         st.rerun()
#                     except Exception as e:
#                         st.error(e)

#             return  # 👈 IMPORTANT: stop here

#         # =====================================================
#         # CASE 2: VERSIONS EXIST → SELECT / UPDATE / CREATE
#         # =====================================================
#         version_map = {v["version"]: v for v in versions}
#         version_numbers = sorted(version_map.keys())

#         selected_version = st.selectbox(
#             "Select Version",
#             version_numbers,
#             index=len(version_numbers) - 1,
#             key="ver_select"
#         )

#         current_version = version_map[selected_version]
#         is_latest = selected_version == max(version_numbers)

#         content = st.text_area(
#             "Version Content",
#             value=current_version["content"],
#             key="ver_content",
#             height=300,
#             disabled=not is_latest
#         )

#         st.caption(
#             f"Created at: {current_version['created_at']} | "
#             f"Version: {selected_version}"
#         )

#         col1, col2 = st.columns(2)

#         # ----------------------------
#         # UPDATE VERSION
#         # ----------------------------
#         with col1:
#             if st.button("Update Version", key="ver_update", disabled=not is_latest):
#                 if not content.strip():
#                     st.error("Version content required")
#                 else:
#                     try:
#                         update_version(
#                             token=token,
#                             playbook_name=pb_name,
#                             version=selected_version,
#                             content=content
#                         )
#                         show_success(f"Version `{selected_version}` updated")
#                         st.rerun()
#                     except Exception as e:
#                         st.error(e)

#         # ----------------------------
#         # CREATE NEW VERSION
#         # ----------------------------
#         with col2:
#             if st.button("Create New Version", key="ver_create"):
#                 if not content.strip():
#                     st.error("Version content required")
#                 else:
#                     try:
#                         create_version(token, pb_name, content)
#                         show_success(f"New version added to `{pb_name}`")
#                         st.rerun()
#                     except Exception as e:
#                         st.error(e)

def show_success(message):
    st.success(f"✅ {message}")
    st.toast(message)

def editor_dashboard():
    token = st.session_state["token"]
    st.header("Editor Dashboard")

    with st.expander("Versions"):
        # ----------------------------
        # PLAYBOOK SELECTION
        # ----------------------------
        playbooks = list_playbooks(token)

        if not playbooks:
            st.warning("Create a playbook first")
            return

        pb_map = {pb["name"]: pb for pb in playbooks}

        pb_name = st.selectbox(
            "Select Playbook",
            list(pb_map.keys()),
            index=None,
            placeholder="Choose playbook",
            key="pb_select"
        )

        if not pb_name:
            st.info("Select a playbook to manage versions")
            return

        selected_pb = pb_map[pb_name]

        st.markdown(
            f"""
            **Latest Version:** `{selected_pb.get("latest_version", 0)}`
            
            **Total Versions:** `{selected_pb.get("total_versions", 0)}`
            """
        )

        # ----------------------------
        # LIST VERSIONS
        # ----------------------------
        resp = list_versions(token, pb_name)
        versions = resp.get("versions", [])

        # =====================================================
        # CASE 1: NO VERSION EXISTS → ONLY CREATE FLOW
        # =====================================================
        if not versions:
            st.info("No versions exist yet. Create the first version.")

            content = st.text_area(
                "Version Content",
                key="ver_content",
                height=300
            )

            if st.button("Create Version", key="ver_create"):
                if not content.strip():
                    st.error("Version content required")
                else:
                    try:
                        create_version(token, pb_name, content)
                        show_success(f"First version created for `{pb_name}`")
                        st.rerun()
                    except Exception as e:
                        st.error(e)

            return  # 👈 IMPORTANT: stop here

        # =====================================================
        # CASE 2: VERSIONS EXIST → SELECT / UPDATE / CREATE
        # =====================================================
        version_map = {v["version"]: v for v in versions}
        version_numbers = sorted(version_map.keys())

        selected_version = st.selectbox(
            "Select Version",
            version_numbers,
            index=len(version_numbers) - 1,
            key="ver_select"
        )

        current_version = version_map[selected_version]
        is_latest = selected_version == max(version_numbers)

        content = st.text_area(
            "Version Content",
            value=current_version["content"],
            key="ver_content",
            height=300,
            disabled=not is_latest
        )

        st.caption(
            f"Created at: {current_version['created_at']} | "
            f"Version: {selected_version}"
        )

        col1, col2 = st.columns(2)

        # ----------------------------
        # UPDATE VERSION
        # ----------------------------
        with col1:
            if st.button("Update Version", key="ver_update", disabled=not is_latest):
                if not content.strip():
                    st.error("Version content required")
                else:
                    try:
                        update_version(
                            token=token,
                            playbook_name=pb_name,
                            version=selected_version,
                            content=content
                        )
                        show_success(f"Version `{selected_version}` updated")
                        st.rerun()
                    except Exception as e:
                        st.error(e)

        # ----------------------------
        # CREATE NEW VERSION
        # ----------------------------
        with col2:
            if st.button("Create New Version", key="ver_create"):
                if not content.strip():
                    st.error("Version content required")
                else:
                    try:
                        create_version(token, pb_name, content)
                        show_success(f"New version added to `{pb_name}`")
                        st.rerun()
                    except Exception as e:
                        st.error(e)
