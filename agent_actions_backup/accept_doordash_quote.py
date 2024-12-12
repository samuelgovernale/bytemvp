from collections.abc import Callable
from pydantic import BaseModel, Field
from cdp_agentkit_core.actions import CdpAction
import requests

from DoorDash.doordash_utils import doordash_headers, DOORDASH_BASE_URL, handle_doordash_response

ACCEPT_DOORDASH_QUOTE_PROMPT = """
This tool accepts a previously obtained quote using the external_delivery_id and optional tip.
"""


class AcceptDoorDashQuoteInput(BaseModel):
    external_delivery_id: str = Field(
        None,
        description=
        "The external_delivery_id used when getting the quote. If not provided, will use stored value from previous quote."
    )
    tip: int = Field(default=0,
                     description="Tip amount in cents, e.g. 599 for $5.99")
    dropoff_phone_number: str = Field(
        None,
        description=
        "Dropoff phone number in E.164 format, e.g. `+18605029731`. If not provided, will use stored value from previous quote."
    )


def accept_door_dash_quote(external_delivery_id: str = None,
                           tip: int = 0,
                           dropoff_phone_number: str = None,
                           *,
                           storage: dict,
                           **kwargs) -> str:
    """Accept a DoorDash delivery quote."""

    # Use stored values if parameters not provided
    external_delivery_id = external_delivery_id or storage.get(
        "external_delivery_id")
    dropoff_phone_number = dropoff_phone_number or storage.get("phone_number")

    # Validate required information
    if not external_delivery_id or not dropoff_phone_number:
        return "Error: Missing delivery details. Please get a quote first."

    endpoint = f"{DOORDASH_BASE_URL}/quotes/{external_delivery_id}/accept"
    headers = doordash_headers()

    request_body = {"tip": tip, "dropoff_phone_number": dropoff_phone_number}

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
