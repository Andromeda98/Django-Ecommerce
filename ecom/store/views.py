
from django.shortcuts import render, redirect
from .models import Book, Category, Profile
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms

from payment.forms import ShippingForm
from payment.models import ShippingAddress

from .forms import SignUpForm, UpdateUserForm, ChangePasswordForm, UserInfoForm
from django.db.models import Q
from cart.cart import Cart
import json


def search(request):
    """
    Vista de búsqueda de libros.
    
    Permite buscar libros por nombre o descripción usando una consulta de texto.
    Utiliza Q objects de Django para realizar búsquedas case-insensitive en múltiples campos.
    
    Args:
        request (HttpRequest): Objeto de solicitud HTTP.
    
    Returns:
        HttpResponse: Página de resultados de búsqueda con los libros encontrados.
    
    Ejemplos:
        POST /search/ con {'searched': 'python'}
        Retorna libros que contengan 'python' en nombre o descripción.
    """
    # Determine if they filled out the form
    if request.method == "POST":
        searched = request.POST['searched']
        
        # Query the Books DB Model
        products = Book.objects.filter(Q(name__icontains=searched)|Q(description__icontains = searched))
        
        # Test for null
        if not products.exists():
            messages.success(request, "That Product Does Not Exist")
            return render(request, 'search.html', {})
        else:
            return render(request, 'search.html', {'searched': searched, 'products': products})
    else:
        return render(request, 'search.html', {})


def update_info(request):
    """
    Vista para actualizar la información del perfil y dirección de envío del usuario.
    
    Permite a usuarios autenticados modificar su información personal y detalles de envío.
    Utiliza dos formularios simultáneamente: UserInfoForm y ShippingForm.
    
    Args:
        request (HttpRequest): Objeto de solicitud HTTP.
    
    Returns:
        HttpResponse: Formulario de actualización o redirección a home.
    
    Notas:
        - Requiere autenticación del usuario.
        - Utiliza get_or_create para evitar errores si no existe el perfil.
    """
    if request.user.is_authenticated:
        #Get Current User
        current_user, created = Profile.objects.get_or_create(user=request.user)
        #Get Current shipping User info

        shipping_user, created = ShippingAddress.objects.get_or_create(user=request.user)
        form = UserInfoForm(request.POST or None, instance=current_user)
        shipping_form = ShippingForm(request.POST or None, instance=shipping_user)


        if form.is_valid() or shipping_form.is_valid():
            form.save()
            shipping_form.save()
            messages.success(request, "Your Info Has Been Updated")
            return redirect('home')

        return render(request, 'update_info.html', {'form': form, 'shipping_form': shipping_form})
    else:
        messages.success(request, "You Must Be Logged In")
        return redirect('home')


def category_summary(request):
    """
    Vista que muestra un resumen de todas las categorías de libros disponibles.
    
    Args:
        request (HttpRequest): Objeto de solicitud HTTP.
    
    Returns:
        HttpResponse: Página con listado completo de categorías.
    """
    categories = Category.objects.all()
    return render(request, 'category_summary.html', {"categories": categories })


def category(request, category_name):
    """
    Vista que muestra todos los libros de una categoría específica.
    
    Recibe el nombre de la categoría desde la URL, reemplaza guiones por espacios
    y filtra los libros que pertenecen a dicha categoría.
    
    Args:
        request (HttpRequest): Objeto de solicitud HTTP.
        category_name (str): Nombre de la categoría desde la URL.
    
    Returns:
        HttpResponse: Página con libros de la categoría o redirección si no existe.
    
    Ejemplos:
        /category/ciencia-ficcion/ → Muestra libros de "ciencia ficcion"
    """
    # Replace Hyphens with Spaces
    category_name = category_name.replace('-', ' ')
    
    # Grab the category from the URL
    try:
        # Look Up The Category
        category = Category.objects.get(name=category_name)
        products = Book.objects.filter(category=category)
        return render(request, 'category.html', {'products': products, 'category': category})
    except Category.DoesNotExist:
        messages.success(request, "That Category Doesn't Exist")
        return redirect('home')



