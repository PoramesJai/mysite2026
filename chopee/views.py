from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from .models import Category, Product, ProductImage, CartItem, Order, OrderItem, Review

# Helper to get cart item count for header
def get_cart_count(request):
    if request.user.is_authenticated:
        return sum(item.quantity for item in request.user.cart_items.all())
    return 0

# 1. Home View (with Search, Filter and Sort)
def home_view(request):
    categories = Category.objects.all()
    products = Product.objects.all()

    # Search Query
    q = request.GET.get('q', '')
    if q:
        products = products.filter(Q(name__icontains=q) | Q(description__icontains=q))

    # Category Filter
    category_slug = request.GET.get('category', '')
    selected_category = None
    if category_slug:
        selected_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=selected_category)

    # Location Filter
    locations = request.GET.getlist('location')
    if locations:
        products = products.filter(location__in=locations)

    # Rating Filter
    rating = request.GET.get('rating', '')
    if rating:
        products = products.filter(rating__gte=float(rating))

    # Price Filters
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    if min_price:
        try:
            products = products.filter(price__gte=float(min_price))
        except ValueError:
            pass
    if max_price:
        try:
            products = products.filter(price__lte=float(max_price))
        except ValueError:
            pass

    # Sorting
    sort = request.GET.get('sort', 'pop') # pop, new, price_asc, price_desc
    if sort == 'new':
        products = products.order_by('-created_at')
    elif sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    else: # Default: Popular / sales count
        products = products.order_by('-sold_count')

    # Popular locations list for sidebar filter
    popular_locations = ['กรุงเทพมหานคร', 'นนทบุรี', 'สมุทรปราการ', 'ปทุมธานี', 'เชียงใหม่', 'ชลบุรี']

    context = {
        'categories': categories,
        'products': products,
        'q': q,
        'selected_category': selected_category,
        'selected_locations': locations,
        'popular_locations': popular_locations,
        'selected_rating': rating,
        'min_price': min_price,
        'max_price': max_price,
        'sort': sort,
        'cart_count': get_cart_count(request),
    }
    return render(request, 'chopee/home.html', context)

# 2. Product Detail View
def product_detail_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = product.reviews.all().order_by('-created_at')
    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:6]
    
    # Mock product variations for Shopee vibe
    colors = ['สีดำ Classic', 'สีขาว Minimal', 'สีส้ม Chopee Signature', 'สีน้ำเงิน Space Blue']
    sizes = ['S', 'M', 'L', 'XL', 'Free Size']

    context = {
        'product': product,
        'reviews': reviews,
        'related_products': related_products,
        'colors': colors,
        'sizes': sizes,
        'cart_count': get_cart_count(request),
    }
    return render(request, 'chopee/product_detail.html', context)

# 3. Cart View
@login_required(login_url='chopee:login')
def cart_view(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.total_price for item in cart_items)
    
    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'cart_count': get_cart_count(request),
    }
    return render(request, 'chopee/cart.html', context)

# 4. Add to Cart View
@login_required(login_url='chopee:login')
def add_to_cart_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += quantity
    else:
        cart_item.quantity = quantity
    cart_item.save()
    
    messages.success(request, f"เพิ่ม {product.name} ลงตะกร้าแล้ว!")
    
    # Handle "Buy Now" vs "Add to Cart"
    action = request.POST.get('action', 'add')
    if action == 'buy':
        return redirect('chopee:checkout')
    
    return redirect('chopee:product_detail', product_id=product.id)

