from api.client import api_request


def list_playbooks(token):
    res = api_request("GET", "/playbooks/", token)
    return res["playbooks"]


def create_playbook(token, name, title, description):
    return api_request(
        "POST",
        "/playbooks/",
        token,
        {
            "playbook_name": name,
            "title": title,
            "description": description
        }
    )


def delete_playbook(token, playbook_name):
    return api_request(
        "DELETE",
        "/playbooks/",
        token,
        {"playbook_name": playbook_name}
    )
