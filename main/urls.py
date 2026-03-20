from django.urls import path
from . import views

urlpatterns = [
    path('', views.welcome, name='welcome'),
    path('home/', views.home, name='home'),
    path('home/<str:subcategory_name>/', views.home, name='home_subcategory'),
    path('category/<int:category_id>/', views.category_detail, name='category_detail'),
    path('subcategory/<int:subcategory_id>/', views.subcategory_detail, name='subcategory_detail'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('search/', views.search, name='search'),
    path('about-us/', views.about_us, name='about_us'),
    path('contact-us/', views.contact_us, name='contact_us'),

    path('login/', views.login_view, name='login'),
    path('admin-login/', views.admin_login_view, name='admin_login'),
    path('signup/', views.signup, name='signup'),
    path('logout-user/', views.logout_user, name='logout_user'),
    path('logout-admin/', views.logout_admin, name='logout_admin'),
    path('profile/', views.profile, name='profile'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('update-quantity/', views.update_quantity, name='update_quantity'),
    path('remove-item/', views.remove_item, name='remove_item'),
    path('cart/count/', views.cart_count, name='cart_count'),
    # Facebook OAuth URLs
    path('auth/facebook/', views.facebook_login, name='facebook_login'),
    path('auth/facebook/callback/', views.facebook_callback, name='facebook_callback'),
    # Google OAuth URLs
    path('auth/google/', views.google_login, name='google_login'),
    path('auth/google/callback/', views.google_callback, name='google_callback'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
]
