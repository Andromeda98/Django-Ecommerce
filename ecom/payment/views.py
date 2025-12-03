
from django.shortcuts import render, redirect
from cart.cart import Cart
from payment.forms import ShippingForm, PaymentForm
from payment.models import ShippingAddress, Order, OrderItem
from django.contrib.auth.models import User
from django.contrib import messages
from store.models import Book, Profile
import datetime



def orders(request, pk):
    """
    Vista de detalle de un pedido específico (solo administradores).
    
    Permite a los administradores ver los detalles completos de un pedido
    y actualizar su estado de envío.
    
    Args:
        request (HttpRequest): Objeto de solicitud HTTP.
        pk (int): ID del pedido a mostrar.
    
    Returns:
        HttpResponse: Página con detalles del pedido y sus items.
    
    Notas:
        - Requiere autenticación y permisos de superusuario.
        - Permite marcar el pedido como enviado/no enviado.
    """
    if request.user.is_authenticated and request.user.is_superuser:
        # Get the order
        order = Order.objects.get(id=pk)
        # Get the order items
        items = OrderItem.objects.filter(order=pk)
        
        if request.POST:
            status = request.POST['shipping_status']
            # Check if true or false
            if status == "true":
                # Get the order
                order = Order.objects.filter(id=pk)
                # Update the status
                now = datetime.datetime.now()
                order.update(shipped=True, date_shipped=now)
            else:
                # Get the order
                order = Order.objects.filter(id=pk)
                # Update the status
                order.update(shipped=False)
            messages.success(request, "Shipping Status Updated")
            return redirect('home')


        return render(request, 'payment/orders.html', {"order": order, "items": items})

    else:
        messages.error(request, "Acceso Denegado - Solo Administradores")
        return redirect('home')

def not_shipped_dash(request):
    """
    Dashboard de pedidos no enviados (solo administradores).
    
    Muestra todos los pedidos pendientes de envío y permite marcarlos como enviados.
    
    Args:
        request (HttpRequest): Objeto de solicitud HTTP.
    
    Returns:
        HttpResponse: Página con lista de pedidos no enviados.
    
    Notas:
        - Requiere autenticación y permisos de superusuario.
        - Al marcar como enviado, registra automáticamente la fecha actual.
    """
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objects.filter(shipped=False)
        
        if request.POST:
            status = request.POST['shipping_status']
            num = request.POST['num']

            order = Order.objects.filter(id=num)
            # grab Date and time
            now = datetime.datetime.now()

            # update order
            order.update(shipped=True, date_shipped=now)

            # redirect
            messages.success(request, "Shipping Status Updated")
            return redirect('home')

        return render(request, "payment/not_shipped_dash.html", {"orders":orders})
    else:
        messages.error(request, "Acceso Denegado - Solo Administradores")
        return redirect('home')

def shipped_dash(request):
    """
    Dashboard de pedidos enviados (solo administradores).
    
    Muestra todos los pedidos que ya han sido enviados y permite revertir su estado.
    
    Args:
        request (HttpRequest): Objeto de solicitud HTTP.
    
    Returns:
        HttpResponse: Página con lista de pedidos enviados.
    
    Notas:
        - Requiere autenticación y permisos de superusuario.
        - Permite cambiar el estado de enviado a no enviado si es necesario.
    """
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objects.filter(shipped=True)
        
        if request.POST:
            status = request.POST['shipping_status']
            num = request.POST['num']

            order = Order.objects.filter(id=num)



            # grab Date and time
            now = datetime.datetime.now()

            # update order
            order.update(shipped=False)

            # redirect
            messages.success(request, "Shipping Status Updated")
            return redirect('home')

        return render(request, "payment/shipped_dash.html", {"orders":orders})
    else:
        messages.error(request, "Acceso Denegado - Solo Administradores")
        return redirect('home')


def process_order(request):
    """
    Vista para procesar y crear un pedido completo.
    
    Recibe la información de facturación, obtiene los datos de envío de la sesión,
    crea el pedido (Order) y sus items (OrderItem) asociados. Funciona tanto para
    usuarios autenticados como invitados.
    
    Args:
        request (HttpRequest): Objeto de solicitud HTTP con datos del formulario de pago.
    
    Returns:
        HttpResponse: Redirección a home después de crear el pedido exitosamente.
    
    Notas:
        - Obtiene datos de envío desde request.session['my_shipping'].
        - Para usuarios autenticados, guarda el user en Order y OrderItem.
        - Limpia el carrito tanto de la sesión como del campo old_cart del Profile.
        - Calcula el precio usando sale_price si is_sale es True, sino usa price normal.
    
    Ejemplos:
        Crea Order con full_name, email, shipping_address, amount_paid.
        Crea OrderItem por cada producto con order_id, product_id, quantity, price.
    """
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

                
            # Delete Cart from Database (old cart field)
            current_user = Profile.objects.filter(user_id=request.user.id)
            # Delete shopping cart in database (old cart field)
            current_user.update(old_cart="")


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
    """
    Vista de información de facturación.
    
    Recibe los datos de envío del formulario anterior, los guarda en la sesión
    y muestra el formulario de pago (tarjeta de crédito, etc.).
    
    Args:
        request (HttpRequest): Objeto de solicitud HTTP con datos de envío.
    
    Returns:
        HttpResponse: Página con formulario de facturación y resumen del carrito.
    
    Notas:
        - Guarda los datos de envío en request.session['my_shipping'].
        - La sesión se usará posteriormente en process_order().
    """
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
    """
    Vista del proceso de checkout (pago).
    
    Muestra el formulario de dirección de envío y el resumen del carrito.
    Para usuarios autenticados, precarga su dirección guardada.
    
    Args:
        request (HttpRequest): Objeto de solicitud HTTP.
    
    Returns:
        HttpResponse: Página de checkout con formulario de envío y resumen del carrito.
    
    Notas:
        - Usa get_or_create para evitar errores si el usuario no tiene ShippingAddress.
        - Maneja el caso de múltiples direcciones (MultipleObjectsReturned) tomando la primera.
    """
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
    """
    Vista de confirmación de pago exitoso.
    
    Args:
        request (HttpRequest): Objeto de solicitud HTTP.
    
    Returns:
        HttpResponse: Página de confirmación de pedido procesado exitosamente.
    """
    return render(request, "payment/payment_success.html", {})
