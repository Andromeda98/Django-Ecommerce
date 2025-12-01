
from django.shortcuts import render, redirect
from cart.cart import Cart
from payment.forms import ShippingForm, PaymentForm
from payment.models import ShippingAddress, Order, OrderItem
from django.contrib.auth.models import User
from django.contrib import messages
from store.models import Product

def not_shipped_dash(request):
    if request.user.is_authenticated:
        orders = Order.objects.filter(shipped=False)
        return render(request, "payment/not_shipped_dash.html", {"orders":orders})
    else:
        messages.success(request, "Access Denied")
        return redirect('home')

def shipped_dash(request):
    if request.user.is_authenticated:
        orders = Order.objects.filter(shipped=True)
        return render(request, "payment/shipped_dash.html", {"orders":orders})
    else:
        messages.success(request, "Access Denied")
        return redirect('home')


def process_order(request):
    if request.POST:
        # Get the cart
        cart = Cart(request)
        cart_products = cart.get_prods()      # QuerySet
        quantities = cart.get_quants()        # Diccionario
        totals = cart.cart_total()

        # Get Billing Info from the last page
        payment_form = PaymentForm(request.POST or None)

        # Get Shipping Session Data
        my_shipping = request.session.get('my_shipping')
        print(my_shipping)

        full_name = my_shipping['shipping_full_name']
        email = my_shipping['shipping_email']

        # Create Shipping Address from session info
        shipping_address = (
            f"{my_shipping['shipping_address1']}\n"
            f"{my_shipping['shipping_address2']}\n"
            f"{my_shipping['shipping_city']}\n"
            f"{my_shipping['shipping_state']}\n"
            f"{my_shipping['shipping_zipcode']}\n"
            f"{my_shipping['shipping_country']}"
        )

        amount_paid = totals

        # Usuario autenticado
        if request.user.is_authenticated:
            user = request.user

            create_order = Order(
                user=user,
                full_name=full_name,
                email=email,
                shipping_address=shipping_address,
                amount_paid=amount_paid
            )
            create_order.save()

            # Get the order ID
            order_id = create_order.pk

            # Create order items
            for product in cart_products:
                product_id = product.id

                # Price
                price = product.sale_price if product.is_sale else product.price

                # Quantity
                for key, value in quantities.items():
                    if int(key) == product.id:
                        create_order_item = OrderItem(
                            order_id=order_id,
                            product_id=product_id,
                            user=user,
                            quantity=value,
                            price=price
                        )
                        create_order_item.save()

            # Delete our cart
            for key in list(request.session.keys()):
                if key == "session_key":
                    del request.session[key]

            messages.success(request, "Order Placed!")
            return redirect('home')

        # Usuario NO autenticado
        else:
            create_order = Order(
                full_name=full_name,
                email=email,
                shipping_address=shipping_address,
                amount_paid=amount_paid
            )
            create_order.save()

            order_id = create_order.pk

            for product in cart_products:
                product_id = product.id
                price = product.sale_price if product.is_sale else product.price

                for key, value in quantities.items():
                    if int(key) == product.id:
                        create_order_item = OrderItem(
                            order_id=order_id,
                            product_id=product_id,
                            quantity=value,
                            price=price
                        )
                        create_order_item.save()

            # Delete our cart
            for key in list(request.session.keys()):
                if key == "session_key":
                    del request.session[key]

            messages.success(request, "Order Placed!")
            return redirect('home')

    else:
        messages.success(request, "Access Denied")
        return redirect('home')

def billing_info(request):
    if request.POST:
        # Get the cart
        cart = Cart(request)
        cart_products = cart.get_prods()
        quantities = cart.get_quants()
        totals = cart.cart_total()


        # Create a session with Shipping Info
        my_shipping = request.POST
        request.session['my_shipping'] = my_shipping

        # Check if user is logged in
        if request.user.is_authenticated:
            # Get the Billing Form
            billing_form = PaymentForm()
            return render(request, "payment/billing_info.html", {
                "cart_products": cart_products,
                "quantities": quantities,
                "totals": totals,
                "shipping_info": request.POST,
                "billing_form": billing_form
            })
        else:
            # Not logged in
            billing_form = PaymentForm()
            return render(request, "payment/billing_info.html", {
                "cart_products": cart_products,
                "quantities": quantities,
                "totals": totals,
                "shipping_info": request.POST,
                "billing_form": billing_form
            })

        # Fallback (if needed)
        shipping_form = request.POST
        return render(request, "payment/billing_info.html", {
            "cart_products": cart_products,
            "quantities": quantities,
            "totals": totals,
            "shipping_form": shipping_form
        })
    else:
        messages.success(request, "Access Denied")
        return redirect('home')

# def checkout(request):
#     # Get the cart
#     cart = Cart(request)
#     cart_products = cart.get_prods()
#     quantities = cart.get_quants()
#     totals = cart.cart_total()

#     if request.user.is_authenticated:
#         # Checkout as logged in user
#         # Shipping User
#         shipping_user = ShippingAddress.objects.get(user_id=request.user.id)
#         # Shipping Form
#         shipping_form = ShippingForm(request.POST or None, instance=shipping_user)
#         return render(request, "payment/checkout.html", {
#             "cart_products": cart_products,
#             "quantities": quantities,
#             "totals": totals,
#             "shipping_form": shipping_form
#         })
#     else:
#         # Checkout as guest
#         shipping_form = ShippingForm(request.POST or None)
#         return render(request, "payment/checkout.html", {
#             "cart_products": cart_products,
#             "quantities": quantities,
#             "totals": totals,
#             "shipping_form": shipping_form
#         })

def checkout(request):
    # Get the cart
    cart = Cart(request)
    cart_products = cart.get_prods()
    quantities = cart.get_quants()
    totals = cart.cart_total()

    if request.user.is_authenticated:
        # Checkout as logged in user
        # Shipping User - USAR get_or_create PARA EVITAR EL ERROR
        try:
            shipping_user, created = ShippingAddress.objects.get_or_create(user=request.user)
        except ShippingAddress.MultipleObjectsReturned:
            # Si hay múltiples, tomar el primero
            shipping_user = ShippingAddress.objects.filter(user=request.user).first()
        
        # Shipping Form
        shipping_form = ShippingForm(request.POST or None, instance=shipping_user)
        return render(request, "payment/checkout.html", {
            "cart_products": cart_products,
            "quantities": quantities,
            "totals": totals,
            "shipping_form": shipping_form
        })
    else:
        # Checkout as guest
        shipping_form = ShippingForm(request.POST or None)
        return render(request, "payment/checkout.html", {
            "cart_products": cart_products,
            "quantities": quantities,
            "totals": totals,
            "shipping_form": shipping_form
        })


def payment_success(request):
    return render(request, "payment/payment_success.html", {})
