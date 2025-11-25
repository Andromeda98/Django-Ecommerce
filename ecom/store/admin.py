
from django.contrib import admin
from django.contrib.auth.models import User
from .models import Category, Customer, Product, Order, Profile

# Registrar modelos en el admin
admin.site.register(Category)
admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(Profile)

# Mezclar la información del perfil con la del usuario
class ProfileInline(admin.StackedInline):
    model = Profile


# Extender el modelo User en el admin
class UserAdmin(admin.ModelAdmin):
    model = User
    fields = ["username", "first_name", "last_name", "email"]
    inlines = [ProfileInline]

# Desregistrar el User original
admin.site.unregister(User)

# Registrar el nuevo UserAdmin
admin.site.register(User, UserAdmin)

