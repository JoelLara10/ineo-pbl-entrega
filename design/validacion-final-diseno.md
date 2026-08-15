# Validación final de diseño — INEO (clinica-web-react)

**Proyecto:** INEO / clinica-web-react  
**Tipo de documento:** Cierre de diseño de interfaz  
**Fecha de referencia:** Agosto 2026  
**Alcance:** Toda la aplicación web (módulos de producto + sistema visual)

---

## 1. Objetivo

Validar que el diseño de la aplicación está **completo, coherente y listo para implementación / evidencia de sprint**, cubriendo:

1. Identidad visual y consistencia entre módulos  
2. Pantallas y flujos principales  
3. Responsive  
4. Accesibilidad básica (WCAG A/AA aplicable)  
5. Internacionalización (ES / EN)  
6. Evidencias (mockups, capturas, documentos)

Este documento **consolida** los entregables de diseño y define el **criterio de cierre** global.

---

## 2. Mapa de módulos de diseño

| Módulo | Rol en la UI | Evidencias principales |
|--------|--------------|------------------------|
| **Autenticación / Layout** | Login, sidebar, shell | Diseño del layout del proyecto |
| **Administrativo** | Pacientes, alta, detalle, censo | Mockups + responsive pacientes |
| **Enfermería** | Panel camas, signos, valoración, balance | Mockups + responsive enfermería |
| **Médico** | Panel áreas, detalle clínico | Capturas médico |
| **Estudios** | Solicitudes / resultados lab y gabinete | Capturas estudios |
| **Configuración** | Camas, usuarios, catálogos, backup, perfil | Capturas configuración |
| **Spark** | Dashboard y análisis de datos | Capturas Spark |
| **Sistema visual** | Idiomas, tokens de color/comportamiento | Validación de idiomas |

---

## 3. Inventario de entregables de diseño

### 3.1 Mockups (propuesta / wire visual simple)

| Ruta | Descripción | Estado |
|------|-------------|--------|
| `design/mockups/pacientes-listado.png` | Listado de pacientes | ☐ |
| `design/mockups/paciente-alta.png` | Alta / edición de paciente | ☐ |
| `design/mockups/paciente-detalle.png` | Cuenta / detalle administrativo | ☐ |
| `design/mockups/censo.png` | Censo hospitalario | ☐ |
| `design/mockups/enfermeria-panel.png` | Panel de enfermería | ☐ |
| `design/mockups/enfermeria-signos.png` | Signos vitales | ☐ |
| `design/mockups/enfermeria-valoracion.png` | Valoración de enfermería | ☐ |
| `design/mockups/enfermeria-balance.png` | Balance hídrico | ☐ |

> HTML de apoyo generados: `mockups-ineo.html`, `mockups-enfermeria.html` (colorimetría verde para propuesta).

### 3.2 Capturas (diseño real del proyecto)

| Ruta | Descripción | Estado |
|------|-------------|--------|
| `design/capturas/medico/` | Panel médico y detalle | ☐ |
| `design/capturas/estudios/` | Gestión de estudios | ☐ |
| `design/capturas/configuracion/` | Panel de configuración | ☐ |
| `design/capturas/spark/` | Dashboard y análisis Spark | ☐ |

> HTML de apoyo: `capturas-modulos.html`, `capturas-spark.html` (estilo azul/púrpura del sistema).

### 3.3 Documentos de diseño

| Ruta | Contenido | Estado |
|------|-----------|--------|
| `design/responsive/pacientes-responsive.md` | Responsive módulo pacientes | ☐ |
| `design/responsive/enfermeria-responsive.md` | Responsive módulo enfermería | ☐ |
| `design/responsive/validacion-final.md` | Validación responsive global | ☐ |
| `design/accesibilidad/checklist.md` | Checklist WCAG aplicable | ☐ |
| `design/sistema-visual/validacion-idiomas.md` | Validación ES / EN | ☐ |
| `design/validacion-final-diseno.md` | Este documento (cierre global) | ☐ |

---

## 4. Criterios de validación por dimensión

### 4.1 Consistencia visual

- [ ] Headers de módulo con jerarquía clara (eyebrow + título + acciones)
- [ ] Cards, badges y botones con el mismo lenguaje visual dentro de cada familia (admin / clínico / spark)
- [ ] Estados distinguibles: ocupada/libre, listo/pendiente, error/éxito
- [ ] Color de acento del sistema (`#667eea` / gradientes clínico) usado de forma coherente
- [ ] Mockups de propuesta (verde) no se mezclan como “UI final” en capturas de producto

**Notas de diseño del producto actual:**

| Familia | Referencia visual |
|---------|-------------------|
| Clínico (médico / enfermería / estudios) | Gradiente azul → púrpura en headers |
| Administrativo | Paneles blancos, stats con borde de acento, tablas |
| Spark | `Spark.css`: acento `#667eea`, cards, data-grid, toolbar |

### 4.2 Cobertura de pantallas críticas

| Flujo | Cubierto en diseño | Evidencia |
|-------|--------------------|-----------|
| Login / acceso | ☐ | |
| Navegación lateral por módulos | ☐ | |
| CRUD / listado pacientes | ☐ | Mockups admin |
| Registro de signos / valoración / balance | ☐ | Mockups enfermería |
| Atención médica (panel + detalle) | ☐ | Capturas médico |
| Ciclo de estudios (solicitud → resultado) | ☐ | Capturas estudios |
| Configuración del sistema | ☐ | Capturas config |
| Análisis Spark (dashboard + run + resultados) | ☐ | Capturas Spark |

