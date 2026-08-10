# Inventario del sistema anterior

**Proyecto:** Sistema de Gestión Clínica INEO  
**Sprint:** 1 — Arquitectura y bases  
**Responsable:** Jesús  
**Historias relacionadas:** MIG-001 y MIG-002

## 1. Objetivo

Documentar los componentes existentes que serán integrados en el repositorio de entrega del PBL. Este inventario se elaboró a partir de los repositorios `api_hospital` y `clinica-web-react`; por lo tanto, representa el estado recibido antes de organizar la solución por sprints.

## 2. Repositorios de origen

| Componente | Repositorio | Tecnología principal | Función |
|---|---|---|---|
| Backend | `jaimediaz25/api_hospital` | Python, Flask y MongoDB | API REST, reglas de negocio, autenticación y acceso a datos |
| Frontend | `JoelLara10/clinica-web-react` | React y Vite | Interfaz web para los distintos roles clínicos y administrativos |

Los historiales originales permanecen en sus repositorios. El nuevo repositorio únicamente documenta la integración y reconstrucción de la entrega final.

## 3. Inventario del backend

### 3.1 Estructura general

| Elemento | Responsabilidad |
|---|---|
| `app.py` | Crea la aplicación Flask, configura CORS, registra blueprints, inicia tareas programadas y publica rutas generales |
| `config.py` | Centraliza MongoDB, JWT, prefijo `/api/v1`, CORS y paginación |
| `routes/` | Define los endpoints HTTP organizados por dominio |
| `services/` | Implementa reglas de negocio y operaciones de cada dominio |
| `models/` | Contiene modelos de usuario, paciente, cita y examen |
| `schemas/` | Define estructuras y validaciones de datos clínicos |
| `middleware/` | Valida el token y protege rutas privadas |
| `utils/` | Conexión a MongoDB, validadores, secuencias, fechas y respaldos |
| `scheduler/` | Ejecuta tareas automáticas |
| `requirements.txt` | Declara las dependencias de Python |

### 3.2 Módulos funcionales identificados

- Autenticación y usuarios.
- Pacientes y expediente clínico.
- Información médica y de enfermería.
- Camas, servicios y catálogos.
- Citas.
- Estudios, exámenes y carga de resultados.
- Facturación, corte de caja y administración.
- Reportes y generación de PDF.
- Analítica clínica y análisis con Spark.
- Respaldos y monitoreo de desempeño.

### 3.3 Endpoints base

La API utiliza el prefijo `/api/v1`. Los blueprints se registran desde `app.py`; entre los grupos principales se encuentran `auth`, `patients`, `medical`, `catalog`, `pdf`, `exams`, `backup` y `performance`. Además, existen rutas de salud (`/health`) y descripción básica (`/`).

### 3.4 Configuración y datos

- Motor de persistencia: MongoDB.
- Base predeterminada: `hospital_db`.
- Puerto predeterminado: `5001`.
- Autenticación: token JWT enviado como `Bearer`.
- Expiración configurada: 8 horas para acceso y 30 días para renovación.
- Orígenes CORS: entornos locales y direcciones de red autorizadas.

## 4. Inventario del frontend

### 4.1 Estructura general

| Elemento | Responsabilidad |
|---|---|
| `src/main.jsx` | Punto de entrada de React |
| `src/App.jsx` | Integra el router y los proveedores de autenticación y pacientes |
| `src/router/AppRouter.jsx` | Declara navegación y rutas según el rol |
| `src/context/` | Mantiene sesión y paciente seleccionado |
| `src/services/` | Encapsula llamadas Axios a la API y mecanismos de caché |
| `src/pages/` | Agrupa pantallas por módulo y rol |
| `src/components/` | Reúne componentes comunes, formularios, paginación y layout |
| `src/i18n/` | Contiene traducciones en español e inglés |

### 4.2 Módulos funcionales identificados

- Inicio de sesión y control de sesión.
- Dashboard principal.
- Administración y configuración.
- Registro, consulta, censo y detalle de pacientes.
- Enfermería: signos vitales, valoración, cuidados, medicamentos, balance y notas.
- Médico: historia clínica, diagnóstico, receta, notas, estudios e impresiones.
- Estudios de laboratorio y gabinete.
- Analítica y paneles Spark.
- Configuración de usuarios, camas, servicios, diagnósticos, respaldos y automatización.

### 4.3 Integración con la API

El servicio `src/services/api.js` utiliza Axios. La URL puede definirse mediante `VITE_API_URL`; si no existe, se construye con el host actual, el puerto `5001` y el prefijo `/api/v1`. Un interceptor añade el token almacenado en `@ineo_token` y elimina la sesión local cuando recibe un código HTTP 401.

## 5. Dependencias principales

| Capa | Dependencias relevantes |
|---|---|
| Frontend | React, React Router, Axios, Material UI, i18next y Moment |
| Backend | Flask, Flask-CORS, PyMongo, JWT y utilidades declaradas en `requirements.txt` |
| Infraestructura local | Node.js/npm, Python/pip y MongoDB |

## 6. Elementos que no deben integrarse

Por seguridad y limpieza del repositorio no deben copiarse:

- Archivos `.env` con secretos o direcciones privadas.
- Entornos `venv/` o `.venv/`.
- `node_modules/`, `dist/` y cachés.
- `__pycache__/` y archivos `*.pyc`.
- Respaldos generados y archivos reales de pacientes.
- Resultados clínicos cargados en `static/resultados/`.
- Registros, temporales y archivos generados durante la ejecución.

Se debe proporcionar `.env.example` únicamente con nombres de variables y valores de ejemplo no sensibles.

## 7. Riesgos y observaciones

| Riesgo | Impacto | Acción propuesta |
|---|---|---|
| Configuración distribuida entre código y entorno | Conexiones incorrectas al cambiar de equipo | Centralizar variables y documentar `.env.example` |
| Datos clínicos o respaldos dentro del repositorio de origen | Exposición de información | Excluirlos del repositorio de entrega |
| Dependencia del host y puerto local | Fallos de conexión frontend–API | Configurar `VITE_API_URL` y documentar puertos |
| Rutas y módulos agregados progresivamente | Integración incompleta | Incorporar archivos según el sprint y validar cada módulo |
| Ausencia de una frontera visual de capas | Dificulta mantenimiento | Adoptar la arquitectura objetivo descrita en Sprint 1 |

## 8. Criterio de finalización

MIG-001 se considera documentada cuando los repositorios, módulos, tecnologías, dependencias, datos excluidos y riesgos quedan inventariados. MIG-002 se completa con la definición de la arquitectura objetivo y la estrategia de migración descritas en los documentos complementarios.
