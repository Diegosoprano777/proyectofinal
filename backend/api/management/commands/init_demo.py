from decimal import Decimal

from django.core.management import call_command
from django.core.management.base import BaseCommand


USUARIOS_DEMO = [
    {'nombre': 'Administrador SENA', 'correo': 'admin@sena.edu.co', 'password': 'admin123', 'rol': 'ADMIN'},
    {'nombre': 'Cliente SENA', 'correo': 'cliente@sena.edu.co', 'password': 'cliente123', 'rol': 'CLIENTE'},
]

LOTES_DEMO = [
    {
        'codigo_lote': 'HASS-V-001', 'estado_maduracion': 'VERDE',
        'precio_kg': Decimal('7500'), 'stock_kg': Decimal('500'), 'dias_consumo': 7,
        'descripcion': 'Aguacate Hass recién cosechado, ideal para distribución y almacenamiento.',
    },
    {
        'codigo_lote': 'HASS-V-002', 'estado_maduracion': 'VERDE',
        'precio_kg': Decimal('7200'), 'stock_kg': Decimal('350'), 'dias_consumo': 8,
        'descripcion': 'Lote verde de exportación, calibre grande, finca en Antioquia.',
    },
    {
        'codigo_lote': 'HASS-P-001', 'estado_maduracion': 'PINTON',
        'precio_kg': Decimal('8500'), 'stock_kg': Decimal('280'), 'dias_consumo': 4,
        'descripcion': 'Aguacate Hass pintón, listo para consumo en pocos días.',
    },
    {
        'codigo_lote': 'HASS-P-002', 'estado_maduracion': 'PINTON',
        'precio_kg': Decimal('8300'), 'stock_kg': Decimal('200'), 'dias_consumo': 3,
        'descripcion': 'Lote pintón calibre mediano, ideal para supermercados.',
    },
    {
        'codigo_lote': 'HASS-M-001', 'estado_maduracion': 'MADURO',
        'precio_kg': Decimal('9500'), 'stock_kg': Decimal('150'), 'dias_consumo': 1,
        'descripcion': 'Aguacate Hass maduro, consumo inmediato. Ideal para restaurantes.',
    },
    {
        'codigo_lote': 'HASS-M-002', 'estado_maduracion': 'MADURO',
        'precio_kg': Decimal('9000'), 'stock_kg': Decimal('120'), 'dias_consumo': 2,
        'descripcion': 'Lote maduro para guacamole y procesamiento.',
    },
]

# Aguacate criollo colombiano de cáscara delgada y lisa
LOTES_PAPELILLO = [
    {
        'codigo_lote': 'PAPEL-V-001', 'estado_maduracion': 'VERDE',
        'precio_kg': Decimal('5200'), 'stock_kg': Decimal('400'), 'dias_consumo': 6,
        'descripcion': 'Papelillo criollo de cáscara delgada, fruto grande. Cosecha del Tolima.',
    },
    {
        'codigo_lote': 'PAPEL-P-001', 'estado_maduracion': 'PINTON',
        'precio_kg': Decimal('5800'), 'stock_kg': Decimal('260'), 'dias_consumo': 3,
        'descripcion': 'Papelillo pintón, pulpa cremosa y suave. Ideal para tiendas de barrio.',
    },
    {
        'codigo_lote': 'PAPEL-M-001', 'estado_maduracion': 'MADURO',
        'precio_kg': Decimal('6200'), 'stock_kg': Decimal('180'), 'dias_consumo': 1,
        'descripcion': 'Papelillo maduro listo para el almuerzo: sabor tradicional colombiano.',
    },
]


class Command(BaseCommand):
    help = (
        'Ejecuta makemigrations + migrate y deja la BD en estado demo: 2 usuarios, '
        '6 lotes Hass y 3 Papelillo con stock inicial, sin apartados.'
    )

    def handle(self, *args, **options):
        from api.models import Apartado, ProductoLote, UsuarioPersonalizado

        self.stdout.write(self.style.MIGRATE_HEADING('1) makemigrations'))
        call_command('makemigrations', 'api', interactive=False)

        self.stdout.write(self.style.MIGRATE_HEADING('2) migrate'))
        call_command('migrate', interactive=False)

        self.stdout.write(self.style.MIGRATE_HEADING('3) Usuarios demo'))
        for data in USUARIOS_DEMO:
            usuario, creado = UsuarioPersonalizado.objects.get_or_create(
                correo=data['correo'],
                defaults={'nombre': data['nombre'], 'rol': data['rol']},
            )
            usuario.nombre = data['nombre']
            usuario.rol = data['rol']
            usuario.set_password(data['password'])
            usuario.save()
            accion = 'creado' if creado else 'actualizado'
            self.stdout.write(f"   - {usuario.correo} / {data['password']} ({usuario.rol}) {accion}")

        self.stdout.write(self.style.MIGRATE_HEADING('4) Lotes de aguacate (Hass + Papelillo)'))
        Apartado.objects.all().delete()
        lotes = [(d, 'Hass') for d in LOTES_DEMO] + [(d, 'Papelillo') for d in LOTES_PAPELILLO]
        codigos = [d['codigo_lote'] for d, _ in lotes]
        borrados, _ = ProductoLote.objects.exclude(codigo_lote__in=codigos).delete()
        if borrados:
            self.stdout.write(f'   - {borrados} registro(s) de prueba eliminados')
        for data, variedad in lotes:
            lote, creado = ProductoLote.objects.update_or_create(
                codigo_lote=data['codigo_lote'],
                defaults={**data, 'variedad': variedad},
            )
            accion = 'creado' if creado else 'reiniciado'
            self.stdout.write(f'   - {lote} {accion}')

        self.stdout.write(self.style.SUCCESS('\nBase de datos demo lista. Ejecuta: python manage.py runserver 8000'))
