# inventario/models.py - CORREGIDO
from django.db import models

class TipoSistema(models.Model):
    id_tipo_sistema = models.AutoField(primary_key=True)
    nombre_sistema = models.CharField(max_length=100)
    activo_sistema = models.BooleanField(default=True)  # ⭐ NOMBRE EXACTO

    class Meta:
        db_table = 'tipo_sistema'
        managed = False

    def __str__(self):
        return self.nombre_sistema

class Equipos(models.Model):
    id_equipos = models.AutoField(primary_key=True)
    objeto = models.CharField(max_length=200)
    marca = models.CharField(max_length=100)
    modelo = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=100, unique=True)
    cantidad_por_unidad = models.IntegerField(default=1)
    cantidad_por_cajas = models.IntegerField(default=0)
    id_tipo_sistema = models.ForeignKey(
        TipoSistema, 
        on_delete=models.CASCADE,
        db_column='id_tipo_sistema',
        null=True,
        blank=True
    )
    fecha_creacion = models.DateTimeField()
    activo_equipos = models.BooleanField(default=True)

    class Meta:
        db_table = 'equipos'
        managed = False

    def __str__(self):
        return f"{self.objeto} - {self.serial_number}"