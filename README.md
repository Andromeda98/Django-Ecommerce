# 📚 Librería Online - Sistema de Comercio Electrónico con Django

Sistema completo de comercio electrónico para venta de libros desarrollado con Django 5.2.8, Bootstrap 5 y SQLite. Proyecto de Trabajo Final de Grado (TFG).

## 🚀 Características Principales

### Para Clientes
- ✅ **Catálogo de Libros**: Navegación intuitiva con categorías y búsqueda avanzada
- ✅ **Sistema de Ofertas**: Precios especiales destacados visualmente
- ✅ **Carrito Inteligente**: Persistencia entre sesiones con tecnología AJAX
- ✅ **Checkout Completo**: Proceso de compra guiado paso a paso
- ✅ **Gestión de Perfil**: Actualización de datos personales y dirección
- ✅ **Responsive Design**: Optimizado para móviles, tablets y desktop

### Para Administradores
- 🔐 **Panel Administrativo**: Gestión completa de productos, categorías y pedidos
- 📦 **Control de Pedidos**: Dashboards separados para pedidos enviados y pendientes
- 👥 **Gestión de Usuarios**: Administración de perfiles y permisos
- 📊 **Reportes**: Visualización de ventas y estadísticas

## 🛠️ Tecnologías Utilizadas

- **Backend**: Django 5.2.8, Python 3.11
- **Frontend**: Bootstrap 5.2.3, Bootstrap Icons, jQuery 3.7.1
- **Base de Datos**: SQLite 3
- **Autenticación**: Django Authentication System
- **Almacenamiento**: Django Media Files

## 📋 Requisitos Previos

- Python 3.11 o superior
- pip (gestor de paquetes de Python)
- Git (opcional, para clonar el repositorio)

## 🔧 Instalación

### 1. Clonar el Repositorio

```bash
git clone https://github.com/Andromeda98/Django-Ecommerce.git
cd Django-Ecommerce
```

### 2. Crear Entorno Virtual

**Windows:**
```bash
python -m venv virt
virt\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv virt
source virt/bin/activate
```

### 3. Instalar Dependencias

```bash
pip install django pillow
```

### 4. Configurar Base de Datos

```bash
cd ecom
python manage.py migrate
```

### 5. Crear Superusuario (Administrador)

```bash
python manage.py createsuperuser
```

Ingresa:
- Username: `admin` (o el que prefieras)
- Email: tu email
- Password: contraseña segura

### 6. Cargar Datos de Prueba (Opcional)

Puedes añadir libros y categorías desde el panel admin o usar la interfaz web.

### 7. Iniciar Servidor de Desarrollo

```bash
python manage.py runserver
```

El sitio estará disponible en: **http://127.0.0.1:8000/**

## 🎯 Acceso al Sistema

### Panel de Administración
- **URL**: http://127.0.0.1:8000/admin/
- **Usuario**: El superusuario creado anteriormente
- Desde aquí puedes:
  - Añadir/editar/eliminar libros
  - Gestionar categorías
  - Ver usuarios registrados
  - Administrar perfiles

### Dashboards de Pedidos (Solo Administradores)
- **Pedidos No Enviados**: http://127.0.0.1:8000/payment/not_shipped_dash
- **Pedidos Enviados**: http://127.0.0.1:8000/payment/shipped_dash

### Sitio Web Principal
- **Inicio**: http://127.0.0.1:8000/
- **Registro**: http://127.0.0.1:8000/register/
- **Login**: http://127.0.0.1:8000/login/
- **Carrito**: http://127.0.0.1:8000/cart/
- **Checkout**: http://127.0.0.1:8000/payment/checkout

## 📁 Estructura del Proyecto

```
Django-Ecommerce/
├── ecom/                      # Directorio principal del proyecto
│   ├── ecom/                  # Configuración de Django
│   │   ├── settings.py        # Configuración global
│   │   ├── urls.py            # URLs principales
│   │   └── wsgi.py            # Servidor WSGI
│   ├── store/                 # App: Catálogo y Usuarios
│   │   ├── models.py          # Book, Category, Profile
│   │   ├── views.py           # Lógica de vistas
│   │   ├── urls.py            # Rutas de /store/
│   │   ├── forms.py           # Formularios
│   │   └── templates/         # HTML del catálogo
│   ├── cart/                  # App: Carrito de Compras
│   │   ├── cart.py            # Clase Cart (lógica)
│   │   ├── views.py           # Operaciones AJAX
│   │   ├── context_processors.py
│   │   └── templates/         # cart_summary.html
│   ├── payment/               # App: Checkout y Pedidos
│   │   ├── models.py          # Order, OrderItem, ShippingAddress
│   │   ├── views.py           # Proceso de pago
│   │   ├── forms.py           # Formularios de envío
│   │   └── templates/payment/ # Checkout, confirmación
│   ├── static/                # CSS, JS, imágenes estáticas
│   ├── media/                 # Imágenes de productos subidas
│   ├── db.sqlite3             # Base de datos SQLite
│   └── manage.py              # Herramienta CLI de Django
├── virt/                      # Entorno virtual (no en Git)
└── README.md                  # Este archivo
```

