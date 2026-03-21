import requests
from django.core.exceptions import ObjectDoesNotExist
import logging
from .models import NewOrder

logger = logging.getLogger(__name__)

APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbz_x4y1xhXBfDQmajQfGo5yKujP_jm2GuMWe3qzmf02-TIGXoUcIjFxbLs9uLsvpgFV/exec"

def save_order_to_sheets(order: NewOrder):
    """
    Save order data to Google Sheet via Apps Script.
    Columns: Timestamp, Username, Address, Mobile, Product Code, Quantity, Price, Size
    """
    try:
        # Use order.price (total)
        total_price: float = float(order.price)

        # Username
        username: str = order.user.username if order.user and order.user.username else "Anonymous"

        payload: dict[str, str | float] = {
            "username": username,
            "address": order.address,
            "mobile": order.mobile_number,
            "product_code": order.product_code,
            "quantity": order.quantity,
            "price": total_price,
            "size": order.size or ""
        }

        response = requests.post(APPS_SCRIPT_URL, json=payload)
        response.raise_for_status()

        order_id = getattr(order, 'id', 'unknown')
        print("Apps Script Response:", response.text)
        logger.info(f"Order {order_id} saved to Apps Script successfully.")

    except ObjectDoesNotExist:
        error_msg = f"Product {order.product_code} not found."
        print("Error:", error_msg)
        logger.error(error_msg)
    except requests.RequestException as e:
        error_msg = f"Apps Script request failed: {str(e)}"
        print(error_msg)
        logger.error(error_msg)
    except Exception as e:
        error_msg = f"Error saving to Apps Script: {str(e)}"
        print(error_msg)
        logger.error(f"Error saving order {getattr(order, 'id', 'unknown')}: {str(e)}")

