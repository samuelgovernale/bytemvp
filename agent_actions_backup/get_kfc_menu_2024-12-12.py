from collections.abc import Callable
from pydantic import BaseModel
from cdp_agentkit_core.actions import CdpAction
import json
from pathlib import Path

# Define the prompt for the action
GET_KFC_MENU_PROMPT = """
This tool retrieves the KFC menu items, including details like descriptions, prices, calories, and images.
It can show all available menu items to help users make their selection.
"""

class GetKFCMenuInput(BaseModel):
    """Input schema left empty as no parameters are needed to fetch the menu"""
    pass

def get_kfc_menu() -> str:
    """
    Retrieves and formats KFC menu items from the JSON file.
    
    Returns:
        str: Formatted string containing menu items with their details
    """
    try:
        # Read the menu JSON file
        # Note: Adjust the path according to your project structure
        menu_path = Path("menu/kfc/kfc_menu.json")
        with open(menu_path, 'r') as file:
            menu_data = json.load(file)

        # Format the menu items into a readable string
        menu_output = "🍗 KFC Menu Items:\n\n"
        
        for item in menu_data.get("menuItems", []):
            # Format each menu item with relevant details
            menu_output += (
                f"📌 {item['name']}\n"
                f"Description: {item['description']}\n"
                f"Price: ${item['price']:.2f}\n"
                f"Calories: {item['calories']}\n"
                f"Image: {item['image']}\n"
                f"Components:\n"
            )
            
            # Add component details
            components = item.get("components", {})
            for comp_type, comp_details in components.items():
                menu_output += f"  - {comp_type}: {comp_details.get('name', '')} "
                if "size" in comp_details:
                    menu_output += f"({comp_details['size']}) "
                menu_output += f"x{comp_details.get('quantity', 1)}\n"
            
            menu_output += "\n" + "-"*50 + "\n\n"

        return menu_output

    except FileNotFoundError:
        return "Error: Menu file not found."
    except json.JSONDecodeError:
        return "Error: Invalid menu file format."
    except Exception as e:
        return f"Unexpected error: {str(e)}"

class GetKFCMenuAction(CdpAction):
    name: str = "get_kfc_menu"
    description: str = GET_KFC_MENU_PROMPT
    args_schema: type[BaseModel] | None = GetKFCMenuInput
    func: Callable[..., str] = get_kfc_menu