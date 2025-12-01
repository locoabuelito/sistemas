# usuarios/models.py
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone

class UsuarioTecnicoManager(BaseUserManager):
    def create_user(self, correo_tecnico, password=None, **extra_fields):
        if not correo_tecnico:
            raise ValueError('El correo electrónico es obligatorio')
        
        correo_tecnico = self.normalize_email(correo_tecnico)
        user = self.model(correo_tecnico=correo_tecnico, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, correo_tecnico, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('activo_tecnico', True)
        
        # Establecer valores por defecto para campos requeridos
        if 'id_sector_tecnico' not in extra_fields:
            # Obtener un sector por defecto o crear uno si no existe
            from .models import Sector
            sector_default, created = Sector.objects.get_or_create(
                id_sector_tecnico=1,
                defaults={
                    'nombre_sector': 'Administración',
                    'activo_sector': True
                }
            )
            extra_fields['id_sector_tecnico'] = sector_default
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser debe tener is_superuser=True.')
        
        return self.create_user(correo_tecnico, password, **extra_fields)

class Sector(models.Model):
    id_sector_tecnico = models.AutoField(primary_key=True)
    nombre_sector = models.CharField(max_length=200)
    activo_sector = models.BooleanField(default=True)
    
    def __str__(self):
        return self.nombre_sector
    
    class Meta:
        db_table = 'sector_tecnico'
        verbose_name = 'Sector'
        verbose_name_plural = 'Sectores'

class UsuarioTecnico(AbstractBaseUser, PermissionsMixin):
    id_usuario_tecnico = models.AutoField(primary_key=True)
    nombre_tecnico = models.CharField(max_length=100)
    correo_tecnico = models.EmailField(max_length=150, unique=True)
    id_sector_tecnico = models.ForeignKey(Sector, on_delete=models.PROTECT, db_column='id_sector_tecnico', default=1)  # Valor por defecto
    fecha_creacion = models.DateTimeField(default=timezone.now)
    activo_tecnico = models.BooleanField(default=True)
    
    # Campos requeridos para el modelo de usuario personalizado
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True, blank=True)
    
    objects = UsuarioTecnicoManager()
    
    USERNAME_FIELD = 'correo_tecnico'
    REQUIRED_FIELDS = ['nombre_tecnico']  # Solo nombre_tecnico, no id_sector_tecnico
    
    def __str__(self):
        return f"{self.nombre_tecnico} - {self.id_sector_tecnico.nombre_sector}"
    
    def get_full_name(self):
        return self.nombre_tecnico
    
    def get_short_name(self):
        return self.nombre_tecnico
    
    @property
    def is_active(self):
        return self.activo_tecnico
    
    def display_completo(self):
        return f"{self.nombre_tecnico} - {self.correo_tecnico} ({self.id_sector_tecnico.nombre_sector})"
    
    class Meta:
        db_table = 'usuario_tecnico'
        verbose_name = 'Técnico'
        verbose_name_plural = 'Técnicos'
        ordering = ['nombre_tecnico']