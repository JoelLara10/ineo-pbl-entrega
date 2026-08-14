# Validación de idiomas (ES / EN)

**Proyecto:** clinica-web-react (INEO)  
**Sistema i18n:** `react-i18next` + archivos `src/i18n/locales/es.json` y `en.json`  
**Idioma por defecto:** Español (`es`)  
**Persistencia:** `localStorage` clave `@ineo_lang`

---

## 1. Configuración actual

| Elemento | Valor |
|----------|--------|
| Librería | `i18next` + `react-i18next` |
| Recursos | `es` y `en` en `src/i18n/locales/` |
| Inicialización | `src/i18n/index.js` |
| Fallback | `es` |
| Guardado de preferencia | `localStorage.getItem('@ineo_lang')` |

```js
// src/i18n/index.js (resumen)
const savedLang = localStorage.getItem('@ineo_lang') || 'es';
i18n.use(initReactI18next).init({
  resources: { es: { translation: es }, en: { translation: en } },
  lng: savedLang,
  fallbackLng: 'es',
  interpolation: { escapeValue: false },
});
```

---

## 2. Alcance de la validación

Se valida que **todas las cadenas visibles al usuario** usen claves `t('...')` y existan en **ambos** archivos de idioma, en estos módulos:

| Módulo | Rutas / pantallas principales |
|--------|--------------------------------|
| Comunes | Login, layout, sidebar, dashboard, mensajes genéricos |
| Administrativo | Pacientes, alta, detalle, censo, corte de caja |
| Enfermería | Panel, signos, valoración, balance, notas, cuidados |
| Médico | Panel, detalle, signos, notas, diagnósticos, recetas, estudios |
| Estudios | Solicitudes lab/gab, resultados, subir/ver/editar |
| Configuración | Camas, usuarios, diagnósticos, servicios, backup, automatización, perfil |

---

## 3. Criterios de aceptación

### 3.1 Cobertura de claves

- [ ] Toda cadena de UI usa `t('clave')` o `t('clave', { ... })` (sin texto hardcodeado en JSX salvo datos dinámicos de API).
- [ ] Cada clave usada en código existe en `es.json` **y** en `en.json`.
- [ ] No hay claves huérfanas críticas (usadas en un idioma y ausentes en el otro).
- [ ] Interpolaciones (`{{name}}`, `{{count}}`, etc.) coinciden en ES y EN.

### 3.2 Cambio de idioma

- [ ] El selector de idioma (perfil / configuración / sidebar, según implementación) cambia `i18n.language` y persiste en `@ineo_lang`.
- [ ] Al recargar la página se respeta el idioma guardado.
- [ ] El cambio se refleja de inmediato en headers, menús, botones, tablas, formularios y mensajes.

### 3.3 Fechas y números

- [ ] Fechas con `moment` o `toLocaleDateString` usan locale según `i18n.language` (`es` / `en` o `es-MX` / `en-US`).
- [ ] Moneda (módulo administrativo) formatea según idioma (ej. `es-MX` → MXN).

### 3.4 Contenido dinámico

- [ ] Datos de pacientes, camas, estudios, etc. **no** se traducen (nombres propios, IDs).
- [ ] Estados de UI sí se traducen: Ocupada/Libre, Pendiente/Completado, botones, títulos de sección.

---

## 4. Checklist por módulo

### Común / Layout
| Elemento | ES | EN | Notas |
|----------|----|----|-------|
| Menú lateral (módulos) | ☐ | ☐ | |
| Botón cerrar sesión | ☐ | ☐ | |
| Loading / errores genéricos | ☐ | ☐ | `common.loading`, etc. |
| Selector de idioma | ☐ | ☐ | |

### Administrativo
| Pantalla | ES | EN |
|----------|----|----|
| Listado pacientes | ☐ | ☐ |
| Alta / edición paciente | ☐ | ☐ |
| Detalle / cuenta | ☐ | ☐ |
| Censo | ☐ | ☐ |
| Labels de formulario (CURP, apellidos, área, cama…) | ☐ | ☐ |

