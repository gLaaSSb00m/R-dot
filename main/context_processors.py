from .models import Category

def cart_item_count(request):
    cart = request.session.get('cart', {})
    total_quantity = sum(cart.values()) if cart else 0
    return {'cart_item_count': total_quantity}

def categories_processor(request):
    all_categories = Category.objects.all()
    nav_categories = all_categories[:5]  # First 5 categories for navigation
    return {
        'nav_categories': nav_categories,
        'all_categories': all_categories
    }
