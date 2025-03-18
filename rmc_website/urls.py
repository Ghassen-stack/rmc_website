from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from main import views

urlpatterns = [
    # Admin Order Management URLs (MUST COME BEFORE THE ADMIN URLS)
    path('admin/orders/', views.admin_order_management, name='admin_order_management'),
    path('admin/orders/update/<int:order_id>/', views.update_order_status, name='update_order_status'),

    # Admin URL (Django Admin)
    path('admin/', admin.site.urls),

    # Main App URLs
    path('', views.home, name='home'),
    path('products/', views.all_products, name='all_products'),
    path('products/<str:category>/', views.products, name='products'),
    path('team/', views.team, name='team'),
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),

    # Authentication URLs
    path('login/', auth_views.LoginView.as_view(template_name='main/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),

    # Cart URLs
    path('cart/', views.cart, name='cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:cart_item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('search/', views.search, name='search'),
    path('checkout/', views.checkout, name='checkout'),
    path('cart-count/', views.cart_count, name='cart_count'),
    path('update-cart-item/<int:cart_item_id>/', views.update_cart_item, name='update_cart_item'),
    path('order-confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('track-order/<int:order_id>/', views.track_order, name='track_order'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)