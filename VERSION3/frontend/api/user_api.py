from api.client import api_request

def create_user(token, username, password):
    return api_request(
        "POST",
        "/users",
        token=token,
        json={"username": username, "password": password}
    )

def assign_role(token, username, role):
    return api_request(
        "POST",
        "/users/assign-role",
        token=token,
        json={
            "user_name": username,
              "role": role
            }
    )

def list_users(token):
    return api_request(
        "GET",
        "/users/all-users",
        token=token
    )
