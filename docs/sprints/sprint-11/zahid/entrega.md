# Entrega técnica del Sprint 11 de Zahid

Se desarrolló y ejecutó la parte de Zahid de PBL-39 y PBL-49. Se conservaron
ocho casos nominados, cinco capturas de la sesión PWA, salidas reales de
Terraform y reportes originales JMeter. El responsable de revisión es Jesús;
su aprobación no se ha registrado. No se creó un PR ni se modificaron work items.

## Resultados

| Comprobación | Resultado observado |
|---|---|
| CP-S11-IAC-01 a 04 | Cuatro casos aprobados técnicamente con Terraform/Docker reales |
| CP-S11-SIT-03 | PWA con dos cuentas, red desconectada, cierre local y CacheStorage verificados |
| CP-S11-PERF-01 | 2922 muestras; 0 errores; p95 228 ms; 10 usuarios |
| CP-S11-PERF-02 | 1226 muestras; 0 errores; p95 426 ms; pico de 20 y recuperación a 5 |
| CP-S11-PERF-03 | 510 escrituras aceptadas y persistidas; 0 errores; p95 52 ms; IDs y sumas concordantes |
| Regresión API | 162 pruebas aprobadas, XML disponible |
| Controles del ejecutor | 3 pruebas aprobadas, XML disponible |
| Render remoto | HTTPS: salud, readiness y raíz 200; pacientes sin token 401 |

Los percentiles JSON se calculan por rango más próximo; JMeter interpola sus
decimales y presenta además login en su fila total. El rendimiento se midió
en QA local, no en el servicio Render. Sus objetivos son los propuestos en Azure
y siguen pendientes de ratificación humana. Los reportes no almacenan tokens.

## Estado por tarea

| Tarea | Entrega | Condición de cierre |
|---|---|---|
| PBL-39-T1 #504 | Inventario del repositorio y runbook Render | Contrastar configuración real del panel |
| PBL-39-T2 #505 | Blueprint, inicio existente y readiness documentados | Ejecutar y evidenciar un nuevo despliegue autorizado en Render |
| PBL-39-T3 #506 | Smoke HTTPS y guía de recuperación | Vincular logs, SHA y resultado del redepliegue remoto |
| PBL-39-T4 #591 | Ciclo de vida Terraform, scripts y cuatro casos reales | Revisión cruzada de Jesús |
| PBL-39-T5 #592 | Tres casos JMeter y caso PWA; documentos y capturas | Ratificar objetivos y revisar evidencia |
| PBL-49-T1 #545 | Escenarios, concurrencia, duración y objetivos propuestos | Ratificación del equipo |
| PBL-49-T2 #546 | JMX versionados, datos y guardas de resultados vacíos | Revisión de código |
| PBL-49-T3 #547 | Ejecución no gráfica, JTL y tres dashboards HTML | Revisión de resultados |
| PBL-49-T4 #548 | Correcciones, repruebas y conciliación MongoDB | Aceptación del responsable de calidad |

## Límites y pendientes concretos

La gestión de Render no estaba conectada. No se presume la rama, el SHA ni
variables del servicio existente y no se afirmó haber recreado su despliegue.
El blueprint quedó preparado con auto-deploy desactivado. Instalar y conectar
Render permite completar la verificación administrativa y el redepliegue.

La auditoría del árbol heredado del frontend registró siete alertas altas
relacionadas con picomatch y la cadena Vite/Vitest. El JSON original se conserva;
los arreglos sugeridos implican cambios mayores/downgrades fuera de estas dos
historias. Requieren tratamiento o excepción expresa para el gate del equipo.
No se aprobaron UAT/OAT, reuniones ni firmas en nombre de personas ausentes.

## Evidencia y reproducción

Los diez Word están en este directorio. El informe reúne resultados e incidencias;
el índice de anexos enumera capturas. Los originales están en
evidence/sprint-11/zahid y el manifiesto verifica su integridad. Los fallos
iniciales se conservaron en attempts/ junto con las repruebas actuales.
La preparación y ejecución se documentaron en qa/sprint-11/README.md.
El workflow manual sprint11-zahid.yml quedó preparado, sin atribuirle una
ejecución en GitHub Actions que no ocurrió. Los recursos Docker desechables
se limpiaron al concluir; se conservan sus registros de limpieza.
