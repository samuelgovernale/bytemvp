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

import requests

endpoint = "https://openapi.doordash.com/drive/v2/deliveries/"

headers = {"Accept-Encoding": "application/json",
           "Authorization": "Bearer " + token,
           "Content-Type": "application/json"}

request_body = { # Modify pickup and drop off addresses below
    "external_delivery_id": "D-1234567",
    "pickup_address": "901 Market Street 6th Floor San Francisco, CA 94103",
    "pickup_business_name": "Wells Fargo SF Downtown",
    "pickup_phone_number": "+16505555555",
    "pickup_instructions": "Enter gate code 1234 on the callbox.",
    "dropoff_address": "901 Market Street 6th Floor San Francisco, CA 94103",
    "dropoff_business_name": "Wells Fargo SF Downtown",
    "dropoff_phone_number": "+16505555555",
    "dropoff_instructions": "Enter gate code 1234 on the callbox.",
    "order_value": 1999
}

create_delivery = requests.post(endpoint, headers=headers, json=request_body) # Create POST request


print(create_delivery.status_code)
print(create_delivery.text)
print(create_delivery.reason)