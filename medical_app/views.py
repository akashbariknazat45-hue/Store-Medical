from django.shortcuts import render, redirect
from .models import Medical_Product, Medical_Favourite, Medical_Cart, Medical_Category, Medical_Address
from .models import OrderItem, Madical_Order
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .templatetags.helper import get_favourites_count
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
import random
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q
from groq import Groq
import base64
import traceback

# setting a razorpay client globally
client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

# Create your views here.

def home_func(request):
    search = request.GET.get('search', '')
    category = request.GET.get('category', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')

    popular = request.GET.get('popular')
    new = request.GET.get('new')
    show_categories = request.GET.get('categories')

    products = Medical_Product.objects.filter(
        product_is_active=True
    )

    categories = Medical_Category.objects.all()

    # Search
    if search:
        products = products.filter(
            product_name__icontains=search
        )

    # Category
    if category:
        products = products.filter(
            product_category__category_slug=category
        )

    # Price
    if min_price:
        products = products.filter(
            product_price__gte=min_price
        )

    if max_price:
        products = products.filter(
            product_price__lte=max_price
        )

    # Popular Items
    if popular:
        products = products.filter(
            product_is_featured=True
        )

    # New Arrivals
    elif new:
        products = products.order_by(
            '-product_created_at'
        )

    context = {
        'products': products,
        'categories': categories,
        'search': search,
        'selected_category': category,
        'min_price': min_price,
        'max_price': max_price,
        'popular': popular,
        'new': new,
        'show_categories': show_categories,

        # CART PRODUCT IDS
    }

    return render(request, 'index.html', context)


def contact_func(request):
    return render(request,"contact.html")

def about_func(request):
    return render(request, "about.html")


def get_product_detail_view(request, pslug):

    product = Medical_Product.objects.filter(
        product_slug=pslug
    ).first()

    cart_product_ids = []

    if request.user.is_authenticated:
        cart_product_ids = Medical_Cart.objects.filter(
            user=request.user
        ).values_list(
            'product_id',
            flat=True
        )
        favourite_product_ids = Medical_Favourite.objects.filter(
            user=request.user
        ).values_list(
            'product_id',
            flat=True
        )


    context = {
        'product': product,
        'cart_product_ids': cart_product_ids,
        'favourite_product_ids': favourite_product_ids,
    }

    return render(
        request,
        'specific_product.html',
        context
    )
def add_to_favourites(request, userid, pid):

    user = User.objects.filter(id=userid).first()

    if not user:
        messages.error(request, "No User found")
        return redirect('home')

    product = Medical_Product.objects.filter(id=pid).first()

    if not product:
        messages.error(request, "No Product found")
        return redirect('home')

    # Already Favourite কিনা check
    already_favourite = Medical_Favourite.objects.filter(
        user=user,
        product=product
    ).exists()

    if already_favourite:
        return redirect('favourites')

    # Favourite এ add
    Medical_Favourite.objects.create(
        user=user,
        product=product
    )

    messages.success(
        request,
        "Product Added To Your Favourites"
    )

    return redirect('home')

def favourites(request):
    user = request.user
    print(get_favourites_count(user.id))
    items = Medical_Favourite.objects.filter(user = user)
    context = {
        'items': items

    }
    return render(request, "favourites.html",context)

def remove_from_favourites(request, userid, pid):
    if not Medical_Favourite.objects.filter(user = userid).first():
        messages.error(request,"No User found with these user id")
        return redirect('home')

    if not Medical_Favourite.objects.filter(product = pid).first():
        messages.error(request,"No Product found with these user id")
        return redirect('home')

    favourites_obj = Medical_Favourite.objects.filter(user = userid, product = pid).first()
    favourites_obj.delete()

    messages.success(request,"Product Remove from Your Favourites")
    return redirect("favourites")


def get_cart_items(request):
    user = request.user
    items = Medical_Cart.objects.filter(user=user)
    context = {
        "items": items
    }
    return render(request,"carts.html", context)


def delete_item_from_cart(request, pid):
    user = request.user
    product = Medical_Product.objects.filter(id=pid).first()
    if not product:
        messages.error(request,"Product Not Found")
        return redirect('cart')

    cart_item = Medical_Cart.objects.filter(user=user, product=product).first()
    cart_item.delete()
    messages.success(request,"Product Remove from Your Cart")
    return redirect('cart')

def update_cart_item(request):
    user = request.user
    if request.method == "POST":
        product = request.POST['product']
        quantity = request.POST['quantity']

        product = Medical_Product.objects.filter(id=product).first()
        cart_item = Medical_Cart.objects.filter(user=user, product=product).first()
        cart_item.quantity = quantity
        cart_item.save()

        messages.success(request,"Cart Item updated Successfully !")
        return redirect('cart')


def add_items_to_cart(request):
    if request.method == "POST":

        product_id = request.POST['product']
        quantity = request.POST['quantity']

        product = Medical_Product.objects.filter(id=product_id).first()

        if not product:
            messages.error(request, "Product not found!")
            return redirect('home')

        # Check product already exists in cart
        cart_item = Medical_Cart.objects.filter(
            user=request.user,
            product=product
        ).first()

        if cart_item:
            messages.info(request, "Product is already in your cart!")
            return redirect('cart')

        # Add new product
        Medical_Cart.objects.create(
            user=request.user,
            product=product,
            quantity=quantity
        )

        messages.success(
            request,
            "Product Added to Cart Successfully!"
        )

        return redirect('cart')

def manage_address(request):

    addresses = Medical_Address.objects.filter(user=request.user).order_by('-is_default', '-created_at')

    context = {
        'addresses': addresses
    }

    return render(request, "manage_address.html", context)



def add_address(request):

    if request.method == "POST":

        Medical_Address.objects.create(
            user=request.user,
            name=request.POST.get('name'),
            mobile=request.POST.get('mobile'),
            email=request.POST.get('email'),
            address=request.POST.get('address'),
            city=request.POST.get('city'),
            state=request.POST.get('state'),
            pincode=request.POST.get('pincode'),
            landmark=request.POST.get('landmark'),
            address_type=request.POST.get('address_type'),
        )

        messages.success(
            request,
            "Address added successfully!"
        )

        return redirect('manage_address')

    return render(request, "add_address.html")



def edit_address(request, address_id):

    address = get_object_or_404(
        Medical_Address,
        id=address_id,
        user=request.user
    )

    if request.method == "POST":

        address.name = request.POST.get('name')
        address.mobile = request.POST.get('mobile')
        address.email = request.POST.get('email')
        address.address = request.POST.get('address')
        address.city = request.POST.get('city')
        address.state = request.POST.get('state')
        address.pincode = request.POST.get('pincode')
        address.landmark = request.POST.get('landmark')
        address.address_type = request.POST.get('address_type')

        address.save()

        messages.success(
            request,
            "Address updated successfully!"
        )

        return redirect('manage_address')

    context = {
        'address': address
    }

    return render(request,"edit_address.html",context)


def delete_address(request, address_id):

    address = get_object_or_404(
        Medical_Address,
        id=address_id,
        user=request.user
    )

    address.delete()

    messages.success(
        request,
        "Address deleted successfully!"
    )

    return redirect('manage_address')



def default_address(request, address_id):

    address = get_object_or_404(
        Medical_Address,
        id=address_id,
        user=request.user
    )

    # সব address থেকে default remove
    Medical_Address.objects.filter(
        user=request.user
    ).update(is_default=False)

    # এই address-টাকে default করা
    address.is_default = True
    address.save()

    messages.success(
        request,
        "Default address changed successfully!"
    )

    return redirect('manage_address')

''' Auth function here '''

def user_login(request):
    if request. method == "POST":
        username = request.POST ['username'] #Unique
        password = request.POST ['password']


        if not User.objects.filter(username = username).first():
            messages. error (request, "User with this Username Not Exists!")
            return redirect ('login')
        authenticated_user = authenticate(request, username = username, password = password)
        if authenticated_user:
            login (request, authenticated_user)
            return redirect ('home')
        else:
            messages. error (request, "Invalid Password !")
            return redirect('login')

    return render(request, "login.html")

def user_register(request):
    if request.method == "POST":
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email'] # Unique
        username = request.POST['username'] # Unique
        password = request.POST['password']

        if User.objects.filter (email = email).first():
            messages.error(request, "User with this Email Already Exists !")
            return redirect('register')

        if User.objects.filter(username = username).first():
            messages.error(request, "User with this Username Already Exists !")
            return redirect('register')

        user_obj = User.objects.create(
            first_name = first_name,
            last_name = last_name,
            email = email,
            username = username,
            password = make_password (password)
        )

        if user_obj:
            messages.success (request, "User created successfully!")
            return redirect('register')
        else:
            messages.error(request, "Server Error: User Not Create")
            return redirect('register')

    return render(request, "register.html")

def user_logout(request):
    logout(request)
    return redirect('login')


@login_required
def change_password(request):

    if request.method == "POST":

        form = PasswordChangeForm(
            user=request.user,
            data=request.POST
        )

        if form.is_valid():

            user = form.save()

            # Keep user logged in after password change
            update_session_auth_hash(request, user)

            messages.success(
                request,
                "Your password has been changed successfully."
            )

            return redirect("home")

    else:

        form = PasswordChangeForm(
            user=request.user
        )

    return render(
        request,
        "change_password.html",
        {
            "form": form
        }
    )

def checkout(request):
    total_amount = 0
    user = request.user
    cart_items = Medical_Cart.objects.filter(user = user)
    address = Medical_Address.objects.filter(user = user)

    for i in cart_items:
        total_amount += i.product.product_price * i.quantity

    context = {
        'cart_items':cart_items,
        'total_amount' : total_amount,
        'address' : address
    }
    return render(request, "checkout.html", context)


def process_order(request):
    user = request.user
    if request.method == "POST":
        if 'address' not in request.POST:
            messages.error(request, "Address not selected !")
            return redirect('checkout')

        if 'payment_mode' not in request.POST:
            messages.error(request, "Payment Method not selected !")
            return redirect('checkout')

        address_id = request.POST['address']
        payment_mode = request.POST['payment_mode']

        address = Medical_Address.objects.filter(id=address_id).first()
        cart_items = Medical_Cart.objects.filter(user = user)

        if not cart_items.exists():
            messages.error(request, "There are no Products inside your cart !")
            return redirect('checkout')

        total_amount = sum(items.product.product_price * items.quantity for items in cart_items )
        tracking_no = 'MED' + str(random.randint(11111, 99999))

        if payment_mode == 'cod':
            try:
                #creating new Order
                new_order = Madical_Order.objects.create(
                    user = user,
                    shipping_address = address,
                    total_amount = total_amount,
                    payment_mode = 'cod',
                    payment_status = 'Pending',
                    tracking_no = tracking_no,
                )

                #  Move data from cart items to Orderitems
                for items in cart_items:
                    OrderItem.objects.create(
                        order = new_order,
                        product = items.product,
                        quantity = items.quantity
                    )
                cart_items.delete()
                context = {
                    'orderid' : new_order.order_id,
                    'date' : new_order.created_at,
                    'total' : new_order.total_amount
                }
                return render(request, 'success.html', context)

            except Exception as e:
                messages.warning(request, "Order not Generate Due to : ", e)
                return redirect('checkout')

        elif payment_mode == 'upi':
            razorpay_amount = int(total_amount*100)
            razorpay_order = client.order.create({
                'amount' : razorpay_amount,
                'currency' : 'INR',
                'payment_capture' : 1
            })
            new_order = Madical_Order.objects.create(
                user = request.user,
                shipping_address = address,
                total_amount = total_amount,
                payment_mode = 'online',
                payment_status = 'completed',
                tracking_no = tracking_no,
                razorpay_order_id = razorpay_order['id']
            )

            for items in cart_items:
                OrderItem.objects.create(
                    order = new_order,
                    product = items.product,
                    quantity = items.quantity
                )
            cart_items.delete()

            context = {
                'order': new_order,
                'razorpay_order_id' : razorpay_order ['id'],
                'razorpay_key_id': settings.RAZORPAY_KEY_ID,
                'amount': razorpay_amount,
                'currency':'INR',
                'callback_url': request.build_absolute_uri('/payment-callback/')
            }
            return render(request, 'razorpay_checkout.html', context)


        else:
            pass

    return HttpResponse("Order Processed")


def user_orders(request):
    user = request.user

    orders = Madical_Order.objects.filter(user=user).order_by("-id")

    context = {
        "orders": orders
    }

    return render(request,"orders.html",context)

@login_required
def order_bill(request, orderid):

    order = get_object_or_404(
        Madical_Order,
        order_id=orderid,
        user=request.user
    )

    order_items = OrderItem.objects.filter(order=order)

    subtotal = 0

    for item in order_items:
        subtotal += item.product.product_price * item.quantity

    delivery_charge = 0

    total = order.total_amount

    context = {
        'order': order,
        'order_items': order_items,
        'subtotal': subtotal,
        'delivery_charge': delivery_charge,
        'total': total,
    }

    return render(request, "bill.html", context)

def cancel_order(request, orderid):
    user = request.user
    order = Madical_Order.objects.filter(order_id=orderid).first()
    order.delete()
    messages.success(request,f"Order #{orderid} cancelled and deleted successfully.")
    return redirect('orders')



@csrf_exempt
def payment_callback(request):
    if request.method == "POST":
        razorpay_payment_id = request.POST.get('razorpay_payment_id', '')
        razorpay_order_id = request.POST.get('razorpay_order_id', '')
        razorpay_signature = request.POST.get('razorpay_signature', '')

        order = Madical_Order.objects.filter(razorpay_order_id=razorpay_order_id).first()
        if not order:
            messages.error(request, "Order not found.")
            return redirect('checkout')

        # Verify signature with Razorpay SDK
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }

        try:
            client.utility.verify_payment_signature(params_dict)

            # Signature matches - complete the order
            order.payment_status = 'completed'
            order.razorpay_payment_id = razorpay_payment_id
            order.razorpay_signeture = razorpay_signature
            order.save()

            # Empty user's cart
            Medical_Cart.objects.filter(user=order.user).delete()

            messages.success(request, f"Payment successful! Your order has been placed. {razorpay_signature}")
            return redirect('home')

        except razorpay.errors.SignatureVerificationError:
            order.payment_status = 'Failed'
            order.save()
            messages.error(request, "Payment verification failed. Please try again.")
            return redirect('checkout')


    return redirect('checkout')

