from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate
from django.contrib import messages
from django.db.models import Q
from django.conf import settings
from django.http import HttpResponseRedirect, HttpRequest, JsonResponse
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from django.urls import reverse
import requests
from functools import wraps
from typing import Optional, Any, Callable
from .models import Product, Category, Banner, Subcategory, NewOrder
from .forms import CustomUserCreationForm, CheckoutForm
from .backends import save_order_to_sheets


def get_session_user(request: HttpRequest) -> Optional[User]:
    """Get authenticated user from user session data"""
    user_id = request.session.get('user_auth_id')  # type: ignore
    session_hash = request.session.get('user_auth_hash')  # type: ignore
    if user_id and session_hash:
        try:
            user = User.objects.get(pk=user_id)
            expected_hash = user.get_session_auth_hash()
            if expected_hash == session_hash:
                return user
        except User.DoesNotExist:
            pass
    return None


def get_session_admin_user(request: HttpRequest) -> Optional[User]:
    """Get authenticated admin user from admin session data"""
    admin_id = request.session.get('admin_auth_id')  # type: ignore
    session_hash = request.session.get('admin_auth_hash')  # type: ignore
    if admin_id and session_hash:
        try:
            user = User.objects.get(pk=admin_id)
            expected_hash = user.get_session_auth_hash()
            if expected_hash == session_hash:
                user.is_staff = True  # Ensure admin context
                return user
        except User.DoesNotExist:
            pass
    return None


def clear_user_session(request: HttpRequest) -> None:
    """Clear user session data"""
    request.session.pop('user_auth_id', None)  # type: ignore
    request.session.pop('user_auth_hash', None)  # type: ignore


def clear_admin_session(request: HttpRequest) -> None:
    """Clear admin session data"""
    request.session.pop('admin_auth_id', None)  # type: ignore
    request.session.pop('admin_auth_hash', None)  # type: ignore



def user_required(view_func: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(view_func)
    def wrapper(request: HttpRequest, *args: Any, **kwargs: Any) -> Any:
        user = get_session_user(request)
        if not user:
            return redirect('login')
        if user.is_staff:
            messages.info(request, 'Admin users please use admin login.')
            return redirect('admin_login')
        request.user = user
        return view_func(request, *args, **kwargs)
    return wrapper

def admin_required(view_func: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(view_func)
    def wrapper(request: HttpRequest, *args: Any, **kwargs: Any) -> Any:
        admin_user = get_session_admin_user(request)
        if not admin_user:
            return redirect('admin_login')
        request.user = admin_user
        return view_func(request, *args, **kwargs)
    return wrapper

def home(request: HttpRequest, subcategory_name: Optional[str] = None):
    type_name = request.GET.get('type')
    
    # Get subcategories for the current type (for tabs)
    if type_name:
        request.session['selected_type'] = type_name
        subcategories = Subcategory.objects.filter(category__type__name__iexact=type_name)
    else:
        type_name = request.session.get('selected_type', 'Fashion')
        subcategories = Subcategory.objects.filter(category__type__name__iexact=type_name)
    
    # Handle subcategory filtering
    selected_subcategory = None
    if subcategory_name:
        # Filter by specific subcategory
        selected_subcategory = subcategory_name
        products = Product.objects.filter(subcategory__name__iexact=subcategory_name).order_by('?')[:16]
        banners = Banner.objects.filter(type__name__iexact=type_name)
    else:
        # Filter by type (all products in that type)
        products = Product.objects.filter(subcategory__category__type__name__iexact=type_name).order_by('?')[:16]
        banners = Banner.objects.filter(type__name__iexact=type_name)
    
    return render(request, 'home.html', {
        'banners': banners, 
        'products': products, 
        'selected_type': type_name,
        'subcategories': subcategories,
        'selected_subcategory': selected_subcategory
    })

def welcome(request: HttpRequest):
    return render(request, 'welcome.html')

def category_detail(request: HttpRequest, category_id: int):
    category = get_object_or_404(Category, id=category_id)
    subcategories = Subcategory.objects.filter(category=category).prefetch_related('products')
    subcategories_with_products: list[dict[str, Any]] = []
    for subcategory in subcategories:
        products = Product.objects.filter(subcategory=subcategory)
        subcategories_with_products.append({'subcategory': subcategory, 'products': products})
    return render(request, 'category_detail.html', {'category': category, 'subcategories_with_products': subcategories_with_products})

def subcategory_detail(request: HttpRequest, subcategory_id: int):
    subcategory = get_object_or_404(Subcategory, id=subcategory_id)
    subcategories = Subcategory.objects.filter(category=subcategory.category)
    products = Product.objects.filter(subcategory=subcategory)
    return render(request, 'subcategory_detail.html', {'subcategory': subcategory, 'products': products, 'subcategories': subcategories})

def product_detail(request: HttpRequest, product_id: int):
    product = get_object_or_404(Product, id=product_id)
    related_products = Product.objects.filter(subcategory=product.subcategory).exclude(id=product_id)[:4]
    return render(request, 'product_detail.html', {
        'product': product,
        'related_products': related_products
    })

def search(request: HttpRequest):
    query = request.GET.get('q', '') or ''
    products = []
    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
    return render(request, 'search_results.html', {'products': products, 'query': query})

def about_us(request: HttpRequest):
    type_name = request.GET.get('type')
    if type_name:
        request.session['selected_type'] = type_name
    return render(request, 'about_us.html')

def contact_us(request: HttpRequest):
    type_name = request.GET.get('type')
    if type_name:
        request.session['selected_type'] = type_name
    return render(request, 'contact_us.html')



def login_view(request: HttpRequest):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user and not user.is_staff:
            request.session['user_auth_id'] = user.pk
            request.session['user_auth_hash'] = user.get_session_auth_hash()
            request.session.modified = True
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'login.html')

def admin_login_view(request: HttpRequest):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user and user.is_staff:
            request.session['admin_auth_id'] = user.pk
            request.session['admin_auth_hash'] = user.get_session_auth_hash()
            request.session.modified = True
            return redirect('admin:index')
        else:
            messages.error(request, 'Invalid admin credentials or not an admin user')
    return render(request, 'admin_login.html')

def signup(request: HttpRequest):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Signup successful! Please login to continue.')
            return redirect('login')
        else:
            messages.error(request, 'Please correct the errors below')
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})

