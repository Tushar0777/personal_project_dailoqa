import requests

BASE_URL = "http://localhost:8000"

def api_request(method, endpoint, token=None, json=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    res = requests.request(
        method,
        BASE_URL + endpoint,
        headers=headers,
        json=json
    )

    if res.status_code >= 400:
        raise Exception(res.text)

    return res.json()