@login_required
@require_POST
def ai_chat(request):
    # =====================================================
    # CREATE GROQ CLIENT
    # =====================================================
    client = Groq(
            api_key=settings.GROQ_API_KEY
    )

    try:

        # =========================================
        # CHECK PRESCRIPTION IMAGE
        # =========================================

        prescription_file = request.FILES.get(
            "prescription"
        )

        if prescription_file:

            return process_prescription(
                request,
                client,
                prescription_file
            )


        # =========================================
        # NORMAL TEXT CHAT
        # =========================================

        data = json.loads(
            request.body.decode("utf-8")
        )

        user_message = data.get(
            "message",
            ""
        ).strip()


        if not user_message:

            return JsonResponse({
                "error": "Please enter a message."
            }, status=400)
        # =====================================================
        # 1. CHECK PREVIOUS PENDING PRODUCTS
        # =====================================================

        pending_products = request.session.get("ai_pending_products", [])

        confirmation_words = [
            "yes",
            "yes add",
            "add them",
            "add all",
            "confirm",
            "confirm add",
            "add",
            "okay add",
            "ok add"
        ]

        normalized_message = user_message.lower().strip()

        if pending_products and normalized_message in confirmation_words:

            added_products = []
            failed_products = []

            for item in pending_products:

                try:
                    product = Medical_Product.objects.get(
                        id=item["id"],
                        product_is_active=True
                    )

                    requested_quantity = int(item.get("quantity", 1))

                    # Stock check
                    if product.product_quantity_in_stock <= 0:
                        failed_products.append(
                            f"{product.product_name} is out of stock."
                        )
                        continue

                    # Existing cart item
                    cart_item, created = Medical_Cart.objects.get_or_create(
                        user=request.user,
                        product=product,
                        defaults={
                            "quantity": min(
                                requested_quantity,
                                product.product_quantity_in_stock
                            )
                        }
                    )

                    if not created:

                        new_quantity = (
                            cart_item.quantity + requested_quantity
                        )

                        if new_quantity > product.product_quantity_in_stock:
                            new_quantity = product.product_quantity_in_stock

                        cart_item.quantity = new_quantity
                        cart_item.save(update_fields=["quantity"])

                    added_products.append(product.product_name)

                except Medical_Product.DoesNotExist:

                    failed_products.append(
                        f"Product ID {item['id']} not found."
                    )

            # Clear pending products
            request.session["ai_pending_products"] = []
            request.session.modified = True

            if added_products:

                reply = (
                    "✅ Added to your cart:\n"
                    + "\n".join(
                        f"• {name}"
                        for name in added_products
                    )
                )

                if failed_products:
                    reply += (
                        "\n\n⚠️ Some items could not be added:\n"
                        + "\n".join(
                            f"• {item}"
                            for item in failed_products
                        )
                    )

                return JsonResponse({
                    "success": True,
                    "action": "add_to_cart",
                    "reply": reply
                })

            return JsonResponse({
                "success": True,
                "reply": "Sorry, none of the selected products could be added."
            })

        # =====================================================
        # 3. GET ACTIVE PRODUCTS
        # =====================================================

        all_products = Medical_Product.objects.filter(
            product_is_active=True
        ).select_related(
            "product_category"
        )

        product_data = []

        for product in all_products[:100]:

            product_data.append({
                "id": product.id,
                "name": product.product_name,
                "price": str(product.product_price),
                "stock": product.product_quantity_in_stock,
                "category": product.product_category.category_name,
                "description": product.product_description[:200]
            })

        product_context = json.dumps(
            product_data,
            ensure_ascii=False
        )

        # =====================================================
        # 4. AI UNDERSTANDS USER REQUEST
        # =====================================================

        prompt = f"""
        You are MedCare AI Assistant for a medical store.

        User message:
        {user_message}

        Available products in the database:
        {product_context}

        Your job is ONLY to understand the user's request and match
        products from the provided database.

        IMPORTANT RULES:

        1. NEVER invent a product.
        2. NEVER invent a product ID.
        3. Only use products from the database.
        4. If user asks to add something to cart, identify matching
        database products.
        5. If quantity is mentioned, use that quantity.
        6. If quantity is not mentioned, use 1.
        7. If the user gives a prescription or multiple medicines,
        identify the medicine/product names but DO NOT automatically
        add them to the cart.
        8. Prescription products must require user confirmation first.
        9. Never change medicine name or dosage.
        10. Never diagnose the user.
        11. Never recommend a medicine that does not exist in the database.
        12. If there is no exact match, return the closest database
            product only if the name is clearly similar.
        13. Return ONLY valid JSON.

        JSON format:

        {{
            "action": "search" | "add_to_cart" | "prescription" | "chat",
            "product_ids": [],
            "quantities": [],
            "reply": "short friendly response"
        }}

        Examples:

        User:
        "thermometer add to cart"

        Return:
        {{
            "action": "add_to_cart",
            "product_ids": [PRODUCT_ID],
            "quantities": [1],
            "reply": "I found the thermometer."
        }}

        User:
        "add 2 thermometer"

        Return:
        {{
            "action": "add_to_cart",
            "product_ids": [PRODUCT_ID],
            "quantities": [2],
            "reply": "I found the thermometer."
        }}

        User:
        "Paracetamol 650 and thermometer are in my prescription"

        Return:
        {{
            "action": "prescription",
            "product_ids": [PRODUCT_ID_1, PRODUCT_ID_2],
            "quantities": [1, 1],
            "reply": "I found matching products from your prescription. Please confirm before adding them to your cart."
        }}

        User:
        "hello"

        Return:
        {{
            "action": "chat",
            "product_ids": [],
            "quantities": [],
            "reply": "Hello! How can I help you find products from MedCare?"
        }}
        """

        # =====================================================
        # 5. GROQ RESPONSE
        # =====================================================

        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2
        )


        ai_text = response.choices[0].message.content.strip()

        # Remove markdown code block if AI returns it
        if ai_text.startswith("```"):
            ai_text = ai_text.replace("```json", "")
            ai_text = ai_text.replace("```", "")
            ai_text = ai_text.strip()

        # =====================================================
        # 6. CONVERT AI JSON
        # =====================================================

        try:
            ai_result = json.loads(ai_text)

        except json.JSONDecodeError:

            return JsonResponse({
                "success": True,
                "action": "chat",
                "reply": ai_text
            })

        action = ai_result.get("action", "chat")

        product_ids = ai_result.get(
            "product_ids",
            []
        )

        quantities = ai_result.get(
            "quantities",
            []
        )

        reply = ai_result.get(
            "reply",
            ""
        )

        # =====================================================
        # 7. VALIDATE PRODUCT IDs FROM DATABASE
        # =====================================================

        matched_products = []

        for index, product_id in enumerate(product_ids):

            try:

                product = Medical_Product.objects.get(
                    id=int(product_id),
                    product_is_active=True
                )

                quantity = 1

                if index < len(quantities):

                    try:
                        quantity = int(quantities[index])
                    except (ValueError, TypeError):
                        quantity = 1

                if quantity < 1:
                    quantity = 1

                matched_products.append({
                    "id": product.id,
                    "name": product.product_name,
                    "price": str(product.product_price),
                    "stock": product.product_quantity_in_stock,
                    "quantity": quantity
                })

            except (
                Medical_Product.DoesNotExist,
                ValueError,
                TypeError
            ):
                continue

        # =====================================================
        # 8. PRESCRIPTION
        # =====================================================

        if action == "prescription":

            if not matched_products:

                return JsonResponse({
                    "success": True,
                    "action": "prescription",
                    "reply": (
                        "I couldn't find matching products "
                        "in the MedCare database."
                    )
                })

            # Save products temporarily in session
            request.session["ai_pending_products"] = [
                {
                    "id": item["id"],
                    "quantity": item["quantity"]
                }
                for item in matched_products
            ]

            request.session.modified = True

            product_lines = []

            for item in matched_products:

                product_lines.append(
                    f"• {item['name']} — ₹{item['price']}"
                )

            reply = (
                "I found these matching products:\n\n"
                + "\n".join(product_lines)
                + "\n\n"
                "⚠️ Please check the names against your prescription.\n"
                "Reply **Yes, add them** if you want me to add "
                "these products to your cart."
            )

            return JsonResponse({
                "success": True,
                "action": "prescription",
                "reply": reply,
                "products": matched_products
            })

        # =====================================================
        # 9. ADD TO CART
        # =====================================================

        if action == "add_to_cart":

            if not matched_products:

                return JsonResponse({
                    "success": True,
                    "action": "search",
                    "reply": (
                        "Sorry, I couldn't find that product "
                        "in our store."
                    ),
                    "products": []
                })

            added_products = []
            unavailable_products = []

            for item in matched_products:

                product = Medical_Product.objects.get(
                    id=item["id"]
                )

                quantity = item["quantity"]

                # -------------------------------
                # Stock check
                # -------------------------------

                if product.product_quantity_in_stock <= 0:

                    unavailable_products.append(
                        f"{product.product_name} is out of stock."
                    )

                    continue

                # -------------------------------
                # Existing cart
                # -------------------------------

                cart_item, created = Medical_Cart.objects.get_or_create(
                    user=request.user,
                    product=product,
                    defaults={
                        "quantity": min(
                            quantity,
                            product.product_quantity_in_stock
                        )
                    }
                )

                if not created:

                    new_quantity = (
                        cart_item.quantity + quantity
                    )

                    if new_quantity > product.product_quantity_in_stock:
                        new_quantity = product.product_quantity_in_stock

                    cart_item.quantity = new_quantity

                    cart_item.save(
                        update_fields=["quantity"]
                    )

                added_products.append(
                    product.product_name
                )

            # -------------------------------
            # Response
            # -------------------------------

            if added_products:

                reply = (
                    "✅ Added to your cart:\n"
                    + "\n".join(
                        f"• {name}"
                        for name in added_products
                    )
                )

                if unavailable_products:

                    reply += (
                        "\n\n⚠️ "
                        + "\n".join(unavailable_products)
                    )

                return JsonResponse({
                    "success": True,
                    "action": "add_to_cart",
                    "reply": reply,
                    "products": matched_products
                })

            return JsonResponse({
                "success": True,
                "action": "search",
                "reply": "\n".join(unavailable_products),
                "products": matched_products
            })

        # =====================================================
        # 10. NORMAL SEARCH / CHAT
        # =====================================================

        return JsonResponse({
            "success": True,
            "action": action,
            "reply": reply,
            "products": matched_products
        })

    except Exception as e:
        import traceback

        print("\n================ AI CHAT ERROR ================")
        print("ERROR:", str(e))
        traceback.print_exc()
        print("================================================\n")

        return JsonResponse({
            "success": False,
            "message": str(e)
        }, status=500)


