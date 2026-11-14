from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario, Publicacion, Solicitud, Calificacion, Reporte


class RegistroForm(UserCreationForm):
    nombre = forms.CharField(max_length=100)
    correo = forms.EmailField()

    class Meta:
        model = Usuario
        fields = ("username", "nombre", "correo", "password1", "password2")

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.nombre = self.cleaned_data["nombre"]
        usuario.correo = self.cleaned_data["correo"]
        if commit:
            usuario.save()
        return usuario


class PublicacionForm(forms.ModelForm):
    class Meta:
        model = Publicacion
        fields = [
            "tipo",
            "titulo",
            "categoria",
            "descripcion",
            "estado_objeto",
            "valor_tokens",
            "ubicacion",
            "coord_x",
            "coord_y",
            "imagen",
        ]
        widgets = {
            "descripcion": forms.Textarea(attrs={"rows": 5}),
            "coord_x": forms.HiddenInput(),
            "coord_y": forms.HiddenInput(),
        }

        labels = {
            "valor_tokens": "Valor o recompensa en tokens (0 si es regalo)",
        }

    def clean(self):
        datos = super().clean()
        tipo = datos.get("tipo")
        valor = datos.get("valor_tokens") or 0

        if tipo == "REGALO":
            datos["valor_tokens"] = 0
        elif tipo == "INTERCAMBIO" and valor < 1:
            self.add_error("valor_tokens", "En un intercambio debes poner al menos 1 token.")

        return datos    

class SolicitudForm(forms.ModelForm):
    class Meta:
        model = Solicitud
        fields = ["tipo_solicitud", "mensaje"]
        widgets = {
            "mensaje": forms.Textarea(
                attrs={"rows": 4, "placeholder": "Escribe un mensaje breve..."}
            )
        }


class CalificacionForm(forms.ModelForm):
    class Meta:
        model = Calificacion
        fields = ["puntuacion", "comentario"]
        widgets = {
            "puntuacion": forms.Select(
                choices=[
                    (1, "1 - Muy mala"),
                    (2, "2 - Mala"),
                    (3, "3 - Regular"),
                    (4, "4 - Buena"),
                    (5, "5 - Excelente"),
                ]
            ),
            "comentario": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Escribe un comentario sobre la interacción..."
                }
            ),
        }

class ReporteForm(forms.ModelForm):
    class Meta:
        model = Reporte
        fields = ["motivo"]
        widgets = {
            "motivo": forms.TextInput(
                attrs={"placeholder": "Ej: Información falsa, objeto prohibido..."}
            )
        }