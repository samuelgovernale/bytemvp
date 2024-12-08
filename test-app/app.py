from os import access
import jwt.utils
import time
import math

accessKey = {
  "developer_id": "afb0b74e-d0c8-4520-9818-5f35dd222626",
  "key_id": "80292a83-c57e-4dd8-b775-761b0d592557",
  "signing_secret": "CE_xMOBi56_uegC-rQfm1_zsP2Nxgr73ozSbARxMg2E"
}

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
    headers={"dd-ver": "DD-JWT-V1"})

print(token)