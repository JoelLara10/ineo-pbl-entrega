# Checklist de accesibilidad — INEO

**Proyecto:** clinica-web-react  
**Referencia:** WCAG 2.2 nivel **A / AA** (prácticas aplicables a SPA clínica)  
**Alcance:** UI web de módulos administrativos, clínicos, estudios, configuración y Spark

---

## 1. Principios

| Principio | Qué validamos |
|-----------|----------------|
| **Perceptible** | Texto, contraste, alternativas a no-texto |
| **Operable** | Teclado, focos, targets táctiles, sin trampas de foco |
| **Comprensible** | Labels, mensajes de error, idioma de página |
| **Robusto** | Roles/semántica, compatibilidad con AT básicas |

---

## 2. Checklist general (todos los módulos)

### 2.1 Estructura y semántica

- [ ] Uso de encabezados jerárquicos (`h1` → `h2` → `h3`) sin saltos arbitrarios
- [ ] Landmarks principales: `main`, navegación (sidebar), si aplica `header`/`footer`
- [ ] Botones son `<button>` (no solo `div`/`span` con click)
- [ ] Enlaces son `<a>` cuando navegan; botones cuando ejecutan acción
- [ ] Tablas con `<th>` y alcance claro (o cards equivalentes en móvil)

### 2.2 Teclado y foco

- [ ] Toda acción principal operable solo con teclado (Tab / Shift+Tab / Enter / Espacio)
- [ ] Orden de tabulación lógico (no salta de forma confusa)
- [ ] Foco visible en controles interactivos
- [ ] No hay trampas de foco en modales/drawers (Esc o botón cierra y devuelve foco)
- [ ] Skip link opcional al contenido principal (recomendado)

### 2.3 Formularios

- [ ] Cada input tiene `<label>` asociado (o `aria-label` / `aria-labelledby`)
- [ ] Campos obligatorios indicados de forma no solo por color
- [ ] Mensajes de error asociados al campo (texto +, si aplica, `aria-describedby`)
- [ ] Placeholders no sustituyen al label
- [ ] Selects y textareas con el mismo criterio de etiquetado

### 2.4 Contraste y tipografía

- [ ] Texto normal: contraste ≥ **4.5:1** respecto al fondo (AA)
- [ ] Texto grande (≥18pt o 14pt negrita): ≥ **3:1**
- [ ] Iconos informativos y bordes de controles con contraste suficiente
- [ ] No transmitir información solo por color (ej. “Ocupada” también en texto/badge)
- [ ] Zoom del navegador al 200% no rompe layouts críticos

### 2.5 Imágenes y no-texto

- [ ] Imágenes informativas con `alt` descriptivo
- [ ] Imágenes decorativas con `alt=""` o CSS background
- [ ] Iconos de acción con nombre accesible (texto visible o `aria-label`)
- [ ] Gráficas Spark: título/figcaption o texto alternativo del resultado

### 2.6 Movimiento y tiempo

- [ ] Animaciones no esenciales no bloquean el uso
- [ ] Si hay auto-actualización (ej. status Spark running), el usuario puede seguir operando
- [ ] Confirmaciones destructivas (eliminar resultado, cerrar cuenta) requieren acción explícita

### 2.7 Idioma

- [ ] `lang` en `<html>` coherente con el idioma activo (es / en)
- [ ] Cambio de idioma actualiza textos de UI (ver `design/sistema-visual/validacion-idiomas.md`)

---

## 3. Checklist por módulo

### 3.1 Login y layout

| Ítem | Estado | Notas |
|------|--------|-------|
| Formulario login etiquetado | ☐ | |
| Errores de autenticación legibles | ☐ | |
| Sidebar: ítems con nombre accesible | ☐ | |
| Botón cerrar sesión operable por teclado | ☐ | |

### 3.2 Administrativo (pacientes / censo)

