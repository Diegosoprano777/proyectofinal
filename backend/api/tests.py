from decimal import Decimal

from rest_framework.test import APITestCase

from .models import Apartado, ProductoLote, UsuarioPersonalizado
from .security import generar_token


class BaseAPITest(APITestCase):
    def setUp(self):
        self.admin = UsuarioPersonalizado(nombre='Admin', correo='admin@test.co', rol='ADMIN')
        self.admin.set_password('admin123')
        self.admin.save()
        self.cliente = UsuarioPersonalizado(nombre='Cliente', correo='cliente@test.co', rol='CLIENTE')
        self.cliente.set_password('cliente123')
        self.cliente.save()
        self.lote = ProductoLote.objects.create(
            codigo_lote='T-1', variedad='Hass', estado_maduracion='VERDE',
            precio_kg=Decimal('7000'), stock_kg=Decimal('100'), dias_consumo=7,
        )
        ProductoLote.objects.create(
            codigo_lote='T-2', variedad='Papelillo', estado_maduracion='MADURO',
            precio_kg=Decimal('6000'), stock_kg=Decimal('50'), dias_consumo=1,
        )

    def como(self, usuario):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {generar_token(usuario)}')


class UsuariosTests(BaseAPITest):
    def test_login_correcto_devuelve_token(self):
        r = self.client.post('/api/usuarios/login', {'correo': 'admin@test.co', 'password': 'admin123'}, format='json')
        self.assertEqual(r.status_code, 200)
        self.assertIn('token', r.data)
        self.assertNotIn('password', r.data['usuario'])

    def test_login_incorrecto_401(self):
        r = self.client.post('/api/usuarios/login', {'correo': 'admin@test.co', 'password': 'x'}, format='json')
        self.assertEqual(r.status_code, 401)

    def test_registro_no_permite_autoasignarse_admin(self):
        r = self.client.post('/api/usuarios/registro', {
            'nombre': 'Hacker', 'correo': 'h@test.co', 'password': 'secreto1', 'rol': 'ADMIN',
        }, format='json')
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.data['usuario']['rol'], 'CLIENTE')

    def test_registro_correo_duplicado(self):
        r = self.client.post('/api/usuarios/registro', {
            'nombre': 'Otro', 'correo': 'cliente@test.co', 'password': 'secreto1',
        }, format='json')
        self.assertEqual(r.status_code, 400)


class CatalogoTests(BaseAPITest):
    def test_listar_y_filtrar(self):
        self.assertEqual(len(self.client.get('/api/catalogo').data), 2)
        r = self.client.get('/api/catalogo?estado_maduracion=maduro')
        self.assertEqual([l['codigo_lote'] for l in r.data], ['T-2'])
        r = self.client.get('/api/catalogo?variedad=papelillo')
        self.assertEqual([l['codigo_lote'] for l in r.data], ['T-2'])

    def test_crear_lote_requiere_admin(self):
        data = {'codigo_lote': 'N-1', 'variedad': 'Hass', 'estado_maduracion': 'VERDE',
                'precio_kg': '8000', 'stock_kg': '10', 'dias_consumo': 5}
        self.assertEqual(self.client.post('/api/catalogo', data, format='json').status_code, 401)
        self.como(self.cliente)
        self.assertEqual(self.client.post('/api/catalogo', data, format='json').status_code, 403)
        self.como(self.admin)
        self.assertEqual(self.client.post('/api/catalogo', data, format='json').status_code, 201)

    def test_cambiar_maduracion_solo_admin(self):
        self.como(self.cliente)
        r = self.client.patch(f'/api/catalogo/{self.lote.id}', {'estado_maduracion': 'MADURO'}, format='json')
        self.assertEqual(r.status_code, 403)
        self.como(self.admin)
        r = self.client.patch(f'/api/catalogo/{self.lote.id}', {'estado_maduracion': 'MADURO'}, format='json')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['estado_maduracion'], 'MADURO')


class ApartarTests(BaseAPITest):
    def test_apartar_descuenta_stock_y_registra(self):
        self.como(self.cliente)
        r = self.client.post(f'/api/catalogo/{self.lote.id}/apartar', {'cantidad_kg': 10}, format='json')
        self.assertEqual(r.status_code, 200)
        self.lote.refresh_from_db()
        self.assertEqual(self.lote.stock_kg, Decimal('90'))
        apartado = Apartado.objects.get()
        self.assertEqual(apartado.usuario, self.cliente)
        self.assertEqual(apartado.total, Decimal('70000'))

    def test_apartar_sin_sesion_401(self):
        r = self.client.post(f'/api/catalogo/{self.lote.id}/apartar', {'cantidad_kg': 1}, format='json')
        self.assertEqual(r.status_code, 401)

    def test_no_permite_sobreventa(self):
        self.como(self.cliente)
        r = self.client.post(f'/api/catalogo/{self.lote.id}/apartar', {'cantidad_kg': 101}, format='json')
        self.assertEqual(r.status_code, 400)
        self.lote.refresh_from_db()
        self.assertEqual(self.lote.stock_kg, Decimal('100'))

    def test_apartados_cliente_ve_los_suyos_admin_todos(self):
        Apartado.objects.create(usuario=self.cliente, lote=self.lote, cantidad_kg=1, precio_kg=7000, total=7000)
        Apartado.objects.create(usuario=self.admin, lote=self.lote, cantidad_kg=2, precio_kg=7000, total=14000)
        self.como(self.cliente)
        self.assertEqual(len(self.client.get('/api/apartados').data), 1)
        self.como(self.admin)
        self.assertEqual(len(self.client.get('/api/apartados').data), 2)

    def test_token_invalido_401(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer basura')
        self.assertEqual(self.client.get('/api/apartados').status_code, 401)
