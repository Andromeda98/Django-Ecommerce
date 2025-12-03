
from django.db import models
from django.contrib.auth.models import User
from store.models import Book
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
import datetime


class ShippingAddress(models.Model):
    """
    Dirección de envío específica para cada pedido.
    
    Almacena la dirección de entrega asociada a un pedido concreto,
    separada del perfil del usuario para permitir envíos a direcciones
    alternativas (regalo, oficina, etc.).
    
    Atributos:
        user (ForeignKey): Usuario asociado (opcional para compras como invitado)
        shipping_full_name (CharField): Nombre completo del destinatario
        shipping_email (CharField): Email de contacto para el envío
        shipping_address1 (CharField): Dirección principal de envío
        shipping_address2 (CharField): Información complementaria (opcional)
        shipping_city (CharField): Ciudad de destino
        shipping_state (CharField): Provincia o estado (opcional)
        shipping_zipcode (CharField): Código postal (opcional)
        shipping_country (CharField): País de destino
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    shipping_full_name = models.CharField(max_length=255)
    shipping_email = models.CharField(max_length=255)
    shipping_address1 = models.CharField(max_length=255)
    shipping_address2 = models.CharField(max_length=255, null=True, blank=True)
    shipping_city = models.CharField(max_length=255)
    shipping_state = models.CharField(max_length=255, null=True, blank=True)
    shipping_zipcode = models.CharField(max_length=255, null=True, blank=True)
    shipping_country = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = "Shipping Address"

    def __str__(self):
        """Retorna identificador de la dirección de envío."""
        return f"Shipping Address - {str(self.id)}"
    


def create_shipping(sender, instance, created, **kwargs):
    """
    Signal que crea automáticamente una dirección de envío al registrar un usuario.
    
    Args:
        sender: El modelo que envía la señal (User)
        instance: La instancia del usuario creada
        created (bool): True si el usuario fue creado (no actualizado)
        **kwargs: Argumentos adicionales de la señal
    """
    if created:
        user_shipping = ShippingAddress(user=instance)
        user_shipping.save()

# Conectar la función al signal post_save del modelo User
post_save.connect(create_shipping, sender=User)



class Order(models.Model):
    """
    Pedido realizado por un cliente.
    
    Representa un pedido completo con información del comprador,
    dirección de envío, total pagado y estado de envío.
    Los detalles de productos se almacenan en OrderItem.
    
    Atributos:
        user (ForeignKey): Usuario que realizó el pedido (NULL para invitados)
        full_name (CharField): Nombre completo del comprador
        email (EmailField): Email de contacto
        shipping_address (TextField): Dirección de envío completa (texto plano)
        amount_paid (DecimalField): Monto total pagado
        date_ordered (DateTimeField): Fecha y hora del pedido (automático)
        shipped (BooleanField): Indica si el pedido ha sido enviado
        date_shipped (DateTimeField): Fecha de envío (se asigna automáticamente)
    
    Nota:
        El campo date_shipped se actualiza automáticamente mediante un
        signal pre_save cuando shipped cambia de False a True.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    full_name = models.CharField(max_length=250)
    email = models.EmailField(max_length=250)
    shipping_address = models.TextField(max_length=15000)
    amount_paid = models.DecimalField(max_digits=7, decimal_places=2)
    date_ordered = models.DateTimeField(auto_now_add=True)
    shipped = models.BooleanField(default=False)
    date_shipped = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        """Retorna identificador del pedido."""
        return f'Order - {str(self.id)}'
    


@receiver(pre_save, sender=Order)
def set_shipped_date_on_update(sender, instance, **kwargs):
    """
    Signal que asigna automáticamente la fecha de envío.
    
    Cuando el estado 'shipped' cambia de False a True, este signal
    actualiza automáticamente el campo 'date_shipped' con la fecha
    y hora actual, eliminando la necesidad de hacerlo manualmente.
    
    Args:
        sender: El modelo que envía la señal (Order)
        instance: La instancia del pedido que se está guardando
        **kwargs: Argumentos adicionales de la señal
    """
    if instance.pk:
        now = datetime.datetime.now()
        obj = sender._default_manager.get(pk=instance.pk)
        # Solo actualizar si el estado cambió de no enviado a enviado
        if instance.shipped and not obj.shipped:
            instance.date_shipped = now

    
class OrderItem(models.Model):
    """
    Línea de detalle de un pedido (un producto dentro de un Order).
    
    Representa cada libro individual comprado en un pedido,
    almacenando cantidad, precio al momento de la compra y relaciones
    con el pedido, producto y usuario.
    
    Atributos:
        order (ForeignKey): Pedido al que pertenece este ítem
        product (ForeignKey): Libro comprado
        user (ForeignKey): Usuario que compró (opcional para invitados)
        quantity (PositiveBigIntegerField): Cantidad de unidades compradas
        price (DecimalField): Precio unitario al momento de la compra
    
    Nota:
        El precio se guarda para mantener histórico, incluso si el precio
        del libro cambia posteriormente en el catálogo.
    
    Ejemplo:
        >>> order_item = OrderItem.objects.create(
        ...     order=order,
        ...     product=book,
        ...     quantity=2,
        ...     price=book.sale_price if book.is_sale else book.price
        ... )
    """
    # Claves foráneas
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Book, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    quantity = models.PositiveBigIntegerField(default=1)
    price = models.DecimalField(max_digits=7, decimal_places=2)

    def __str__(self):
        """Retorna identificador del ítem de pedido."""
        return f'Order Item - {str(self.id)}'

