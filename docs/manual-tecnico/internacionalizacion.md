# Manual técnico — Internacionalización

**Sistema:** INEO — React  
**Sprint:** 4 — Médico, Estudios y Configuración  
**Responsable:** Jesús

## 1. Objetivo

Documentar la implementación bilingüe español–inglés, la organización de recursos, el uso de claves y las pruebas necesarias para evitar textos sin traducir.

## 2. Arquitectura

| Elemento | Ruta |
|---|---|
| Inicialización | `src/i18n/index.js` |
| Español | `src/i18n/locales/es.json` |
| Inglés | `src/i18n/locales/en.json` |
| Integración React | `react-i18next` |
| Motor | `i18next` |

La inicialización registra los recursos `es` y `en`, activa `LanguageDetector` e integra i18next con React. Los componentes consumen traducciones mediante `useTranslation()`.

## 3. Uso en componentes

```jsx
import { useTranslation } from 'react-i18next';

const { t, i18n } = useTranslation();
return <h1>{t('medical.headerTitle')}</h1>;
```

Para valores dinámicos:

```jsx
t('medical.greeting', { name: userName })
t('studies.confirmDelete', { tipo })
```

Las variables deben conservar el mismo nombre en ambos idiomas.

## 4. Organización de claves

Los JSON agrupan las claves por módulo: `login`, `sidebar`, `dashboard`, `medical`, `nursing`, `studies`, `config` y formularios clínicos. Una clave debe describir su significado, no el texto literal.

Ejemplo:

```json
{
  "config": {
    "backups": "Copias de Seguridad",
    "backupCreate": "Crear respaldo"
  }
}
```

Su equivalente inglés conserva exactamente la ruta:

```json
{
  "config": {
    "backups": "Backups",
    "backupCreate": "Create backup"
  }
}
```

## 5. Agregar una traducción

1. Definir una clave estable en `es.json`.
2. Agregar la misma clave en `en.json`.
3. Reemplazar el texto fijo por `t('grupo.clave')`.
4. Comprobar interpolaciones, acentos y pluralización.
5. Probar la pantalla completa en ambos idiomas.

No traduzca valores de base de datos, nombres propios, códigos médicos, identificadores, rutas, estados contractuales de la API ni contenido escrito por usuarios.

## 6. Cambio y detección de idioma

El detector selecciona el idioma disponible según su configuración y el selector puede usar:

```js
i18n.changeLanguage('es');
i18n.changeLanguage('en');
```

Para fechas se utiliza el idioma activo, por ejemplo `es-MX` o `en-US`. La localización visual de una fecha no modifica el valor ISO almacenado por la API.

## 7. Convenciones

- Usar claves en inglés técnico, minúsculas y estilo `camelCase`.
- Mantener idéntica jerarquía en `es.json` y `en.json`.
- Evitar concatenar fragmentos traducidos; traducir la oración completa.
- Usar interpolación para nombres, cantidades y archivos.
- No incluir JSX, HTML ni datos sensibles en los archivos de idioma.
- Usar `defaultValue` solo como protección temporal; la clave debe agregarse a ambos recursos.

## 8. Riesgos detectables

Los textos escritos directamente en componentes no cambian de idioma. También pueden aparecer claves en pantalla cuando una ruta falta, el JSON es inválido o hay diferencias de mayúsculas. Los datos del servidor pueden permanecer en español porque forman parte del contrato o de los catálogos, no de la interfaz.

## 9. Validación automática sugerida

Una prueba debe recorrer ambos objetos y comparar sus rutas completas. El resultado esperado es:

```text
claves_es - claves_en = 0
claves_en - claves_es = 0
```

También debe ejecutarse el compilado de React para detectar JSON inválido e imports incorrectos.

## 10. Pruebas manuales

1. Iniciar en español y recorrer login, panel, Médico, Estudios y Configuración.
2. Cambiar a inglés sin recargar.
3. Revisar títulos, botones, alertas, confirmaciones, estados y pantallas vacías.
4. Verificar interpolaciones con nombres y archivos.
5. Revisar fechas en `es-MX` y `en-US`.
6. Recargar y comprobar el comportamiento del detector.
7. Confirmar que expedientes y datos clínicos no se alteren.

## 11. Criterio de aceptación

La interfaz puede utilizarse en español e inglés, ambos recursos contienen las mismas claves funcionales, las interpolaciones son correctas y el cambio de idioma no modifica datos clínicos ni contratos de la API.
