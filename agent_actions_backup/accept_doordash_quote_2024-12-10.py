from collections.abc import Callable
from pydantic import BaseModel, Field
from cdp_agentkit_core.actions import CdpAction
import requests

from DoorDash.doordash_utils import doordash_headers, DOORDASH_BASE_URL, handle_doordash_response

ACCEPT_DOORDASH_QUOTE_PROMPT = """
This tool accepts a previously obtained quote using the external_delivery_id and optional tip.
"""

class AcceptDoorDashQuoteInput(BaseModel):
    external_delivery_id: str = Field(..., description="The external_delivery_id used when getting the quote.")
    tip: int = Field(default=0, description="Tip amount in cents, e.g. 599 for $5.99")
    dropoff_phone_number: str = Field(..., description="Dropoff phone number in e.g. `8605029731`")

def accept_door_dash_quote(external_delivery_id: str, tip: int, dropoff_phone_number: str) -> str:
    endpoint = f"{DOORDASH_BASE_URL}/quotes/{external_delivery_id}/accept"
    headers = doordash_headers()

    request_body = {
        "tip": tip,
        "dropoff_phone_number": dropoff_phone_number
    }

    try:
        response = requests.post(endpoint, headers=headers, json=request_body)
        data = handle_doordash_response(response)
        if "error" in data:
            return f"Error accepting quote: {data['error']}\nResponse: {data['response_content']}"
        
        return f"Quote accepted. Delivery status: {data.get('delivery_status','unknown')}, Tracking URL: {data.get('tracking_url', '')}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"

class AcceptDoorDashQuoteAction(CdpAction):
    name: str = "accept_door_dash_quote"
    description: str = ACCEPT_DOORDASH_QUOTE_PROMPT
    args_schema: type[BaseModel] | None = AcceptDoorDashQuoteInput
    func: Callable[..., str] = accept_door_dash_quote