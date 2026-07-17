# Despliegue en Railway (todo el stack)

El Escáner Legislativo MX corre como **cinco servicios** en un mismo proyecto de
Railway. Railway sí puede alojar todo el stack (a diferencia de Vercel, que no
corre Celery ni bases de datos): Mongo y Redis como servicios de datos, y api,
worker y frontend construidos desde los `Dockerfile` de este monorepo.

```
┌─────────────┐   ┌─────────────┐
│  frontend   │   │   worker    │  (Celery: cola normtrace + tagger + beat)
│ (nginx/Vue) │   │ qhld-tasks  │
└──────┬──────┘   └──────┬──────┘
       │ HTTP            │ broker/back
       ▼                 ▼
┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│     api     │──▶│    mongo    │   │    redis    │
│  (FastAPI)  │   │  (datos)    │   │ broker+cache│
└─────────────┘   └─────────────┘   └─────────────┘
```

## 1. Servicios de datos

Crea en el proyecto los servicios de base de datos que ofrece Railway:

- **MongoDB** (plantilla oficial de Railway). Anota su usuario/clave/host.
- **Redis** (plantilla oficial de Railway).

> El cliente de `tipi_data` **siempre** conecta con credenciales (authSource
> `admin` por defecto). Si usas la plantilla de Mongo de Railway, toma su
> `MONGO_INITDB_ROOT_USERNAME/PASSWORD` y su host privado para las variables de
> abajo. En local (`docker-compose.yml`) esas credenciales son `qhld/qhld`.

## 2. Servicios de aplicación (desde este repo)

Para cada uno: **New Service → GitHub Repo → este repositorio**, deja el
*Root Directory* en `/` (la raíz del monorepo; los Dockerfiles necesitan
`packages/` como contexto) y apunta *Config as code* al JSON correspondiente:

| Servicio  | Config as code                | Dockerfile                        |
|-----------|-------------------------------|-----------------------------------|
| api       | `deploy/railway/api.json`     | `api/Dockerfile`                  |
| worker    | `deploy/railway/worker.json`  | `packages/qhld-tasks/Dockerfile`  |
| frontend  | `deploy/railway/frontend.json`| `frontend/Dockerfile-mx`          |

El `api` escucha en `$PORT` (Railway lo inyecta); expón un dominio público para
él. El `worker` no expone puerto. El `frontend` sirve nginx en el puerto 80.

## 3. Variables de entorno

### api
```
MONGO_HOST=<host privado de mongo>
MONGO_PORT=27017
MONGO_DB_NAME=mx
MONGO_USER=<usuario mongo>
MONGO_PASSWORD=<clave mongo>
CACHE_REDIS_HOST=<host privado de redis>
CACHE_REDIS_PORT=6379
BROKER=redis://<host redis>:6379/2
RESULT_BACKEND=redis://<host redis>:6379/3
TAGGER_MAX_WORDS=5000
COUNTRY=mexico           # managers de tipo/estatus de iniciativa mexicanos (F1)
USE_ALERTS=False
```

### worker
```
MONGO_HOST=<host privado de mongo>
MONGO_PORT=27017
MONGO_DB_NAME=mx
MONGO_USER=<usuario mongo>
MONGO_PASSWORD=<clave mongo>
CACHE_REDIS_HOST=<host privado de redis>
BROKER=redis://<host redis>:6379/2
RESULT_BACKEND=redis://<host redis>:6379/3
```

Cuando exista la etapa NormTrace (F4), el worker necesitará además
`LLM_PROVIDER`, `LLM_MODEL`, `LLM_API_KEY` (nunca commitear la clave).

### frontend
La URL del backend se **hornea en build** (Vite). Define como *build variable*:
```
VITE_VUE_APP_BACKEND_URL=https://<dominio-publico-del-api>.up.railway.app
```
El resto de la config sale de `frontend/.env.mx`.

## 4. Cargar el diccionario (una vez)

Tras el primer deploy del `api`, carga el seed mexicano en Mongo. Desde la
consola del servicio `api` (o un job one-off con la misma imagen y variables):

```bash
python /app/knowledgebase/load_kb.py                                  # 17 ODS (kb "mx")
python /app/knowledgebase/load_kb.py /app/knowledgebase/seeds/rsi_mx.seed.json  # marco RSI (kb "rsi_mx")
```

Verifica:
```bash
curl "https://<api>.up.railway.app/topics/?knowledgebase=mx"   # 3 ODS mexicanos
```

## 5. Notas

- Los `Dockerfile` de producción usan contexto de build = raíz del monorepo y
  hornean el código (Railway no monta volúmenes). Los `Dockerfile-dev` son solo
  para `docker compose` local (usan bind-mounts y `--reload`).
- El puerto del `api` sale de `$PORT`; no lo fijes a mano en Railway.
- Escalado: el `worker` puede replicarse; el `-B` (beat) debe correr en **una
  sola** réplica para no duplicar tareas periódicas. Si escalas el worker,
  separa un servicio `beat` (`celery -A tipi_tasks beat`) y quita `-B` del worker.
