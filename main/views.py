from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.db.models import Q
from django.conf import settings
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
import requests
import json
from .models import Product, Category, Banner, Subcategory, Blog, NewOrder
from .forms import CustomUserCreationForm, CheckoutForm

def home(request):
    type_name = request.GET.get('type')
    if type_name:
        products = Product.objects.filter(subcategory__category__type__name=type_name)[:8]
    else:
        products = Product.objects.all()[:8]
    return render(request, 'home.html', {'banners': Banner.objects.all(), 'products': products})

def welcome(request):
    return render(request, 'welcome.html')

def category_detail(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    subcategories = category.subcategories.all().prefetch_related('products')
    subcategories_with_products = []
    for subcategory in subcategories:
        products = subcategory.products.all()
        subcategories_with_products.append({'subcategory': subcategory, 'products': products})
    return render(request, 'category_detail.html', {'category': category, 'subcategories_with_products': subcategories_with_products})

def search(request):
    query = request.GET.get('q', '')
    products = []
    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
    return render(request, 'search_results.html', {'products': products, 'query': query})

def about_us(request):
    return render(request, 'about_us.html')

def contact_us(request):
    return render(request, 'contact_us.html')

def products(request):
    blogs = Blog.objects.all().order_by('-created_at')[:5]  # Get latest 5 blog posts
    return render(request, 'products.html', {'blogs': blogs})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'login.html')

def signup(request):
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

def logout_view(request):
    logout(request)
    return redirect('home')

def profile(request):
    if not request.user.is_authenticated:
        return redirect('login')

    # Get user's orders
    orders = NewOrder.objects.filter(user=request.user).order_by('-created_at')

    return render(request, 'profile.html', {'orders': orders})

def cart(request):
    # For now, we'll use session-based cart
    cart_items = request.session.get('cart', {})
    cart_data = []
    total_items = 0
    total_price = 0

    for product_id, quantity in cart_items.items():
        try:
            product = Product.objects.get(id=product_id)
            item_total = product.price * quantity
            cart_data.append({
                'id': product_id,
                'product': product,
                'quantity': quantity,
                'total': item_total
            })
            total_items += quantity
            total_price += item_total
        except Product.DoesNotExist:
            pass

    return render(request, 'cart.html', {
        'cart_items': cart_data,
        'total_items': total_items,
        'total_price': total_price
    })

from django.views.decorators.http import require_POST
from django.urls import reverse
from django.http import HttpResponseRedirect

@require_POST
def add_to_cart(request):
    product_id = request.POST.get('product_id')
    if not product_id:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Product ID is required'})
        return HttpResponseRedirect(reverse('home'))

    cart = request.session.get('cart', {})
    if product_id in cart:
        cart[product_id] += 1
    else:
        cart[product_id] = 1
    request.session['cart'] = cart

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

from django.http import JsonResponse

def update_quantity(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))
        cart = request.session.get('cart', {})

        if product_id in cart:
            if quantity > 0:
                cart[product_id] = quantity
            else:
                cart.pop(product_id)
            request.session['cart'] = cart
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'Product not in cart'})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def remove_item(request):
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

def cart_count(request):
    cart = request.session.get('cart', {})
    total_quantity = sum(cart.values()) if cart else 0
    return JsonResponse({'count': total_quantity})

# Facebook OAuth Configuration
FACEBOOK_APP_ID = getattr(settings, 'FACEBOOK_APP_ID', 'your_facebook_app_id')
FACEBOOK_APP_SECRET = getattr(settings, 'FACEBOOK_APP_SECRET', 'your_facebook_app_secret')
FACEBOOK_REDIRECT_URI = getattr(settings, 'FACEBOOK_REDIRECT_URI', 'http://localhost:8000/auth/facebook/callback/')

def facebook_login(request):
    """Initiate Facebook OAuth login"""
    facebook_auth_url = (
        f"https://www.facebook.com/v18.0/dialog/oauth?"
        f"client_id={FACEBOOK_APP_ID}&"
        f"redirect_uri={FACEBOOK_REDIRECT_URI}&"
        f"scope=email,public_profile&"
        f"response_type=code"
    )
    return HttpResponseRedirect(facebook_auth_url)

def facebook_callback(request):
    """Handle Facebook OAuth callback"""
    code = request.GET.get('code')
    if not code:
        messages.error(request, 'Facebook login failed - no authorization code received')
        return redirect('login')

    # Exchange code for access token
    token_url = 'https://graph.facebook.com/v18.0/oauth/access_token'
    token_data = {
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
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Create new user with Facebook data
            username = f"fb_{facebook_id}"
            # Ensure username is unique
            counter = 1
            original_username = username
            while User.objects.filter(username=username).exists():
                username = f"{original_username}_{counter}"
                counter += 1

            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=name.split(' ')[0] if ' ' in name else name,
                last_name=' '.join(name.split(' ')[1:]) if ' ' in name else ''
            )

        # Log the user in
        login(request, user)
        messages.success(request, f'Welcome {user.first_name or user.username}!')
        return redirect('home')

    except requests.RequestException as e:
        messages.error(request, f'Facebook login failed - {str(e)}')
        return redirect('login')
    except json.JSONDecodeError:
        messages.error(request, 'Facebook login failed - invalid response from Facebook')
        return redirect('login')

def checkout(request):
    cart_items = request.session.get('cart', {})
    if not cart_items:
        messages.error(request, 'Your cart is empty')
        return redirect('cart')

    cart_data = []
    total_price = 0
    for product_id, quantity in cart_items.items():
        try:
            product = Product.objects.get(id=product_id)
            item_total = product.price * quantity
            cart_data.append({
                'product': product,
                'quantity': quantity,
                'total': item_total
            })
            total_price += item_total
        except Product.DoesNotExist:
            pass

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            address = form.cleaned_data['address']
            mobile_number = form.cleaned_data['mobile_number']

            # Create NewOrder entries for each cart item
            for item in cart_data:
                NewOrder.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    address=address,
                    mobile_number=mobile_number,
                    product_code=str(item['product'].id),  # Using product ID as code
                    product_name=item['product'].name,
                    product_image=item['product'].image,
                    quantity=item['quantity']
                )

            # Clear the cart
            request.session['cart'] = {}
            messages.success(request, 'Order placed successfully!')
            return redirect('home')
    else:
        form = CheckoutForm()

    return render(request, 'checkout.html', {
        'form': form,
        'cart_items': cart_data,
        'total_price': total_price
    })
