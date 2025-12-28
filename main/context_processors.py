from .models import Category, Subcategory

def cart_item_count(request):
    cart = request.session.get('cart', {})
    total_quantity = sum(cart.values()) if cart else 0
    return {'cart_item_count': total_quantity}

def categories_processor(request):
    type_name = request.GET.get('type')
    current_category = None

    # Check if we're on a category detail page
    if request.resolver_match and request.resolver_match.url_name == 'category_detail':
        category_id = request.resolver_match.kwargs.get('category_id')
        if category_id:
            try:
                current_category = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                pass

    # Check if we're on a subcategory detail page
    elif request.resolver_match and request.resolver_match.url_name == 'subcategory_detail':
        subcategory_id = request.resolver_match.kwargs.get('subcategory_id')
        if subcategory_id:
            try:
                current_subcategory = Subcategory.objects.get(id=subcategory_id)
                current_category = current_subcategory.category
            except Subcategory.DoesNotExist:
                pass

    if current_category:
        # Show categories from the same type as the current category, or all if no type
        if type_name:
            all_categories = Category.objects.filter(type__name__iexact=type_name)
        else:
            all_categories = Category.objects.all()
        # Always include the current category in nav_categories
        nav_categories = [current_category]
        # Add other categories, excluding the current one
        other_categories = all_categories.exclude(id=current_category.id)[:4]
        nav_categories.extend(other_categories)
    else:
        if type_name:
            all_categories = Category.objects.filter(type__name__iexact=type_name)
        else:
            all_categories = Category.objects.all()
        nav_categories = all_categories[:5]

    return {
        'nav_categories': nav_categories,
        'all_categories': all_categories,
        'current_category': current_category
    }

def subcategories_processor(request):
    type_name = request.GET.get('type')

    # Check if we're on a subcategory detail page
    if request.resolver_match and request.resolver_match.url_name == 'subcategory_detail':
        subcategory_id = request.resolver_match.kwargs.get('subcategory_id')
        if subcategory_id:
            try:
                current_subcategory = Subcategory.objects.get(id=subcategory_id)
                # Show subcategories from the same category as the current subcategory
                all_subcategories = Subcategory.objects.filter(category=current_subcategory.category)
                # Always include the current subcategory in nav_subcategories
                nav_subcategories = [current_subcategory]
                # Add other subcategories from the same category, excluding the current one
                other_subcategories = all_subcategories.exclude(id=current_subcategory.id)[:4]
                nav_subcategories.extend(other_subcategories)
            except Subcategory.DoesNotExist:
                all_subcategories = Subcategory.objects.all()
                nav_subcategories = all_subcategories[:5]
        else:
            all_subcategories = Subcategory.objects.all()
            nav_subcategories = all_subcategories[:5]
    elif type_name:
        all_subcategories = Subcategory.objects.filter(category__type__name=type_name)
        nav_subcategories = all_subcategories[:5]
    else:
        all_subcategories = Subcategory.objects.all()
        nav_subcategories = all_subcategories[:5]

    return {
        'nav_subcategories': nav_subcategories,
        'all_subcategories': all_subcategories
    }

def toggle_visibility_processor(request):
    # Show toggle on home and product-related pages
    show_toggle = request.resolver_match.url_name in ['home', 'subcategory_detail', 'category_detail', 'search']
    return {'show_toggle': show_toggle}
