# PBL-26-T5 — Validación del ambiente sintético

**Responsable:** Jaime Díaz González  
**Sprint:** 7 (Sprint 1 del PBL)  
**Base validada:** `main` después de las PR #34 y #36

## Procedimiento

Se ejecutó la suite completa de `backend/api_hospital` usando la configuración de prueba versionada. Las pruebas trabajan con `mongomock`, semillas sintéticas y limpieza entre casos; no consultan expedientes clínicos reales.

```bash
pytest -q
```

## Resultado observado

- 82 pruebas aprobadas.
- 7 pruebas omitidas porque requieren iniciar el motor Spark real; su ejecución está cubierta por el workflow de integración Spark.
- 0 errores de colección.
- 0 pruebas fallidas.

También se verificó la aplicación web:

```bash
npm test -- --run
npm run lint
npm run build
```

- 38 pruebas web aprobadas, incluidas 3 validaciones específicas de Jaime.
- Lint aprobado.
- Compilación de producción aprobada.

## Criterios de terminado

- Los datos utilizados son sintéticos y repetibles.
- Cada prueba recibe colecciones aisladas.
- La semilla incluye usuarios por rol y registros controlados.
- La rama no contiene copias duplicadas de fixtures, workflows o componentes.
- La evidencia corresponde a la versión actual de `main`, no a la rama antigua incompatible.

**Resultado:** PBL-26-T5 validado localmente y listo para revisión en pull request.
