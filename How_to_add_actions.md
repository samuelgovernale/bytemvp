Instructions for adding actions to the agent.

1. Create the .py action file (See example /home/runner/bytemvp/.pythonlibs/lib/python3.12/site-packages/cdp_agentkit_core/actions/get_doordash_quote.py) (take note of any CDP kit dependencies)
2. Import the action into the agent __init__.py file here: /home/runner/bytemvp/.pythonlibs/lib/python3.12/site-packages/cdp_agentkit_core/actions/__init__.py
Example: from cdp_agentkit_core.actions.get_doordash_quote import GetDoorDashQuoteAction
3. Add the action class to the list of the agent's CDP_ACTIONS in file here /home/runner/bytemvp/.pythonlibs/lib/python3.12/site-packages/cdp_agentkit_core/actions/__init__.py
CDP_ACTIONS = get_all_cdp_actions()

__all__ = [
    "CdpAction",
    "GetWalletDetailsAction",
    "DeployNftAction",
    "DeployTokenAction",
    "GetBalanceAction",
    "MintNftAction",
    "RegisterBasenameAction",
    "RequestFaucetFundsAction",
    "TradeAction",
    "TransferAction",
    "WowCreateTokenAction",
    "WowBuyTokenAction",
    "WowSellTokenAction",
    "GetDoorDashQuoteAction",
    "CDP_ACTIONS",
]