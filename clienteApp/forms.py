from django import forms

class GraffitiForm(forms.Form):
    imagen = forms.FileField(required=True)
    estado = forms.CharField(required=True)
    fechaCaptura = forms.DateTimeField(label='Fecha de Captura', required=True)