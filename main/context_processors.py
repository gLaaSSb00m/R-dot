from .models import Category, Subcategory

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

def subcategories_processor(request):
    type_name = request.GET.get('type')
    if type_name:
        all_subcategories = Subcategory.objects.filter(category__type__name=type_name)
    else:
        all_subcategories = Subcategory.objects.all()
    nav_subcategories = all_subcategories[:5]  # First 5 subcategories for navigation
    return {
        'nav_subcategories': nav_subcategories,
        'all_subcategories': all_subcategories
    }

def toggle_visibility_processor(request):
    # Show toggle on home and product-related pages
    show_toggle = request.resolver_match.url_name in ['home', 'subcategory_detail', 'category_detail', 'search']
    return {'show_toggle': show_toggle}
