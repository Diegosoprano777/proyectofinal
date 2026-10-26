import sys
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)

def build_pdf(filename="AvoLote_Guia_Presentacion_Docente.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        rightMargin=40, leftMargin=40,
        topMargin=40, bottomMargin=40
    )

    styles = getSampleStyleSheet()

    # Colores corporativos AvoLote
    c_primary = colors.HexColor("#064e3b")     # Emerald 900
    c_secondary = colors.HexColor("#047857")   # Emerald 700
    c_accent = colors.HexColor("#65a30d")      # Lime 600
    c_dark = colors.HexColor("#1c1917")        # Stone 900
    c_light = colors.HexColor("#f5f5f4")       # Stone 100
    c_border = colors.HexColor("#e7e5e4")

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=c_primary,
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=c_secondary,
        spaceAfter=15
    )

    h1_style = ParagraphStyle(
        'Header1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=c_primary,
        spaceBefore=14,
        spaceAfter=6
    )

    h2_style = ParagraphStyle(
        'Header2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=c_secondary,
        spaceBefore=8,
        spaceAfter=4
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=c_dark,
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'BulletText',
        parent=body_style,
        leftIndent=14,
        firstLineIndent=-10,
        spaceAfter=4
    )

    quote_style = ParagraphStyle(
        'QuoteStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#065f46"),
        leftIndent=15,
        rightIndent=15,
        spaceBefore=4,
        spaceAfter=6
    )

    story = []

    # PORTADA / ENCABEZADO
    story.append(Paragraph("AvoLote &mdash; Gu&iacute;a de Sustentaci&oacute;n y Defensa T&eacute;cnica", title_style))
    story.append(Paragraph("M&oacute;dulo de Usuarios, Cat&aacute;logo de Aguacates (Hass y Papelillo) y Reservas en Tiempo Real &bull; SENA 2026", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=c_primary, spaceBefore=0, spaceAfter=12))

    # FICHA RESUMEN DEL PROYECTO
    summary_data = [
        [Paragraph("<b>Proyecto:</b>", body_style), Paragraph("AvoLote (Cat&aacute;logo y Gesti&oacute;n de Aguacate Hass y Papelillo)", body_style)],
        [Paragraph("<b>Backend:</b>", body_style), Paragraph("Django 6 + Django REST Framework + django-cors-headers + SQLite", body_style)],
        [Paragraph("<b>Frontend:</b>", body_style), Paragraph("Angular 21 (Signals, Standalone Components, Control Flow @if/@for) + TailwindCSS v4", body_style)],
        [Paragraph("<b>Repositorio GitHub:</b>", body_style), Paragraph("https://github.com/Diegosoprano777/proyectofinal", body_style)],
        [Paragraph("<b>Backend en Render:</b>", body_style), Paragraph("https://proyectofinal-pctw.onrender.com/api/", body_style)],
        [Paragraph("<b>Usuarios Demo:</b>", body_style), Paragraph("Admin: admin@sena.edu.co (admin123) &bull; Cliente: cliente@sena.edu.co (cliente123)", body_style)],
    ]
    t_summary = Table(summary_data, colWidths=[110, 420])
    t_summary.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f0fdf4")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#86efac")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#bbf7d0")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_summary)
    story.append(Spacer(1, 12))

    # SECCION 1: OBJETIVOS Y ALCANCE
    story.append(Paragraph("1. Alcance y Objetivos de la Entrega", h1_style))
    story.append(Paragraph(
        "El proyecto resuelve la necesidad de los productores y comercializadores agr&iacute;colas de presentar su oferta de aguacates "
        "clasificados por variedad y estado de maduraci&oacute;n, permitiendo a clientes minoristas o mayoristas apartar stock en tiempo real "
        "con sincronizaci&oacute;n garantizada mediante transacciones at&oacute;micas en el servidor.",
        body_style
    ))
    story.append(Paragraph("&bull; <b>Cat&aacute;logo Din&aacute;mico:</b> Clasificaci&oacute;n por variedad (Hass y Papelillo criollo) y estado de maduraci&oacute;n (Verde, Pint&oacute;n, Maduro) con fotograf&iacute;as asociadas.", bullet_style))
    story.append(Paragraph("&bull; <b>Seguridad y Roles:</b> Autenticaci&oacute;n v&iacute;a token firmado con perfiles diferenciados (ADMIN y CLIENTE). El registro p&uacute;blico s&oacute;lo permite rol CLIENTE.", bullet_style))
    story.append(Paragraph("&bull; <b>Control de Inventario Transaccional:</b> Resta inmediata de stock al apartar, impidiendo sobreventas mediante bloqueo con <i>select_for_update()</i>.", bullet_style))
    story.append(Paragraph("&bull; <b>Ciclo de Vida de Apartados:</b> Estados PENDIENTE, ENTREGADO y CANCELADO, con devoluci&oacute;n autom&aacute;tica de kilogramos al lote al cancelar.", bullet_style))

    # SECCION 2: ARQUITECTURA TECNICA
    story.append(Paragraph("2. Arquitectura de Software y Tecnolog&iacute;as", h1_style))
    story.append(Paragraph(
        "Se adopt&oacute; un modelo desacoplado (Decoupled Single Page Application) que separa completamente la l&oacute;gica de negocio "
        "en una API REST robusta y un cliente web reactivo de &uacute;ltima generaci&oacute;n:",
        body_style
    ))

    arch_data = [
        [Paragraph("<b>Capa</b>", body_style), Paragraph("<b>Tecnolog&iacute;a &amp; Componentes</b>", body_style), Paragraph("<b>Responsabilidad</b>", body_style)],
        [
            Paragraph("<b>Frontend</b>", body_style),
            Paragraph("Angular 21 + TailwindCSS v4<br/>&bull; Angular Signals (reactividad fina)<br/>&bull; Control flow @if / @for<br/>&bull; HttpInterceptor funcional", body_style),
            Paragraph("Experiencia de usuario moderna, filtros instant&aacute;neos sin recargas, gesti&oacute;n de sesi&oacute;n en localStorage e inyecci&oacute;n autom&aacute;tica de tokens Bearer.", body_style)
        ],
        [
            Paragraph("<b>Backend API</b>", body_style),
            Paragraph("Django 6 + DRF<br/>&bull; ModelSerializers con validaciones<br/>&bull; TokenFirmadoAuthentication<br/>&bull; Gunicorn + Whitenoise", body_style),
            Paragraph("Endpoints REST seguros, hashing de contrase&ntilde;as con PBKDF2, reglas de autorizaci&oacute;n por rol y ejecuci&oacute;n de transacciones ACID en base de datos.", body_style)
        ],
        [
            Paragraph("<b>Persistencia</b>", body_style),
            Paragraph("SQLite con WAL Mode<br/>&bull; UsuarioPersonalizado<br/>&bull; ProductoLote<br/>&bull; Apartado (con FK e integridad)", body_style),
            Paragraph("Almacenamiento relacional de usuarios, lotes con stock en kilogramos y registro hist&oacute;rico auditable de cada apartado.", body_style)
        ],
    ]
    t_arch = Table(arch_data, colWidths=[70, 220, 240])
    t_arch.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#064e3b")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_arch)
    story.append(Spacer(1, 10))

    story.append(PageBreak())

    # SECCION 3: MODELO DE DATOS Y REGLAS DE NEGOCIO
    story.append(Paragraph("3. Modelo Relacional y Reglas de Negocio", h1_style))
    story.append(Paragraph(
        "El modelo relacional se dise&ntilde;&oacute; siguiendo estrictamente los principios de normalizaci&oacute;n e integridad referencial:",
        body_style
    ))

    story.append(Paragraph("<b>Entidades Principales:</b>", h2_style))
    story.append(Paragraph("&bull; <b>UsuarioPersonalizado:</b> Contiene <i>nombre, correo (UK), password (hasheado)</i> y <i>rol ('ADMIN' | 'CLIENTE')</i>.", bullet_style))
    story.append(Paragraph("&bull; <b>ProductoLote:</b> Contiene <i>codigo_lote (UK), variedad ('Hass' | 'Papelillo'), estado_maduracion ('VERDE' | 'PINTON' | 'MADURO'), precio_kg, stock_kg, dias_consumo</i> y <i>descripcion</i>.", bullet_style))
    story.append(Paragraph("&bull; <b>Apartado:</b> Tabla intermedia relacional con claves for&aacute;neas a Usuario y Lote, guardando <i>cantidad_kg, precio_kg hist&oacute;rico, total en COP, estado ('PENDIENTE' | 'ENTREGADO' | 'CANCELADO')</i> y marcas de tiempo.", bullet_style))

    story.append(Paragraph("<b>Reglas Cr&iacute;ticas Implementadas en el Backend:</b>", h2_style))
    story.append(Paragraph("1. <b>Prevenci&oacute;n de Elevaci&oacute;n de Privilegios:</b> El serializador de registro marca el campo <i>rol</i> como solo lectura, asignando forzosamente <i>CLIENTE</i> a cualquier registro p&uacute;blico.", bullet_style))
    story.append(Paragraph("2. <b>Prevenci&oacute;n de Concurrencia y Sobreventa:</b> En <i>POST /api/catalogo/&lt;pk&gt;/apartar</i> se usa <i>select_for_update()</i> dentro de un bloque <i>transaction.atomic()</i>. Si la cantidad solicitada supera el stock, se rechaza con error 400 antes de mutar el registro.", bullet_style))
    story.append(Paragraph("3. <b>Devoluci&oacute;n Autom&aacute;tica de Stock:</b> Al cambiar el estado de un apartado a <i>CANCELADO</i>, el sistema devuelve exactamente los kilogramos apartados al lote correspondiente de forma at&oacute;mica.", bullet_style))

    story.append(Spacer(1, 8))

    # SECCION 4: MATRIZ DE ENDPOINTS DE LA API
    story.append(Paragraph("4. Matriz de Servicios REST (API Endpoints)", h1_style))

    api_data = [
        [Paragraph("<b>M&eacute;todo</b>", body_style), Paragraph("<b>Endpoint</b>", body_style), Paragraph("<b>Permiso</b>", body_style), Paragraph("<b>Descripci&oacute;n</b>", body_style)],
        [Paragraph("POST", body_style), Paragraph("/api/usuarios/login", body_style), Paragraph("P&uacute;blico", body_style), Paragraph("Valida credenciales y genera token firmado de 12 horas.", body_style)],
        [Paragraph("POST", body_style), Paragraph("/api/usuarios/registro", body_style), Paragraph("P&uacute;blico", body_style), Paragraph("Registra nuevo cliente; previene asignaci&oacute;n de ADMIN.", body_style)],
        [Paragraph("GET", body_style), Paragraph("/api/catalogo", body_style), Paragraph("P&uacute;blico", body_style), Paragraph("Lista lotes. Soporta ?estado_maduracion= y ?variedad=.", body_style)],
        [Paragraph("POST", body_style), Paragraph("/api/catalogo", body_style), Paragraph("Solo ADMIN", body_style), Paragraph("Crea un nuevo lote agr&iacute;cola en el inventario.", body_style)],
        [Paragraph("PATCH", body_style), Paragraph("/api/catalogo/&lt;id&gt;", body_style), Paragraph("Solo ADMIN", body_style), Paragraph("Actualiza la maduraci&oacute;n de un lote existente.", body_style)],
        [Paragraph("POST", body_style), Paragraph("/api/catalogo/&lt;id&gt;/apartar", body_style), Paragraph("Autenticado", body_style), Paragraph("Resta stock de forma at&oacute;mica y crea registro de Apartado.", body_style)],
        [Paragraph("GET", body_style), Paragraph("/api/apartados", body_style), Paragraph("Autenticado", body_style), Paragraph("Cliente ve sus apartados; Admin visualiza todos con nombres.", body_style)],
        [Paragraph("PATCH", body_style), Paragraph("/api/apartados/&lt;id&gt;/estado", body_style), Paragraph("Autenticado", body_style), Paragraph("ENTREGADO (s&oacute;lo admin) o CANCELADO (devuelve stock).", body_style)],
    ]
    t_api = Table(api_data, colWidths=[55, 175, 75, 225])
    t_api.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#064e3b")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#fafaf9")]),
    ]))
    story.append(t_api)

    story.append(PageBreak())

    # SECCION 5: GUION PASO A PASO PARA LA SUSTENTACION
    story.append(Paragraph("5. Guion Pr&aacute;ctico de Sustentaci&oacute;n (Demostraci&oacute;n en 3 Minutos)", h1_style))
    story.append(Paragraph(
        "Sigue este orden exacto durante la sustentaci&oacute;n para cubrir todos los criterios de evaluaci&oacute;n de forma fluida y profesional:",
        body_style
    ))

    # Paso 1
    story.append(Paragraph("<b>Minuto 0:00 - 0:40 &bull; Introducci&oacute;n y Arquitectura</b>", h2_style))
    story.append(Paragraph(
        "<i>\"Buenos d&iacute;as profesor. Para el avance de hoy presentamos el m&oacute;dulo de Usuarios y Cat&aacute;logo de Aguacates 'AvoLote'. "
        "Construimos una arquitectura totalmente desacoplada con Django REST Framework en el backend y Angular 21 con Signals y TailwindCSS v4 en el frontend. "
        "Ambas capas est&aacute;n desplegadas en la nube: la API en Render y el cliente en Vercel, conectadas v&iacute;a HTTPS con CORS seguro.\"</i>",
        quote_style
    ))

    # Paso 2
    story.append(Paragraph("<b>Minuto 0:40 - 1:40 &bull; Demostraci&oacute;n Rol CLIENTE</b>", h2_style))
    story.append(Paragraph("1. En la pantalla de login, se&ntilde;ala los botones de acceso r&aacute;pido demo y pulsa <b>'Entrar como Cliente'</b>.", bullet_style))
    story.append(Paragraph("2. Muestra la barra superior: indica que el sistema detect&oacute; el rol <i>CLIENTE</i> y s&oacute;lo muestra las opciones correspondientes.", bullet_style))
    story.append(Paragraph("3. Demuestra los filtros reactivos: pulsa en <b>Papelillo</b> (muestra que las fotos cambian a la variedad criolla de c&aacute;scara lisa) y combina con el filtro <b>Maduro</b>.", bullet_style))
    story.append(Paragraph("4. En un lote con stock (ej: 400 kg), ingresa <b>15 kg</b> y haz clic en <b>'Apartar Aguacates'</b>. Se&ntilde;ala la notificaci&oacute;n toast de confirmaci&oacute;n y c&oacute;mo el stock baj&oacute; a 385 kg en vivo.", bullet_style))
    story.append(Paragraph("5. Abre el bot&oacute;n <b>'📦 Mis apartados'</b>. Muestra el registro en estado <i>⏳ Pendiente</i> con total calculado en pesos colombianos ($ COP).", bullet_style))
    story.append(Paragraph("6. Pulsa <b>'Cancelar'</b> en ese apartado. Explica al docente: <i>'Al cancelar, la base de datos ejecuta una transacci&oacute;n que retorna de inmediato los 15 kg al inventario para que otro comprador pueda adquirirlos'</i>.", bullet_style))

    # Paso 3
    story.append(Paragraph("<b>Minuto 1:40 - 2:30 &bull; Demostraci&oacute;n Rol ADMINISTRADOR ('Pap&aacute;')</b>", h2_style))
    story.append(Paragraph("1. Cierra sesi&oacute;n y pulsa el bot&oacute;n <b>'Entrar como Pap&aacute; Admin'</b>.", bullet_style))
    story.append(Paragraph("2. Resalta que ahora se despliega el <b>Panel R&aacute;pido Admin</b> (protegido tanto en frontend como en los endpoints del backend).", bullet_style))
    story.append(Paragraph("3. Ve a la pesta&ntilde;a <b>'Cambiar maduraci&oacute;n'</b>: selecciona un lote en estado Verde y c&aacute;mbialo a Maduro. Observa c&oacute;mo la tarjeta cambia de badge, color y fotograf&iacute;a al instante.", bullet_style))
    story.append(Paragraph("4. Abre <b>'📦 Apartados'</b>: demuestra que el Admin visualiza todos los apartados globales con el nombre de cada cliente que solicit&oacute; el pedido, y que posee el bot&oacute;n <b>'✓ Entregar'</b> para despacharlo.", bullet_style))

    # Paso 4
    story.append(Paragraph("<b>Minuto 2:30 - 3:00 &bull; Pruebas Unitarias y Calidad</b>", h2_style))
    story.append(Paragraph(
        "<i>\"Adem&aacute;s de la interfaz visual, dejamos implementada una suite de 12 pruebas unitarias automatizadas en Django "
        "(python manage.py test api) que validan el 100% de los casos de negocio: prevenci&oacute;n de sobreventa, no elevaci&oacute;n de privilegios "
        "y aislamiento entre usuarios. Todo el proyecto se encuentra respaldado en GitHub con control de versiones.\"</i>",
        quote_style
    ))

    story.append(Spacer(1, 10))

    # SECCION 6: PREGUNTAS FRECUENTES DEL PROFESOR
    story.append(Paragraph("6. Respuestas a Preguntas Frecuentes del Evaluador", h1_style))

    faq_data = [
        [
            Paragraph("<b>Pregunta Probable</b>", body_style),
            Paragraph("<b>Respuesta T&eacute;cnica Sugerida</b>", body_style)
        ],
        [
            Paragraph("&iquest;C&oacute;mo evitan que dos personas aparten el mismo stock a la vez?", body_style),
            Paragraph("Usamos transacciones at&oacute;micas en Django con <i>select_for_update()</i>. Esto bloquea la fila del lote en base de datos hasta que la resta de stock se confirme, evitando condiciones de carrera.", body_style)
        ],
        [
            Paragraph("&iquest;Por qu&eacute; no usaron el User por defecto de Django?", body_style),
            Paragraph("El requerimiento solicitaba un modelo ligero con campos espec&iacute;ficos (nombre, correo, rol). Usamos <i>UsuarioPersonalizado</i> con contrase&ntilde;as cifradas mediante el algoritmo PBKDF2 de Django para mantener la seguridad.", body_style)
        ],
        [
            Paragraph("&iquest;Por qu&eacute; usar Signals en Angular en vez de RxJS tradicional?", body_style),
            Paragraph("Angular Signals es el nuevo est&aacute;ndar oficial de Angular (zoneless-ready). Ofrece reactividad de grano fino, mejor rendimiento de renderizado y elimina fugas de memoria t&iacute;picas de suscripciones manuales.", body_style)
        ],
        [
            Paragraph("&iquest;Qu&eacute; pasos siguen para el proyecto final?", body_style),
            Paragraph("Migrar de SQLite a PostgreSQL en la nube, reemplazar tokens firmados por JWT con refresh tokens, permitir al Admin subir im&aacute;genes personalizadas por lote y generar reportes anal&iacute;ticos de ventas en PDF.", body_style)
        ],
    ]
    t_faq = Table(faq_data, colWidths=[180, 350])
    t_faq.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#064e3b")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor("#f0fdf4"), colors.white]),
    ]))
    story.append(t_faq)

    doc.build(story)
    print(f"PDF generado exitosamente: {filename}")

if __name__ == '__main__':
    build_pdf()