def process_prescription(
    request,
    client,
    prescription_file
):

    try:

        # =========================================
        # FILE VALIDATION
        # =========================================

        allowed_types = [
            "image/jpeg",
            "image/png",
            "image/webp"
        ]

        if prescription_file.content_type not in allowed_types:

            return JsonResponse({
                "error": "Only JPG, PNG or WEBP images are allowed."
            }, status=400)


        # 10 MB limit

        if prescription_file.size > 10 * 1024 * 1024:

            return JsonResponse({
                "error": "Prescription image must be less than 10 MB."
            }, status=400)


        # =========================================
        # READ IMAGE
        # =========================================

        image_bytes = prescription_file.read()


        # =========================================
        # BASE64
        # =========================================

        base64_image = base64.b64encode(
            image_bytes
        ).decode("utf-8")


        mime_type = prescription_file.content_type


        image_data_url = (
            f"data:{mime_type};base64,{base64_image}"
        )


        # =========================================
        # PRESCRIPTION PROMPT
        # =========================================

        prescription_prompt = """
You are MedCare AI, a medical store shopping assistant.

Analyze the uploaded prescription image.

Your task is ONLY to identify medicine names and quantities
that are clearly visible in the prescription.

IMPORTANT RULES:

1. Do not diagnose the patient.
2. Do not recommend new medicines.
3. Do not change medicine names.
4. Do not change dosage.
5. Do not invent medicine names.
6. If a medicine name is unclear, mark it as unclear.
7. Only extract information that is actually visible.
8. Quantity should be extracted only if clearly visible.
9. Do not infer missing information.

Return ONLY valid JSON.

Format:

{
    "readable": true,
    "medicines": [
        {
            "name": "medicine name",
            "quantity": 1,
            "dosage": "visible dosage or empty string"
        }
    ],
    "unclear_items": [],
    "reply": "short friendly response"
}

If the prescription cannot be read:

{
    "readable": false,
    "medicines": [],
    "unclear_items": [
        "reason"
    ],
    "reply": "Please upload a clearer prescription image."
}
"""


        # =========================================
        # GROQ VISION
        # =========================================

        response = client.chat.completions.create(

            model="qwen/qwen3.8-27b",

            messages=[
                {
                    "role": "user",

                    "content": [

                        {
                            "type": "text",

                            "text": prescription_prompt
                        },

                        {
                            "type": "image_url",

                            "image_url": {
                                "url": image_data_url
                            }
                        }

                    ]
                }
            ],

            temperature=0,

            max_completion_tokens=1500,

            response_format={
                "type": "json_object"
            }

        )


        # =========================================
        # AI RESPONSE
        # =========================================

        ai_text = (
            response
            .choices[0]
            .message
            .content
            .strip()
        )


        ai_data = json.loads(
            ai_text
        )


        # =========================================
        # IMAGE NOT READABLE
        # =========================================

        if not ai_data.get("readable", False):

            return JsonResponse({

                "action": "prescription",

                "reply": ai_data.get(
                    "reply",
                    "I could not clearly read the prescription."
                ),

                "products": []

            })


        medicines = ai_data.get(
            "medicines",
            []
        )


        if not medicines:

            return JsonResponse({

                "action": "prescription",

                "reply": (
                    "I couldn't find any clearly readable "
                    "medicine names in the prescription."
                ),

                "products": []

            })


        # =========================================
        # DATABASE PRODUCTS
        # =========================================

        products = Medical_Product.objects.filter(
            product_quantity_in_stock__gt=0
        )


        matched_products = []

        unclear_items = []


        # =========================================
        # MATCH MEDICINES WITH DATABASE
        # =========================================

        for medicine in medicines:

            medicine_name = (
                medicine.get("name", "")
                .strip()
            )

            if not medicine_name:
                continue


            quantity = medicine.get(
                "quantity",
                1
            )


            try:

                quantity = int(quantity)

            except (ValueError, TypeError):

                quantity = 1


            if quantity < 1:
                quantity = 1


            # Exact / contains matching

            matched_product = None


            for product in products:

                db_name = (
                    product.product_name
                    .strip()
                    .lower()
                )

                search_name = (
                    medicine_name
                    .lower()
                )


                if (
                    search_name == db_name
                    or search_name in db_name
                    or db_name in search_name
                ):

                    matched_product = product

                    break


            if matched_product:

                matched_products.append({

                    "id": matched_product.id,

                    "name": matched_product.product_name,

                    "price": float(
                        matched_product.product_price
                    ),

                    "stock": matched_product.product_quantity_in_stock,

                    "quantity": quantity

                })

            else:

                unclear_items.append(
                    medicine_name
                )


        # =========================================
        # NO PRODUCTS MATCHED
        # =========================================

        if not matched_products:

            return JsonResponse({

                "action": "prescription",

                "reply": (
                    "I read the prescription, but I couldn't "
                    "find the prescribed medicines in our store."
                ),

                "products": [],

                "unavailable_items": unclear_items

            })


        # =========================================
        # SAVE PENDING PRODUCTS
        # =========================================

        request.session[
            "ai_pending_products"
        ] = [

            {
                "product_id": item["id"],
                "quantity": item["quantity"]
            }

            for item in matched_products

        ]

        request.session.modified = True


        # =========================================
        # RESPONSE
        # =========================================

        reply = (
            "I found the following medicines "
            "from your prescription. "
            "Please confirm before adding them to your cart."
        )


        return JsonResponse({

            "action": "prescription",

            "reply": reply,

            "products": matched_products,

            "unavailable_items": unclear_items

        })


    except Exception as e:

        traceback.print_exc()

        return JsonResponse({

            "error": (
                "Unable to process the prescription: "
                + str(e)
            )

        }, status=500)