from django.db import models
from usuarios.models import UsuarioTecnico

class EquiposWarehouse(models.Model):
    id_equipos_warehouse = models.AutoField(primary_key=True)
    modelo_equipos_warehouse = models.CharField(max_length=100)
    serial_equipos_warehouse = models.CharField(max_length=100, blank=True, null=True)
    activo_equipos_warehouse = models.BooleanField(default=True)
    hash_teorico = models.CharField(max_length=50, blank=True, null=True)
    
    # Nuevos campos para la ficha técnica (asegúrate que existan en tu DB o manéjalos con cuidado)
    # Si no existen en la DB, Django los ignorará al leer si usas managed=False, 
    # pero si intentas acceder y no están, dará error.
    # Asumo que existen por tu solicitud anterior.
    mac_equipos_warehouse = models.CharField(max_length=50, blank=True, null=True)
    firmware_equipos_warehouse = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.modelo_equipos_warehouse} - {self.serial_equipos_warehouse}"
    
    class Meta:
        db_table = 'equipos_warehouse'
        managed = False

class Ubicacion(models.Model):
    id_ubicacion = models.AutoField(primary_key=True)
    nombre_ubicacion = models.CharField(max_length=255)
    activo_ubicacion = models.BooleanField(default=True)
    id_tipo_sistema = models.IntegerField(blank=True, null=True)
    
    def __str__(self):
        return self.nombre_ubicacion
    
    class Meta:
        db_table = 'ubicacion'
        managed = False

class UbicacionWarehouse(models.Model):
    id_ubicacion_warehouse = models.AutoField(primary_key=True)
    id_ubicacion = models.ForeignKey(Ubicacion, models.DO_NOTHING, db_column='id_ubicacion')
    rack = models.CharField(max_length=50)
    fila = models.CharField(max_length=50)
    columna = models.CharField(max_length=50)
    activo_ubicacion_warehouse = models.BooleanField(default=True)

    class Meta:
        db_table = 'ubicacion_warehouse'
        managed = False

class AsignacionUbicacionWarehouse(models.Model):
    id_asignacion = models.AutoField(primary_key=True)
    id_equipos_warehouse = models.ForeignKey(EquiposWarehouse, models.DO_NOTHING, db_column='id_equipos_warehouse')
    id_ubicacion_warehouse = models.ForeignKey(UbicacionWarehouse, models.DO_NOTHING, db_column='id_ubicacion_warehouse')
    fecha_asignacion = models.DateTimeField(auto_now_add=True)
    fecha_desasignacion = models.DateTimeField(blank=True, null=True)
    activo_asignacion_equipo_ubicacion = models.BooleanField(default=True)
    observaciones = models.TextField(blank=True, null=True)

    class Meta:
        # CORRECCIÓN IMPORTANTE: Nombre real de tu tabla en PostgreSQL
        db_table = 'asignacion_equipo_ubicacion'
        managed = False

class TipoProblema(models.Model):
    id_tipo_problema = models.AutoField(primary_key=True)
    nombre_problema = models.CharField(max_length=200)
    descripcion_problema = models.CharField(max_length=200, blank=True, null=True)
    problema_activo = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'tipo_problema'
        managed = False