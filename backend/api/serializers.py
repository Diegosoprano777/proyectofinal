from decimal import Decimal

from rest_framework import serializers

from .models import Apartado, ProductoLote, UsuarioPersonalizado


class UsuarioSerializer(serializers.ModelSerializer):
    """Serializer de lectura/registro. El password nunca se devuelve en la respuesta."""

    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = UsuarioPersonalizado
        fields = ['id', 'nombre', 'correo', 'password', 'rol', 'fecha_registro']
        # 'rol' es solo lectura: nadie puede auto-asignarse ADMIN desde el registro
        read_only_fields = ['id', 'rol', 'fecha_registro']

    def validate_correo(self, value):
        value = value.lower().strip()
        if UsuarioPersonalizado.objects.filter(correo=value).exists():
            raise serializers.ValidationError('Ya existe un usuario con este correo.')
        return value

    def create(self, validated_data):
        raw_password = validated_data.pop('password')
        usuario = UsuarioPersonalizado(**validated_data)
        usuario.set_password(raw_password)
        usuario.save()
        return usuario


class LoginSerializer(serializers.Serializer):
    correo = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class ProductoLoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductoLote
        fields = [
            'id', 'codigo_lote', 'variedad', 'estado_maduracion',
            'precio_kg', 'stock_kg', 'dias_consumo', 'descripcion',
        ]
        read_only_fields = ['id']

    def validate_precio_kg(self, value):
        if value <= 0:
            raise serializers.ValidationError('El precio por kg debe ser mayor a 0.')
        return value

    def validate_stock_kg(self, value):
        if value < 0:
            raise serializers.ValidationError('El stock no puede ser negativo.')
        return value


class ApartarSerializer(serializers.Serializer):
    cantidad_kg = serializers.DecimalField(
        max_digits=10, decimal_places=2, min_value=Decimal('0.01')
    )


class ApartadoSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.CharField(source='usuario.nombre', read_only=True)
    usuario_correo = serializers.CharField(source='usuario.correo', read_only=True)
    codigo_lote = serializers.CharField(source='lote.codigo_lote', read_only=True)
    variedad = serializers.CharField(source='lote.variedad', read_only=True)
    estado_maduracion = serializers.CharField(source='lote.estado_maduracion', read_only=True)

    class Meta:
        model = Apartado
        fields = [
            'id', 'lote', 'codigo_lote', 'variedad', 'estado_maduracion',
            'usuario', 'usuario_nombre', 'usuario_correo',
            'cantidad_kg', 'precio_kg', 'total', 'estado', 'fecha', 'fecha_actualizacion',
        ]
        read_only_fields = fields


class CambiarEstadoApartadoSerializer(serializers.Serializer):
    estado = serializers.ChoiceField(choices=[Apartado.Estado.ENTREGADO, Apartado.Estado.CANCELADO])
