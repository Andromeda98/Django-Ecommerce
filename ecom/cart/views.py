from django.shortcuts import render, get_object_or_404
from .cart import Cart
from store.models import Book
from django.http import JsonResponse
from django.contrib import messages


def cart_summary(request):
    """
    Vista que muestra el resumen completo del carrito de compras.
    
    Obtiene los productos del carrito, sus cantidades y el total a pagar.
    
    Args:
        request (HttpRequest): Objeto de solicitud HTTP.
    
    Returns:
        HttpResponse: Página con el resumen del carrito incluyendo productos, cantidades y total.
    """
    cart = Cart(request)
    cart_products = cart.get_prods()
    quantities = cart.get_quants()
    totals = cart.cart_total()
    return render(request, "cart_summary.html", {'cart_products': cart_products, "quantities": quantities, "totals": totals})

def cart_add(request):
    """
    Vista AJAX para añadir un libro al carrito de compras.
    
    Recibe el ID del producto y la cantidad mediante POST, busca el libro en la base de datos
    y lo añade al carrito de la sesión. Retorna la cantidad total de items en el carrito.
    
    Args:
        request (HttpRequest): Objeto de solicitud HTTP con action='post', product_id y product_qty.
    
    Returns:
        JsonResponse: Respuesta JSON con la cantidad total de items en el carrito.
    
    Ejemplos:
        POST con {'action': 'post', 'product_id': 5, 'product_qty': 2}
        Retorna {'qty': 3} si había 1 item previamente.
    """
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
    """
    Vista AJAX para eliminar un libro del carrito de compras.
    
    Recibe el ID del producto mediante POST y lo elimina del carrito.
    
    Args:
        request (HttpRequest): Objeto de solicitud HTTP con action='post' y product_id.
    
    Returns:
        JsonResponse: Respuesta JSON con el ID del producto eliminado.
    
    Ejemplos:
        POST con {'action': 'post', 'product_id': 5}
        Retorna {'product': 5}
    """
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
    """
    Vista AJAX para actualizar la cantidad de un libro en el carrito.
    
    Recibe el ID del producto y la nueva cantidad mediante POST.
    
    Args:
        request (HttpRequest): Objeto de solicitud HTTP con action='post', product_id y product_qty.
    
    Returns:
        JsonResponse: Respuesta JSON con la nueva cantidad del producto.
    
    Ejemplos:
        POST con {'action': 'post', 'product_id': 5, 'product_qty': 3}
        Retorna {'qty': 3}
    """
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