# 5. Update Cart View (POST)
@login_required(login_url='chopee:login')
def update_cart_view(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        action = request.POST.get('action') # 'increase', 'decrease' or 'input'
        cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
        
        if action == 'increase':
            cart_item.quantity += 1
        elif action == 'decrease':
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
            else:
                cart_item.delete()
                return redirect('chopee:cart')
        elif action == 'input':
            qty = int(request.POST.get('quantity', 1))
            if qty > 0:
                cart_item.quantity = qty
            else:
                cart_item.delete()
                return redirect('chopee:cart')
                
        cart_item.save()
    return redirect('chopee:cart')

# 6. Remove from Cart View
@login_required(login_url='chopee:login')
def remove_from_cart_view(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    cart_item.delete()
    messages.success(request, "ลบสินค้าออกจากตะกร้าแล้ว")
    return redirect('chopee:cart')

# 7. Checkout View
@login_required(login_url='chopee:login')
def checkout_view(request):
    cart_items = CartItem.objects.filter(user=request.user)
    if not cart_items.exists():
        messages.warning(request, "กรุณาเพิ่มสินค้าลงตะกร้าก่อนทำการสั่งซื้อ")
        return redirect('chopee:home')
        
    total_price = sum(item.total_price for item in cart_items)
    shipping_cost = 40.00 # Dummy fixed shipping
    grand_total = float(total_price) + shipping_cost

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'shipping_cost': shipping_cost,
        'grand_total': grand_total,
        'cart_count': get_cart_count(request),
    }
    return render(request, 'chopee/checkout.html', context)

# 8. Place Order View (POST)
@login_required(login_url='chopee:login')
def place_order_view(request):
    if request.method == 'POST':
        cart_items = CartItem.objects.filter(user=request.user)
        if not cart_items.exists():
            return redirect('chopee:home')
            
        shipping_name = request.POST.get('shipping_name')
        shipping_phone = request.POST.get('shipping_phone')
        shipping_address = request.POST.get('shipping_address')
        payment_method = request.POST.get('payment_method', 'เก็บเงินปลายทาง')
        
        # Calculate totals
        total_items_price = sum(item.total_price for item in cart_items)
        shipping_cost = 40.00
        grand_total = float(total_items_price) + shipping_cost
        
        # Create Order
        order = Order.objects.create(
            user=request.user,
            shipping_name=shipping_name,
            shipping_phone=shipping_phone,
            shipping_address=shipping_address,
            payment_method=payment_method,
            total_price=grand_total,
            status='Paid' # Simulate paid order immediately
        )
        
        # Create OrderItems and decrement stock
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                product_name=item.product.name,
                quantity=item.quantity,
                price=item.product.price
            )
            # Update product stock & sold count
            product = item.product
            product.stock = max(0, product.stock - item.quantity)
            product.sold_count += item.quantity
            product.save()
            
        # Clear Cart
        cart_items.delete()
        
        return redirect('chopee:order_success', order_id=order.id)
        
    return redirect('chopee:checkout')

# 9. Order Success View
@login_required(login_url='chopee:login')
def order_success_view(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    context = {
        'order': order,
        'cart_count': get_cart_count(request),
    }
    return render(request, 'chopee/order_success.html', context)

# 10. Profile / Order History View
@login_required(login_url='chopee:login')
def profile_view(request):
    status_filter = request.GET.get('status', 'all')
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    if status_filter != 'all':
        orders = orders.filter(status=status_filter)
        
    context = {
        'orders': orders,
        'status_filter': status_filter,
        'cart_count': get_cart_count(request),
    }
    return render(request, 'chopee/profile.html', context)

# 11. Login View
def login_view(request):
    if request.user.is_authenticated:
        return redirect('chopee:home')
        
    next_url = request.GET.get('next', 'chopee:home')
    if request.method == 'POST':
        username = request.POST.get('username')
        passw = request.POST.get('password')
        user = authenticate(request, username=username, password=passw)
        if user is not None:
            login(request, user)
            messages.success(request, f"ยินดีต้อนรับกลับมา, {user.username}!")
            if next_url.startswith('/'):
                return redirect(next_url)
            return redirect('chopee:home')
        else:
            messages.error(request, "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")
            
    return render(request, 'chopee/login.html', {'next': next_url})

# 12. Register View
def register_view(request):
    if request.user.is_authenticated:
        return redirect('chopee:home')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        passw = request.POST.get('password')
        passw_confirm = request.POST.get('password_confirm')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "ชื่อผู้ใช้นี้มีคนใช้แล้ว")
        elif passw != passw_confirm:
            messages.error(request, "รหัสผ่านไม่ตรงกัน")
        else:
            user = User.objects.create_user(username=username, email=email, password=passw)
            login(request, user)
            messages.success(request, "สมัครสมาชิกสำเร็จ! ยินดีต้อนรับสู่ Chopee")
            return redirect('chopee:home')
            
    return render(request, 'chopee/register.html')

# 13. Logout View
def logout_view(request):
    logout(request)
    messages.success(request, "ออกจากระบบสำเร็จ")
    return redirect('chopee:home')
