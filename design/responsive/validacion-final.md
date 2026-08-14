# Validación responsive final — INEO

**Proyecto:** clinica-web-react  
**Alcance:** Validación integral de comportamiento responsive en todos los módulos de diseño entregados  
**Breakpoints de referencia:**

| Nombre   | Ancho            | Uso                          |
|----------|------------------|------------------------------|
| Mobile   | `< 720px`        | Teléfonos                    |
| Tablet   | `720px – 1024px` | Tablets / landscape          |
| Desktop  | `> 1024px`       | Escritorio                   |

---

## 1. Objetivo

Confirmar que la interfaz se adapta sin pérdida de funcionalidad ni de legibilidad en:

- Administrativo (pacientes, censo)
- Enfermería
- Médico
- Estudios
- Configuración
- Spark (análisis)
- Layout global (sidebar + contenido)

---

## 2. Criterios generales de aceptación

- [ ] Sin **scroll horizontal** no intencional en 320px–1920px
- [ ] Textos y controles legibles sin zoom forzado
- [ ] Áreas táctiles mínimas ~40–44px en móvil
- [ ] Header / toolbar no se rompe al rotar el dispositivo
- [ ] Tablas densas se convierten en cards o permiten scroll contenido en móvil
- [ ] Grids (camas, stats, formularios, cards de módulos) reducen columnas de forma coherente
- [ ] Botones primarios accesibles sin quedar ocultos bajo el teclado (forms)

---

## 3. Checklist por módulo

### 3.1 Layout global (MainLayout / Sidebar)

| Criterio | Mobile | Tablet | Desktop | Evidencia |
|----------|--------|--------|---------|-----------|
| Sidebar colapsable / menú hamburguesa | ☐ | ☐ | ☐ | |
| Contenido principal ocupa el ancho útil | ☐ | ☐ | ☐ | |
| No hay solapamiento menú ↔ contenido | ☐ | ☐ | ☐ | |

### 3.2 Administrativo — Pacientes / Censo

| Criterio | Mobile | Tablet | Desktop | Evidencia |
|----------|--------|--------|---------|-----------|
| Summary/stats en 2 cols (móvil) | ☐ | ☐ | ☐ | |
| Tabla → cards o scroll controlado | ☐ | ☐ | ☐ | |
| Formulario alta 1 col en móvil | ☐ | ☐ | ☐ | |
| Buscador a 100% en móvil | ☐ | ☐ | ☐ | |
| Ver docs: `design/responsive/pacientes-responsive.md` | | | | |

### 3.3 Enfermería

| Criterio | Mobile | Tablet | Desktop | Evidencia |
|----------|--------|--------|---------|-----------|
| Grid de camas 2 cols en móvil | ☐ | ☐ | ☐ | |
| Formularios signos/valoración/balance 1 col | ☐ | ☐ | ☐ | |
| Historial legible (métricas en chips) | ☐ | ☐ | ☐ | |
| Ver docs: `design/responsive/enfermeria-responsive.md` | | | | |

### 3.4 Médico

| Criterio | Mobile | Tablet | Desktop | Evidencia |
|----------|--------|--------|---------|-----------|
| Panel por áreas adaptable | ☐ | ☐ | ☐ | |
| Detalle paciente: menú de acciones en grid responsive | ☐ | ☐ | ☐ | |
| Formularios clínicos usables en móvil | ☐ | ☐ | ☐ | |

### 3.5 Estudios

| Criterio | Mobile | Tablet | Desktop | Evidencia |
|----------|--------|--------|---------|-----------|
| Tabs usables (scroll o wrap) en móvil | ☐ | ☐ | ☐ | |
| Tarjetas de solicitud/resultado a ancho completo | ☐ | ☐ | ☐ | |
| Botones Subir/Ver/Editar/Eliminar táctiles | ☐ | ☐ | ☐ | |

### 3.6 Configuración

| Criterio | Mobile | Tablet | Desktop | Evidencia |
|----------|--------|--------|---------|-----------|
| Grid de módulos 1–2 cols en móvil | ☐ | ☐ | ☐ | |
| Formularios de config (camas, usuarios…) 1 col | ☐ | ☐ | ☐ | |

### 3.7 Spark (análisis)

| Criterio | Mobile | Tablet | Desktop | Evidencia |
|----------|--------|--------|---------|-----------|
| Dashboard de 4 módulos en 1 col móvil | ☐ | ☐ | ☐ | |
| Toolbar (Volver / Actualizar / Ejecutar) apilable | ☐ | ☐ | ☐ | |
| Data-grid de resultados 1 col en móvil | ☐ | ☐ | ☐ | |
| Galería de visualizaciones adaptable | ☐ | ☐ | ☐ | |
| CSS existente: `@media (max-width: 700px)` en `Spark.css` | | | | |

---

## 4. Matriz de dispositivos de prueba

| Dispositivo / viewport | Ancho aprox. | Prioridad |
|------------------------|--------------|-----------|
| iPhone SE / Android pequeño | 320–375px | Alta |
| iPhone / Android medio | 390–430px | Alta |
| Tablet portrait | 768px | Media |
| Tablet landscape / laptop pequeña | 1024px | Media |
| Desktop | 1280–1920px | Alta |

---

## 5. Procedimiento de validación

1. Abrir la app en Chrome DevTools (o navegador real).
2. Probar cada módulo en **320px**, **768px** y **1280px**.
3. Marcar los checklists de la sección 3.
4. Capturar al menos **1 evidencia por módulo** en móvil (opcional tablet).
5. Registrar fallos en la sección 6.

### Evidencias sugeridas

| Archivo | Descripción |
|---------|-------------|
| `design/capturas/responsive/pacientes-mobile.png` | Listado pacientes &lt;720px |
| `design/capturas/responsive/enfermeria-mobile.png` | Panel enfermería móvil |
| `design/capturas/responsive/medico-mobile.png` | Panel médico móvil |
| `design/capturas/responsive/estudios-mobile.png` | Estudios con tabs |
| `design/capturas/responsive/config-mobile.png` | Grid configuración |
| `design/capturas/responsive/spark-mobile.png` | Dashboard Spark móvil |

---

## 6. Hallazgos (completar en la revisión)

| ID | Módulo | Viewport | Descripción | Severidad | Estado |
|----|--------|----------|-------------|-----------|--------|
| R-01 | | | | Baja / Media / Alta | Abierto / Resuelto |
| R-02 | | | | | |

---

## 7. Criterio de cierre

La validación responsive final se considera **aprobada** cuando:

1. No existen bloqueantes (severidad Alta) abiertos.
2. Todos los módulos de la sección 3 cumplen los criterios generales.
3. Existe evidencia (capturas o checklist firmado) de prueba en móvil y desktop.
4. Los documentos por módulo (`pacientes-responsive.md`, `enfermeria-responsive.md`) siguen vigentes y no contradicen esta validación.

---

**Archivo:** `design/responsive/validacion-final.md`  
**Relacionado:**  
- `design/responsive/pacientes-responsive.md`  
- `design/responsive/enfermeria-responsive.md`  
- `design/capturas/spark/` (HTML de capturas Spark)
