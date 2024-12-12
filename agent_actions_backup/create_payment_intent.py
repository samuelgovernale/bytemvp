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

PAYMENT_INTENT_QUOTE_PROMPT = """
This tool will create a payment that the user can pay online with Coinbase Commerce. The result of this tool contains a payment url that needs to be show to the user. This payment only needs to be created once the user confirms they wish to pay and that the menu selection is confirmed.
"""


class PaymentIntentInput(BaseModel):
    """Input argument schema for the action."""

    checkout_id: str = Field(
        ...,
        description=
        "Checkout ID for the selected product, looks like UUID: 500bda97-f137-4bea-a044-16db74a9561b",
    )


def create_payment_intent(checkout_id: str, *, storage: dict, **kwargs) -> str:
    request_body = {
        "checkout_id": "499ace89-f137-4bea-a044-16db74a9468e",
    }

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        "X-CC-Api-Key": os.environ.get("COINBASE_COMMERCE_API_KEY"),
    }

    try:
        raw_resp = requests.post("https://api.commerce.coinbase.com/charges",
                                 headers=headers,
                                 json=request_body)

        resp = json.loads(raw_resp.text)
        logging.info(f"payment {resp}")

        storage['charge_id'] = resp['data']["id"]

        return f"payment url is {resp['data']['hosted_url']}"

    except Exception as e:
        return f"Unexpected error: {str(e)}"


class PaymentIntentAction(CdpAction):
    name: str = "create_payment_intent"
    description: str = PAYMENT_INTENT_QUOTE_PROMPT
    args_schema: type[BaseModel] | None = PaymentIntentInput
    func: Callable[..., str] = create_payment_intent
