from typing import Dict, Any
from django.http import HttpRequest
from .models import Category, Subcategory


def cart_item_count(request: HttpRequest) -> Dict[str, Any]:
    cart = request.session.get('cart', {})
    total_quantity = sum(item['quantity'] for item in cart.values()) if cart else 0
    return {'cart_item_count': total_quantity}


def categories_processor(request: HttpRequest) -> Dict[str, Any]:
    type_name = request.GET.get('type') or request.session.get('selected_type', 'Fashion')
    current_category = None

    resolver = request.resolver_match

    # Category detail page
    if resolver and resolver.url_name == 'category_detail':
        category_id = resolver.kwargs.get('category_id')
        if category_id:
            try:
                current_category = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                current_category = None

    # Subcategory detail page
    elif resolver and resolver.url_name == 'subcategory_detail':
        subcategory_id = resolver.kwargs.get('subcategory_id')
        if subcategory_id:
            try:
                current_subcategory = Subcategory.objects.get(id=subcategory_id)
                current_category = current_subcategory.category
            except Subcategory.DoesNotExist:
                current_category = None

    # Get categories
    if type_name:
        all_categories = Category.objects.filter(type__name__iexact=type_name)
    else:
        all_categories = Category.objects.all()

    # Navigation categories
    if current_category:
        nav_categories = [current_category]
        other_categories = all_categories.exclude(pk=current_category.pk)[:4]
        nav_categories.extend(other_categories)
    else:
        nav_categories = list(all_categories[:5])

    return {
        'nav_categories': nav_categories,
        'all_categories': all_categories,
        'current_category': current_category
    }


def subcategories_processor(request: HttpRequest) -> Dict[str, Any]:
    type_name = request.GET.get('type') or request.session.get('selected_type', 'Fashion')

    resolver = request.resolver_match

    if resolver and resolver.url_name == 'subcategory_detail':
        subcategory_id = resolver.kwargs.get('subcategory_id')

        if subcategory_id:
            try:
                current_subcategory = Subcategory.objects.get(id=subcategory_id)

                all_subcategories = Subcategory.objects.filter(
                    category=current_subcategory.category
                )

                nav_subcategories = [current_subcategory]
                other_subcategories = all_subcategories.exclude(
                    pk=current_subcategory.pk
                )[:4]

                nav_subcategories.extend(other_subcategories)

            except Subcategory.DoesNotExist:
                all_subcategories = Subcategory.objects.all()
                nav_subcategories = list(all_subcategories[:5])
        else:
            all_subcategories = Subcategory.objects.all()
            nav_subcategories = list(all_subcategories[:5])

    elif type_name:
        all_subcategories = Subcategory.objects.filter(
            category__type__name=type_name
        )
        nav_subcategories = list(all_subcategories[:5])

    else:
        all_subcategories = Subcategory.objects.all()
        nav_subcategories = list(all_subcategories[:5])

    return {
        'nav_subcategories': nav_subcategories,
        'all_subcategories': all_subcategories
    }


def toggle_visibility_processor(request: HttpRequest) -> Dict[str, Any]:
    show_toggle = True
    selected_type = request.session.get('selected_type', 'Fashion')

    return {
        'show_toggle': show_toggle,
        'selected_type': selected_type
    }


def auth_context(request: HttpRequest) -> Dict[str, Any]:
    """Provide user and admin_user from session for templates"""
    from .views import get_session_user, get_session_admin_user

    # When rendering admin pages, Django's own auth system is in use.
    # We must not override the 'user' object in the context, as it would
    # break admin templates that expect the standard user object.
    if request.resolver_match and request.resolver_match.app_name == 'admin':
        return {'admin_user': get_session_admin_user(request)}

    return {
        'user': get_session_user(request),
        'admin_user': get_session_admin_user(request)
    }
