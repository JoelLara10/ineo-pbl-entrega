# Sprint 1 — Entrega de Joel

**Responsable:** Joel, Product Owner y desarrollador web  
**Alcance:** únicamente las historias asignadas a Joel en la hoja `PBL`.

## Historias atendidas

| Historia | Entrega | Estado |
| --- | --- | --- |
| PBL-01 | Panel Spark y cinco rutas protegidas: panel, Analytics, MET, clínico y no supervisado. | Implementada y cubierta por prueba estructural |
| PBL-03 | Flujo frontend de ejecución, consulta periódica, estados pendiente/procesando/completado/fallido y carga de resultados. | Frontend implementado; integración final depende de PBL-02 y PBL-13 |
| PBL-06 | Restauración del idioma, persistencia automática y utilidades comunes para fecha y cantidad en `es-MX` y `en-US`. | Implementada y cubierta por pruebas unitarias |

## Tareas realizadas

### PBL-01

- Verificar rutas y dependencias del módulo Spark.
- Confirmar acceso protegido por rol en el enrutador.
- Añadir una prueba que comprueba las cinco rutas requeridas.

### PBL-03

- Normalizar respuestas de estado aunque la API use `state`, `status`, `phase` o un objeto anidado.
- Mantener la consulta periódica mientras el análisis está pendiente o procesándose.
- Detener la consulta y mostrar un error seguro si falla la petición de estado.
- Cargar resultados al finalizar y tratar una respuesta 404 como ausencia de resultados.
- Mostrar explícitamente los estados pendiente, procesando, completado y fallido.

### PBL-06

- Normalizar los idiomas admitidos a `es` y `en`.
- Restaurar el idioma guardado al iniciar la aplicación.
- Guardar automáticamente cualquier cambio de idioma.
- Sincronizar el atributo `lang` del documento.
- Incorporar formateadores comunes para fechas y cantidades.

## Dependencia externa al trabajo de Joel

PBL-03 depende de PBL-02 y PBL-13, asignadas a Zahid. El repositorio todavía no contiene el blueprint ni el servicio backend de Spark; por eso el flujo frontend queda listo y probado, pero no debe declararse funcional de extremo a extremo hasta que esos endpoints estén disponibles.

## Verificación

Ejecutar desde `frontend/clinica-web-react`:

```bash
npm test
npm run lint
npm run build
```
