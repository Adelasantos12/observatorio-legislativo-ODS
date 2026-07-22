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
| engine    | `deploy/railway/engine.json`  | `engine/Dockerfile` (opcional)    |

El `api` escucha en `$PORT` (Railway lo inyecta); expón un dominio público para
él. El `worker` no expone puerto. El `frontend` sirve nginx en el puerto 80.

El servicio **`engine` es opcional** y solo hace falta para los trabajos por
lotes (`qhld sil-ejecutivo`, `iniclave-minutas`, `minutas-coding`,
`normtrace-atribucion`). Trae el CLI `qhld` y las dependencias de OCR. No expone
puerto. Necesita las mismas variables de Mongo que el api (`MONGO_HOST`,
`MONGO_PORT`, `MONGO_DB_NAME`, `MONGO_USER`, `MONGO_PASSWORD`). Para crearlo:
New Service → Deploy from repo → en **Settings → Build** pon *Dockerfile Path* =
`engine/Dockerfile` (o *Config file* = `deploy/railway/engine.json`). La **siembra
del api NO necesita este servicio**.

## 3. Variables de entorno

> **Redis en Railway requiere autenticación.** La plantilla de Redis expone la
> conexión con credenciales en `REDIS_URL` (algo como
> `redis://default:CLAVE@redis.railway.internal:6379`). **La forma recomendada es
> añadir una sola variable de referencia** en el api y en el worker:
> `REDIS_URL=${{Redis.REDIS_URL}}` (ajusta `Redis` al nombre real de tu servicio).
> El código deriva de ahí el broker (db 2), el backend (db 3) y la caché (db 8)
> con su contraseña. Si en su lugar fijas `BROKER`/`RESULT_BACKEND` a mano, la URL
> **debe** incluir usuario y contraseña, o el worker fallará con
> `Authentication required`. Sin `REDIS_URL` ni `BROKER` (docker-compose local) se
> usan los defaults `redis://redis:6379`.

### api
```
MONGO_HOST=<host privado de mongo>
MONGO_PORT=27017
MONGO_DB_NAME=mx
MONGO_USER=<usuario mongo>
MONGO_PASSWORD=<clave mongo>
REDIS_URL=${{Redis.REDIS_URL}}   # referencia a la plantilla Redis (con credenciales)
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
REDIS_URL=${{Redis.REDIS_URL}}   # referencia a la plantilla Redis (con credenciales)
```

Codificación NormTrace (etapa 3) — el worker consume también la cola `normtrace`
(ya incluido en el `CMD` del Dockerfile: `-Q celery,normtrace`). Variables:
```
LLM_PROVIDER=mock          # mock (heurístico local, sin clave) | anthropic | openai
LLM_MODEL=                 # p. ej. claude-sonnet-5 o gpt-4o-mini
LLM_API_KEY=               # SOLO si LLM_PROVIDER != mock; nunca commitear
NORMTRACE_MAX_UNITS=50     # presupuesto de unidades por documento
```
Con `LLM_PROVIDER=mock` (por defecto) el escáner deep funciona sin clave ni costo
(codificación heurística marcada `needs_human_review`). El cerebro jurídico y el
esquema van horneados en la imagen del worker (`COPY normtrace`).

### Atribución de origen de las minutas (OCR de dictámenes)

Las minutas que no son de origen Ejecutivo llevan su grupo parlamentario en el
PDF del dictamen. Esos PDFs son **escaneos sin capa de texto**, así que el job
hace **OCR** (la imagen del `engine` ya trae `tesseract-ocr`, `tesseract-ocr-spa`
y `poppler-utils`). Se corre desde la imagen del `engine`:

```bash
qhld normtrace-atribucion            # usa la base por defecto verificada
# o con base/pruebas explícitas:
qhld normtrace-atribucion --base-url "https://www.diputados.gob.mx/LeyesBiblio/iniclave/" --limit 20
```

Variables (opcionales; ya traen default correcto):
```
INICLAVE_PDF_BASE=https://www.diputados.gob.mx/LeyesBiblio/iniclave/  # {base}66/{CLAVE}/{archivo}.pdf
NORMTRACE_OCR_PAGES=3     # primeras N páginas por dictamen
```

Es **incremental**: solo toca minutas sin origen documentado, nunca pisa
`validado_autora`, y lo que el OCR no reconoce queda "por documentar" (jamás se
inventa el grupo). Reporta "X atribuidas, Y sin dictamen, Z por documentar".

### frontend
La URL del backend se **hornea en build** (Vite). Define como *build variable*:
```
VITE_VUE_APP_BACKEND_URL=https://<dominio-publico-del-api>.up.railway.app
```
El resto de la config sale de `frontend/.env.mx`.

## 4. Cargar los datos (una vez)

Tras el primer deploy del `api`, **hay que sembrar Mongo**: sin esto el escáner
no tiene diccionario y los tableros Huella/Minutas salen en 0 (y los expedientes
dan "no encontrado"). Desde la consola del servicio `api` (pestaña del servicio →
*Shell/Terminal*, o un job one-off con la misma imagen y variables), un solo
comando lo carga todo (idempotente, son upserts):

```bash
python /app/knowledgebase/load_all.py
```

Esto carga, en orden e idempotente, con estos conteos esperados al corte:

| Colección / kb | Conteo |
|---|---|
| `topics` kb `mx` (diccionario ODS) | 17 |
| `topics` kb `rsi_mx` (marco RSI) | 8 |
| `executive_initiatives` (Huella módulo A) | 82 |
| `minutas` (Huella módulo B, LXVI) | 139 (62 DOF · 75 en revisora · 2 devueltas) |
| ficha dorada LGA (servida de disco, no colección) | 34 filas |

Volver a correrlo no duplica ni pisa la codificación (`validado_autora` intacto).

> El tablero `/huella/ejecutivo` cachea su agregado 1 h. Si ya lo habías abierto
> vacío, **reinicia el servicio `api`** tras sembrar (o espera al TTL) para ver
> los números. El análisis NormTrace de la Ley General de Aguas se sirve del CSV
> dorado horneado en la imagen, no depende de este seed.

Verifica:
```bash
curl "https://<api>.up.railway.app/topics/?knowledgebase=mx"     # 3 ODS mexicanos
curl "https://<api>.up.railway.app/huella/ejecutivo" | head -c 300   # KPIs != 0
curl "https://<api>.up.railway.app/minutas/" | head -c 300           # minutas != 0
```

## 5. Notas

- Los `Dockerfile` de producción usan contexto de build = raíz del monorepo y
  hornean el código (Railway no monta volúmenes). Los `Dockerfile-dev` son solo
  para `docker compose` local (usan bind-mounts y `--reload`).
- El puerto del `api` sale de `$PORT`; no lo fijes a mano en Railway.
- Escalado: el `worker` puede replicarse; el `-B` (beat) debe correr en **una
  sola** réplica para no duplicar tareas periódicas. Si escalas el worker,
  separa un servicio `beat` (`celery -A tipi_tasks beat`) y quita `-B` del worker.
