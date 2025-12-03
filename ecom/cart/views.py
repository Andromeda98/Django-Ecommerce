from django.shortcuts import render, get_object_or_404
from .cart import Cart
from store.models import Book
from django.http import JsonResponse
from django.contrib import messages


def cart_summary(request):
    cart = Cart(request)
    cart_products = cart.get_prods()
    quantities = cart.get_quants()
    totals = cart.cart_total()
    return render(request, "cart_summary.html", {'cart_products': cart_products, "quantities": quantities, "totals": totals})

def cart_add(request):
    # Get the cart
    cart = Cart(request)

    # test for POST
    
    if request.POST.get('action') == 'post':
        # Get stuff
        product_id = int(request.POST.get('product_id'))
        product_qty = int(request.POST.get('product_qty'))

        # lookup product in DB
        product = get_object_or_404(Book, id=product_id)

        # Save to session
        cart.add(product=product, quantity=product_qty)

        # Get Cart Quantity
        cart_quantity = cart.__len__()

        # Return response
        # response = JsonResponse({'Product Name: ': product.name})
        response = JsonResponse({'qty': cart_quantity})
        messages.success(request, "Libro añadido al carrito")

        return response

    
    

def cart_delete(request):
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        # Obtener el ID del producto
        product_id = int(request.POST.get('product_id'))

        # Llamar a la función delete en la clase Cart
        cart.delete(product=product_id)

        # Responder con JSON
        response = JsonResponse({'product': product_id})
        # return redirect('cart_summary')
        messages.success(request, "Libro eliminado del carrito de la compra")

        return response


def cart_update(request):
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        # Obtener datos del POST
        product_id = int(request.POST.get('product_id'))
        product_qty = int(request.POST.get('product_qty'))

        # Actualizar el carrito
        cart.update(product=product_id, quantity=product_qty)

        # Responder con JSON
        response = JsonResponse({'qty': product_qty})
        # return redirect('cart_summary')
        messages.success(request, "Tu carrito ha sido añadido")

        return response
