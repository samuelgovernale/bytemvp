from collections.abc import Callable
from decimal import Decimal

from cdp import Wallet, Cdp
from pydantic import BaseModel, Field
from cdp.address import Address
from web3 import Web3

from cdp_agentkit_core.actions import CdpAction

import os

import json

from os import access
import jwt.utils
import time
import math
import requests

NETWORK_ID = os.environ.get("NETWORK_ID")

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

GET_DOORDASH_QUOTE_PROMPT = """
This tool will get a quote for a DoorDash delivery and return the quoted fee to the user. It takes the user's physical address location and phone number as input"""


class GetDoorDashQuoteInput(BaseModel):
    """Input argument schema for the action."""

    pyhsical_address: str = Field(
        ...,
        description="The phsyical address of the user, e.g. `242 E 14th St, New York NY 10003-4105, United States`",
    )
    phone_number: str = Field(
        ...,
        description="The phone number of the user, e.g. `8605029731`",
    )

def get_door_dash_quote(physical_address: str, phone_number: str) -> str:
    """Get a quote for a DoorDash delivery.

    Args:
        physical_address (str): The physical address of the user
        phone_number (str): The phone number of the user

    Returns:
        str: A message containing the quote information
    """
    try:
        # API endpoint for DoorDash quotes
        endpoint = "https://openapi.doordash.com/drive/v2/quotes"
        
        # Generate unique delivery ID using timestamp
        delivery_id = f"D-{int(time.time())}"
        
        # Construct request headers with JWT token
        headers = {
            "Accept-Encoding": "application/json",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Construct request body with required parameters
        request_body = {
            "external_delivery_id": delivery_id,
            "dropoff_address": physical_address,
            "dropoff_phone_number": phone_number,
            # Using sample pickup location (KFC) for demo
            "pickup_external_business_id": "KFC-123",
            "pickup_external_store_id": "KFC-NYC-242"
        }
        
        # Make POST request to DoorDash API
        response = requests.post(endpoint, headers=headers, json=request_body)
        response.raise_for_status()  # Raise exception for non-200 status codes
        
        # Parse response and extract fee
        quote_data = response.json()
        fee_in_cents = quote_data.get('fee', 0)
        fee_in_dollars = fee_in_cents / 100  # Convert cents to dollars
        
        # Format response message with fee and estimated delivery time
        estimated_delivery = quote_data.get('dropoff_time_estimated', '').replace('T', ' ').replace('Z', ' UTC')
        return f"Delivery quote: ${fee_in_dollars:.2f}\nEstimated delivery time: {estimated_delivery}"

    except requests.RequestException as e:
        return f"Error getting DoorDash quote: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"

class GetDoorDashQuoteAction(CdpAction):
    """Get a quote for a DoorDash delivery."""

    name: str = "get_door_dash_quote"
    description: str = GET_DOORDASH_QUOTE_PROMPT
    args_schema: type[BaseModel] | None = GetDoorDashQuoteInput
    func: Callable[..., str] = get_door_dash_quote
