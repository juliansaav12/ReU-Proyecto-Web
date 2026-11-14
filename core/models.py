from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Usuario(AbstractUser):
    ROLES = [
        ("ESTUDIANTE", "Estudiante"),
        ("MODERADOR", "Moderador"),
        ("ADMIN", "Administrador"),
    ]

    nombre = models.CharField(max_length=100)
    correo = models.EmailField(unique=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    estado = models.BooleanField(default=True)
    rol = models.CharField(max_length=20, choices=ROLES, default="ESTUDIANTE")
    tokens = models.PositiveIntegerField(default=20)

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

    def __str__(self):
        return self.nombre or self.username


class Categoria(models.Model):
    nombre = models.CharField(max_length=80, unique=True)

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Publicacion(models.Model):
    TIPO_CHOICES = [
        ("PERDIDO", "Perdido"),
        ("ENCONTRADO", "Encontrado"),
        ("INTERCAMBIO", "Intercambio"),
        ("REGALO", "Regalo"),
    ]

    ESTADO_OBJETO_CHOICES = [
        ("BUENO", "Bueno"),
        ("REGULAR", "Regular"),
        ("USADO", "Usado"),
    ]

    ESTADO_PUBLICACION_CHOICES = [
        ("ACTIVA", "Activa"),
        ("EN_PROCESO", "En proceso"),
        ("RESUELTA", "Resuelta"),
        ("CANCELADA", "Cancelada"),
    ]

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="publicaciones",
    )
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name="publicaciones",
    )
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    titulo = models.CharField(max_length=150)
    descripcion = models.TextField()
    estado_objeto = models.CharField(
        max_length=20,
        choices=ESTADO_OBJETO_CHOICES,
        blank=True,
    )
    ubicacion = models.CharField(max_length=150, blank=True)
    valor_tokens = models.PositiveIntegerField(default=0)
    coord_x = models.FloatField(null=True, blank=True)
    coord_y = models.FloatField(null=True, blank=True)
    imagen = models.ImageField(upload_to="publicaciones/", blank=True, null=True)
    fecha_publicacion = models.DateTimeField(auto_now_add=True)
    estado_publicacion = models.CharField(
        max_length=20,
        choices=ESTADO_PUBLICACION_CHOICES,
        default="ACTIVA",
    )

    class Meta:
        ordering = ["-fecha_publicacion"]

    def __str__(self):
        return self.titulo


class Solicitud(models.Model):
    TIPO_SOLICITUD_CHOICES = [
        ("DEVOLUCION", "Devolución"),
        ("INTERCAMBIO", "Intercambio"),
        ("REGALO", "Regalo"),
    ]

    ESTADO_CHOICES = [
        ("PENDIENTE", "Pendiente"),
        ("ACEPTADA", "Aceptada"),
        ("RECHAZADA", "Rechazada"),
        ("COMPLETADA", "Completada"),
    ]

    publicacion = models.ForeignKey(
        Publicacion,
        on_delete=models.CASCADE,
        related_name="solicitudes",
    )
    usuario_solicitante = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="solicitudes_enviadas",
    )
    tipo_solicitud = models.CharField(
        max_length=20,
        choices=TIPO_SOLICITUD_CHOICES,
    )
    mensaje = models.TextField(blank=True)
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default="PENDIENTE",
    )
    fecha_solicitud = models.DateTimeField(auto_now_add=True)

    tokens_retenidos = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-fecha_solicitud"]

    def __str__(self):
        return f"{self.usuario_solicitante} - {self.publicacion}"


class Calificacion(models.Model):
    solicitud = models.ForeignKey(
        Solicitud,
        on_delete=models.CASCADE,
        related_name="calificaciones",
    )
    usuario_evaluador = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="calificaciones_realizadas",
    )
    usuario_evaluado = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="calificaciones_recibidas",
    )
    puntuacion = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comentario = models.TextField(blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["solicitud", "usuario_evaluador"],
                name="una_calificacion_por_usuario_solicitud",
            )
        ]

    def __str__(self):
        return f"{self.puntuacion}/5 - {self.usuario_evaluado}"


class Reporte(models.Model):
    publicacion = models.ForeignKey(
        Publicacion,
        on_delete=models.CASCADE,
        related_name="reportes",
    )
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
    )
    motivo = models.CharField(max_length=200)
    revisado = models.BooleanField(default=False)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha"]

    def __str__(self):
        return f"Reporte: {self.publicacion.titulo}"