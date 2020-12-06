from django import forms

class GraffitiForm(forms.Form):
    imagen = forms.FileField(required=True)
    estado = forms.CharField(required=True)
    fechaCaptura = forms.DateField(required=True, label='Fecha de captura', widget=forms.DateInput())