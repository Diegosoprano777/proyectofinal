from django.contrib import admin

from .models import Apartado, ProductoLote, UsuarioPersonalizado


@admin.register(UsuarioPersonalizado)
class UsuarioPersonalizadoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'correo', 'rol', 'fecha_registro')
    list_filter = ('rol',)
    search_fields = ('nombre', 'correo')


@admin.register(ProductoLote)
class ProductoLoteAdmin(admin.ModelAdmin):
    list_display = ('codigo_lote', 'variedad', 'estado_maduracion', 'precio_kg', 'stock_kg', 'dias_consumo')
    list_filter = ('estado_maduracion', 'variedad')
    search_fields = ('codigo_lote',)


@admin.register(Apartado)
class ApartadoAdmin(admin.ModelAdmin):
    list_display = ('id', 'fecha', 'usuario', 'lote', 'cantidad_kg', 'precio_kg', 'total')
    list_filter = ('lote__variedad', 'lote__estado_maduracion')
    search_fields = ('usuario__correo', 'lote__codigo_lote')
