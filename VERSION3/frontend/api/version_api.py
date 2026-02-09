from api.client import api_request

def list_versions(token, playbook_name):
    return api_request("GET", f"/playbooks/{playbook_name}/versions", token)

def create_version(token, playbook_id, content):
    return api_request(
        "POST",
        f"/playbooks/{playbook_id}/versions",
        token,
        {"content": content}
    )

def get_latest_version(token, playbook_name):
    return api_request(
        "GET",
        f"/playbooks/{playbook_name}/versions/latest",
        token
    )

def get_version(token, playbook_name, version):
    return api_request(
        "GET",
        f"/playbooks/{playbook_name}/versions/{version}",
        token
    )
def delete_version(token, playbook_id, version_id):
    return api_request(
        "DELETE",
        f"/playbooks/{playbook_id}/versions/{version_id}",
        token
    )
# @router.put("/{playbook_name}/versions/{version}
def update_version(token,playbook_name,version,content):
    return api_request(
        "PUT",
        f"/playbooks/{playbook_name}/versions/{version}",
        token,
        {"content":content}
    )
