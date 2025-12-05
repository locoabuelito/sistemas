# usuarios/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.utils.translation import gettext_lazy as _
from .models import UsuarioTecnico

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
    
class UsuarioTecnicoCreationForm(UserCreationForm):
    """
    Formulario para CREAR usuarios desde el admin.
    Maneja automáticamente la contraseña y su confirmación.
    """
    class Meta:
        model = UsuarioTecnico
        fields = ('correo_tecnico', 'nombre_tecnico', 'id_sector_tecnico')

class UsuarioTecnicoChangeForm(UserChangeForm):
    """
    Formulario para EDITAR usuarios desde el admin.
    Permite cambiar datos y tiene el enlace para resetear password.
    """
    class Meta:
        model = UsuarioTecnico
        fields = '__all__'