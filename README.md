# ReU — Reencuentra, Reutiliza, Intercambia

Proyecto web desarrollado para la materia Programación en la Web (UIS). Permite a la comunidad universitaria reportar objetos perdidos o encontrados, intercambiar cosas mediante un sistema de tokens o regalar objetos que ya no se utilizan.

## 1. Tecnologías

- Python
- Django
- SQLite para desarrollo
- HTML5
- CSS3
- JavaScript (para marcar la ubicación en el mapa del campus)
- Pillow para imágenes
- Mailtrap (SMTP de pruebas para notificaciones por correo)

## 2. Estructura

```text
ReU-Proyecto-Web/
├── manage.py
├── requirements.txt
├── db.sqlite3                  # base de datos SQLite con datos de prueba
├── reu_project/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── core/
│   ├── models.py
│   ├── forms.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   └── migrations/
├── media/
│   └── publicaciones/
├── templates/
│   ├── registration/
│   └── moderacion.html         # y demás vistas (base, home, explorar, detalle, publicar, perfil, etc.)
└── static/
    ├── css/style.css
    └── img/mapa_uis.webp
```

## 3. Instalación

En VS Code abre una terminal dentro de la carpeta del proyecto:

```bash
python -m venv .venv
```

En Windows (CMD):

```bash
.venv\Scripts\activate.bat
```

Luego:

```bash
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

*(Si se desea crear un administrador nuevo desde cero, ejecutar `python manage.py createsuperuser`. Para probar el envío de correos en `reu_project/settings.py`, basta con poner el usuario y la contraseña del Sandbox de Mailtrap).*

Abre:

```text
http://127.0.0.1:8000/
```

Administración:

```text
http://127.0.0.1:8000/admin/
```

## 4. Primeros datos y roles

El sistema maneja tres roles en el modelo `Usuario`: **Estudiante**, **Moderador** y **Administrador**.

Desde `/admin/` el administrador puede gestionar las categorías iniciales (Tecnología, Libros, Papelería, Ropa y accesorios, Hogar, Otros) y asignar el rol de **Moderador** a cualquier usuario para que tenga acceso al panel `/moderacion/`.

Los estudiantes pueden registrarse directamente desde `/registro/`.

## 5. Flujo principal

1. Un estudiante se registra (inicia con 20 tokens) e inicia sesión.
2. Crea una publicación (Perdido, Encontrado, Intercambio o Regalo), puede asignarle un valor o recompensa en tokens y marcar con un clic el punto exacto en el mapa del campus de la UIS.
3. Otro estudiante explora, filtra publicaciones y revisa el detalle junto con el punto marcado en el mapa.
4. El segundo estudiante envía una solicitud (si es intercambio, el sistema retiene los tokens correspondientes) y el dueño recibe una notificación por correo.
5. El dueño acepta o rechaza la solicitud desde su perfil; el solicitante recibe un correo con la respuesta (si se rechaza, los tokens retenidos se reembolsan y la publicación vuelve a quedar activa).
6. Al marcar la interacción como completada, se transfieren los tokens o el servidor entrega un bono automático (+2 en regalos, +3 en devoluciones sin recompensa) y avisa por correo para calificar.
7. Los participantes se califican entre sí.
8. Si alguna publicación es inapropiada o falsa, cualquier usuario puede reportarla y el moderador puede revisar el reporte en `/moderacion/`, cancelar la publicación o bloquear al estudiante.
9. Los datos actualizan las estadísticas de impacto en la página principal.

## 6. Relación con el modelo conceptual

- Usuario 1:N Publicacion
- Categoria 1:N Publicacion
- Publicacion 1:N Solicitud
- Usuario 1:N Solicitud
- Solicitud 1:N Calificacion (limitada por usuario evaluador mediante una restricción única).
- Usuario 1:N Calificacion (como evaluador y como evaluado).
- Publicacion 1:N Reporte
- Usuario 1:N Reporte

## 7. Alcance del proyecto

No se implementan en esta versión:

- pagos con dinero real
- domicilios/envíos
- chat en tiempo real
- GPS en tiempo real
- integración con redes sociales
- aplicación móvil
- IA
- subastas

La prioridad es contar con una aplicación web MPA funcional, clara y manejable para el proyecto académico.