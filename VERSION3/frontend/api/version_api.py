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

def delete_version(token, playbook_id, version_id):
    return api_request(
        "DELETE",
        f"/playbooks/{playbook_id}/versions/{version_id}",
        token
    )
