from django.db import models
from django.utils import timezone

# Importación de modelos externos (asegúrate de que la ruta sea correcta)
from usuarios.models import UsuarioTecnico

# ==============================================================================
# BLOQUE 1: CATÁLOGOS Y TABLAS MAESTRAS
# Tablas que sirven de referencia para seleccionar opciones (Dropdowns/Selects)
# ==============================================================================

class TipoProblema(models.Model):
    """
    Catálogo de los posibles fallos o problemas que pueden presentar los equipos.
    Ej: 'Falla de Fuente', 'Hashboard dañado', etc.
    """
    id_tipo_problema = models.AutoField(primary_key=True)
    nombre_problema = models.CharField(max_length=200)
    descripcion_problema = models.CharField(max_length=200, blank=True, null=True)
    problema_activo = models.BooleanField(default=True)
    
    def __str__(self):
        return self.nombre_problema

    class Meta:
        db_table = 'tipo_problema'
        managed = False  # Tabla existente en PostgreSQL


class Ubicacion(models.Model):
    """
    Define las áreas generales o almacenes.
    Ej: 'Almacén Principal', 'Laboratorio', 'Despacho'.
    """
    id_ubicacion = models.AutoField(primary_key=True)
    nombre_ubicacion = models.CharField(max_length=255)
    activo_ubicacion = models.BooleanField(default=True)
    id_tipo_sistema = models.IntegerField(blank=True, null=True)
    
    def __str__(self):
        return self.nombre_ubicacion
    
    class Meta:
        db_table = 'ubicacion'
        managed = False


# ==============================================================================
# BLOQUE 2: ACTIVOS Y HARDWARE
# Información técnica de los equipos físicos.
# ==============================================================================

class EquiposWarehouse(models.Model):
    """
    Inventario principal de equipos.
    Contiene la identificación única (Serial, MAC) y datos técnicos.
    """
    id_equipos_warehouse = models.AutoField(primary_key=True)
    modelo_equipos_warehouse = models.CharField(max_length=100)
    serial_equipos_warehouse = models.CharField(max_length=100, blank=True, null=True)
    
    # Estado general del activo en el sistema (no confundir con estado de reparación)
    activo_equipos_warehouse = models.BooleanField(default=True)
    
    # Datos técnicos específicos
    hash_teorico = models.CharField(max_length=50, blank=True, null=True)
    mac_equipos_warehouse = models.CharField(max_length=50, blank=True, null=True)
    firmware_equipos_warehouse = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.modelo_equipos_warehouse} - {self.serial_equipos_warehouse}"
    
    class Meta:
        db_table = 'equipos_warehouse'
        managed = False


# ==============================================================================
# BLOQUE 3: LOGÍSTICA Y UBICACIÓN FÍSICA
# Gestión detallada de coordenadas (Racks) y asignaciones históricas.
# ==============================================================================

class UbicacionWarehouse(models.Model):
    """
    Coordenadas específicas dentro de una Ubicación general.
    Ej: Rack A, Fila 1, Columna 2 dentro del 'Almacén Principal'.
    """
    id_ubicacion_warehouse = models.AutoField(primary_key=True)
    # Relación con la ubicación general
    id_ubicacion = models.ForeignKey(Ubicacion, models.DO_NOTHING, db_column='id_ubicacion')
    
    rack = models.CharField(max_length=50)
    fila = models.CharField(max_length=50)
    columna = models.CharField(max_length=50)
    activo_ubicacion_warehouse = models.BooleanField(default=True)

    def __str__(self):
        return f"Rack: {self.rack} | F: {self.fila} - C: {self.columna}"

    class Meta:
        db_table = 'ubicacion_warehouse'
        managed = False


class AsignacionUbicacionWarehouse(models.Model):
    """
    Tabla intermedia (Historial de movimientos).
    Registra qué equipo está en qué coordenada y cuándo se movió.
    """
    id_asignacion = models.AutoField(primary_key=True)
    
    # Relaciones
    id_equipos_warehouse = models.ForeignKey(EquiposWarehouse, models.DO_NOTHING, db_column='id_equipos_warehouse')
    id_ubicacion_warehouse = models.ForeignKey(UbicacionWarehouse, models.DO_NOTHING, db_column='id_ubicacion_warehouse')
    
    # Trazabilidad temporal
    fecha_asignacion = models.DateTimeField(auto_now_add=True)
    fecha_desasignacion = models.DateTimeField(blank=True, null=True)
    
    # Indica si es la ubicación actual
    activo_asignacion_equipo_ubicacion = models.BooleanField(default=True)
    observaciones = models.TextField(blank=True, null=True)

    class Meta:
        # Nota: Corresponde al nombre real de la tabla en PostgreSQL
        db_table = 'asignacion_equipo_ubicacion'
        managed = False


# ==============================================================================
# BLOQUE 4: GESTIÓN DE REPARACIONES (PROCESO PRINCIPAL)
# CRUD principal para el flujo de trabajo de los técnicos.
# ==============================================================================

class SolicitudReparacion(models.Model):
    """
    Ticket o Ficha de entrada al taller.
    Vincula un equipo, un técnico y un tipo de problema reportado.
    """
    id_solicitud = models.AutoField(primary_key=True)
    
    # Relaciones (Foreign Keys con mapeo explícito a columnas de BD)
    equipo = models.ForeignKey(EquiposWarehouse, models.DO_NOTHING, db_column='id_equipos_warehouse')
    tecnico = models.ForeignKey(UsuarioTecnico, models.DO_NOTHING, db_column='id_usuario_tecnico')
    tipo_problema = models.ForeignKey(TipoProblema, models.DO_NOTHING, db_column='id_tipo_problema')
    
    # Datos operativos del formulario
    th_cantidad = models.FloatField(help_text="Terahash reportado o medido")
    descripcion = models.TextField(help_text="Detalle adicional de la falla")
    estado = models.CharField(max_length=20, default='pendiente') # Ej: pendiente, en_proceso, finalizado
    
    # Trazabilidad
    fecha_creacion = models.DateTimeField(default=timezone.now)
    
    # Soft Delete (Borrado lógico para no perder historial)
    solicitud_activa = models.BooleanField(default=True)

    def __str__(self):
        return f"Solicitud #{self.id_solicitud} - {self.equipo.serial_equipos_warehouse}"

    class Meta:
        db_table = 'solicitud_reparacion'
        managed = False