## 🗄️ Modelos de Base de Datos

### Store App
- **Book**: Productos (libros) con nombre, precio, descripción, imagen, categoría, ofertas
- **Category**: Categorías de libros (Ficción, Filosofía, etc.)
- **Profile**: Perfil extendido del usuario con dirección y carrito persistente

### Payment App
- **Order**: Pedidos con usuario, total, dirección, fecha de envío
- **OrderItem**: Líneas de detalle de cada pedido (libro, cantidad, precio)
- **ShippingAddress**: Dirección de envío específica por pedido

## 🎨 Características Técnicas

### Patrones de Diseño Implementados
- **MVT (Model-View-Template)**: Arquitectura base de Django
- **Signal Pattern**: Creación automática de perfiles y actualización de fechas
- **Facade Pattern**: Clase Cart simplifica operaciones complejas
- **Repository Pattern**: Django ORM abstrae consultas SQL
- **Context Processor**: Carrito disponible globalmente en templates

### Seguridad
- 🔒 Contraseñas cifradas con PBKDF2 (600,000 iteraciones)
- 🔒 Protección CSRF en todos los formularios
- 🔒 Validación de permisos (is_superuser) en vistas administrativas
- 🔒 Prevención de inyección SQL mediante ORM
- 🔒 Validación de entrada en formularios (backend y frontend)

### Optimizaciones
- ⚡ AJAX para operaciones del carrito sin recargar página
- ⚡ `select_related()` y `prefetch_related()` para reducir queries N+1
- ⚡ Carga diferida de imágenes
- ⚡ Responsive design con Bootstrap Grid

## 📱 Funcionalidades Paso a Paso

### Flujo de Compra
1. Usuario navega el catálogo
2. Añade libros al carrito (AJAX)
3. Revisa carrito y modifica cantidades
4. Procede al checkout
5. Ingresa información de envío
6. Confirma pedido
7. Recibe confirmación con número de orden

### Gestión Administrativa
1. Admin accede a dashboards
2. Revisa pedidos no enviados
3. Marca pedidos como enviados
4. Sistema registra fecha de envío automáticamente
5. Pedido se mueve a dashboard de enviados

## 🐛 Solución de Problemas

### El servidor no inicia
```bash
# Verifica que el entorno virtual esté activado
virt\Scripts\activate  # Windows
source virt/bin/activate  # Linux/Mac

# Verifica dependencias
pip list
```

### Error de migraciones
```bash
python manage.py makemigrations
python manage.py migrate
```

### Imágenes no se muestran
Asegúrate de que `settings.py` tenga:
```python
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

### Error "Permission Denied" en admin
Verifica que el usuario tenga `is_superuser=True` en la base de datos.

## 📚 Documentación Adicional

- [Documentación de Django](https://docs.djangoproject.com/)
- [Bootstrap 5 Documentation](https://getbootstrap.com/docs/5.2/)
- [Django ORM Guide](https://docs.djangoproject.com/en/5.2/topics/db/queries/)

## 👨‍💻 Autor

**Rodrigo** - Trabajo Final de Grado (TFG)
- GitHub: [@Andromeda98](https://github.com/Andromeda98)
- Repositorio: [Django-Ecommerce](https://github.com/Andromeda98/Django-Ecommerce)

## 📄 Licencia

Este proyecto fue desarrollado como Trabajo Final de Grado académico.

## 🙏 Agradecimientos

- Framework Django por proporcionar una base sólida
- Bootstrap por el sistema de diseño responsive
- Comunidad de código abierto por las bibliotecas utilizadas

---

**Nota para evaluadores del TFG**: Este README incluye toda la información necesaria para instalar, configurar y ejecutar el proyecto. Para documentación técnica detallada, consultar la memoria del TFG.
