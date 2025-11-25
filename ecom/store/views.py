
from django.shortcuts import render, redirect
from .models import Product, Category, Profile
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
    # Determine if they filled out the form
    if request.method == "POST":
        searched = request.POST['searched']
        
        # Query the Products DB Model
        products = Product.objects.filter(Q(name__icontains=searched)|Q(description__icontains = searched))
        
        # Test for null
        if not products.exists():
            messages.success(request, "That Product Does Not Exist")
            return render(request, 'search.html', {})
        else:
            return render(request, 'search.html', {'searched': searched})
    else:
        return render(request, 'search.html', {})


def update_info(request):
    if request.user.is_authenticated:
        #Get Current User
        current_user = Profile.objects.get(user__id=request.user.id)
        #Get Current shipping User info

        shipping_user = ShippingAddress.objects.get(user__id=request.user.id)
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
    categories = Category.objects.all()
    return render(request, 'category_summary.html', {"categories": categories })


def category(request, foo):
    # Replace Hyphens with Spaces
    foo = foo.replace('-', ' ')
    
    # Grab the category from the URL
    try:
        # Look Up The Category
        category = Category.objects.get(name=foo)
        products = Product.objects.filter(category=category)
        return render(request, 'category.html', {'products': products, 'category': category})
    except Category.DoesNotExist:
        messages.success(request, "That Category Doesn't Exist")
        return redirect('home')



def update_password(request):
    if request.user.is_authenticated:
        current_user = request.user
        # Did they fill out the form
        if request.method == 'POST':
            form = ChangePasswordForm(current_user, request.POST)
            # Is the form valid
            if form.is_valid():
                form.save()
                messages.success(request, "Your Password Has Been Updated!")
                login(request, current_user)
                return redirect('update_user')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)
                return redirect('update_password')
        else:
            form = ChangePasswordForm(current_user)
            return render(request, 'update_password.html', {'form': form})
    else:
        messages.success(request, "You Must Be Logged In To Update Your Password")
        return redirect('home')

def update_user(request):
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



def product(request, pk):
    product = Product.objects.get(id=pk)
    return render(request, 'product.html', {'product': product})

def home(request):
    products = Product.objects.all()
    return render(request, 'home.html', {'products': products})

def about(request):
    return render(request, 'about.html', {})


def login_user(request):
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
    logout(request)
    messages.success(request, "You have been logged out")
    return redirect('home')


def register_user(request):
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
