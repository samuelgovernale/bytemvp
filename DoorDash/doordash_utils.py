import os
import time
import math
import jwt.utils
import requests

DOORDASH_BASE_URL = "https://openapi.doordash.com/drive/v2"
NETWORK_ID = os.environ.get("NETWORK_ID")

accessKey = {
    "developer_id": os.environ.get("dd_developer_id"),
    "key_id": os.environ.get("dd_key_id"),
    "signing_secret": os.environ.get("dd_signing_secret"),
}

def get_doordash_jwt():
    token = jwt.encode(
        {
            "aud": "doordash",
            "iss": accessKey["developer_id"],
            "kid": accessKey["key_id"],
            "exp": str(math.floor(time.time() + 300)),
            "iat": str(math.floor(time.time())),
        },
        jwt.utils.base64url_decode(accessKey["signing_secret"]),
        algorithm="HS256",
        headers={"dd-ver": "DD-JWT-V1"}
    )
    return token

def doordash_headers():
    return {
        "Accept-Encoding": "application/json",
        "Authorization": f"Bearer {get_doordash_jwt()}",
        "Content-Type": "application/json"
    }

def handle_doordash_response(response: requests.Response):
    try:
        response.raise_for_status()
        return response.json()
    except requests.HTTPError as e:
        return {
            "error": str(e),
            "response_content": response.text
        }
