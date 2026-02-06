from api.client import api_request

def login(username, password):
    return api_request(
        "POST",
        "/auth/login",
        json={"user_name": username, "password": password}
    )
