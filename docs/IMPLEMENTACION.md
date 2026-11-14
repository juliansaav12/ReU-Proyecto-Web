# Guía de implementación de ReU

## Modelos

`core/models.py` contiene las cinco entidades principales:

- Usuario
- Categoria
- Publicacion
- Solicitud
- Calificacion

El modelo `Usuario` extiende el usuario de Django para mantener autenticación segura con el sistema de Django y agregar los datos propios de ReU.

## Vistas

`core/views.py` contiene:

- Inicio
- Explorar y filtrar
- Detalle
- Registro
- Crear publicación
- Editar publicación
- Eliminar publicación
- Solicitar objeto
- Perfil
- Aceptar/rechazar/completar solicitudes
- Calificar usuarios

## URLs

Las rutas están separadas en:

- `reu_project/urls.py`: rutas generales y administración.
- `core/urls.py`: funcionalidades de ReU.

## Templates

Los templates usan herencia desde `templates/base.html`.

Esto permite mantener el menú y el pie de página en un solo archivo.

## Base de datos

Para desarrollo se utiliza SQLite. Django genera las tablas mediante:

```bash
python manage.py makemigrations
python manage.py migrate
```

Para una versión posterior se puede cambiar a MySQL modificando `DATABASES` en `settings.py`.

## Próximas mejoras recomendadas

1. Validar mejor imágenes y formularios.
2. Agregar paginación.
3. Agregar favoritos.
4. Mejorar permisos del administrador.
5. Agregar estadísticas visuales.
6. Añadir JavaScript para mejorar filtros y experiencia.
7. Migrar a MySQL si el profesor lo exige.
