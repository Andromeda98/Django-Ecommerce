from django.shortcuts import get_object_or_404
from store.models import Product, Profile


class Cart():
    def __init__(self, request):
        self.session = request.session

        self.request = request

        # Get the current session key if it exists
        cart = self.session.get('session_key')

        # If the user is new, no session key! Create one
        if 'session_key' not in request.session:
            cart = self.session['session_key'] = {}

        # Make sure cart is available on all pages of site
        self.cart = cart


        
    def db_add(self, product, quantity):
        product_id = str(product)
        product_qty = str(quantity)

        # Lógica para añadir al carrito
        if product_id in self.cart:
            pass
        else:
            # Guardar cantidad en el carrito
            self.cart[product_id] = int(product_qty)

        # Marcar la sesión como modificada
        self.session.modified = True

        # Si el usuario está autenticado, guardar el carrito en su perfil
        if self.request.user.is_authenticated:
            # Obtener el perfil del usuario actual
            current_user = Profile.objects.filter(user_id=self.request.user.id)

            # Convertir el carrito a string y reemplazar comillas simples por dobles
            carty = str(self.cart)  # Ejemplo: {'3': 1, '2': 4}
            carty = carty.replace("'", '"')  # Convertir a {"3": 1, "2": 4}

            # Guardar el carrito en el campo old_cart del perfil
            current_user.update(old_cart=str(carty))

    
    def add(self, product, quantity):
        product_id = str(product.id)
        product_qty = str(quantity)

        # Lógica para añadir al carrito
        if product_id in self.cart:
            pass
        else:
            # Guardar cantidad en el carrito
            self.cart[product_id] = int(product_qty)

        # Marcar la sesión como modificada
        self.session.modified = True

        # Si el usuario está autenticado, actualizar su perfil
        
        # Deal with logged in user
        if self.request.user.is_authenticated:
            # Get the current user profile
            current_user = Profile.objects.filter(user_id=self.request.user.id)

            # Convert cart dictionary to string
            carty = str(self.cart)  # Example: {'3': 1, '2': 4}
            carty = carty.replace("'", '"')  # Convert to {"3": 1, "2": 4}

            # Save carty to the Profile model
            current_user.update(old_cart=str(carty))



    
    
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


        if self.request.user.is_authenticated:
            # Obtener el perfil del usuario actual
            current_user = Profile.objects.filter(user_id=self.request.user.id)

            # Convertir el carrito a string y reemplazar comillas simples por dobles
            carty = str(self.cart)  # Ejemplo: {'3': 1, '2': 4}
            carty = carty.replace("'", '"')  # Convertir a {"3": 1, "2": 4}

            # Guardar el carrito en el campo old_cart del perfil
            current_user.update(old_cart=str(carty))


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

        if self.request.user.is_authenticated:
            # Obtener el perfil del usuario actual
            current_user = Profile.objects.filter(user_id=self.request.user.id)

            # Convertir el carrito a string y reemplazar comillas simples por dobles
            carty = str(self.cart)  # Ejemplo: {'3': 1, '2': 4}
            carty = carty.replace("'", '"')  # Convertir a {"3": 1, "2": 4}

            # Guardar el carrito en el campo old_cart del perfil
            current_user.update(old_cart=str(carty))


