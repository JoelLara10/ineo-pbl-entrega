# Diseño Responsive — Módulo Pacientes (INEO)

**Proyecto:** clinica-web-react  
**Módulo:** Administrativo / Pacientes  
**Pantallas cubiertas:**
- Listado de pacientes (`PacientesScreen`)
- Alta / edición de paciente (`NuevoPacienteScreen`)
- Detalle / cuenta del paciente (`PacienteDetailScreen`)
- Censo (`CensoScreen`)

**Colorimetría de referencia:** verde (mockups)  
**Breakpoints propuestos** (alineados al CSS actual y convenciones comunes):

| Nombre   | Ancho          | Uso principal              |
|----------|----------------|----------------------------|
| Mobile   | `< 720px`      | Teléfonos                  |
| Tablet   | `720px – 1024px` | Tablets / landscape móvil |
| Desktop  | `> 1024px`     | Escritorio                 |

> El CSS actual de `Administrativo.css` ya contempla `@media (max-width: 720px)`. Este documento detalla el comportamiento esperado por componente.

---

## 1. Principios generales

1. **Mobile-first** donde sea posible: estilos base para móvil y mejoras progresivas en tablet/desktop.
2. **Tablas → tarjetas en móvil:** las tablas densas se convierten en cards apiladas.
3. **Touch-friendly:** botones y áreas táctiles mínimas de ~40–44px.
4. **Sin scroll horizontal** no intencional; el contenido se reorganiza o hace scroll vertical.
5. **Jerarquía clara:** el header, el resumen y las acciones principales siempre visibles o accesibles.

---

## 2. Breakpoints y layout global

### 2.1 Contenedor de página (`.adm-page`)

| Viewport | Padding | Comportamiento |
|----------|---------|----------------|
| Mobile   | `12px`  | Una columna, sin márgenes laterales grandes |
| Tablet   | `16–20px` | Una columna, más aire |
| Desktop  | `24px`  | Contenido centrado o a ancho completo del layout principal |

### 2.2 Header (`.adm-header`)

| Viewport | Layout |
|----------|--------|
| **Desktop / Tablet** | Fila: [Atrás] [Título + subtítulo] …… [Acciones] |
| **Mobile** | Se apila: título arriba; acciones debajo o en fila con wrap. El botón de volver se mantiene a la izquierda. |

**Reglas:**
- En móvil el subtítulo puede ocultarse o reducirse a una línea.
- Botones de acción (Nuevo paciente, Actualizar) pasan a ancho completo o se agrupan en wrap.
- El gradiente y contraste se mantienen en todos los tamaños.

### 2.3 Resumen / stats (`.adm-summary`)

| Viewport | Columnas |
|----------|----------|
| Mobile   | 2 columnas (grid) |
| Tablet   | 2–3 columnas |
| Desktop  | 3–4 columnas (`auto-fit, minmax(150px, 1fr)`) |

---

## 3. Listado de pacientes (`pacientes-listado`)

### 3.1 Desktop / Tablet (≥ 720px)

- Tabla completa con columnas: Expediente, Paciente, Edad, Teléfono, Área, Cama, Acciones.
- Buscador a ancho flexible.
- Paginación centrada debajo de cada grupo (Activos, etc.).
- Botones Ver / Editar en línea.

### 3.2 Mobile (< 720px)

**Tabla → lista de tarjetas**

Cada fila se convierte en una card:

```
┌─────────────────────────────────┐
│ EXP-1042              [Ver] [Editar] │
│ García López, María             │
│ 45 años · 555-0142              │
│ Área: Hospitalización · Cama: C-12 │
└─────────────────────────────────┘
```

**Cambios:**
- Ocultar columnas de baja prioridad en tabla (o no usar tabla).
- Mostrar: expediente + nombre como título; edad, teléfono, área y cama como metadatos.
- Acciones siempre visibles (botones o iconos grandes).
- Buscador a 100% de ancho.
- Stats en 2 columnas.
- Paginación compacta (‹ 1/5 ›).

### 3.3 Toolbar

- Buscador: `min-width` se reduce; en móvil ocupa 100%.
- Sin filtros secundarios por ahora (si se agregan, van en un drawer o debajo del buscador en móvil).

---

## 4. Alta de paciente (`paciente-alta`)

### 4.1 Formulario

| Viewport | Grid de campos |
|----------|----------------|
| Desktop  | 2 columnas (`.adm-form-grid`) |
| Tablet   | 2 columnas |
| Mobile   | 1 columna |

**Secciones** (se mantienen apiladas en todos los tamaños):
1. Datos personales  
2. Datos de atención  
3. Médicos asignados  
4. Datos familiares  

### 4.2 Campos especiales

- **Alergias (textarea):** siempre a ancho completo (`grid-column: 1 / -1`).
- **Médicos (checkboxes):** en móvil se apilan en 1 columna; en tablet/desktop en fila con wrap.
- **Botones Cancelar / Guardar:** en móvil a ancho completo, uno debajo del otro o en fila si cabe; Guardar con mayor peso visual (verde).

### 4.3 Select y date

- Controles nativos a 100% de ancho del campo.
- Evitar que el teclado en móvil oculte el botón Guardar (scroll al foco o sticky footer opcional).

---

## 5. Detalle / cuenta del paciente (`paciente-detalle`)

### 5.1 Resumen de montos

Mismo comportamiento que el summary del listado (2 cols en móvil, 4 en desktop).

### 5.2 Tabla de cuentas y tabla de cargos

| Viewport | Comportamiento |
|----------|----------------|
| Desktop / Tablet | Tabla completa |
| Mobile | Cards por cuenta/cargo |

**Card de cuenta (ejemplo):**
```
AT-2041 · EXP-1042
García López, María
Área: Hospitalización
Saldo: $2,126.00
[ Abrir cuenta ]
```