def logout_admin(request: HttpRequest):
    clear_admin_session(request)
    messages.success(request, 'Admin logged out successfully.')
    return redirect('welcome')

@user_required
def profile(request: HttpRequest):
    # Get user's orders
    orders = NewOrder.objects.filter(user=request.user).order_by('-created_at')

    return render(request, 'profile.html', {'orders': orders})

@user_required
def cart(request: HttpRequest):
    # For now, we'll use session-based cart
    cart_items = request.session.get('cart', {})
    cart_data: list[dict[str, Any]] = []
    total_items = 0
    total_price = 0

    for product_id_str, item_data in cart_items.items():
        try:
            product_id = int(product_id_str)
            product = Product.objects.get(id=product_id)
            quantity = item_data['quantity']
            price = product.discount_price if product.discount_price else product.price
            item_total = price * quantity
            cart_data.append({
                'id': product_id_str,
                'product': product,
                'quantity': quantity,
                'size': item_data.get('size'),
                'total': float(item_total)
            })
            total_items += quantity
            total_price += item_total
        except (Product.DoesNotExist, KeyError):
            pass

    return render(request, 'cart.html', {
        'cart_items': cart_data,
        'total_items': total_items,
        'total_price': total_price
    })

@require_POST
def add_to_cart(request: HttpRequest):
    product_id = request.POST.get('product_id')
    if not product_id:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Product ID is required'})
        return HttpResponseRedirect(reverse('home'))

    product = get_object_or_404(Product, id=product_id)
    qty = int(request.POST.get('quantity', 1))
    size = request.POST.get('size') if product.is_fashion else ''
    cart = request.session.get('cart', {})
    cart[str(product_id)] = {'quantity': qty, 'size': size}
    request.session['cart'] = cart
    request.session.modified = True

    # Check if request is AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'message': 'Product added to cart'})

    # Stay on the current page
    referrer = request.META.get('HTTP_REFERER')
    if referrer:
        return HttpResponseRedirect(referrer)
    else:
        # If no referrer, redirect to current path
        return HttpResponseRedirect(request.path)

def update_quantity(request: HttpRequest):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))
        cart = request.session.get('cart', {})

        if product_id in cart:
            cart[product_id]['quantity'] = quantity
            request.session['cart'] = cart
            request.session.modified = True
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'Product not in cart'})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def remove_item(request: HttpRequest):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        cart = request.session.get('cart', {})

        if product_id in cart:
            cart.pop(product_id)
            request.session['cart'] = cart
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'Product not in cart'})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def cart_count(request: HttpRequest):
    cart = request.session.get('cart', {})
    total_quantity = sum(item['quantity'] for item in cart.values()) if cart else 0
    return JsonResponse({'count': total_quantity})

