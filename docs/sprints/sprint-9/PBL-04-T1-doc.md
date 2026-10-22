# PBL-04 — Análisis técnico de estados vacíos y errores accionables

## 1. Objetivo

Garantizar que el módulo de Analytics de INEO informe claramente al administrador cuando un análisis no se ha ejecutado, no existen datos, hay un problema de conexión, el análisis continúa procesándose o la ejecución ha fallado.

## 2. Alcance

- Analytics general.
- Analytics MET.
- Analytics clínico.
- Analytics no supervisado.
- Consulta de resultados, ejecución y consulta del estado.
- Mensajes de error, acciones de recuperación y pruebas de regresión.

## 3. Archivos identificados

- `frontend/clinica-web-react/src/pages/spark/SparkAnalysisScreen.jsx`: presentación de estados y acciones.
- `frontend/clinica-web-react/src/services/sparkService.js`: solicitudes HTTP para resultados, ejecución y estado.
- `frontend/clinica-web-react/src/i18n/locales/es.json`: mensajes en español.
- `frontend/clinica-web-react/src/pages/spark/Spark.css`: presentación visual de los estados.
- `frontend/clinica-web-react/src/pages/spark/SparkAnalysisScreen.test.jsx`: pruebas funcionales del componente.
- `docs/manual-tecnico/spark.md`: documentación técnica de la integración.

## 4. Dependencias

- React y React Router.
- react-i18next.
- Servicio HTTP del frontend.
- API de Analytics.
- Servicios de procesamiento y almacenamiento de resultados.
- Vitest y React Testing Library para pruebas.

## 5. Casos límite

1. El análisis todavía no se ha ejecutado.
2. La ejecución terminó sin resultados.
3. La API no responde o la conexión falla.
4. La consulta de resultados falla, pero la consulta de estado responde.
5. El análisis permanece en ejecución.
6. El servidor informa que la ejecución falló.
7. El usuario intenta ejecutar dos veces la misma operación.
8. El resultado contiene datos vacíos o estructuras incompletas.
9. Una respuesta de error no debe presentarse como una consulta exitosa.
10. Los resultados anteriores no deben eliminarse innecesariamente al fallar una actualización.

## 6. Criterios de aceptación

- Cada estado se distingue visualmente y mediante un mensaje claro.
- Cada estado ofrece una acción de recuperación adecuada cuando corresponda.
- Las operaciones en curso no se duplican.
- Los cuatro tipos de Analytics conservan su funcionamiento.
- Las gráficas incluyen título, etiquetas, valores, unidades, leyenda y periodo cuando corresponda.
- Las pruebas funcionales y de regresión quedan documentadas.
- No se modifican funciones ajenas al alcance.

## 7. Riesgos y bloqueos

La implementación del frontend no acredita por sí sola que la API permita ejecutar y consultar los cuatro tipos de Analytics. Se debe verificar la existencia, el contrato, la autorización y el funcionamiento de cada endpoint antes de aprobar la integración completa.

## 8. Evidencia requerida

- Diferencias de código revisadas.
- Resultados de lint y compilación.
- Pruebas funcionales y de regresión.
- Evidencias de ejecución en el entorno de pruebas.
- Pull Request revisado e integrado conforme al flujo de ramas del equipo.

## 9. Definición de terminado

La tarea se considera terminada cuando el análisis está documentado, se identificaron los archivos y dependencias reales y se establecieron los casos límite y las pruebas de aceptación.