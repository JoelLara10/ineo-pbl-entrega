# PBL-21-T2 — Implementación: unificar diseño de Valoración de Enfermería

**Sistema:** Sistema de Gestión Clínica INEO  
**Historia:** PBL-21 — Valoración de Enfermería con el mismo diseño que los demás formularios  
**Tarea:** T2 — Programar unificación visual (encabezado, secciones, campos, botones, espaciado y móvil)  
**Rama:** `sprints/jaime-sprint-7`  
**Fecha:** 2026-10-04  
**Responsable:** Jaime Díaz González  

---

## 1. Objetivo

Aplicar el **patrón visual aprobado de enfermería** (el de Signos Vitales / Nota de Enfermería) a la pantalla de **Valoración de Enfermería**, sin modificar la lógica de negocio, endpoints ni validaciones.

---

## 2. Criterio de aceptación

> Conserva todas sus funciones y validaciones; visualmente sigue el patrón aprobado de enfermería.

| Requisito | Cómo se cumple |
|---|---|
| Conservar funciones | Mismos campos, mismo `GET/POST .../nursing-assessment`, mismos alerts |
| Conservar validaciones | Sin paciente no se envía; botones deshabilitados si no hay atención |
| Patrón visual | Header, patient card, form con labels, footer de acciones, historial en cards |

---

## 3. Archivos modificados

| Archivo | Cambio |
|---|---|
| `frontend/clinica-web-react/src/pages/enfermeria/EnfermeriaAssessmentScreen.jsx` | UI unificada al patrón de enfermería |
| `frontend/clinica-web-react/src/i18n/locales/es.json` | Claves `newRecord`, `selectPatientFirst`, `records`, `loadingHistory` |
| `frontend/clinica-web-react/src/i18n/locales/en.json` | Mismas claves en inglés |

**No se modificó:** backend, rutas, servicios API, permisos, campos del payload.

---

## 4. Qué se unificó (UI)

1. **Encabezado:** gradiente azul–morado, botón volver, eyebrow “ENFERMERÍA”, título.
2. **Tarjeta de paciente:** avatar, nombre de sección y meta (Exp / Atención).
3. **Formulario:** título “Nueva valoración”, campos con **label + input**, textarea de observaciones.
4. **Botones:** Recargar (secundario) y Guardar (primario con gradiente).
5. **Historial:** cards con fecha, métricas en grid y observaciones.
6. **Espaciado / móvil:** padding de página, `grid` con `auto-fit` / `minmax` para apilar en pantallas estrechas.
7. **Footer:** mensaje INEO + icono de escudo.

---

## 5. Qué se conservó (lógica)

- Estado `formData`: `estado_general`, `dolor`, `movilidad`, `riesgo_caidas`, `riesgo_upp`, `observaciones`
- `loadHistory` → `GET /appointments/{idAtencion}/nursing-assessment`
- `handleSubmit` → `POST` con el mismo body
- Limpieza del formulario tras guardar
- `window.alert` de éxito / error
- Dependencia de `selectedPatient` / `location.state`

---

## 6. Definición de terminado

- [x] Cambio en la rama
- [x] Visual alineado al patrón de enfermería
- [x] Funciones y validaciones existentes conservadas
- [x] Listo para validación (T3)