def update_password(request):
    """
    Vista para cambiar la contraseña del usuario autenticado.
    
    Permite al usuario actualizar su contraseña validando el formulario ChangePasswordForm.
    Después del cambio exitoso, mantiene la sesión del usuario activa.
    
    Args:
        request (HttpRequest): Objeto de solicitud HTTP.
    
    Returns:
        HttpResponse: Formulario de cambio de contraseña o redirección.
    
    Notas:
        - Requiere autenticación.
        - Usa set_password() para hashear correctamente la contraseña.
    """
    if request.user.is_authenticated:
        current_user = request.user
        # Did they fill out the form
        if request.method == 'POST':
            form = ChangePasswordForm(request.POST)
            # Is the form valid
            if form.is_valid():
                current_user.set_password(form.cleaned_data['password1'])
                current_user.save()
                messages.success(request, "Your Password Has Been Updated!")
                login(request, current_user)
                return redirect('update_user')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)
                return redirect('update_password')
        else:
            form = ChangePasswordForm()
            return render(request, 'update_password.html', {'form': form})
    else:
        messages.success(request, "You Must Be Logged In To Update Your Password")
        return redirect('home')

def update_user(request):
    """
    Vista para actualizar los datos básicos del usuario (username, email, etc.).
    
    Args:
        request (HttpRequest): Objeto de solicitud HTTP.
    
    Returns:
        HttpResponse: Formulario de actualización o redirección a home.
    
    Notas:
        - Requiere autenticación.
        - Mantiene la sesión activa después de actualizar mediante login().
    """
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        user_form = UpdateUserForm(request.POST or None, instance=current_user)

        if user_form.is_valid():
            user_form.save()
            login(request, current_user)
            messages.success(request, "User has been updated successfully.")
            return redirect('home')

        return render(request, "update_user.html", {'user_form': user_form})
    else:
        messages.success(request, "You must be logged in to update your profile.")
        return redirect('home')



def product(request, product_id):
    """
    Vista de detalle de un libro específico.
    
    Args:
        request (HttpRequest): Objeto de solicitud HTTP.
        product_id (int): ID del libro a mostrar.
    
    Returns:
        HttpResponse: Página con detalles completos del libro.
    """
    product = Book.objects.get(id=product_id)
    return render(request, 'product.html', {'product': product})

def home(request):
    """
    Vista principal que muestra el catálogo completo de libros.
    
    Args:
        request (HttpRequest): Objeto de solicitud HTTP.
    
    Returns:
        HttpResponse: Página de inicio con todos los libros disponibles.
    """
    products = Book.objects.all()
    return render(request, 'home.html', {'products': products})

def about(request):
    """
    Vista de la página "Acerca de".
    
    Args:
        request (HttpRequest): Objeto de solicitud HTTP.
    
    Returns:
        HttpResponse: Página con información sobre la tienda.
    """
    return render(request, 'about.html', {})


def login_user(request):
    """
    Vista de inicio de sesión de usuario.
    
    Autentica al usuario y restaura su carrito guardado desde la base de datos.
    Convierte el carrito almacenado en formato JSON a un diccionario de Python
    y lo carga en la sesión actual.
    
    Args:
        request (HttpRequest): Objeto de solicitud HTTP.
    
    Returns:
        HttpResponse: Redirección a home o formulario de login.
    
    Notas:
        - Restaura el carrito antiguo del campo old_cart del Profile.
        - Usa json.loads() para deserializar el carrito guardado.
    """
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # Do some shopping cart stuff
            current_user = Profile.objects.get(user_id=request.user.id)

            # Get their saved cart from database
            saved_cart = current_user.old_cart

            # Convert database string to Python dictionary
            if saved_cart:
                converted_cart = json.loads(saved_cart)

                # Get the cart instance
                cart = Cart(request)

                # Loop through the cart and add the items from saved_cart
                for key, value in converted_cart.items():
                    cart.db_add(product=key, quantity=value)

            messages.success(request, "You Have Been Logged In")
            return redirect('home')
        else:
            messages.success(request, "There was an error logging in")
            return redirect('login')
    else:
        return render(request, 'login.html', {})


def logout_user(request):
    """
    Vista de cierre de sesión.
    
    Args:
        request (HttpRequest): Objeto de solicitud HTTP.
    
    Returns:
        HttpResponse: Redirección a la página de inicio.
    """
    logout(request)
    messages.success(request, "You have been logged out")
    return redirect('home')


def register_user(request):
    """
    Vista de registro de nuevos usuarios.
    
    Crea un nuevo usuario usando el formulario SignUpForm y automáticamente
    inicia sesión después del registro exitoso.
    
    Args:
        request (HttpRequest): Objeto de solicitud HTTP.
    
    Returns:
        HttpResponse: Redirección a update_info para completar perfil o formulario de registro.
    
    Notas:
        - Después del registro redirige a update_info para completar datos.
        - La señal create_profile crea automáticamente el Profile asociado.
    """
    form = SignUpForm()
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            # log in user
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, "Tu usuario ha sido creado, por favor rellena la informacion")
            return redirect('update_info')
        else:
            messages.success(request, "Whoops! There was an error")
            return redirect('register')
    else:
        return render(request, 'register.html', {'form': form})
