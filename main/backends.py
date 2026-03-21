import requests
from django.core.exceptions import ObjectDoesNotExist
import logging
from django.conf import settings
from .models import NewOrder

logger = logging.getLogger(__name__)

APPS_SCRIPT_URL = getattr(settings, 'APPS_SCRIPT_URL', '')

def save_order_to_sheets(order: NewOrder):
 
    if not APPS_SCRIPT_URL:
        logger.warning("APPS_SCRIPT_URL not configured - skipping sheet save")
        return
        
    try:
        # Use order.price (total)
        total_price: float = float(order.price)  # type: ignore

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
