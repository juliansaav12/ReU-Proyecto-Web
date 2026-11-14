from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import (
    CalificacionForm,
    PublicacionForm,
    RegistroForm,
    ReporteForm,
    SolicitudForm,
)
from .models import Categoria, Publicacion, Reporte, Solicitud, Calificacion, Usuario


def home(request):
    context = {
        "recuperados": Publicacion.objects.filter(
            tipo__in=["PERDIDO", "ENCONTRADO"],
            estado_publicacion="RESUELTA",
        ).count(),
        "intercambios": Publicacion.objects.filter(
            tipo="INTERCAMBIO",
            estado_publicacion="RESUELTA",
        ).count(),
        "regalos": Publicacion.objects.filter(
            tipo="REGALO",
            estado_publicacion="RESUELTA",
        ).count(),
        "reutilizados": Publicacion.objects.filter(
            estado_publicacion="RESUELTA"
        ).count(),
        "ultimas": Publicacion.objects.filter(
            estado_publicacion="ACTIVA"
        )[:6],
    }
    return render(request, "home.html", context)

def enviar_aviso(usuario, asunto, mensaje):
    if usuario.correo:
        send_mail(
            asunto,
            mensaje,
            settings.DEFAULT_FROM_EMAIL,
            [usuario.correo],
            fail_silently=True,
        )

def explorar(request):
    publicaciones = Publicacion.objects.filter(estado_publicacion="ACTIVA")

    q = request.GET.get("q", "").strip()
    tipo = request.GET.get("tipo", "")
    categoria = request.GET.get("categoria", "")

    if q:
        publicaciones = publicaciones.filter(
            Q(titulo__icontains=q)
            | Q(descripcion__icontains=q)
            | Q(ubicacion__icontains=q)
        )

    if tipo:
        publicaciones = publicaciones.filter(tipo=tipo)

    if categoria:
        publicaciones = publicaciones.filter(categoria_id=categoria)

    context = {
        "publicaciones": publicaciones,
        "categorias": Categoria.objects.all(),
        "tipo_actual": tipo,
        "categoria_actual": categoria,
        "q": q,
    }
    return render(request, "explorar.html", context)


def detalle(request, pk):
    publicacion = get_object_or_404(Publicacion, pk=pk)

    promedio = publicacion.usuario.calificaciones_recibidas.aggregate(
        promedio=Avg("puntuacion")
    )["promedio"]

    context = {
            "publicacion": publicacion,
            "promedio": promedio,
            "solicitud_form": SolicitudForm(),
            "reporte_form": ReporteForm(),
        }
    return render(request, "detalle.html", context)


