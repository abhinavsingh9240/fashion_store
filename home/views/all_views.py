import razorpay
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from verify_email.email_handler import send_verification_email
from fashion_store import settings
from home.forms import RegistrationForm, LoginForm, CartForm, OrderItemForm
from home.models import Category, Product, Section, Size, Cart, Order, OrderItem, OrderPayment


# Create your views here.
def index(request):
    categories = Category.objects.all()

    context = {
        "categories": categories,
        "sizes": Size.objects.all(),
        "sections": Section.objects.all(),
    }
    return render(request, "index.html", context=context)


def list_view(request):
    products = Product.objects.all()
    category_id = request.GET.get('category')
    size = request.GET.get('size')
    section = request.GET.get('section')
    if category_id:
        products = products.filter(category__id=category_id)
    if size:
        products = products.filter(size__name=size)
    if section:
        products = products.filter(section__name=section)
    context = {
        "products": products
    }
    return render(request, "list.html", context=context)


def product_view(request, product_id):
    product = Product.objects.get(id=product_id)
    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect('sign_in')

        if 'add-cart' in request.POST:
            cart_form = CartForm(request.POST)
            if cart_form.is_valid():
                cart_instance = cart_form.save(commit=False)
                cart_instance.user = request.user
                cart_instance.product_id = product_id
                cart_instance.save()

        elif 'buy-now' in request.POST:
            order_item_form = OrderItemForm(request.POST)
            if order_item_form.is_valid():
                order_item = order_item_form.save(commit=False)
                order_item.product = product
                order_item.price = product.price * order_item.quantity

                order = Order.objects.create(user=request.user)
                order_item.order = order
                order_item.save()

                return redirect('order_page', order_id=order.id)

    context = {
        "product": product
    }
    return render(request, 'product_page.html', context=context)


@login_required
@csrf_exempt
def cart_panel(request):
    if request.method == "POST":
        item_id = request.POST.get('id')
        cart_instance = Cart.objects.get(id=item_id)
        if cart_instance.user.id == request.user.id:
            cart_instance.delete()

    cart_items = Cart.objects.filter(user=request.user)
    items = []
    total_price = 0
    for item in cart_items:
        data = {
            'id': item.id,
            'quantity': item.quantity,
            'image': item.product.get_dp_url(),
            'size': item.size.name,
            'name': item.product.name,
            'price': item.product.price * item.quantity,
            'product_id': item.product.id,
        }
        items.append(data)
        total_price += data['price']

    response = {
        'items': items,
        'total_price': total_price,
    }
    return JsonResponse(response)


@csrf_exempt
def search_view(request):
    products = []
    results = []
    if request.method == "POST":
        query = request.POST.get('query')
        if query:
            query = query.strip()
            products = Product.objects.filter(name__icontains=query)

    for product in products:
        results.append({
            'image': product.get_dp_url(),
            'name': product.name,
            'product_id': product.id,
        })

    return JsonResponse({'results': results})


def signin_view(request):
    form = LoginForm()
    message = ""
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email_phone = form.cleaned_data["email_phone"]
            password = form.cleaned_data["password"]

            # user = authenticate(request, username=email_phone, password=password)
            try:
                user = User.objects.get(username=email_phone)
                if user.check_password(password):
                    login(request, user)
                    if user.is_active:
                        return redirect('index')
                    else:
                        return redirect('request-new-link-from-email')

            except Exception as e:
                print(e)

            message = "Invalid Credentials"

    context = {
        "message": message,
        "form": form,
    }
    return render(request, 'auth/sign_in.html', context)


def signup_view(request):
    message = ""
    form = RegistrationForm()
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        # Checking if user is already registerd or not
        user = None
        try:
            user = User.objects.get(username=form.cleaned_data["email"])
        except Exception as e:
            print(e)

        if form.is_valid() and user is None:
            # user = form.save(commit=False)
            inactive_user = send_verification_email(request, form)
            inactive_user.username = inactive_user.email
            inactive_user.save()
            return redirect("sign_in")

        elif user:
            message = "User with email already exist"

    context = {
        "form": form,
        "message": message,
    }
    return render(request, template_name='auth/sign_up.html', context=context)


def signout_view(request):
    if request.method == "POST":
        logout(request)
        # return render(request, template_name="auth/sign_out.html")
    return redirect("index")


# TODO: Add loginrequired to the views that need it
@login_required
def checkout_view(request):
    if request.method == "POST" and 'cart-order' in request.POST:

        # if order is from cart
        order = Order.objects.create(user=request.user)
        for cart_item in Cart.objects.filter(user=request.user):
            item_price = cart_item.quantity * cart_item.product.price
            OrderItem.objects.create(order=order, product=cart_item.product, quantity=cart_item.quantity,
                                     size=cart_item.size, price=item_price)
            cart_item.delete()
        # return render(request, template_name='order/checkout.html', context={"order": order})
        return redirect('order_page', order_id=order.id)

    return redirect('index')


@login_required
def order_view(request, order_id):
    order = Order.objects.get(id=order_id)
    if request.user == order.user:
        if request.method == "POST" and "cancel-order" in request.POST:
            Order.objects.get(id=order_id).delete()
            return redirect("orders_page")
        context = {
            "order": order
        }
        return render(request, template_name='order/order.html', context=context)
    else:
        return redirect('index')


razorpay_client = razorpay.Client(
    auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))


@login_required
def payment_view(request, order_id):
    order = Order.objects.get(id=order_id)
    if request.method == 'POST' and request.user == order.user:
        total_amount = order.amount

        currency = 'INR'
        razorpay_amount = total_amount * 100

        if hasattr(order, 'orderpayment'):
            razorpay_order_id = order.orderpayment.razorpay_order_id
        else:
            # Create a Razorpay Order
            razorpay_order = razorpay_client.order.create(dict(amount=razorpay_amount,
                                                               currency=currency,
                                                               payment_capture='0'))

            # order id of newly created order.
            razorpay_order_id = razorpay_order['id']

            OrderPayment.objects.create(razorpay_order_id=razorpay_order_id, order=order, amount=total_amount)

        callback_url = '/paymenthandler/'
        context = {'razorpay_order_id': razorpay_order_id, 'razorpay_merchant_key': settings.RAZOR_KEY_ID,
                   'razorpay_amount': razorpay_amount, 'currency': currency, 'callback_url': callback_url,
                   'order': order}
        return render(request, 'order/payment.html', context=context)

    return redirect('index')


@csrf_exempt
def paymenthandler(request):
    # only accept POST request.
    if request.method == "POST":
        try:

            # get the required parameters from post request.
            payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }

            # verify the payment signature.
            result = razorpay_client.utility.verify_payment_signature(
                params_dict)
            if result is not None:
                payment_instance = OrderPayment.objects.get(razorpay_order_id=razorpay_order_id)
                razorpay_amount = payment_instance.amount * 100
                try:

                    # capture the payemt
                    razorpay_client.payment.capture(payment_id, razorpay_amount)
                    payment_instance.order.ordered = True
                    payment_instance.order.save()
                    # render success page on successful caputre of payment
                    return render(request, 'paymentsuccess.html')
                except:

                    # if there is an error while capturing payment.
                    return render(request, 'paymentfail.html')
            else:

                # if signature verification fails.
                return render(request, 'paymentfail.html')
        except:

            # if we don't find the required parameters in POST data
            return HttpResponseBadRequest()
    else:
        # if other than POST request is made.
        return HttpResponseBadRequest()


@login_required
def orders_view(request):
    context = {
        "orders": Order.objects.filter(user=request.user).order_by('-created_at'),
    }
    return render(request, template_name='order/orders.html', context=context)
