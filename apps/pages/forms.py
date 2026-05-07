from django import forms


SERVICIOS = [
    ("", "Selecciona una opción"),
    ("agencia-aduanal", "Agencia Aduanal"),
    ("bodega-patio", "Bodega & Patio"),
    ("transporte", "Transporte de Carga"),
    ("todos", "Todos los servicios"),
]


class ContactForm(forms.Form):
    nombre = forms.CharField(max_length=100, label="Nombre")
    empresa = forms.CharField(max_length=100, required=False, label="Empresa")
    correo = forms.EmailField(label="Correo electrónico")
    telefono = forms.CharField(max_length=30, required=False, label="Teléfono / WhatsApp")
    servicio = forms.ChoiceField(choices=SERVICIOS, required=False, label="Servicio de interés")
    mensaje = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 5}),
        label="Mensaje",
    )
