from collections.abc import Callable
from pydantic import BaseModel, Field
from cdp_agentkit_core.actions import CdpAction
import requests
import logging
import time
import os
import json
from langchain.memory import SimpleMemory

from DoorDash.doordash_utils import doordash_headers, DOORDASH_BASE_URL, handle_doordash_response

CHECK_PAYMENT_PROMPT = """
This tool checks whether the user's payment went through and the user successfully paid for their current order.
"""


class CheckPaymentInput(BaseModel):
    """Input argument schema for the action."""


def check_payment(storage: dict, **kwargs) -> str:
    if "charge_id" not in storage:
        return "No charge found for user"

    charge_id = storage.get("charge_id")

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        "X-CC-Api-Key": os.environ.get("COINBASE_COMMERCE_API_KEY"),
    }

    try:
        raw_resp = requests.get(
            f"https://api.commerce.coinbase.com/charges/{charge_id}",
            headers=headers)

        resp = json.loads(raw_resp.text)
        logging.info(f"check payment {resp}")

        timeline = resp['data']['timeline']
        logging.info(f"payment {charge_id} timeline {timeline}")

        success = any(event.get("status") == 'COMPLETED' for event in timeline)

        if success:
            return f"payment succeeded"
        else:
            return f"payment is still pending"

    except Exception as e:
        return f"Unexpected error: {str(e)}"


class CheckPaymentAction(CdpAction):
    name: str = "check_payment"
    description: str = CHECK_PAYMENT_PROMPT
    args_schema: type[BaseModel] | None = CheckPaymentInput
    func: Callable[..., str] = check_payment
