# Generador de Contenido IA

App web privada para generar contenido orgánico y publicitario para Instagram usando Claude.

## Stack

- **Backend:** FastAPI + SQLAlchemy + PostgreSQL + JWT + Anthropic SDK + Playwright
- **Frontend:** React 18 + Vite + React Router
- **Despliegue:** Docker single-container en Railway

## Funcionalidades

- Login privado (sistema cerrado, sin registro público)
- Generador de contenido con dolores del cliente + formato + idea
- Scraper de URL para autopoblar el contexto del negocio
- Biblioteca de plantillas guardadas
- Dolores del cliente editables por usuario
- Gestión de usuarios multi-cuenta (admin)
- Cambio forzado de contraseña al primer login

## Variables de entorno

Ver `.env.example`. En Railway, el plugin de Postgres inyecta `DATABASE_URL` automáticamente.

| Variable | Notas |
|---|---|
| `DATABASE_URL` | Auto-inyectada por Railway |
| `SECRET_KEY` | Genera con `python -c "import secrets; print(secrets.token_urlsafe(64))"` |
| `ADMIN_EMAIL` | Solo se usa la primera vez para crear el admin |
| `ADMIN_PASSWORD` | Solo se usa la primera vez para crear el admin |
| `ANTHROPIC_API_KEY` | Tu API key de console.anthropic.com |
| `ANTHROPIC_MODEL` | Default: `claude-haiku-4-5-20251001` |
| `APP_ENV` | `production` oculta las docs OpenAPI |

## Desarrollo local

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend (otra terminal)
cd frontend
npm install
npm run dev
```

Abre http://localhost:5173

## Despliegue en Railway

1. Conecta este repo en Railway
2. Agrega plugin de PostgreSQL
3. Define las variables de entorno (todas menos `DATABASE_URL`)
4. Deploy
