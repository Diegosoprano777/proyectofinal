"""Autenticación por token firmado (django.core.signing) y permisos por rol."""
from django.core import signing
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.permissions import BasePermission

from .models import UsuarioPersonalizado

TOKEN_SALT = 'api.usuarios'
TOKEN_MAX_AGE = 60 * 60 * 12  # 12 horas


def generar_token(usuario):
    return signing.dumps({'id': usuario.id, 'rol': usuario.rol}, salt=TOKEN_SALT)


class TokenFirmadoAuthentication(BaseAuthentication):
    """Lee `Authorization: Bearer <token>` y devuelve el UsuarioPersonalizado."""

    keyword = b'bearer'

    def authenticate(self, request):
        partes = get_authorization_header(request).split()
        if not partes or partes[0].lower() != self.keyword:
            return None  # Sin token -> petición anónima
        if len(partes) != 2:
            raise exceptions.AuthenticationFailed('Encabezado Authorization inválido.')

        try:
            data = signing.loads(partes[1].decode(), salt=TOKEN_SALT, max_age=TOKEN_MAX_AGE)
        except signing.SignatureExpired:
            raise exceptions.AuthenticationFailed('La sesión expiró, vuelve a iniciar sesión.')
        except signing.BadSignature:
            raise exceptions.AuthenticationFailed('Token inválido.')

        usuario = UsuarioPersonalizado.objects.filter(pk=data.get('id')).first()
        if usuario is None:
            raise exceptions.AuthenticationFailed('El usuario ya no existe.')
        return usuario, partes[1].decode()

    def authenticate_header(self, request):
        # Hace que DRF responda 401 (no 403) cuando falta el token
        return 'Bearer'


class EstaAutenticado(BasePermission):
    message = 'Debes iniciar sesión.'

    def has_permission(self, request, view):
        return bool(getattr(request.user, 'is_authenticated', False))


class EsAdmin(BasePermission):
    message = 'Solo el administrador puede realizar esta acción.'

    def has_permission(self, request, view):
        return bool(getattr(request.user, 'es_admin', False))
