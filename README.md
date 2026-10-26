# 🥑 AvoLote — Módulo de Usuarios y Catálogo de Aguacates

Catálogo en vivo de lotes de aguacate **Hass** y **Papelillo** por estado de maduración, con apartado de kilos en tiempo real.

| Capa | Tecnología |
|---|---|
| Backend | Django 6 + Django REST Framework + django-cors-headers + SQLite |
| Frontend | Angular 21 (Standalone, Signals, `@if`/`@for`, zoneless) + TailwindCSS v4 |

## Arranque rápido

```powershell
powershell -ExecutionPolicy Bypass -File .\iniciar_demo.ps1
```

El script reinicia la BD demo, levanta Django (`:8000`) y Angular (`:4200`) y abre el navegador.

| Usuario | Correo | Contraseña |
|---|---|---|
| Admin ("Papá") | admin@sena.edu.co | admin123 |
| Cliente | cliente@sena.edu.co | cliente123 |

## Arranque manual

```powershell
cd backend
.\venv\Scripts\python manage.py init_demo        # migraciones + datos demo
.\venv\Scripts\python manage.py runserver 8000

cd frontend
npx ng serve --port 4200
```

## API

| Método | Ruta | Acceso |
|---|---|---|
| POST | `/api/usuarios/login` | Público |
| POST | `/api/usuarios/registro` | Público (siempre crea CLIENTE) |
| GET | `/api/catalogo?estado_maduracion=&variedad=` | Público |
| POST | `/api/catalogo` | ADMIN |
| GET / PATCH | `/api/catalogo/<id>` | GET público · PATCH ADMIN |
| POST | `/api/catalogo/<id>/apartar` `{"cantidad_kg": 5}` | Usuario logueado |
| GET | `/api/apartados` | CLIENTE: los suyos · ADMIN: todos |

Autenticación: `Authorization: Bearer <token>` (token firmado devuelto por login/registro, vigencia 12 h).

## Pruebas

```powershell
cd backend
.\venv\Scripts\python manage.py test api
```
