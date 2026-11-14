from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Usuario, Categoria, Publicacion, Solicitud, Calificacion, Reporte


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Información de ReU",
            {
                "fields": (
                    "nombre",
                    "correo",
                    "rol",
                    "tokens",
                    "estado",
                )
            },
        ),
    )

    fieldsets = UserAdmin.fieldsets + (
        (
            "Información de ReU",
            {
                "fields": (
                    "nombre",
                    "correo",
                    "rol",
                    "tokens",
                    "estado",
                )
            },
        ),
    )

    list_display = (
        "username",
        "nombre",
        "correo",
        "rol",
        "tokens",
        "is_staff",
        "estado",
    )


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre")
    search_fields = ("nombre",)


@admin.register(Publicacion)
class PublicacionAdmin(admin.ModelAdmin):
    list_display = (
        "titulo",
        "tipo",
        "valor_tokens",
        "categoria",
        "usuario",
        "estado_publicacion",
        "fecha_publicacion",
    )
    list_filter = ("tipo", "estado_publicacion", "categoria")
    search_fields = ("titulo", "descripcion", "ubicacion")


@admin.register(Solicitud)
class SolicitudAdmin(admin.ModelAdmin):
    list_display = (
        "publicacion",
        "usuario_solicitante",
        "tipo_solicitud",
        "estado",
        "fecha_solicitud",
    )
    list_filter = ("estado", "tipo_solicitud")


@admin.register(Calificacion)
class CalificacionAdmin(admin.ModelAdmin):
    list_display = (
        "usuario_evaluador",
        "usuario_evaluado",
        "puntuacion",
        "fecha",
    )
    list_filter = ("puntuacion",)


@admin.register(Reporte)
class ReporteAdmin(admin.ModelAdmin):
    list_display = ("publicacion", "usuario", "motivo", "revisado", "fecha")
    list_filter = ("revisado",)