| Ítem | Estado | Notas |
|------|--------|-------|
| Tabla o cards con identificación del paciente | ☐ | |
| Botones Ver / Editar con texto o aria-label | ☐ | |
| Formulario alta: labels en todos los campos | ☐ | |
| Resumen de montos legible (no solo color) | ☐ | |

### 3.3 Enfermería

| Ítem | Estado | Notas |
|------|--------|-------|
| Tarjetas de cama: estado Ocupada/Libre en texto | ☐ | |
| Solo camas ocupadas activas (foco no en deshabilitadas confusas) | ☐ | |
| Formulario signos vitales etiquetado | ☐ | |
| Historial comprensible con fechas | ☐ | |

### 3.4 Médico

| Ítem | Estado | Notas |
|------|--------|-------|
| Panel de áreas y camas igual criterio que enfermería | ☐ | |
| Menú de detalle (signos, nota, diagnóstico…) con nombres claros | ☐ | |

### 3.5 Estudios

| Ítem | Estado | Notas |
|------|--------|-------|
| Tabs con estado seleccionado perceptible | ☐ | |
| Acciones Subir / Ver / Editar / Eliminar nombradas | ☐ | |
| Confirmación al eliminar | ☐ | |

### 3.6 Configuración

| Ítem | Estado | Notas |
|------|--------|-------|
| Cards de módulo con título + descripción | ☐ | |
| Formularios de catálogo etiquetados | ☐ | |

### 3.7 Spark

| Ítem | Estado | Notas |
|------|--------|-------|
| Cards del dashboard con título y estado (listo / sin resultados) | ☐ | |
| Botones Ejecutar / Actualizar con texto visible | ☐ | |
| Resultados en estructura legible (headings + datos) | ☐ | |
| Visualizaciones con pie de figura o alt | ☐ | |
| Mensajes de error y “sin resultados” claros | ☐ | |

---

## 4. Targets táctiles (móvil)

- [ ] Controles principales ≥ **24×24 px** (mínimo WCAG 2.2); recomendado **44×44 px**
- [ ] Espaciado suficiente entre botones de acción en filas densas
- [ ] En móvil, botones de formulario no quedan inaccesibles bajo el teclado virtual

---

## 5. Herramientas de apoyo a la revisión

| Herramienta | Uso |
|-------------|-----|
| Chrome DevTools → Lighthouse (Accessibility) | Barrido automático inicial |
| axe DevTools / WAVE | Problemas de contraste y ARIA |
| Navegación solo teclado | Tab order y foco |
| Zoom 200% | Reflow y legibilidad |
| Lector de pantalla (opcional: NVDA / VoiceOver) | Muestreo en login, listado y un formulario |

> La automatización no sustituye la revisión manual de flujos clínicos.

---

## 6. Severidad de hallazgos

| Severidad | Ejemplo | Acción |
|-----------|---------|--------|
| **Alta** | No se puede enviar un formulario solo con teclado; contraste texto &lt; 3:1 | Bloqueante antes de cierre |
| **Media** | Foco poco visible; label solo por placeholder | Corregir en el sprint |
| **Baja** | Mejora de heading o landmark | Backlog |

---

## 7. Registro de hallazgos

| ID | Módulo | Criterio | Descripción | Severidad | Estado |
|----|--------|----------|-------------|-----------|--------|
| A-01 | | | | | Abierto / Resuelto |
| A-02 | | | | | |

---

## 8. Criterio de cierre

El checklist de accesibilidad se considera **cumplido para el alcance del sprint** cuando:

1. No quedan hallazgos de severidad **Alta** abiertos.
2. Formularios principales (login, alta paciente, signos, estudios) tienen labels y operación por teclado verificada.
3. Contraste de textos de UI principales cumple AA en tema claro actual.
4. Módulo Spark: acciones Ejecutar/Actualizar y estados de resultado son comprensibles sin depender solo del color.

---

**Archivo:** `design/accesibilidad/checklist.md`  
**Relacionado:**  
- `design/sistema-visual/validacion-idiomas.md`  
- `design/responsive/validacion-final.md`  
- Capturas Spark: `design/capturas/spark/`
