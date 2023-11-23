import razorpay
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from fashion_store import settings
from home.forms import RegistrationForm, LoginForm, CartForm, ProductOrder
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
    if request.method == "POST":
        cart_form = CartForm(request.POST)
        if cart_form.is_valid():
            cart_instance = cart_form.save(commit=False)
            cart_instance.user = request.user
            cart_instance.product_id = product_id
            cart_instance.save()

    context = {
        "product": Product.objects.get(id=product_id)
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

            user = authenticate(request, username=email_phone, password=password)

            if user:
                login(request, user)
                return redirect('index')
            else:
                message = "Invalid Credentials"
    context = {
        "message": message,
        "form": form,
    }
    return render(request, 'sign_in.html', context)


def signup_view(request):
    form = RegistrationForm()
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.email
            user.save()

            redirect("sign_in")
    context = {
        "form": form
    }
    return render(request, template_name='sign_up.html', context=context)


def signout_view(request):
    if request.method == "POST":
        logout(request)
        return render(request, template_name="sign_out.html")
    return redirect("index")


def checkout_view(request):
    items = Cart.objects.filter(user=request.user)
    total = 0
    for item in items:
        total += item.product.price * item.quantity
    context = {
        'items': items,
        'total': total,
    }
    return render(request, template_name='order/checkout.html', context=context)


razorpay_client = razorpay.Client(
    auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))


def payment_view(request):
    if request.method == 'POST':
        total_amount = 0
        order = None
        if 'cart-order' in request.POST:
            # if order is from cart
            order = Order.objects.create(user=request.user)
            for cart_item in Cart.objects.filter(user=request.user):
                item_price = cart_item.quantity * cart_item.product.price
                OrderItem.objects.create(order=order, product=cart_item.product, quantity=cart_item.quantity,
                                         size=cart_item.size, price=item_price)
                total_amount += item_price
        elif 'product-order' in request.POST:
            # if ordering product directly
            form = ProductOrder(request.POST)
            quantity = form.cleaned_data['quantity']
            product_id = form.cleaned_data['product_id']
            size_id = form.cleaned_data['size_id']

            product = Product.objects.get(id=product_id)
            total_amount = product.price * quantity

            order = Order.objects.create(user=request.user)
            OrderItem.objects.create(order=order, product=product, quantity=quantity,
                                     size_id=size_id, price=total_amount)

        currency = 'INR'
        razorpay_amount = total_amount * 100
        # Create a Razorpay Order
        razorpay_order = razorpay_client.order.create(dict(amount=razorpay_amount,
                                                           currency=currency,
                                                           payment_capture='0'))

        # order id of newly created order.
        razorpay_order_id = razorpay_order['id']
        callback_url = 'paymenthandler/'

        OrderPayment.objects.create(razorpay_order_id=razorpay_order_id, order=order,amount=total_amount)

        context = {'razorpay_order_id': razorpay_order_id, 'razorpay_merchant_key': settings.RAZOR_KEY_ID,
                   'razorpay_amount': razorpay_amount, 'currency': currency, 'callback_url': callback_url,'order' :order}
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
                payment_instance = OrderPayment.objects.get(razorpay_order_id = razorpay_order_id)
                razorpay_amount = payment_instance.amount * 100
                try:

                    # capture the payemt
                    razorpay_client.payment.capture(payment_id, razorpay_amount)

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
