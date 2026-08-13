# Diseño Responsive — Módulo Enfermería (INEO)

**Proyecto:** clinica-web-react  
**Módulo:** Enfermería  
**Pantallas cubiertas:**
- Panel principal (`EnfermeriaScreen`) → `enfermeria-panel`
- Signos vitales (`EnfermeriaVitalSignsScreen`) → `enfermeria-signos`
- Valoración (`EnfermeriaAssessmentScreen`) → `enfermeria-valoracion`
- Balance hídrico (`EnfermeriaFluidBalanceScreen`) → `enfermeria-balance`

**Colorimetría de referencia:** verde (mockups)  
**Breakpoints propuestos:**

| Nombre   | Ancho            | Uso principal                |
|----------|------------------|------------------------------|
| Mobile   | `< 720px`        | Teléfonos                    |
| Tablet   | `720px – 1024px` | Tablets / landscape móvil    |
| Desktop  | `> 1024px`       | Escritorio                   |

---

## 1. Principios generales

1. **Mobile-first** cuando sea posible.
2. **Grids de camas/campos** se reducen a 1–2 columnas en móvil.
3. **Touch-friendly:** botones y tarjetas de cama con área mínima ~44px.
4. **Sin scroll horizontal** no intencional.
5. **Header + paciente seleccionado** siempre visibles o accesibles al inicio de cada pantalla de detalle.

---

## 2. Layout global compartido

### 2.1 Página

| Viewport | Padding |
|----------|---------|
| Mobile   | `12–16px` |
| Tablet   | `16–20px` |
| Desktop  | `24px` |

### 2.2 Header

| Viewport | Comportamiento |
|----------|----------------|
| Desktop / Tablet | Fila: [Atrás] [Eyebrow + Título] …… [Refresh u otros] |
| Mobile | Se mantiene en fila compacta; título puede reducir tamaño de fuente |

### 2.3 Tarjeta de paciente seleccionado

Presente en signos, valoración y balance:
- Avatar + nombre + meta (Exp / Atención).
- En móvil: sigue en fila; meta puede hacer wrap.
- Borde lateral de acento (verde) se mantiene.

### 2.4 Hero del panel (saludo + total pacientes)

| Viewport | Layout |
|----------|--------|
| Desktop | Fila: saludo a la izquierda, pill de total a la derecha |
| Mobile | Puede apilarse (saludo arriba, pill debajo o a la derecha si cabe) |

---

## 3. Panel de enfermería (`enfermeria-panel`)

### 3.1 Secciones

Tres bloques: **Consulta externa**, **Urgencias**, **Hospitalizados**.

Cada sección:
- Barra de título con icono + contador (badge).
- Grid de tarjetas de cama.
- Paginación si hay más de una página.

### 3.2 Grid de camas

| Viewport | Columnas |
|----------|----------|
| Mobile   | 2 columnas |
| Tablet   | 3 columnas |
| Desktop  | 4+ columnas (`auto-fill, minmax(140px, 1fr)` o similar) |

### 3.3 Tarjeta de cama

Contenido:
- Icono (usuario / cama libre)
- Número de cama
- Nombre del paciente o “Disponible”
- Estado (Ocupada / Libre)

**Mobile:**
- Texto legible; nombre puede truncarse con ellipsis si es muy largo.
- Toda la tarjeta sigue siendo táctil (solo ocupadas navegan).

### 3.4 Paginación

Centrada, compacta en móvil (‹ n / total ›).

---

## 4. Signos vitales (`enfermeria-signos`)

### 4.1 Formulario de nuevo registro

Campos: TA, FC, FR, Temp, SpO2, Peso, Talla.

| Viewport | Grid |
|----------|------|
| Desktop / Tablet | 2–3 columnas (`auto-fit, minmax(160–220px, 1fr)`) |
| Mobile | 1 columna (o 2 si el ancho lo permite cómodamente) |

### 4.2 Botones

- Volver / Guardar.
- En móvil: preferir fila con wrap o Guardar a ancho completo debajo.

### 4.3 Historial

Cada registro:
- Fecha/hora.
- Métricas en mini-cards (TA, FC, FR, etc.).

| Viewport | Métricas |
|----------|----------|
| Desktop | Varias columnas |
| Mobile | 2–3 columnas de métricas por registro |

Los registros se apilan verticalmente en todos los tamaños.

---

## 5. Valoración de enfermería (`enfermeria-valoracion`)

### 5.1 Formulario

Campos:
- Estado general  
- Dolor  
- Movilidad  
- Riesgo de caídas  
- Riesgo UPP  
- Observaciones (textarea a ancho completo)

| Viewport | Grid de inputs |
|----------|----------------|
| Desktop / Tablet | 2 columnas |
| Mobile | 1 columna |

Textarea siempre full-width.

### 5.2 Acciones