### Enfermería
| Pantalla | ES | EN |
|----------|----|----|
| Panel (Consulta / Urgencias / Hospitalizados) | ☐ | ☐ |
| Signos vitales (formulario + historial) | ☐ | ☐ |
| Valoración | ☐ | ☐ |
| Balance hídrico | ☐ | ☐ |
| Ocupada / Disponible / Cama N | ☐ | ☐ |

### Médico
| Pantalla | ES | EN |
|----------|----|----|
| Panel por áreas | ☐ | ☐ |
| Detalle paciente (menú clínico) | ☐ | ☐ |
| Signos / notas / diagnósticos / recetas | ☐ | ☐ |

### Estudios
| Pantalla | ES | EN |
|----------|----|----|
| Tabs (solicitudes lab/gab, resultados) | ☐ | ☐ |
| Tarjetas (Subir / Ver / Editar / Eliminar) | ☐ | ☐ |
| Mensajes vacío y confirmación de borrado | ☐ | ☐ |

### Configuración
| Pantalla | ES | EN |
|----------|----|----|
| Grid de módulos (camas, usuarios, diagnósticos…) | ☐ | ☐ |
| Badges (Admin, Médico, Catálogo…) | ☐ | ☐ |
| Perfil / idioma | ☐ | ☐ |

---

## 5. Procedimiento de prueba manual

1. Iniciar sesión con un usuario de prueba.
2. Ir a **Perfil** o al control de idioma y seleccionar **English**.
3. Verificar que el menú y la pantalla actual cambian a inglés.
4. Recorrer:
   - Dashboard  
   - Administrativo → Pacientes, Censo  
   - Enfermería → Panel y una pantalla de registro  
   - Médico → Panel y detalle  
   - Estudios → cada pestaña  
   - Configuración → panel principal  
5. Volver a **Español** y repetir un muestreo rápido.
6. Recargar el navegador y confirmar que se mantiene el último idioma elegido.

### Evidencia sugerida (capturas)

Colocar en `design/capturas/` o en la carpeta de evidencia del sprint:

| Archivo sugerido | Contenido |
|------------------|-----------|
| `idioma-es-medico.png` | Panel médico en español |
| `idioma-en-medico.png` | Mismo panel en inglés |
| `idioma-es-estudios.png` | Estudios en español |
| `idioma-en-estudios.png` | Estudios en inglés |
| `idioma-es-config.png` | Configuración en español |
| `idioma-en-config.png` | Configuración en inglés |

---

## 6. Problemas frecuentes y cómo detectarlos

| Problema | Cómo se ve | Acción |
|----------|------------|--------|
| Texto hardcodeado | Siempre en un solo idioma | Sustituir por `t('clave')` y agregar clave en ES/EN |
| Clave faltante en EN | Se muestra la clave cruda o el fallback ES | Completar `en.json` |
| Interpolación distinta | `{{name}}` vs texto fijo | Unificar placeholders en ambos JSON |
| Fecha en idioma incorrecto | “Monday” con UI en español | Ajustar `moment.locale` / `toLocaleDateString` al `i18n.language` |
| No persiste el idioma | Al recargar vuelve a ES | Verificar escritura en `localStorage('@ineo_lang')` al cambiar idioma |

---

## 7. Criterio de cierre

La validación de idiomas se considera **aprobada** cuando:

1. No quedan textos de UI hardcodeados en los módulos listados.
2. ES y EN tienen paridad de claves para esas pantallas.
3. El cambio ES ↔ EN es inmediato y se mantiene tras recargar.
4. Se adjuntan al menos 2 pares de capturas (mismo pantalla, ambos idiomas) como evidencia.

---

**Archivo:** `design/sistema-visual/validacion-idiomas.md`  
**Relacionado:** capturas en `design/capturas/medico/`, `design/capturas/estudios/`, `design/capturas/configuracion/`  
**Referencia de código:** `src/i18n/index.js`, `src/i18n/locales/es.json`, `src/i18n/locales/en.json`