### 4.3 Responsive

Validado según `design/responsive/validacion-final.md`:

- [ ] Mobile `< 720px` usable en flujos principales  
- [ ] Tablet y desktop sin roturas de layout  
- [ ] Tablas/listas adaptadas (cards o scroll controlado)  
- [ ] Formularios en una columna en móvil  
- [ ] Spark: toolbar y data-grid adaptables (`Spark.css` ≤700px)

### 4.4 Accesibilidad

Validado según `design/accesibilidad/checklist.md`:

- [ ] Labels en formularios principales  
- [ ] Operación por teclado de acciones críticas  
- [ ] Contraste de textos de UI principales (AA)  
- [ ] Estados no transmitidos solo por color  
- [ ] Iconos de acción con nombre accesible  

### 4.5 Idiomas (ES / EN)

Validado según `design/sistema-visual/validacion-idiomas.md`:

- [ ] Claves i18n en pantallas de diseño entregadas  
- [ ] Cambio de idioma persistente (`@ineo_lang`)  
- [ ] Paridad ES/EN en menús, botones y títulos de módulo  

---

## 5. Matriz de cierre (resumen ejecutivo)

| Dimensión | Documento de detalle | Resultado | Responsable diseño | Fecha |
|-----------|----------------------|-----------|--------------------|-------|
| Mockups admin | `design/mockups/*` | ☐ OK / ☐ Con hallazgos | | |
| Mockups enfermería | `design/mockups/enfermeria-*` | ☐ OK / ☐ Con hallazgos | | |
| Capturas médico / estudios / config | `design/capturas/*` | ☐ OK / ☐ Con hallazgos | | |
| Capturas Spark | `design/capturas/spark/` | ☐ OK / ☐ Con hallazgos | | |
| Responsive global | `design/responsive/validacion-final.md` | ☐ OK / ☐ Con hallazgos | | |
| Accesibilidad | `design/accesibilidad/checklist.md` | ☐ OK / ☐ Con hallazgos | | |
| Idiomas | `design/sistema-visual/validacion-idiomas.md` | ☐ OK / ☐ Con hallazgos | | |

---

## 6. Hallazgos globales abiertos

Registrar solo ítems que afectan el **cierre de diseño** (no bugs de backend).

| ID | Dimensión | Descripción | Severidad | Estado |
|----|-----------|-------------|-----------|--------|
| D-01 | | | Alta / Media / Baja | Abierto / Resuelto |
| D-02 | | | | |

**Severidad orientativa:**

- **Alta:** Impide usar un flujo principal o incumple un requisito de entrega del sprint  
- **Media:** Inconsistencia visible o deuda de responsive/a11y en pantalla secundaria  
- **Baja:** Pulido visual, copy o mejora opcional  

---

## 7. Criterio de aceptación final de diseño

El diseño de la aplicación se considera **validado y cerrado para el alcance del sprint** cuando se cumplen **todas** las condiciones:

1. **Inventario completo:** mockups y capturas de la sección 3 existen en el repositorio (o PR de diseño).  
2. **Sin hallazgos Alta** abiertos en la sección 6.  
3. **Responsive:** `validacion-final.md` marcado como OK o solo con hallazgos Media/Baja documentados.  
4. **Accesibilidad:** checklist sin bloqueantes (labels + teclado + contraste crítico).  
5. **Idiomas:** validación ES/EN realizada al menos en un muestreo de módulos (admin, clínico, spark).  
6. **Coherencia:** las capturas de producto reflejan el diseño implementado (no solo mockups de propuesta).  

---

## 8. Recomendaciones posteriores al cierre

1. Unificar tokens (colores, radios, sombras) en CSS compartido para reducir estilos inline por pantalla.  
2. Extraer patrones comunes: header de módulo, patient card, data toolbar, empty state.  
3. Mantener mockups (propuesta) separados de capturas (producto) en carpetas distintas.  
4. Actualizar este documento si se agregan módulos nuevos (p. ej. más pantallas Spark o reportes).  

---

## 9. Firmas / evidencia de revisión

| Rol | Nombre | Resultado | Fecha |
|-----|--------|-----------|-------|
| Diseño / UX (entrega) | | ☐ Aprobado · ☐ Aprobado con observaciones | |
| Desarrollo frontend | | ☐ Revisado | |
| Producto / lead de proyecto | | ☐ Aceptado | |

---

## 10. Referencias rápidas

| Tema | Ruta |
|------|------|
| Responsive pacientes | `design/responsive/pacientes-responsive.md` |
| Responsive enfermería | `design/responsive/enfermeria-responsive.md` |
| Responsive global | `design/responsive/validacion-final.md` |
| Accesibilidad | `design/accesibilidad/checklist.md` |
| Idiomas | `design/sistema-visual/validacion-idiomas.md` |
| Capturas Spark | `design/capturas/spark/` |
| Código UI Spark | `src/pages/spark/Spark.css`, `SparkDashboard.jsx`, `SparkAnalysisScreen.jsx` |
| i18n | `src/i18n/index.js`, `src/i18n/locales/es.json`, `en.json` |

---

**Archivo:** `design/validacion-final-diseno.md`  
**Uso:** Cierre formal del diseño de toda la aplicación para el repositorio de entrega (ineo-pbl-entrega / clinica-web-react).
