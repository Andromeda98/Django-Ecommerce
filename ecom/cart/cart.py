from django.shortcuts import get_object_or_404
from store.models import Product


class Cart():
    def __init__(self, request):
        self.session = request.session

        # Get the current session key if it exists
        cart = self.session.get('session_key')

        # If the user is new, no session key! Create one
        if 'session_key' not in request.session:
            cart = self.session['session_key'] = {}

        # Make sure cart is available on all pages of site
        self.cart = cart


   
    def add(self, product, quantity):  
        product_id = str(product.id)

        product_qty = str(quantity)
        # Logic
        if product_id in self.cart:
            pass
        else:
            #self.cart[product_id] = {'price': str(product.price)}
            self.cart[product_id] = int(product_qty)


        self.session.modified = True

    
    
    def cart_total(self):
        # Obtener los IDs de los productos en el carrito
        product_ids = self.cart.keys()

        # Buscar esos productos en la base de datos
        products = Product.objects.filter(id__in=product_ids)

        # Obtener las cantidades del carrito
        quantities = self.cart

        # Inicializar el total
        total = 0

        # Calcular el total
        for key, value in quantities.items():
            key = int(key)  # Convertir la clave a entero
            for product in products:
                
                if product.id == key:
                    if product.is_sale:
                        total += product.sale_price * value
                    else:
                        total += product.price * value


        return total



    def __len__(self):
        return len(self.cart)
    
    def get_prods(self):
        # Get ids from cart
        product_ids = self.cart.keys()
        
        # Use ids to lookup products in database model
        products = Product.objects.filter(id__in=product_ids)
        
        # Return those looked up products
        return products
    
    def get_quants(self):
        quantities = self.cart
        return quantities
    
    
    def update(self, product, quantity):
        # Convertir a tipos adecuados
        product_id = str(product)
        product_qty = int(quantity)

        # Obtener el carrito actual
        ourcart = self.cart

        # Actualizar el diccionario del carrito
        ourcart[product_id] = product_qty

        # Marcar la sesión como modificada
        self.session.modified = True

        # Devolver el carrito actualizado
        return self.cart
    
    
    def delete(self, product):
        # Convertir el ID del producto a string
        product_id = str(product)

        # Eliminar del diccionario del carrito si existe
        if product_id in self.cart:
            del self.cart[product_id]

        # Marcar la sesión como modificada
        self.session.modified = True