**Card de cargo:**
```
Consulta especializada
1 × $1,200.00 = $1,200.00
[ 🗑 ]
```

### 5.3 Agregar cargo

- Formulario en 1 columna en móvil.
- Botón “Agregar” a ancho completo en móvil.

### 5.4 Documentos

- Grid de botones: 1 columna en móvil, 2–3 en tablet, auto-fit en desktop.
- Área táctil suficiente en cada documento.

### 5.5 Cerrar cuenta

- Botón de peligro siempre visible al final; en móvil ancho completo.

---

## 6. Censo (`censo`)

### 6.1 Estructura

Igual que el listado de pacientes:
- Summary (Activos / Áreas / Avisos).
- Buscador.
- Secciones por área (Hospitalización, Urgencias, etc.) con tabla o cards.

### 6.2 Mobile

Cada paciente del censo como card:

```
AT-2041 · EXP-1042
García López, María
C-12 · Dr. Mendoza
Motivo: Postoperatorio
Aviso: Alergia  (destacado en color)
```

- Avisos con color de acento (naranja/ámbar) se mantienen legibles.
- Paginación por sección se conserva.

---

## 7. Componentes compartidos

### 7.1 Botones (`.adm-button`)

| Viewport | Altura mínima | Padding |
|----------|---------------|---------|
| Todos    | ~40px         | Adecuado al texto |
| Mobile   | Preferir 44px en acciones principales | Más padding horizontal si es ancho completo |

Variantes:
- Primario / success: verde.
- Light: fondo blanco, texto verde.
- Danger: rojo (cerrar cuenta, eliminar cargo).

### 7.2 Buscador (`.adm-search`)

- Icono a la izquierda.
- Input a 100% del contenedor en móvil.
- Placeholder corto en móvil si es necesario (“Buscar…”).

### 7.3 Paginación

- Controles centrados.
- En móvil: botones ‹ › y texto “página / total” sin ocupar mucho espacio.

### 7.4 Alertas y loading

- Alertas a ancho completo.
- Loading centrado, sin cambios relevantes por breakpoint.

---

## 8. CSS de referencia (ya existente + extensiones sugeridas)

El proyecto ya incluye en `Administrativo.css`:

```css
@media (max-width: 720px) {
  .adm-page { padding: 12px; }
  .adm-header { align-items: flex-start; flex-wrap: wrap; }
  .adm-header-actions { width: 100%; margin-left: 56px; }
  .adm-form-grid { grid-template-columns: 1fr; }
  .adm-table th, .adm-table td { padding: 9px; }
  .adm-summary { grid-template-columns: repeat(2, 1fr); }
}
```

### Extensiones recomendadas

```css
/* Tablas → cards en móvil (patrón) */
@media (max-width: 720px) {
  .adm-table-wrap table { display: none; } /* o mantener y usar card-list alternativo */

  .adm-card-list { display: flex; flex-direction: column; gap: 10px; }
  .adm-patient-card {
    background: #fff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 14px;
  }
  .adm-patient-card .title { font-weight: 700; margin-bottom: 4px; }
  .adm-patient-card .meta { font-size: 13px; color: #64748b; }
  .adm-patient-card .actions { margin-top: 10px; display: flex; gap: 8px; }

  .adm-header-actions { margin-left: 0; }
  .adm-button { min-height: 44px; }
}

/* Tablet intermedio (opcional) */
@media (min-width: 721px) and (max-width: 1024px) {
  .adm-form-grid { grid-template-columns: repeat(2, 1fr); }
  .adm-summary { grid-template-columns: repeat(3, 1fr); }
}
```

> La conversión tabla → cards puede implementarse con dos bloques en el JSX (tabla + lista de cards) controlados por CSS, o con una sola estructura y `display` condicional.

---

## 9. Checklist de aceptación responsive

### Listado de pacientes
- [ ] Sin scroll horizontal en 320px–720px
- [ ] Stats legibles en 2 columnas
- [ ] Buscador usable con teclado móvil
- [ ] Acciones Ver/Editar fáciles de tocar
- [ ] Paginación operable

### Alta de paciente
- [ ] Formulario en 1 columna en móvil
- [ ] Todos los campos accesibles (CURP, fechas, selects)
- [ ] Checkboxes de médicos usables
- [ ] Guardar / Cancelar visibles y táctiles

### Detalle de paciente
- [ ] Montos del summary legibles
- [ ] Cuentas y cargos legibles en card o tabla adaptada
- [ ] Documentos en grid adaptable
- [ ] Cerrar cuenta accesible

### Censo
- [ ] Secciones claras
- [ ] Avisos destacados y legibles
- [ ] Misma calidad de interacción que el listado

### General
- [ ] Header no se rompe
- [ ] Contraste de texto suficiente (WCAG AA donde aplique)
- [ ] No hay elementos solapados al rotar el dispositivo

---

## 10. Notas de implementación

1. Priorizar el breakpoint **720px** ya usado en el proyecto para no introducir inconsistencias.
2. Si se implementan cards en móvil, reutilizar los mismos datos y handlers de las tablas actuales.
3. Mantener i18n: los textos de labels y botones no deben truncarse de forma agresiva; permitir wrap.
4. Probar en:
   - iPhone SE / Android pequeño (~320–375px)
   - Tablet 768px
   - Desktop 1280px+
5. El layout principal (Sidebar + contenido) debe seguir las reglas responsive del `MainLayout` / `Sidebar`; este documento se limita al contenido del módulo administrativo de pacientes.

---

**Archivo:** `design/responsive/pacientes-responsive.md`  
**Relacionado:** mockups en `design/mockups/` (pacientes-listado, paciente-alta, paciente-detalle, censo)
