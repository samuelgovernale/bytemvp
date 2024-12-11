from collections.abc import Callable
from pydantic import BaseModel, Field
from cdp_agentkit_core.actions import CdpAction
import requests

from DoorDash.doordash_utils import doordash_headers, DOORDASH_BASE_URL, handle_doordash_response
from .get_doordash_quote import delivery_memory

GET_DOORDASH_DELIVERY_STATUS_PROMPT = """
When the user asks for an update on the DoorDash delivery status this tool gets the delivery status of a previously obtained quote using the external_delivery_id.
"""

class GetDoorDashDeliveryStatusInput(BaseModel):
    external_delivery_id: str = Field(None, description="The external_delivery_id used when getting the quote. If not provided, will use stored value from previous quote.")


def get_door_dash_delivery_status(external_delivery_id: str = None) -> str:
    """Get the delivery status of a DoorDash delivery."""
    
    # Retrieve stored delivery details if not provided
    stored_details = delivery_memory.load_memory_variables({})
    
    # Use stored values if parameters not provided
    external_delivery_id = external_delivery_id or stored_details.get("external_delivery_id")
    
    # Validate required information
    if not external_delivery_id:
        return "Error: Missing delivery details. Please get a quote first."

    endpoint = f"{DOORDASH_BASE_URL}/deliveries/{external_delivery_id}"
    headers = doordash_headers()

    request_body = {}

    try:
        response = requests.get(endpoint, headers=headers)
        data = handle_doordash_response(response)
        if "error" in data:
            return f"Error getting delivery status: {data['error']}\nResponse: {data['response_content']}"
        
        # Format the delivery status and timing information
        status_info = {
            'status': data.get('delivery_status', 'unknown'),
            'pickup': data.get('pickup_time_estimated', 'not available'),
            'dropoff': data.get('dropoff_time_estimated', 'not available'),
            'tracking_url': data.get('tracking_url', '')
        }
        
        return (
            f"Delivery Status: {status_info['status']}\n"
            f"Estimated Pickup: {status_info['pickup']}\n"
            f"Estimated Dropoff: {status_info['dropoff']}\n"
            f"Tracking URL: {status_info['tracking_url']}"
        )
    except Exception as e:
        return f"Unexpected error: {str(e)}"

class GetDoorDashDeliveryStatusAction(CdpAction):
    name: str = "get_door_dash_delivery_status"
    description: str = GET_DOORDASH_DELIVERY_STATUS_PROMPT
    args_schema: type[BaseModel] | None = GetDoorDashDeliveryStatusInput
    func: Callable[..., str] = get_door_dash_delivery_status