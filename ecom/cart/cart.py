from django.shortcuts import get_object_or_404
from store.models import Book, Profile


class Cart():
    """
    Clase que gestiona la lógica del carrito de compras.
    
    Implementa el patrón Facade para simplificar las operaciones complejas
    del carrito, manejando tanto la sesión temporal como la persistencia
    en base de datos para usuarios autenticados.
    
    Atributos:
        session: Objeto de sesión de Django
        request: Objeto HttpRequest actual
        cart (dict): Diccionario con productos {product_id: quantity}
    """
    
    def __init__(self, request):
        """
        Inicializa el carrito desde la sesión o crea uno nuevo.
        
        Args:
            request: Objeto HttpRequest con información de sesión y usuario
        """
        self.session = request.session
        self.request = request

        # Obtener el carrito de la sesión si existe
        cart = self.session.get('session_key')

        # Si el usuario es nuevo, crear un carrito vacío
        if 'session_key' not in request.session:
            cart = self.session['session_key'] = {}

        # Asegurar que el carrito esté disponible en toda la aplicación
        self.cart = cart


        
    def db_add(self, product, quantity):
        """
        Añade productos desde la base de datos (usado al cargar old_cart).
        
        Similar a add() pero acepta el product_id directamente como string.
        Utilizado principalmente al restaurar el carrito desde old_cart al hacer login.
        
        Args:
            product (str o int): ID del producto
            quantity (str o int): Cantidad de unidades
        """
        product_id = str(product)
        product_qty = str(quantity)

        # Lógica para añadir al carrito desde base de datos
        if product_id in self.cart:
            pass
        else:
            self.cart[product_id] = int(product_qty)

        # Marcar la sesión como modificada
        self.session.modified = True

        # Persistir en base de datos si está autenticado
        if self.request.user.is_authenticated:
            current_user = Profile.objects.filter(user_id=self.request.user.id)
            cart_string = str(self.cart)
            cart_string = cart_string.replace("'", '"')
            current_user.update(old_cart=str(cart_string))

    
    def add(self, product, quantity):
        """
        Añade un producto al carrito con la cantidad especificada.
        
        Si el producto ya existe en el carrito, no modifica la cantidad.
        Para usuarios autenticados, persiste el carrito en la base de datos.
        
        Args:
            product (Book): Instancia del libro a añadir
            quantity (int): Cantidad de unidades a añadir
        
        Ejemplo:
            >>> cart = Cart(request)
            >>> book = Book.objects.get(id=5)
            >>> cart.add(book, 2)
        """
        product_id = str(product.id)
        product_qty = str(quantity)

        # Lógica para añadir al carrito (no suma si ya existe)
        if product_id in self.cart:
            pass
        else:
            # Guardar cantidad en el carrito
            self.cart[product_id] = int(product_qty)

        # Marcar la sesión como modificada para que Django la guarde
        self.session.modified = True

        # Si el usuario está autenticado, guardar en base de datos
        if self.request.user.is_authenticated:
            # Obtener el perfil del usuario actual
            current_user = Profile.objects.filter(user_id=self.request.user.id)

            # Convertir el diccionario del carrito a string JSON
            cart_string = str(self.cart)
            cart_string = cart_string.replace("'", '"')

            # Guardar en el campo old_cart del perfil
            current_user.update(old_cart=str(cart_string))



    
    
    def cart_total(self):
        """
        Calcula el precio total del carrito considerando ofertas.
        
        Itera sobre todos los productos del carrito, aplicando el precio
        de oferta (sale_price) cuando corresponda o el precio regular.
        
        Returns:
            Decimal: Total a pagar por todos los productos del carrito
        
        Ejemplo:
            >>> cart = Cart(request)
            >>> total = cart.cart_total()
            >>> print(f"Total: €{total}")
            Total: €45.97
        """
        # Obtener los IDs de los productos en el carrito
        product_ids = self.cart.keys()

        # Buscar esos productos en la base de datos
        products = Book.objects.filter(id__in=product_ids)

        # Obtener las cantidades del carrito
        quantities = self.cart

        # Inicializar el total
        total = 0

        # Calcular el total considerando ofertas
        for key, value in quantities.items():
            key = int(key)  # Convertir la clave a entero
            for product in products:
                if product.id == key:
                    # Aplicar precio de oferta si está activa
                    if product.is_sale:
                        total += product.sale_price * value
                    else:
                        total += product.price * value

        return total



    def __len__(self):
        """
        Retorna el número total de productos en el carrito.
        
        Returns:
            int: Cantidad de productos diferentes (no la suma de unidades)
        """
        return len(self.cart)
    
    def get_prods(self):
        """
        Obtiene los objetos Book completos de los productos en el carrito.
        
        Consulta la base de datos para recuperar la información completa
        (nombre, precio, imagen, etc.) de cada libro del carrito.
        
        Returns:
            QuerySet: Conjunto de objetos Book presentes en el carrito
        """
        # Obtener IDs de productos del carrito
        product_ids = self.cart.keys()
        
        # Buscar productos en la base de datos
        products = Book.objects.filter(id__in=product_ids)
        
        return products
    
    def get_quants(self):
        """
        Retorna el diccionario con las cantidades de cada producto.
        
        Returns:
            dict: Diccionario {product_id: quantity}
        """
        quantities = self.cart
        return quantities
    
    
    def update(self, product, quantity):
        """
        Actualiza la cantidad de un producto específico en el carrito.
        
        Modifica la cantidad de unidades de un producto existente.
        Para usuarios autenticados, sincroniza con la base de datos.
        
        Args:
            product (int o str): ID del producto a actualizar
            quantity (int): Nueva cantidad de unidades
        
        Returns:
            dict: Carrito actualizado
        
        Ejemplo:
            >>> cart.update(product=5, quantity=3)
        """
        # Convertir a tipos adecuados
        product_id = str(product)
        product_qty = int(quantity)

        # Obtener el carrito actual
        updated_cart = self.cart

        # Actualizar la cantidad del producto
        updated_cart[product_id] = product_qty

        # Marcar la sesión como modificada
        self.session.modified = True

        # Persistir en base de datos si el usuario está autenticado
        if self.request.user.is_authenticated:
            current_user = Profile.objects.filter(user_id=self.request.user.id)
            cart_string = str(self.cart)
            cart_string = cart_string.replace("'", '"')
            current_user.update(old_cart=str(cart_string))

        return self.cart
    
    
    def delete(self, product):
        """
        Elimina completamente un producto del carrito.
        
        Remueve el producto y todas sus unidades del carrito.
        Actualiza la persistencia en base de datos para usuarios autenticados.
        
        Args:
            product (int o str): ID del producto a eliminar
        
        Ejemplo:
            >>> cart.delete(product=5)
            # Elimina el producto con ID 5 del carrito
        """
        # Convertir el ID del producto a string
        product_id = str(product)

        # Eliminar del diccionario del carrito si existe
        if product_id in self.cart:
            del self.cart[product_id]

        # Marcar la sesión como modificada
        self.session.modified = True

        # Actualizar base de datos para usuarios autenticados
        if self.request.user.is_authenticated:
            current_user = Profile.objects.filter(user_id=self.request.user.id)
            cart_string = str(self.cart)
            cart_string = cart_string.replace("'", '"')
            current_user.update(old_cart=str(cart_string))