Recargar + Guardar:
- Desktop: alinea a los extremos o a la derecha.
- Mobile: botones apilados o en fila con ancho generoso.

### 5.3 Historial

Lista de artículos con fecha, enfermero y líneas de valoración.
- Sin cambios estructurales; solo padding y tipografía adaptados en móvil.

---

## 6. Balance hídrico (`enfermeria-balance`)

### 6.1 Formulario

Campos numéricos:
- Ingresos orales (ml)  
- Ingresos IV (ml)  
- Egresos orina (ml)  
- Egresos drenajes (ml)  
- Observaciones (textarea)

| Viewport | Grid |
|----------|------|
| Desktop / Tablet | 2 columnas |
| Mobile | 1 columna |

### 6.2 Historial

Cada ítem muestra:
- Fecha + enfermero  
- Total ingresos / egresos / balance neto  
- Observaciones  

Mismo patrón de lista apilada que valoración.

---

## 7. Componentes compartidos

### 7.1 Botones

| Viewport | Altura mínima recomendada |
|----------|---------------------------|
| Todos    | ~40px |
| Mobile (acciones principales) | ~44px |

Variantes: primario (verde), secundario/gris, ghost en header.

### 7.2 Inputs

- Ancho 100% del campo.
- Padding cómodo para dedo en móvil.
- Labels siempre visibles encima del control.

### 7.3 Badges y pills

- No reducir demasiado el área táctil ni el contraste.
- En móvil pueden quedar debajo del título de sección si no caben en la misma fila.

---

## 8. CSS sugerido (patrones)

```css
/* Base compartida con módulo administrativo donde aplique */
@media (max-width: 720px) {
  .enf-page { padding: 12px; }

  .enf-header {
    padding: 14px 16px;
  }
  .enf-header h1,
  .enf-header h2 {
    font-size: 1.15rem;
  }

  .enf-hero {
    flex-direction: column;
    align-items: flex-start;
  }

  .enf-beds-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 10px;
  }

  .enf-form-grid {
    grid-template-columns: 1fr;
  }

  .enf-metrics {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .enf-button-row {
    flex-direction: column;
  }
  .enf-button-row .btn {
    width: 100%;
    min-height: 44px;
    justify-content: center;
  }

  .enf-patient-card {
    flex-wrap: wrap;
  }
}

@media (min-width: 721px) and (max-width: 1024px) {
  .enf-beds-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
  .enf-form-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (min-width: 1025px) {
  .enf-beds-grid {
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  }
  .enf-form-grid {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  }
}
```

> Los nombres de clase (`.enf-*`) son sugeridos; pueden mapearse a los estilos inline actuales del módulo o extraerse a CSS.

---

## 9. Checklist de aceptación responsive

### Panel de enfermería
- [ ] Grid de camas legible en 320–400px (2 columnas)
- [ ] Camas ocupadas claramente distinguibles y táctiles
- [ ] Secciones (Consulta / Urgencias / Hospitalizados) no se solapan
- [ ] Paginación usable
- [ ] Hero (saludo + total) no desborda

### Signos vitales
- [ ] Formulario usable en 1 columna en móvil
- [ ] Historial con métricas legibles (2+ columnas de chips)
- [ ] Guardar accesible sin zoom forzado

### Valoración
- [ ] Todos los campos y textarea usables
- [ ] Historial legible y con wrap de texto
- [ ] Botones Recargar / Guardar táctiles

### Balance hídrico
- [ ] Inputs numéricos a ancho completo en móvil
- [ ] Totales e historial legibles
- [ ] Misma calidad de interacción que valoración

### General
- [ ] Header no se rompe al rotar el dispositivo
- [ ] Sin scroll horizontal no intencional
- [ ] Contraste suficiente en badges y estados (Ocupada / Libre)
- [ ] Área táctil mínima razonable en tarjetas de cama y botones

---

## 10. Notas de implementación

1. El módulo de enfermería usa estilos **inline** en varios screens; conviene extraer gradualmente a CSS compartido para aplicar media queries de forma consistente.
2. Priorizar el breakpoint **720px** para alinear con el módulo administrativo (`Administrativo.css`).
3. Las tarjetas de cama libres no deben navegar; solo las ocupadas con atención activa.
4. Probar en:
   - iPhone SE / Android pequeño (~320–375px)
   - Tablet 768px
   - Desktop 1280px+
5. i18n: labels y textos largos deben poder hacer wrap; no depender de anchos fijos en px para textos.

---

**Archivo:** `design/responsive/enfermeria-responsive.md`  
**Relacionado:** mockups HTML en `mockups-enfermeria.html`  
**Capturas objetivo:**
- `design/mockups/enfermeria-panel.png`
- `design/mockups/enfermeria-signos.png`
- `design/mockups/enfermeria-valoracion.png`
- `design/mockups/enfermeria-balance.png`