# OAuth configs from settings.py (no fallbacks - will raise KeyError if missing)
# FACEBOOK_APP_ID = settings.FACEBOOK_APP_ID  # Disabled - TODO uncomment with real settings
# FACEBOOK_APP_SECRET = settings.FACEBOOK_APP_SECRET  # Disabled
FACEBOOK_APP_ID = getattr(settings, 'FACEBOOK_APP_ID', None)
FACEBOOK_APP_SECRET = getattr(settings, 'FACEBOOK_APP_SECRET', None)
FACEBOOK_REDIRECT_URI = getattr(settings, 'FACEBOOK_REDIRECT_URI', 'http://localhost:8000/auth/facebook/callback/')

# GOOGLE_CLIENT_ID = settings.GOOGLE_CLIENT_ID  # Disabled
# GOOGLE_CLIENT_SECRET = settings.GOOGLE_CLIENT_SECRET  # Disabled
GOOGLE_CLIENT_ID = getattr(settings, 'GOOGLE_CLIENT_ID', None)
GOOGLE_CLIENT_SECRET = getattr(settings, 'GOOGLE_CLIENT_SECRET', None)
GOOGLE_REDIRECT_URI = getattr(settings, 'GOOGLE_REDIRECT_URI', 'http://localhost:8000/auth/google/callback/')

def facebook_login(_: HttpRequest) -> HttpResponseRedirect:
    """Initiate Facebook OAuth login"""
    facebook_auth_url = (
        f"https://www.facebook.com/v18.0/dialog/oauth?"
        f"client_id={FACEBOOK_APP_ID}&"
        f"redirect_uri={FACEBOOK_REDIRECT_URI}&"
        f"scope=email,public_profile&"
        f"response_type=code"
    )
    return HttpResponseRedirect(facebook_auth_url)

def facebook_callback(request: HttpRequest):
    """Handle Facebook OAuth callback"""
    code = request.GET.get('code')
    if not code:
        messages.error(request, 'Facebook login failed - no authorization code received')
        return redirect('login')

    # Exchange code for access token
    token_url = 'https://graph.facebook.com/v18.0/oauth/access_token'
    token_data: dict[str, str] = {
        'client_id': FACEBOOK_APP_ID,
        'client_secret': FACEBOOK_APP_SECRET,
        'redirect_uri': FACEBOOK_REDIRECT_URI,
        'code': code
    }

    try:
        token_response = requests.post(token_url, data=token_data)
        token_json = token_response.json()

        if 'access_token' not in token_json:
            messages.error(request, 'Facebook login failed - could not get access token')
            return redirect('login')

        access_token = token_json['access_token']

        # Get user info from Facebook
        user_info_url = f'https://graph.facebook.com/me?fields=id,name,email&access_token={access_token}'
        user_response = requests.get(user_info_url)
        user_data = user_response.json()

        if 'email' not in user_data:
            messages.error(request, 'Facebook login failed - could not get user email')
            return redirect('login')

        # Create or get user
        email = user_data['email']
        facebook_id = user_data['id']
        name = user_data['name']

        # Try to find existing user by email or create new one
        user = User.objects.filter(email=email).first()
        if not user:
            username = f"fb_{facebook_id}"
            original_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{original_username}_{counter}"
                counter += 1

            user = User.objects.create(
                username=username,
                email=email,
                first_name=name.split(' ')[0] if ' ' in name else name,
                last_name=' '.join(name.split(' ')[1:]) if ' ' in name else '',
            )
            user.set_unusable_password()
            user.save()

        request.session['user_auth_id'] = user.pk
        request.session['user_auth_hash'] = user.get_session_auth_hash()
        request.session.modified = True
        messages.success(request, f'Welcome {user.first_name or user.username}!')
        return redirect('home')

    except requests.RequestException as e:
        messages.error(request, f'Facebook login failed - {str(e)}')
        return redirect('login')

def google_login(_: HttpRequest) -> HttpResponseRedirect:
    """Initiate Google OAuth login"""
    google_auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={GOOGLE_CLIENT_ID}&"
        f"redirect_uri={GOOGLE_REDIRECT_URI}&"
        f"scope=openid%20email%20profile&"
        f"response_type=code&"
        f"access_type=offline"
    )
    return HttpResponseRedirect(google_auth_url)


def logout_user(request: HttpRequest):
    clear_user_session(request)
    messages.success(request, 'User logged out successfully.')
    return redirect('home')


@admin_required
def admin_dashboard(request: HttpRequest):
    # Stats
    total_users = User.objects.count()
    total_products = Product.objects.count()
    total_orders = NewOrder.objects.count()
    total_revenue = sum([order.quantity * 1000 for order in NewOrder.objects.all()[:100]])  # Approximate revenue

    # Recent orders
    recent_orders = NewOrder.objects.select_related('user').order_by('-created_at')[:10]

    context: dict[str, Any] = {
        'total_users': total_users,
        'total_products': total_products,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'recent_orders': recent_orders,
    }

    return render(request, 'admin/admin_dashboard.html', context)

