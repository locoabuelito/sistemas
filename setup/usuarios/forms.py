# usuarios/forms.py
from django import forms
from django.utils.translation import gettext_lazy as _

class UsuarioTecnicoLoginForm(forms.Form):
    username = forms.CharField(
        label=_('Correo Electrónico'),
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'correo@ejemplo.com',
            'autofocus': True
        })
    )
    password = forms.CharField(
        label=_('Contraseña'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña'
        })
    )
    
    error_messages = {
        'invalid_login': _(
            "Por favor ingrese un correo electrónico y contraseña correctos. "
            "Note que ambos campos pueden ser sensibles a mayúsculas."
        ),
        'inactive': _("Esta cuenta está inactiva."),
    }