def registro(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = RegistroForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            login(request, usuario)
            messages.success(request, "Tu cuenta fue creada correctamente.")
            return redirect("home")
    else:
        form = RegistroForm()

    return render(request, "registration/registro.html", {"form": form})


@login_required
def publicar(request):
    if request.method == "POST":
        form = PublicacionForm(request.POST, request.FILES)
        if form.is_valid():
            publicacion = form.save(commit=False)
            publicacion.usuario = request.user
            publicacion.save()
            messages.success(request, "Publicación creada correctamente.")
            return redirect("detalle", pk=publicacion.pk)
    else:
        form = PublicacionForm()

    return render(request, "publicar.html", {"form": form})


@login_required
def editar_publicacion(request, pk):
    publicacion = get_object_or_404(Publicacion, pk=pk)

    
    
    if publicacion.usuario != request.user and not request.user.is_staff and request.user.rol != "MODERADOR":
        messages.error(request, "No tienes permiso para editar esta publicación.")
        return redirect("detalle", pk=pk)

    if request.method == "POST":
        form = PublicacionForm(request.POST, request.FILES, instance=publicacion)
        if form.is_valid():
            form.save()
            messages.success(request, "Publicación actualizada.")
            return redirect("detalle", pk=pk)
    else:
        form = PublicacionForm(instance=publicacion)

    return render(
        request,
        "publicar.html",
        {"form": form, "edicion": True, "publicacion": publicacion},
    )


@login_required
def eliminar_publicacion(request, pk):
    publicacion = get_object_or_404(Publicacion, pk=pk)

    if publicacion.usuario != request.user and not request.user.is_staff and request.user.rol != "MODERADOR":
        messages.error(request, "No tienes permiso para eliminar esta publicación.")
        return redirect("detalle", pk=pk)

    if request.method == "POST":
        publicacion.delete()
        messages.success(request, "Publicación eliminada.")
        return redirect("explorar")

    return render(
        request,
        "confirmar_eliminacion.html",
        {"publicacion": publicacion},
    )


@login_required
def solicitar(request, pk):
    publicacion = get_object_or_404(Publicacion, pk=pk)

    if publicacion.usuario == request.user:
        messages.error(request, "No puedes solicitar tu propia publicación.")
        return redirect("detalle", pk=pk)

    if publicacion.estado_publicacion != "ACTIVA":
        messages.error(request, "Esta publicación ya no está disponible.")
        return redirect("detalle", pk=pk)

    if request.method == "POST":
        form = SolicitudForm(request.POST)
        if form.is_valid():
            solicitud = form.save(commit=False)
            solicitud.publicacion = publicacion
            solicitud.usuario_solicitante = request.user

            # Si es intercambio se revisa y se retienen los tokens
            if publicacion.tipo == "INTERCAMBIO" and publicacion.valor_tokens > 0:
                if request.user.tokens < publicacion.valor_tokens:
                    messages.error(
                        request,
                        f"No tienes suficientes tokens (necesitas {publicacion.valor_tokens} y tienes {request.user.tokens}).",
                    )
                    return redirect("detalle", pk=pk)

                request.user.tokens -= publicacion.valor_tokens
                request.user.save()
                solicitud.tokens_retenidos = publicacion.valor_tokens

            solicitud.save()
            publicacion.estado_publicacion = "EN_PROCESO"
            publicacion.save(update_fields=["estado_publicacion"])
            messages.success(request, "Solicitud enviada.")
            enviar_aviso(
                publicacion.usuario,
                f"ReU: Nueva solicitud para {publicacion.titulo}",
                f"Hola {publicacion.usuario.nombre}, {request.user.nombre} envió una solicitud para '{publicacion.titulo}'. Entra a ReU para verla.",
            )
            return redirect("perfil")

    return redirect("detalle", pk=pk)


@login_required
def perfil(request):
    mis_publicaciones = Publicacion.objects.filter(usuario=request.user)
    recibidas = Solicitud.objects.filter(publicacion__usuario=request.user)
    enviadas = Solicitud.objects.filter(usuario_solicitante=request.user)

    promedio = request.user.calificaciones_recibidas.aggregate(
        promedio=Avg("puntuacion")
    )["promedio"]

    context = {
        "mis_publicaciones": mis_publicaciones,
        "solicitudes_recibidas": recibidas,
        "solicitudes_enviadas": enviadas,
        "promedio": promedio,
    }
    return render(request, "perfil.html", context)


@login_required
def gestionar_solicitud(request, pk, accion):
    solicitud = get_object_or_404(Solicitud, pk=pk)

    propietario = solicitud.publicacion.usuario
    solicitante = solicitud.usuario_solicitante

    if accion in ["aceptar", "rechazar"]:
        if request.user != propietario:
            messages.error(
                request,
                "Solo el dueño de la publicación puede aceptar o rechazar la solicitud.",
            )
            return redirect("perfil")

        if solicitud.estado != "PENDIENTE":
            messages.info(request, "Esta solicitud ya fue respondida.")
            return redirect("perfil")

        if accion == "aceptar":
            # Si es PERDIDO y ofrece recompensa, se le retienen al dueño
            if solicitud.publicacion.tipo == "PERDIDO" and solicitud.publicacion.valor_tokens > 0:
                if propietario.tokens < solicitud.publicacion.valor_tokens:
                    messages.error(
                        request,
                        f"No tienes suficientes tokens para la recompensa ({solicitud.publicacion.valor_tokens}).",
                    )
                    return redirect("perfil")

                propietario.tokens -= solicitud.publicacion.valor_tokens
                propietario.save()
                solicitud.tokens_retenidos = solicitud.publicacion.valor_tokens

            solicitud.estado = "ACEPTADA"
            solicitud.publicacion.estado_publicacion = "EN_PROCESO"
            solicitud.publicacion.save(update_fields=["estado_publicacion"])

        elif accion == "rechazar":
            # Si había tokens retenidos se devuelven
            if solicitud.tokens_retenidos > 0:
                solicitante.tokens += solicitud.tokens_retenidos
                solicitante.save()
                solicitud.tokens_retenidos = 0

            solicitud.estado = "RECHAZADA"
            # La publicación vuelve a estar activa para que otros puedan solicitarla
            solicitud.publicacion.estado_publicacion = "ACTIVA"
            solicitud.publicacion.save(update_fields=["estado_publicacion"])

    elif accion == "completar":
        if request.user not in [propietario, solicitante]:
            messages.error(
                request,
                "Solo los participantes de la interacción pueden marcarla como completada.",
            )
            return redirect("perfil")

        if solicitud.estado != "ACEPTADA":
            messages.error(
                request,
                "Solo se puede completar una solicitud que haya sido aceptada.",
            )
            return redirect("perfil")

        # si se completa se pasan los tokens
        if solicitud.tokens_retenidos > 0:
            if solicitud.publicacion.tipo == "PERDIDO":
                solicitante.tokens += solicitud.tokens_retenidos
                solicitante.save()
            else:
                propietario.tokens += solicitud.tokens_retenidos
                propietario.save()
            solicitud.tokens_retenidos = 0
        elif solicitud.publicacion.tipo == "REGALO":
            propietario.tokens += 2
            propietario.save()
        elif solicitud.publicacion.tipo == "PERDIDO":
            solicitante.tokens += 3
            solicitante.save()
        elif solicitud.publicacion.tipo == "ENCONTRADO":
            propietario.tokens += 3
            propietario.save()

        solicitud.estado = "COMPLETADA"
        solicitud.publicacion.estado_publicacion = "RESUELTA"
        solicitud.publicacion.save(update_fields=["estado_publicacion"])

    else:
        messages.error(request, "Acción no válida.")
        return redirect("perfil")

    solicitud.save()
    messages.success(request, f"Solicitud {solicitud.get_estado_display().lower()}.")
    if solicitud.estado in ["ACEPTADA", "RECHAZADA"]:
        extra = ""
        if solicitud.estado == "ACEPTADA":
            extra = f" Puedes escribirle a {propietario.nombre} ({propietario.correo}) para coordinar."

        enviar_aviso(
            solicitante,
            f"ReU: Tu solicitud fue {solicitud.get_estado_display().lower()}",
            f"Hola {solicitante.nombre}, tu solicitud para '{solicitud.publicacion.titulo}' fue {solicitud.get_estado_display().lower()}.{extra}",
        )
    elif solicitud.estado == "COMPLETADA":
        otro = solicitante if request.user == propietario else propietario
        enviar_aviso(
            otro,
            f"ReU: Interacción completada - {solicitud.publicacion.titulo}",
            f"Hola {otro.nombre}, la interacción por '{solicitud.publicacion.titulo}' ya fue completada. Entra a ReU para calificar.",
        )
    return redirect("perfil")


@login_required
def calificar(request, solicitud_id):
    solicitud = get_object_or_404(
        Solicitud,
        pk=solicitud_id,
        estado="COMPLETADA",
    )

    propietario = solicitud.publicacion.usuario
    solicitante = solicitud.usuario_solicitante

    # El usuario debe ser uno de los dos participantes
    if request.user.id == propietario.id:
        evaluado = solicitante

    elif request.user.id == solicitante.id:
        evaluado = propietario

    else:
        messages.error(
            request,
            "Solo los participantes de la interacción pueden calificar."
        )
        return redirect("perfil")

    # Evitar que la misma persona califique dos veces
    if Calificacion.objects.filter(
        solicitud=solicitud,
        usuario_evaluador=request.user,
    ).exists():
        messages.info(
            request,
            "Ya calificaste esta interacción."
        )
        return redirect("perfil")

    if request.method == "POST":
        form = CalificacionForm(request.POST)

        if form.is_valid():
            calificacion = form.save(commit=False)

            calificacion.solicitud = solicitud
            calificacion.usuario_evaluador = request.user
            calificacion.usuario_evaluado = evaluado

            calificacion.save()

            messages.success(
                request,
                "Calificación registrada correctamente."
            )

            return redirect("perfil")

    else:
        form = CalificacionForm()

    return render(
        request,
        "calificar.html",
        {
            "form": form,
            "solicitud": solicitud,
            "evaluado": evaluado,
        },
    )

@login_required
def reportar(request, pk):
    publicacion = get_object_or_404(Publicacion, pk=pk)

    if request.method == "POST":
        form = ReporteForm(request.POST)
        if form.is_valid():
            reporte = form.save(commit=False)
            reporte.publicacion = publicacion
            reporte.usuario = request.user
            reporte.save()
            messages.success(request, "Reporte enviado.")

    return redirect("detalle", pk=pk)


@login_required
def moderacion(request):
    if request.user.rol not in ["MODERADOR", "ADMIN"] and not request.user.is_staff:
        messages.error(request, "No tienes permiso.")
        return redirect("home")

    reportes = Reporte.objects.filter(revisado=False)
    usuarios = Usuario.objects.exclude(pk=request.user.pk).exclude(is_staff=True).exclude(is_superuser=True).exclude(rol="ADMIN")

    return render(
        request,
        "moderacion.html",
        {
            "reportes": reportes,
            "usuarios": usuarios,
        },
    )


@login_required
def resolver_reporte(request, pk, accion):
    if request.user.rol not in ["MODERADOR", "ADMIN"] and not request.user.is_staff:
        return redirect("home")

    reporte = get_object_or_404(Reporte, pk=pk)

    if request.method == "POST":
        if accion == "cancelar":
            reporte.publicacion.estado_publicacion = "CANCELADA"
            reporte.publicacion.save()
            messages.success(request, "Publicación cancelada.")
        else:
            messages.info(request, "Reporte descartado.")

        reporte.revisado = True
        reporte.save()

    return redirect("moderacion")


@login_required
def bloquear_usuario(request, pk):
    if request.user.rol not in ["MODERADOR", "ADMIN"] and not request.user.is_staff:
        return redirect("home")

    usuario = get_object_or_404(Usuario, pk=pk)

    if usuario.is_staff or usuario.is_superuser or usuario.rol == "ADMIN":
        messages.error(request, "No puedes bloquear a un administrador.")
        return redirect("moderacion")

    if request.method == "POST":
        # Cambia entre True y False (activo / bloqueado)
        usuario.estado = not usuario.estado
        usuario.is_active = usuario.estado
        usuario.save()

        if usuario.estado:
            messages.success(request, f"Usuario {usuario.nombre} desbloqueado.")
        else:
            messages.success(request, f"Usuario {usuario.nombre} bloqueado.")

    return redirect("moderacion")