# import streamlit as st
# from api.playbook_api import list_playbooks
# from api.version_api import list_versions

# def viewer_dashboard():
#     # token = st.session_state["token"]
#     # st.header("Viewer Dashboard")

#     # playbooks = list_playbooks(token)
#     # st.json(playbooks)

#     # pb = st.text_input("Playbook ID")
#     # if st.button("View Versions"):
#     #     st.json(list_versions(token, pb))

#     token = st.session_state["token"]
#     st.header("Viewer Dashboard")

#     playbooks= list_playbooks(token)

#     if not playbooks:
#         st.info("No playbooks available")
#         return
    
#      # --- Playbook Selector ---
#     playbook_map = {
#         f"{pb['title']}": pb for pb in playbooks
#     }

#     selected_title = st.selectbox(
#         "Select a Playbook",
#         playbook_map.keys()
#     )

#     selected_playbook = playbook_map[selected_title]

#      # --- Playbook Meta Info ---
#     st.subheader("Playbook Details")
#     col1, col2 = st.columns(2)

#     col1.markdown(f"**Name:** {selected_playbook['name']}")
#     col1.markdown(f"**Created By:** {selected_playbook.get('created_by', 'N/A')}")

#     # col2.markdown(f"**Playbook ID:** `{selected_playbook['playbook_id']}`")
#     col2.markdown(f"**Created At:** {selected_playbook.get('created_at', 'N/A')}")

#     st.divider()

#     # ---- Versions ----
#     st.subheader("📂 Versions")

#     version_response = list_versions(token, selected_name)
#     versions = version_response.get("versions", [])

#     if not versions:
#         st.warning("No versions found for this playbook")
#         return

#         # ---- Build dropdown ----
#     version_map = {
#             f"Version {v['version']}": v for v in versions
#         }

#     selected_version_label = st.selectbox(
#             "Select Version",
#             version_map.keys()
#         )

#     selected_version = version_map[selected_version_label]

#         # ---- Display selected version ----
#     st.markdown("### Version Details")

#     st.markdown(f"**Version:** {selected_version['version']}")
#     st.markdown(f"**Created At:** {selected_version.get('created_at', '—')}")

#     if "updated_at" in selected_version:
#             st.markdown(f"**Updated At:** {selected_version['updated_at']}")

#     st.markdown("### Content")
#     st.info(selected_version.get("content", "No content"))










# import streamlit as st
# from api.version_api import (
#     list_versions,
#     get_latest_version,
#     get_version
# )
# from api.playbook_api import list_playbooks

# def viewer_dashboard():
#     token = st.session_state["token"]
#     st.header("Viewer Dashboard")

#     # =======================
#     # Playbook Selection
#     # =======================
#     playbooks = list_playbooks(token)

#     if not playbooks:
#         st.info("No playbooks available")
#         return

#     playbook_map = {pb["name"]: pb for pb in playbooks}

#     selected_playbook_name = st.selectbox(
#         "Select a Playbook",
#         list(playbook_map.keys()),
#         index=None,
#         placeholder="Choose a playbook"
#     )

#     if not selected_playbook_name:
#         return  # stop rendering further

#     selected_playbook = playbook_map[selected_playbook_name]

#     # =======================
#     # Playbook Details
#     # =======================
#     st.subheader("Playbook Details")

#     col1, col2 = st.columns(2)
#     col1.markdown(f"**Name:** `{selected_playbook['name']}`")
#     col1.markdown(f"**Title:** {selected_playbook['title']}")

#     col2.markdown(f"**Created At:** {selected_playbook.get('created_at', '—')}")
#     col2.markdown(f"**Created By:** {selected_playbook.get('created_by', '—')}")

#     st.markdown("**Description**")
#     st.info(selected_playbook.get("description", "No description"))

#     st.divider()

#     # =======================
#     # Version Selection
#     # =======================
#     st.subheader("📂 Versions")

#     version_response = list_versions(token, selected_playbook_name)
#     versions = version_response.get("versions", [])

