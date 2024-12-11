from collections.abc import Callable
from pydantic import BaseModel, Field
from cdp_agentkit_core.actions import CdpAction
import requests
import time
from langchain.memory import SimpleMemory

from DoorDash.doordash_utils import doordash_headers, DOORDASH_BASE_URL, handle_doordash_response

GET_DOORDASH_QUOTE_PROMPT = """
This tool will get a quote for a DoorDash delivery. It requires dropoff details from the user (addresses, phone number) to return the fee and estimated delivery time.
"""

# Initialize memory at module level
delivery_memory = SimpleMemory(memories={
    "external_delivery_id": "",
    "phone_number": "",
})

class GetDoorDashQuoteInput(BaseModel):
    """Input argument schema for the action."""

    physical_address: str = Field(
        ...,
        description="The phsyical address of the user, e.g. `124 E 14th St, New York NY 10003`",
    )
    phone_number: str = Field(
        ...,
        description="The phone number of the user in E.164 format, e.g. `+18605029731`",
    )


def get_door_dash_quote(physical_address: str, phone_number: str) -> str:
    """Get a quote for a DoorDash delivery.

    Args:
        physical_address (str): The physical address of the user
        phone_number (str): The phone number of the user

    Returns:
        str: A message containing the quote information
    """

    endpoint = f"{DOORDASH_BASE_URL}/quotes"
    external_delivery_id = f"D-{int(time.time())}"
    headers = doordash_headers()

    # Store delivery details in memory
    delivery_memory.memories.update({
        "external_delivery_id": external_delivery_id,
        "phone_number": phone_number
    })

    request_body = {
        "external_delivery_id": external_delivery_id,
        "dropoff_address": physical_address,
        "dropoff_phone_number": phone_number,
        "pickup_external_business_id": "KFC-123",
        "pickup_external_store_id": "KFC-NYC-242"
        #TODO: have the pickup_external_business_id and pickup_external_store_id be dynamic
    }

    try:
        response = requests.post(endpoint, headers=headers, json=request_body)
        data = handle_doordash_response(response)
        if "error" in data:
            return f"Error getting quote: {data['error']}\nResponse: {data['response_content']}"

        fee_cents = data.get("fee", 0)
        fee_dollars = fee_cents / 100
        dropoff_time_estimated = data.get("dropoff_time_estimated", "")
        return f"Quote obtained: Fee=${fee_dollars:.2f}, Estimated dropoff time: {dropoff_time_estimated}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"

class GetDoorDashQuoteAction(CdpAction):
    name: str = "get_door_dash_quote"
    description: str = GET_DOORDASH_QUOTE_PROMPT
    args_schema: type[BaseModel] | None = GetDoorDashQuoteInput
    func: Callable[..., str] = get_door_dash_quote