from django.contrib.auth.hashers import check_password, make_password
from django.db import models


class UsuarioPersonalizado(models.Model):
    """Perfil simple de usuario para la demo (independiente de django.contrib.auth.User)."""

    class Rol(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrador'
        CLIENTE = 'CLIENTE', 'Cliente'

    nombre = models.CharField(max_length=120)
    correo = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # Se guarda hasheado (PBKDF2 de Django)
    rol = models.CharField(max_length=10, choices=Rol.choices, default=Rol.CLIENTE)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['id']

    # DRF consulta request.user.is_authenticated en sus permisos
    @property
    def is_authenticated(self):
        return True

    @property
    def es_admin(self):
        return self.rol == self.Rol.ADMIN

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return f'{self.nombre} <{self.correo}> ({self.rol})'


class ProductoLote(models.Model):
    """Lote de aguacate disponible en el catálogo."""

    class EstadoMaduracion(models.TextChoices):
        VERDE = 'VERDE', 'Verde'
        PINTON = 'PINTON', 'Pintón'
        MADURO = 'MADURO', 'Maduro'

    codigo_lote = models.CharField(max_length=30, unique=True)
    variedad = models.CharField(max_length=60, default='Hass')
    estado_maduracion = models.CharField(
        max_length=10, choices=EstadoMaduracion.choices, default=EstadoMaduracion.VERDE
    )
    precio_kg = models.DecimalField(max_digits=10, decimal_places=2)
    stock_kg = models.DecimalField(max_digits=10, decimal_places=2)
    dias_consumo = models.PositiveIntegerField(help_text='Días estimados para consumo óptimo')
    descripcion = models.TextField(blank=True, default='')

    class Meta:
        verbose_name = 'Lote de producto'
        verbose_name_plural = 'Lotes de producto'
        ordering = ['id']

    def __str__(self):
        return f'{self.codigo_lote} - {self.variedad} ({self.estado_maduracion})'


class Apartado(models.Model):
    """Registro de cada apartado (reserva) que descuenta stock de un lote."""

    usuario = models.ForeignKey(UsuarioPersonalizado, on_delete=models.CASCADE, related_name='apartados')
    lote = models.ForeignKey(ProductoLote, on_delete=models.CASCADE, related_name='apartados')
    cantidad_kg = models.DecimalField(max_digits=10, decimal_places=2)
    precio_kg = models.DecimalField(max_digits=10, decimal_places=2, help_text='Precio al momento de apartar')
    total = models.DecimalField(max_digits=12, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Apartado'
        verbose_name_plural = 'Apartados'
        ordering = ['-fecha']

    def __str__(self):
        return f'{self.usuario.correo} apartó {self.cantidad_kg} kg de {self.lote.codigo_lote}'