#     if not versions:
#         st.warning("No versions found for this playbook")
#         return

#     version_map = {
#         f"Version {v['version']}": v for v in versions
#     }

#     selected_version_label = st.selectbox(
#         "Select a Version",
#         list(version_map.keys()),
#         index=None,
#         placeholder="Choose a version"
#     )

#     if not selected_version_label:
#         return

#     selected_version = version_map[selected_version_label]

#     # =======================
#     # Version Details
#     # =======================
#     st.subheader("Version Details")

#     st.markdown(f"**Version:** {selected_version['version']}")
#     st.markdown(f"**Created At:** {selected_version.get('created_at', '—')}")

#     if "updated_at" in selected_version:
#         st.markdown(f"**Updated At:** {selected_version['updated_at']}")

#     st.markdown("**Content**")
#     st.info(selected_version.get("content", "No content"))


import streamlit as st
from api.version_api import (
    list_versions,
    get_latest_version,   # <-- NEW (metadata based)
    get_version
)
from api.playbook_api import list_playbooks


def viewer_dashboard():
    token = st.session_state["token"]
    st.header("Viewer Dashboard")

    # =======================
    # Playbook Selection
    # =======================
    playbooks = list_playbooks(token)

    if not playbooks:
        st.info("No playbooks available")
        return

    playbook_map = {pb["name"]: pb for pb in playbooks}

    selected_playbook_name = st.selectbox(
        "Select a Playbook",
        list(playbook_map.keys()),
        index=None,
        placeholder="Choose a playbook"
    )

    if not selected_playbook_name:
        return

    selected_playbook = playbook_map[selected_playbook_name]

    # =======================
    # Playbook Details
    # =======================
    st.subheader("Playbook Details")

    col1, col2 = st.columns(2)
    col1.markdown(f"**Name:** `{selected_playbook['name']}`")
    col1.markdown(f"**Title:** {selected_playbook['title']}")

    col2.markdown(f"**Created At:** {selected_playbook.get('created_at', '—')}")
    col2.markdown(f"**Created By:** {selected_playbook.get('created_by', '—')}")

    st.markdown("**Description**")
    st.info(selected_playbook.get("description", "No description"))

    # -------- Metadata Info (NEW)
    st.markdown("**Metadata**")
    st.markdown(f"• Latest Version: `{selected_playbook.get('latest_version', '—')}`")
    st.markdown(f"• Total Versions: `{selected_playbook.get('total_versions', '—')}`")

    st.divider()

    # =======================
    # Version Section
    # =======================
    st.subheader("📂 Versions")

    # ---- Load all versions (for dropdown)
    version_response = list_versions(token, selected_playbook_name)
    versions = version_response.get("versions", [])

    if not versions:
        st.warning("No versions found for this playbook")
        return

    # ---- Auto-load latest version from metadata
    latest_version_response = get_latest_version(token, selected_playbook_name)
    latest_version_no = latest_version_response.get("version")

    # Map versions
    version_map = {
        f"Version {v['version']}": v for v in versions
    }

    labels = list(version_map.keys())

    # Auto-select latest version index
    default_index = None
    if latest_version_no is not None:
        latest_label = f"Version {latest_version_no}"
        if latest_label in labels:
            default_index = labels.index(latest_label)

    selected_version_label = st.selectbox(
        "Select a Version",
        labels,
        index=default_index,
        placeholder="Choose a version"
    )

    if not selected_version_label:
        return

    selected_version = version_map[selected_version_label]

    # =======================
    # Version Details
    # =======================
    st.subheader("Version Details")

    st.markdown(f"**Version:** {selected_version['version']}")
    st.markdown(f"**Created At:** {selected_version.get('created_at', '—')}")

    if "updated_at" in selected_version:
        st.markdown(f"**Updated At:** {selected_version['updated_at']}")

    st.markdown("**Content**")
    st.info(selected_version.get("content", "No content"))
