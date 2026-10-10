# Estrategia de ramas y ambientes — INEO

## Decisión

INEO usa tres ramas permanentes:

| Rama | Ambiente | Propósito | Despliegue |
|---|---|---|---|
| `develop` | Desarrollo | Integrar ramas de trabajo y ejecutar UT/UIT | Vercel Preview opcional; API y MongoDB locales |
| `qa` | QA | Ejecutar SIT, regresión, seguridad y UAT con datos sintéticos | Vercel Preview/QA y API/DB exclusivas de QA |
| `main` | Producción | Contener únicamente versiones aprobadas | Vercel producción y API de Render producción |

No se crea una rama `prod`: `main` cumple esa función.

## Flujo obligatorio

1. Actualizar `develop`.
2. Crear `feature/<pbl-id>-descripcion`, `fix/<descripcion>`, `test/<descripcion>` o `docs/<descripcion>`.
3. Abrir Pull Request hacia `develop`.
4. Aprobar CI, revisión de código y criterios de aceptación.
5. Al finalizar el incremento, abrir Pull Request `develop -> qa`.
6. Ejecutar en QA: SIT, regresión, seguridad, smoke y UAT con datos sintéticos.
7. Si QA aprueba, abrir Pull Request `qa -> main`.
8. Desplegar, realizar smoke test y crear una etiqueta, por ejemplo `v1.2.0`.
9. Los errores urgentes salen de `main` como `hotfix/<descripcion>` y regresan después a `develop`.

No hacer push directo a `qa` ni a `main`.

## Variables por ambiente

### Desarrollo local

Backend: copiar `backend/api_hospital/.env.example` a `.env`.

Frontend: copiar `frontend/clinica-web-react/.env.development.example` a `.env.local`.

```dotenv
VITE_API_URL=http://localhost:5001/api/v1
```

El frontend quedará en `http://localhost:5173`, la API en `http://localhost:5001` y MongoDB local en `mongodb://localhost:27017/`.

Para un ambiente integrado reproducible también puede ejecutarse:

```bash
docker compose -f compose.test.yml up --build --abort-on-container-exit
```

Ese ambiente usa API `5002`, MongoDB `27018` y datos sintéticos.

### QA

Crear servicios separados de producción:

- Proyecto o Preview de Vercel asociado a `qa`.
- API de Render exclusiva de QA.
- Base de datos `ineo_qa` o un clúster/usuario exclusivo de QA.
- Usuarios y expedientes completamente sintéticos.

Configurar en Vercel QA:

```dotenv
VITE_API_URL=https://TU-API-QA.onrender.com/api/v1
```

Configurar en Render QA: `MONGO_URI`, `MONGO_DB=ineo_qa`, `SECRET_KEY`, `JWT_SECRET_KEY`, `DEBUG=False`, `ENABLE_SCHEDULER=false` y el origen CORS de la web QA.

### Producción

Configurar en Vercel Production:

```dotenv
VITE_API_URL=https://api-clinica-jx4m.onrender.com/api/v1
```

Los secretos del backend se mantienen únicamente en Render. Nunca se copian a GitHub ni al frontend.

## Validaciones por rama

| Etapa | Validaciones mínimas |
|---|---|
| Pull Request a `develop` | Compilación, lint, UT, UIT, claves i18n y pruebas de API |
| `develop -> qa` | Todo lo anterior, SIT, contratos, Spark, roles y regresión |
| `qa -> main` | UAT aprobada, smoke test, revisión de seguridad, respaldo y plan de reversión |
| Después de producción | `/health`, login, ruta crítica, monitoreo y etiqueta de versión |

## Protección recomendada en GitHub

En Settings > Branches o Rulesets:

- `main`: exigir Pull Request, una aprobación, CI de API y web, conversaciones resueltas y bloquear force-push/eliminación.
- `qa`: exigir Pull Request y CI; bloquear force-push/eliminación.
- `develop`: exigir CI y conversaciones resueltas; impedir push directo cuando sea posible.
- Activar eliminación automática de ramas después del merge.

## Relación con Azure DevOps

Cada rama de trabajo debe incluir el identificador del PBL o de la tarea de Azure. El Pull Request debe enlazar la historia, criterios de aceptación, pruebas ejecutadas y evidencia.
