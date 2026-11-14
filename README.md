# ReU — Django Starter

Proyecto base para **ReU — Reencuentra, Reutiliza, Intercambia**, pensado para la materia Programación en la Web.

## 1. Tecnologías

- Python
- Django
- SQLite para desarrollo
- HTML5
- CSS3
- JavaScript puede agregarse posteriormente
- Pillow para imágenes

## 2. Estructura

```text
ReU_Django/
├── manage.py
├── requirements.txt
├── db.sqlite3                  # se crea al ejecutar migrate
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
├── templates/
└── static/css/
```

## 3. Instalación

En VS Code abre una terminal dentro de la carpeta del proyecto:

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

Luego:

```bash
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Abre:

```text
http://127.0.0.1:8000/
```

Administración:

```text
http://127.0.0.1:8000/admin/
```

## 4. Primeros datos

Después de crear el superusuario, entra al administrador y crea algunas categorías:

- Tecnología
- Libros
- Papelería
- Ropa y accesorios
- Hogar
- Otros

Después puedes registrar estudiantes desde `/registro/`.

## 5. Flujo principal

1. Un estudiante se registra.
2. Inicia sesión.
3. Crea una publicación.
4. Otro estudiante explora y filtra publicaciones.
5. El segundo estudiante envía una solicitud.
6. El dueño acepta o rechaza.
7. Si se realiza la interacción, se marca como completada.
8. Los usuarios pueden calificarse.
9. Los datos permiten mostrar estadísticas de impacto en la página principal.

## 6. Relación con el modelo conceptual

- Usuario 1:N Publicacion
- Categoria 1:N Publicacion
- Publicacion 1:N Solicitud
- Usuario 1:N Solicitud
- Solicitud 1:N Calificacion técnicamente, limitada por usuario evaluador mediante una restricción única.
- Usuario 1:N Calificacion como evaluador y como evaluado.

## 7. Alcance inicial

No se implementan en esta primera versión:

- pagos
- domicilios/envíos
- chat en tiempo real
- GPS en tiempo real
- integración con redes sociales
- aplicación móvil
- IA
- subastas

La prioridad es tener una aplicación web funcional y manejable para el proyecto académico.