def google_callback(request: HttpRequest):
    """Handle Google OAuth callback"""
    code = request.GET.get('code')
    if not code:
        messages.error(request, 'Google login failed - no authorization code received')
        return redirect('login')

    # Exchange code for access token
    token_url = 'https://oauth2.googleapis.com/token'
    token_data: dict[str, str] = {
        'client_id': GOOGLE_CLIENT_ID,
        'client_secret': GOOGLE_CLIENT_SECRET,
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': GOOGLE_REDIRECT_URI,
    }

    try:
        token_response = requests.post(token_url, data=token_data)
        token_json = token_response.json()

        if 'access_token' not in token_json:
            messages.error(request, 'Google login failed - could not get access token')
            return redirect('login')

        access_token = token_json['access_token']

        # Get user info from Google
        user_info_url = f'https://www.googleapis.com/oauth2/v2/userinfo?access_token={access_token}'
        user_response = requests.get(user_info_url)
        user_data = user_response.json()

        if 'email' not in user_data:
            messages.error(request, 'Google login failed - could not get user email')
            return redirect('login')

        # Create or get user
        email = user_data['email']
        google_id = user_data['id']
        name = user_data.get('name', '')

        # Try to find existing user by email or create new one
        user = User.objects.filter(email=email).first()
        if not user:
            username = f"google_{google_id}"
            original_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{original_username}_{counter}"
                counter += 1

            user = User.objects.create(
                username=username,
                email=email,
                first_name=name.split(' ')[0] if ' ' in name else name,
                last_name=' '.join(name.split(' ')[1:] if ' ' in name else ''),
            )
            user.set_unusable_password()
            user.save()

        request.session['user_auth_id'] = user.pk
        request.session['user_auth_hash'] = user.get_session_auth_hash()
        request.session.modified = True
        messages.success(request, f'Welcome {user.first_name or user.username}!')
        return redirect('home')

    except requests.RequestException as e:
        messages.error(request, f'Google login failed - {str(e)}')
        return redirect('login')

@user_required
def checkout(request: HttpRequest):
    cart_items = request.session.get('cart', {})
    if not cart_items:
        messages.error(request, 'Your cart is empty')
        return redirect('cart')

    cart_data: list[dict[str, Any]] = []
    total_price: float = 0
    errors = []
    for product_id_str, item_data in cart_items.items():
        try:
            product_id = int(product_id_str)
            product = Product.objects.get(id=product_id)
            quantity = item_data['quantity']
            size = item_data.get('size')
            price = product.discount_price if product.discount_price else product.price
            item_total = float(price * quantity)
            if product.is_fashion and size and size not in product.available_sizes:
                errors.append(f"Size '{size}' not available for {product.name}")
            cart_data.append({
                'product': product,
                'quantity': quantity,
                'size': size,
                'total': item_total
            })
            total_price += item_total
        except (Product.DoesNotExist, KeyError, ValueError):
            pass

    for error in errors:
        messages.error(request, error)
    if errors:
        # Re-render with errors
        banner_id = request.GET.get('banner')
        banner = None
        if banner_id:
            try:
                banner = Banner.objects.get(id=banner_id)
            except Banner.DoesNotExist:
                pass
        form = CheckoutForm()
        return render(request, 'checkout.html', {
            'form': form,
            'cart_items': cart_data,
            'total_price': total_price,
            'banner': banner
        })

    banner_id = request.GET.get('banner')
    banner = None
    if banner_id:
        try:
            banner = Banner.objects.get(id=banner_id)
        except Banner.DoesNotExist:
            pass

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            address = form.cleaned_data['address']
            mobile_number = form.cleaned_data['mobile_number']

            # Create NewOrder entries for each cart item
            for product_id_str, item_data in cart_items.items():
                product_id = int(product_id_str)
                product = Product.objects.get(id=product_id)
                quantity = item_data['quantity']
                size = item_data.get('size') or ''
                price = product.discount_price if product.discount_price else product.price
                item_total = float(price * quantity)
                new_order = NewOrder.objects.create(
                    user=request.user,
                    address=address,
                    mobile_number=mobile_number,
                    product_code=str(product.pk),
                    product_name=product.name,
                    product_image=product.image,
                    quantity=quantity,
                    size=size,
                    price=item_total
                )
                save_order_to_sheets(new_order)

            # Clear the cart
            request.session['cart'] = {}
            messages.success(request, 'Order placed successfully!')
            return redirect('home')
    else:
        form = CheckoutForm()

    return render(request, 'checkout.html', {
        'form': form,
        'cart_items': cart_data,
        'total_price': total_price,
        'banner': banner
    })

