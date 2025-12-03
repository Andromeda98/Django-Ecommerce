from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save



class Profile(models.Model):
    """
    Perfil extendido del usuario para almacenar información adicional.
    
    Se crea automáticamente cuando un usuario se registra mediante un signal.
    Almacena datos de contacto, dirección y el carrito persistente (old_cart).
    
    Atributos:
        user (OneToOneField): Relación uno-a-uno con el modelo User de Django
        date_modified (DateTimeField): Fecha de última modificación del perfil
        phone (CharField): Número de teléfono del usuario
        address1 (CharField): Dirección principal (calle y número)
        address2 (CharField): Información adicional de dirección (piso, departamento)
        city (CharField): Ciudad de residencia
        state (CharField): Provincia o estado
        zipcode (CharField): Código postal
        country (CharField): País de residencia
        old_cart (CharField): Carrito serializado en JSON para persistencia entre sesiones
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_modified = models.DateTimeField(auto_now=True)
    phone = models.CharField(max_length=20, blank=True)
    address1 = models.CharField(max_length=200, blank=True)
    address2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=200, blank=True)
    state = models.CharField(max_length=200, blank=True)
    zipcode = models.CharField(max_length=200, blank=True)
    country = models.CharField(max_length=200, blank=True)
    old_cart = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        """Retorna el nombre de usuario como representación del perfil."""
        return self.user.username


def create_profile(sender, instance, created, **kwargs):
    """
    Signal que crea automáticamente un perfil cuando se registra un nuevo usuario.
    
    Args:
        sender: El modelo que envía la señal (User)
        instance: La instancia del usuario creada
        created (bool): True si el usuario fue creado (no actualizado)
        **kwargs: Argumentos adicionales de la señal
    """
    if created:
        user_profile = Profile(user=instance)
        user_profile.save()

# Conectar la función create_profile al signal post_save del modelo User
post_save.connect(create_profile, sender=User)


class Category(models.Model):
    """
    Categoría para clasificar libros (Ficción, Filosofía, Historia, etc.).
    
    Permite organizar el catálogo de libros en secciones temáticas,
    facilitando la navegación y búsqueda por parte de los usuarios.
    
    Atributos:
        name (CharField): Nombre de la categoría (máximo 50 caracteres)
    """
    name = models.CharField(max_length=50)

    def __str__(self):
        """Retorna el nombre de la categoría."""
        return self.name
    
    class Meta:
        verbose_name_plural = 'categories'

class Book(models.Model):
    """
    Modelo principal de producto: Libro disponible para la venta.
    
    Representa un libro en el catálogo con toda su información:
    precio, descripción, imagen, categoría y sistema de ofertas.
    
    Atributos:
        name (CharField): Título del libro
        price (DecimalField): Precio regular (máximo 9999.99)
        category (ForeignKey): Categoría a la que pertenece el libro
        description (TextField): Sinopsis y descripción detallada del libro
        image (ImageField): Imagen de portada del libro
        is_sale (BooleanField): Indica si el libro está en oferta
        sale_price (DecimalField): Precio con descuento cuando is_sale=True
    
    Ejemplo:
        >>> book = Book.objects.create(
        ...     name="El Quijote",
        ...     price=19.99,
        ...     category=fiction_category,
        ...     is_sale=True,
        ...     sale_price=14.99
        ... )
    """
    name = models.CharField(max_length=100)
    price = models.DecimalField(default=0, decimal_places=2, max_digits=6)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=1)
    description = models.TextField(default='', blank=True, null=True)
    image = models.ImageField(upload_to='uploads/products/')

    # Sistema de ofertas
    is_sale = models.BooleanField(default=False)
    sale_price = models.DecimalField(default=0, decimal_places=2, max_digits=6)

    def __str__(self):
        """Retorna el nombre del libro."""
        return self.name
