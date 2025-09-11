# E-commerce Django Project

## Overview
This project is a Django-based e-commerce web application featuring product browsing, cart management, user authentication, and order checkout functionality.

## Features Implemented
- Product catalog with categories and subcategories
- Shopping cart with add, update quantity, and remove item functionality
- User signup, login, logout, and profile management
- Checkout process with address and mobile number input
- Order saving with product details (code, name, image) linked to user
- Admin panel integration for managing products, categories, banners, and orders
- Facebook OAuth login integration

## Checkout and Order Management
- Users can proceed to checkout from the cart page
- Checkout form collects shipping address and mobile number
- Orders are saved in the database with product details and user info
- Order history is displayed on the user's profile page

## Screenshots

### Cart Page
![Cart Page](media/screenshots/cart_page.png)

### Checkout Page
![Checkout Page](media/screenshots/checkout_page.png)

### Profile Page with Order History
![Profile Page](media/screenshots/profile_page.png)

## Setup and Run
1. Create and activate a virtual environment
2. Install dependencies: `pip install -r requirements.txt`
3. Run migrations: `python manage.py migrate`
4. Create a superuser: `python manage.py createsuperuser`
5. Run the development server: `python manage.py runserver`
6. Access the site at `http://localhost:8000`

## Notes
- Media files for product images and banners are stored in the `media/` directory
- Admin panel is accessible at `/admin/`
- Facebook OAuth requires configuration of app ID, secret, and redirect URI in settings

## License
MIT License
