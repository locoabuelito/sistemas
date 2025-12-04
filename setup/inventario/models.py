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

class UbicacionDeposito(models.Model):
    id_ubicacion_deposito = models.AutoField(primary_key=True)
    
    nombre_pallet = models.CharField(max_length=100)
    nombre_caja = models.CharField(max_length=100)
    ubicacion_activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'ubicacion_deposito'
        managed = False 

    def __str__(self):
        sistema = self.id_tipo_sistema.nombre_sistema if self.id_tipo_sistema else "N/A"
        return f"{sistema} - P:{self.nombre_pallet} - C:{self.nombre_caja}"

# 2️⃣ ACTUALIZACIÓN DE LA CLASE EQUIPOS
class Equipos(models.Model):
    id_equipos = models.AutoField(primary_key=True)
    objeto = models.CharField(max_length=200)
    marca = models.CharField(max_length=100)
    modelo = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=100, unique=True)
    
    id_tipo_sistema = models.ForeignKey(
        'TipoSistema', 
        on_delete=models.DO_NOTHING,
        db_column='id_tipo_sistema',
        null=True, blank=True
    )
    
    stock_min = models.IntegerField(db_column='stock_min', null=True, blank=True)
    id_usuario_tecnico = models.IntegerField(db_column='id_usuario_tecnico', null=True, blank=True)
    
    # ⭐ CAMBIO AQUÍ: Ahora es ForeignKey en lugar de IntegerField
    id_ubicacion_deposito = models.ForeignKey(
        UbicacionDeposito,
        on_delete=models.DO_NOTHING,
        db_column='id_ubicacion_deposito',
        null=True,
        blank=True
    )

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activo_equipos = models.BooleanField(default=True)

    class Meta:
        db_table = 'equipos'
        managed = False

    def __str__(self):
        return f"{self.objeto} - {self.serial_number}"