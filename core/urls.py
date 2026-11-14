from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("explorar/", views.explorar, name="explorar"),
    path("publicacion/<int:pk>/", views.detalle, name="detalle"),
    path("publicar/", views.publicar, name="publicar"),

    path(
        "publicacion/<int:pk>/editar/",
        views.editar_publicacion,
        name="editar_publicacion",
    ),

    path(
        "publicacion/<int:pk>/eliminar/",
        views.eliminar_publicacion,
        name="eliminar_publicacion",
    ),

    path(
        "publicacion/<int:pk>/solicitar/",
        views.solicitar,
        name="solicitar",
    ),

    path("perfil/", views.perfil, name="perfil"),

    # PRIMERO: ruta específica para calificar
    path(
        "solicitud/<int:solicitud_id>/calificar/",
        views.calificar,
        name="calificar",
    ),

    # DESPUÉS: ruta general para las acciones
    path(
        "solicitud/<int:pk>/<str:accion>/",
        views.gestionar_solicitud,
        name="gestionar_solicitud",
    ),

    path("registro/", views.registro, name="registro"),

    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="registration/login.html"
        ),
        name="login",
    ),

    path("logout/", auth_views.LogoutView.as_view(), name="logout"),

    path("publicacion/<int:pk>/reportar/", views.reportar, name="reportar"),
    path("moderacion/", views.moderacion, name="moderacion"),
    path("moderacion/reporte/<int:pk>/<str:accion>/", views.resolver_reporte, name="resolver_reporte"),
    path("moderacion/usuario/<int:pk>/bloquear/", views.bloquear_usuario, name="bloquear_usuario"),
]