# Generador de Contenido IA — Fase 1

Aplicación web privada que convierte un dolor del cliente + formato en texto listo
para publicar en Instagram, usando el contexto del negocio guardado en la BD.

## Stack

- **Backend:** FastAPI · SQLAlchemy 2 · PostgreSQL · JWT · Anthropic SDK
- **Frontend:** React 18 · Vite · React Router
- **Despliegue:** Docker multi-stage en Railway (un solo servicio)

## Estructura

```
.
├── Dockerfile              # Multi-stage: compila frontend + sirve con FastAPI
├── railway.json            # Configuración de despliegue
├── .env.example            # Plantilla de variables de entorno
├── backend/
│   ├── requirements.txt
│   └── app/
│       ├── main.py         # Entry FastAPI, monta routers y sirve estáticos
│       ├── config.py       # Settings via pydantic-settings
│       ├── database.py     # SQLAlchemy engine + sesiones
│       ├── models.py       # User, BusinessContext
│       ├── schemas.py      # Pydantic schemas
│       ├── security.py     # Hashing + JWT
│       ├── deps.py         # get_current_user
│       ├── seed.py         # Crea admin inicial al arranque
│       ├── routers/        # auth, catalogs, content, context
│       └── services/
│           └── ai_service.py   # Cliente Anthropic + prompts
└── frontend/
    ├── package.json
    ├── vite.config.js
    ├── index.html
    └── src/
        ├── main.jsx, App.jsx, api.js, auth.jsx, index.css
        ├── components/Layout.jsx
        └── pages/Login.jsx, Generator.jsx, Settings.jsx
```

## Variables de entorno

Ver [`.env.example`](.env.example). Las críticas:

| Variable | Descripción |
|---|---|
| `DATABASE_URL` | URL Postgres. Railway la inyecta automáticamente al agregar el plugin. |
| `SECRET_KEY` | Clave JWT. Generar con `python -c "import secrets; print(secrets.token_urlsafe(64))"` |
| `ADMIN_EMAIL` / `ADMIN_PASSWORD` | Usuario creado en el primer arranque. |
| `ANTHROPIC_API_KEY` | Tu key de [console.anthropic.com](https://console.anthropic.com/). |
| `ANTHROPIC_MODEL` | Por defecto `claude-haiku-4-5-20251001`. |
| `APP_ENV` | `production` (oculta docs) o `development`. |

## Desarrollo local

### Opción A: Backend + frontend separados (recomendado para desarrollar)

```bash
# 1) Postgres local
docker run --name pg -e POSTGRES_PASSWORD=dev -e POSTGRES_DB=app -p 5432:5432 -d postgres:16

# 2) Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example ../.env   # editar valores
export $(grep -v '^#' ../.env | xargs)   # cargar al shell
uvicorn app.main:app --reload --port 8000

# 3) Frontend (otra terminal)
cd frontend
npm install
npm run dev   # http://localhost:5173, hace proxy de /api a :8000
```

Para que CORS funcione en local, añade en `.env`:
```
CORS_ORIGINS=http://localhost:5173
```

### Opción B: Docker (mismo flow que producción)

```bash
docker build -t generador .
docker run --rm -p 8000:8000 --env-file .env generador
# abre http://localhost:8000
```

## Despliegue en Railway

1. Crea proyecto nuevo en [railway.app](https://railway.app).
2. **Add Service → Database → PostgreSQL**. Railway expone `DATABASE_URL` automáticamente.
3. **Add Service → GitHub Repo** (o sube el código por CLI). Railway detecta `Dockerfile` y `railway.json`.
4. En el servicio, ve a **Variables** y agrega:
   - `SECRET_KEY` (generar como se indica arriba)
   - `ADMIN_EMAIL`, `ADMIN_PASSWORD`
   - `ANTHROPIC_API_KEY`
   - `ANTHROPIC_MODEL` (opcional, default Haiku 4.5)
   - `APP_ENV=production`
5. **Settings → Networking → Generate Domain** para tener una URL pública.
6. Cuando hagas push a `main`, Railway redespliega solo.
7. (Opcional) Después del primer login, **borra `ADMIN_PASSWORD`** de Railway. El seed
   solo corre si la BD está vacía, así que no se vuelve a usar.

## Notas de seguridad

- **No hay registro público.** El único modo de tener cuenta es definir
  `ADMIN_EMAIL`/`ADMIN_PASSWORD` antes del primer arranque.
- **Contraseñas con bcrypt** (no SHA, no MD5).
- **JWT firmado HS256** con expiración configurable.
- **Docs OpenAPI ocultas** cuando `APP_ENV=production`.
- **API key de Anthropic vive solo en el servidor** — el navegador nunca la ve.
- **El contenedor corre como usuario sin privilegios** (no root).
- **Cookies/localStorage:** el token va en localStorage para simplicidad. Si quieres
  máxima seguridad contra XSS, considera migrar a cookies HttpOnly en Fase 2.

## Próximos pasos (Fase 2)

- Migrar `create_all` → Alembic para gestionar el cambio de esquema.
- Web scraper (BeautifulSoup + Playwright) que autocompleta `BusinessContext`.
- Tabla `saved_templates` + biblioteca (Fase 3).
- Editor de catálogos de dolores (Fase 3).
