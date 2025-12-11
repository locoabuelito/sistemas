from django.db import models
from usuarios.models import UsuarioTecnico

class EquiposWarehouse(models.Model):
    id_equipos_warehouse = models.AutoField(primary_key=True)
    modelo_equipos_warehouse = models.CharField(max_length=200)
    ip_equipos_warehouse = models.CharField(max_length=15, blank=True, null=True)
    mac_equipos_warehouse = models.CharField(max_length=17, blank=True, null=True)
    serial_equipos_warehouse = models.CharField(max_length=100, blank=True, null=True)
    activo_equipos_warehouse = models.BooleanField(default=True)
    ubicacion_warehouse = models.CharField(max_length=100, blank=True, null=True)
    firmware_equipos_warehouse = models.CharField(max_length=100, blank=True, null=True)
    software_equipos_warehouse = models.CharField(max_length=100, blank=True, null=True)
    hardware_equipos_warehouse = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return f"{self.modelo_equipos_warehouse} - {self.serial_equipos_warehouse or 'Sin Serial'}"
    
    class Meta:
        db_table = 'equipos_warehouse'
        verbose_name = 'Equipo Warehouse'
        verbose_name_plural = 'Equipos Warehouse'

class Ubicacion(models.Model):
    id_ubicacion = models.AutoField(primary_key=True)
    nombre_ubicacion = models.CharField(max_length=200)
    activo_ubicacion = models.BooleanField(default=True)
    id_tipo_sistema = models.IntegerField(default=2)
    
    def __str__(self):
        return self.nombre_ubicacion
    
    class Meta:
        db_table = 'ubicacion'
        managed = False
        verbose_name = 'Ubicación'
        verbose_name_plural = 'Ubicaciones'

class TipoProblema(models.Model):
    id_tipo_problema = models.AutoField(primary_key=True)
    nombre_problema = models.CharField(max_length=200)
    descripcion_problema = models.CharField(max_length=200, blank=True, null=True)
    problema_activo = models.BooleanField(default=True)
    
    def __str__(self):
        return self.nombre_problema
    
    class Meta:
        db_table = 'tipo_problema'
        managed = False
        verbose_name = 'Tipo de Problema'
        verbose_name_plural = 'Tipos de Problemas'
        