from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Apartado, ProductoLote, UsuarioPersonalizado
from .security import EsAdmin, EstaAutenticado, generar_token
from .serializers import (
    ApartadoSerializer,
    ApartarSerializer,
    CambiarEstadoApartadoSerializer,
    LoginSerializer,
    ProductoLoteSerializer,
    UsuarioSerializer,
)


# ---------------------------------------------------------------------------
# Usuarios
# ---------------------------------------------------------------------------
class RegistroView(APIView):
    """POST /api/usuarios/registro  (siempre crea rol CLIENTE)"""

    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UsuarioSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        usuario = serializer.save(rol=UsuarioPersonalizado.Rol.CLIENTE)
        return Response(
            {
                'mensaje': 'Usuario registrado correctamente.',
                'usuario': UsuarioSerializer(usuario).data,
                'token': generar_token(usuario),
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """POST /api/usuarios/login"""

    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        correo = serializer.validated_data['correo'].lower().strip()
        password = serializer.validated_data['password']

        usuario = UsuarioPersonalizado.objects.filter(correo=correo).first()
        if usuario is None or not usuario.check_password(password):
            return Response(
                {'detail': 'Credenciales inválidas.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        return Response(
            {
                'mensaje': f'Bienvenido, {usuario.nombre}.',
                'usuario': UsuarioSerializer(usuario).data,
                'token': generar_token(usuario),
            }
        )


# ---------------------------------------------------------------------------
# Catálogo
# ---------------------------------------------------------------------------
class CatalogoListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/catalogo                       -> lista todos los lotes (público)
    GET  /api/catalogo?estado_maduracion=X   -> filtra por VERDE | PINTON | MADURO
    GET  /api/catalogo?variedad=Papelillo    -> filtra por variedad
    POST /api/catalogo                       -> crea un lote (solo ADMIN)
    """

    serializer_class = ProductoLoteSerializer

    def get_permissions(self):
        return [EsAdmin()] if self.request.method == 'POST' else [AllowAny()]

    def get_queryset(self):
        queryset = ProductoLote.objects.all()
        estado = self.request.query_params.get('estado_maduracion')
        variedad = self.request.query_params.get('variedad')
        if estado:
            queryset = queryset.filter(estado_maduracion=estado.upper().strip())
        if variedad:
            queryset = queryset.filter(variedad__iexact=variedad.strip())
        return queryset


class CatalogoDetailView(generics.RetrieveUpdateAPIView):
    """GET /api/catalogo/<pk> (público)  |  PATCH /api/catalogo/<pk> (solo ADMIN)"""

    queryset = ProductoLote.objects.all()
    serializer_class = ProductoLoteSerializer

    def get_permissions(self):
        return [AllowAny()] if self.request.method == 'GET' else [EsAdmin()]


class ApartarLoteView(APIView):
    """POST /api/catalogo/<pk>/apartar  body: {"cantidad_kg": 5}  (usuario logueado)"""

    permission_classes = [EstaAutenticado]

    def post(self, request, pk):
        serializer = ApartarSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cantidad = serializer.validated_data['cantidad_kg']

        with transaction.atomic():
            # select_for_update evita condiciones de carrera al restar stock
            lote = get_object_or_404(ProductoLote.objects.select_for_update(), pk=pk)

            if cantidad > lote.stock_kg:
                return Response(
                    {
                        'detail': f'Stock insuficiente. Solo hay {lote.stock_kg} kg disponibles.',
                        'stock_disponible_kg': lote.stock_kg,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            lote.stock_kg -= cantidad
            lote.save()

            apartado = Apartado.objects.create(
                usuario=request.user,
                lote=lote,
                cantidad_kg=cantidad,
                precio_kg=lote.precio_kg,
                total=cantidad * lote.precio_kg,
            )

        return Response(
            {
                'mensaje': f'Se apartaron {cantidad} kg del lote {lote.codigo_lote}.',
                'cantidad_apartada_kg': cantidad,
                'total_estimado': apartado.total,
                'lote': ProductoLoteSerializer(lote).data,
                'apartado': ApartadoSerializer(apartado).data,
            }
        )


# ---------------------------------------------------------------------------
# Apartados
# ---------------------------------------------------------------------------
class ApartadosListView(generics.ListAPIView):
    """GET /api/apartados -> CLIENTE ve los suyos, ADMIN ve todos."""

    serializer_class = ApartadoSerializer
    permission_classes = [EstaAutenticado]

    def get_queryset(self):
        queryset = Apartado.objects.select_related('usuario', 'lote')
        if not self.request.user.es_admin:
            queryset = queryset.filter(usuario=self.request.user)
        return queryset


class CambiarEstadoApartadoView(APIView):
    """
    PATCH /api/apartados/<pk>/estado  body: {"estado": "ENTREGADO" | "CANCELADO"}
    - ADMIN: puede entregar o cancelar cualquier apartado PENDIENTE.
    - CLIENTE: solo puede cancelar sus propios apartados PENDIENTES.
    - CANCELADO devuelve los kg al stock del lote.
    """

    permission_classes = [EstaAutenticado]

    def patch(self, request, pk):
        serializer = CambiarEstadoApartadoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        nuevo_estado = serializer.validated_data['estado']
        usuario = request.user

        with transaction.atomic():
            apartado = get_object_or_404(
                Apartado.objects.select_for_update().select_related('usuario', 'lote'), pk=pk
            )

            if not usuario.es_admin:
                if apartado.usuario_id != usuario.id:
                    return Response({'detail': 'No puedes modificar apartados de otro usuario.'},
                                    status=status.HTTP_403_FORBIDDEN)
                if nuevo_estado != Apartado.Estado.CANCELADO:
                    return Response({'detail': 'Solo el administrador puede marcar un apartado como entregado.'},
                                    status=status.HTTP_403_FORBIDDEN)

            if apartado.estado != Apartado.Estado.PENDIENTE:
                return Response(
                    {'detail': f'El apartado ya está {apartado.get_estado_display().lower()} y no se puede modificar.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            lote = ProductoLote.objects.select_for_update().get(pk=apartado.lote_id)
            if nuevo_estado == Apartado.Estado.CANCELADO:
                lote.stock_kg += apartado.cantidad_kg  # Devolver los kilos al inventario
                lote.save()

            apartado.estado = nuevo_estado
            apartado.save()
            apartado.lote = lote

        mensajes = {
            Apartado.Estado.ENTREGADO: f'Apartado de {apartado.cantidad_kg} kg de {lote.codigo_lote} marcado como entregado.',
            Apartado.Estado.CANCELADO: f'Apartado cancelado: se devolvieron {apartado.cantidad_kg} kg al lote {lote.codigo_lote}.',
        }
        return Response({
            'mensaje': mensajes[nuevo_estado],
            'apartado': ApartadoSerializer(apartado).data,
            'lote': ProductoLoteSerializer(lote).data,
        })
