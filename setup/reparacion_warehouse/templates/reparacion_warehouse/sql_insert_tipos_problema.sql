-- Script SQL para insertar tipos de problema iniciales
-- Ejecutar en PostgreSQL

INSERT INTO tipo_problema (nombre_problema, descripcion_problema, problema_activo) VALUES
('Falla de Hardware', 'Problemas relacionados con componentes físicos defectuosos', TRUE),
('Error de Software', 'Errores en el sistema operativo o aplicaciones de minería', TRUE),
('Problema de Red', 'Problemas de conectividad de red o comunicación', TRUE),
('Falla de Alimentación', 'Problemas con fuente de poder o suministro eléctrico', TRUE),
('Problema de Temperatura', 'Sobrecalentamiento de equipos o fallas térmicas', TRUE),
('Bajo Rendimiento', 'Rendimiento inferior al esperado sin causa aparente', TRUE),
('Problema de Conectividad', 'Fallas en la comunicación con la pool o servicios', TRUE),
('Falla en Sistema de Ventilación', 'Problemas con ventiladores o sistema de enfriamiento', TRUE),
('Otros', 'Problemas no categorizados en las opciones anteriores', TRUE);

-- Ver los tipos de problema insertados
SELECT * FROM tipo_problema ORDER BY id_tipo_problema;
