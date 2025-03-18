# Django core imports
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test  # Add user_passes_test here
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.core.mail import send_mail
from django.template.loader import get_template
from django.template.exceptions import TemplateDoesNotExist

# Stripe imports
import stripe
from django.conf import settings

# Local imports
from .models import Product, TeamMember, Cart, CartItem, Order

# Home view
def home(request):
    try:
        template = get_template('main/home.html')  # Check if the template exists
    except TemplateDoesNotExist:
        print("Template not found. Searching in:")
        for loader in template.engine.template_loaders:
            print(loader.get_dirs())
        raise
    return render(request, 'main/home.html')

# Products view
def products(request, category):
    products = Product.objects.filter(category=category)
    sort_by = request.GET.get('sort', 'name')

    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    else:
        products = products.order_by('name')

    # Pagination
    paginator = Paginator(products, 10)  # Show 10 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'category': category,
        'products': page_obj,
        'sort_by': sort_by,
    }
    return render(request, 'main/products.html', context)

# Team view
def team(request):
    team = TeamMember.objects.all()  # Fetch all team members
    return render(request, 'main/team.html', {'team': team})

# Contact view
def contact(request):
    return render(request, 'main/contact.html')

# About view
def about(request):
    return render(request, 'main/about.html')

# Register view
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'main/register.html', {'form': form})

# Add to cart view
@login_required(login_url='/login/')
def add_to_cart(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

        if not created:
            cart_item.quantity += 1
            cart_item.save()

        return JsonResponse({'status': 'success', 'message': f'{product.name} added to cart!'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

# Cart view
@login_required
def cart(request):
    cart = Cart.objects.filter(user=request.user).first()
    if cart:
        cart_items = cart.cartitem_set.all()  # Ensure this returns valid CartItem objects
        total = sum(item.total_price() for item in cart_items)
    else:
        cart_items = []
        total = 0

    # Debugging: Print cart items
    print("Cart Items:", cart_items)

    context = {
        'cart_items': cart_items,
        'total': total,
    }

    return render(request, 'main/cart.html', context)

# Update cart item view
@login_required
def update_cart_item(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id, cart__user=request.user)
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
        else:
            cart_item.delete()
        messages.success(request, 'Cart updated successfully!')
    return redirect('cart')

# Remove from cart view
@login_required
def remove_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id, cart__user=request.user)
    cart_item.delete()
    return redirect('cart')

# Base context (for cart count)
def base_context(request):
    cart_items_count = 0
    if request.user.is_authenticated:
        cart_items_count = Cart.objects.filter(user=request.user).count()
    return {'cart_items_count': cart_items_count}

# Search view
def search(request):
    query = request.GET.get('q')  # Get the search query from the URL parameters
    if query:
        results = Product.objects.filter(name__icontains=query)  # Search by product name
    else:
        results = Product.objects.none()  # Return no results if no query is provided

    context = {
        'query': query,
        'results': results,
    }
    return render(request, 'main/search.html', context)

# All products view
def all_products(request):
    products = Product.objects.all()  # Fetch all products
    context = {
        'products': products,
        'message': 'Explore all our products!',
    }
    return render(request, 'main/all_products.html', context)

# Login view
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # Redirect to the home page after login
    else:
        form = AuthenticationForm()
    return render(request, 'main/login.html', {'form': form})

# Logout view
def logout_view(request):
    logout(request)
    return redirect('home')  # Redirect to the home page after logout

# Checkout view
@login_required
def checkout(request):
    # Fetch the user's cart
    cart = Cart.objects.get(user=request.user)
    cart_items = cart.cartitem_set.all()
    total = sum(item.total_price() for item in cart_items)

    print("Debug: Cart Items:", cart_items)  # Debugging: Print cart items
    print("Debug: Total:", total)  # Debugging: Print total

    if request.method == 'POST':
        print("Debug: POST request received")  # Debugging: Confirm POST request
        try:
            # Create an order
            print("Debug: Creating order...")  # Debugging: Before order creation
            order = Order.objects.create(
                user=request.user,
                total=total,
                status='Pending',  # Default status
                location='Warehouse',  # Default location
            )
            print("Debug: Order Created - ID:", order.id)  # Debugging: Print order ID

            # Clear the cart
            print("Debug: Clearing cart...")  # Debugging: Before clearing cart
            cart_items.delete()
            print("Debug: Cart Cleared")  # Debugging: Confirm cart is cleared

            # Redirect to the order confirmation page
            print("Debug: Redirecting to order confirmation...")  # Debugging: Before redirect
            return redirect('order_confirmation', order_id=order.id)
        except Exception as e:
            print("Debug: Error:", str(e))  # Debugging: Print the error
            messages.error(request, f"Error creating order: {str(e)}")
            return redirect('cart')

    context = {
        'cart_items': cart_items,
        'total': total,
    }
    return render(request, 'main/checkout.html', context)

# Order history view
@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'orders': orders,
    }
    return render(request, 'main/order_history.html', context)

# Cart count view
@login_required
def cart_count(request):
    cart = Cart.objects.filter(user=request.user).first()
    count = cart.cartitem_set.count() if cart else 0
    return JsonResponse({'count': count})

# Send confirmation email
def send_confirmation_email(user, order):
    subject = 'Order Confirmation'
    message = f'Thank you for your order! Your order total is {order.total} TND.'
    send_mail(subject, message, 'noreply@example.com', [user.email])

# Order confirmation view
@login_required
def order_confirmation(request, order_id):
    # Fetch the order
    order = get_object_or_404(Order, id=order_id, user=request.user)

    context = {
        'order': order,
    }
    return render(request, 'main/order_confirmation.html', context)

# Track order view
@login_required
def track_order(request, order_id):
    # Fetch the order for the logged-in user
    order = get_object_or_404(Order, id=order_id, user=request.user)

    context = {
        'order': order,
    }
    return render(request, 'main/track_order.html', context)

# Admin order management view
@login_required
@user_passes_test(lambda u: u.is_staff)  # Only allow staff users
def admin_order_management(request):
    # Fetch all orders
    orders = Order.objects.all().order_by('-created_at')

    context = {
        'orders': orders,
    }
    return render(request, 'main/admin_order_management.html', context)

# Update order status view
@login_required
@user_passes_test(lambda u: u.is_staff)  # Only allow staff users
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        order.status = new_status
        order.save()
        messages.success(request, f'Order {order.id} status updated to {new_status}.')
        return redirect('admin_order_management')

    context = {
        'order': order,
    }
    return render(request, 'main/update_order_status.html', context)