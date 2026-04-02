# Loginco Corp

> **"Cero estrés, aduanal"**

Plataforma comercial principal de Loginco (`loginco.com.mx`) que centraliza y comercializa tres líneas de servicio:

| Servicio | Subdominio |
|---|---|
| Agencia Aduanal | `agencia-aduanal.loginco.com.mx` |
| Bodega & Patio | `bodega-patio.loginco.com.mx` |
| Transporte | `transporte.loginco.com.mx` |

## Stack Tecnológico

- **Backend:** Python 3.12 · Django 5.x
- **Base de datos:** SQLite (desarrollo) · PostgreSQL 16+ (producción)
- **CMS Admin:** Django Admin + [Unfold](https://github.com/unfoldadmin/django-unfold)
- **IA:** Anthropic Claude API (`claude-sonnet-4-6`)
- **Media:** django-imagekit (conversión WebP automática en 3 tamaños)
- **SEO:** django-meta · sitemaps · Open Graph · JSON-LD
- **Tareas programadas:** django-apscheduler (sin Redis)
- **Servidor:** Gunicorn + Nginx · WhiteNoise para estáticos
- **Linting:** Ruff

## Requisitos Previos

- Python 3.12+
- pip
- PostgreSQL 16+ (solo para producción)

## Instalación (Desarrollo)

```bash
# Clonar y entrar al proyecto
git clone <url-del-repo>
cd "Loginco Corp"

# Crear entorno virtual
python -m venv .venv
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements/development.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus valores (DJANGO_SECRET_KEY es obligatorio)

# Aplicar migraciones y crear superusuario
python manage.py migrate
python manage.py createsuperuser

# Iniciar servidor de desarrollo
python manage.py runserver
```

El servidor arranca en `http://localhost:8000`. APScheduler inicia automáticamente con el servidor.

### Con Docker

```bash
docker compose up -d
docker compose run web python manage.py migrate
docker compose run web python manage.py createsuperuser
```

## Estructura del Proyecto

```
config/                     Configuración Django
├── settings/
│   ├── base.py             Configuración compartida
│   ├── development.py      SQLite + debug toolbar
│   └── production.py       PostgreSQL + WhiteNoise
├── urls.py
├── wsgi.py / asgi.py

apps/
├── core/                   Modelos base (TimeStampedModel) + scheduler
├── pages/                  Páginas estáticas (Home, About, Contact)
├── services/               Landing de servicios
├── blog/                   CMS: Post, Category, Tag, SiteTarget
├── media_manager/          MediaFile con WebP automático (3 tamaños)
├── seo/                    SEOMixin + sitemaps
└── ai_assistant/           Integración Claude API (Fase 3)

templates/                  Templates Django (base.html con SEO completo)
static/                     Archivos estáticos (CSS, JS, imágenes)
media/                      Archivos subidos (excluido de git)
requirements/               Dependencias por entorno
```

## Apps Principales

### Blog (CMS)

Motor de contenido central. Los posts se clasifican por `Category`, `Tag` y `SiteTarget` (sub-sitio de destino). Soporta publicación programada vía APScheduler (job cada minuto).

### Media Manager

Gestión centralizada de imágenes y videos. Las imágenes se convierten automáticamente a WebP en tres tamaños (400px, 800px, 1280px) mediante django-imagekit y un signal `post_save`.

### SEO

`SEOMixin` abstracto disponible para cualquier modelo. Incluye campos para meta tags, Open Graph, Twitter Card y JSON-LD. Sitemaps registrados en `/sitemap.xml`.

### AI Assistant (Fase 3 — pendiente)

Generación de contenido asistida por IA desde el admin. Tipos: `full_post`, `meta_only`, `excerpt`, `improve`, `alt_text`.

## URLs

| Ruta | Vista |
|---|---|
| `/` | Home |
| `/nosotros/` | About |
| `/contacto/` | Contact |
| `/servicios/` | Índice de servicios |
| `/blog/` | Lista de posts |
| `/blog/<slug>/` | Detalle de post |
| `/blog/categoria/<slug>/` | Posts por categoría |
| `/sitemap.xml` | Sitemap index |
| `/admin/` | Django Admin (CMS) |

## Variables de Entorno

Copia `.env.example` a `.env` y configura:

| Variable | Requerida | Descripción |
|---|---|---|
| `DJANGO_SECRET_KEY` | ✅ | Clave secreta de Django |
| `DJANGO_DEBUG` | — | `True` en desarrollo (default) |
| `DJANGO_ALLOWED_HOSTS` | — | Hosts permitidos (separados por coma) |
| `ANTHROPIC_API_KEY` | — | API key para generación de contenido IA |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | Producción | Credenciales PostgreSQL |

Ver `.env.example` para la lista completa.

## Comandos Útiles

```bash
# Tests
python manage.py test apps/                          # Todos los tests
python manage.py test apps.blog.tests                # Tests de una app
python manage.py test apps.blog.tests.PostModelTest  # Clase específica

# Linting y formateo
ruff check .
ruff format .

# Migraciones
python manage.py makemigrations
python manage.py migrate
```

## Producción

El stack de producción usa Docker Compose con tres servicios:

```bash
docker compose -f docker-compose.prod.yml up -d
```

- **web** — Gunicorn (3 workers)
- **db** — PostgreSQL 16 Alpine
- **nginx** — Proxy reverso con SSL (Let's Encrypt)

La configuración de Nginx está en `nginx.conf` (HTTPS, gzip, headers de seguridad).

## Estado del Proyecto

| Fase | Estado |
|---|---|
| 1 — Fundación (modelos, admin, Docker) | ✅ Completada |
| 2 — CMS Core (posts, sitemaps, templates) | ✅ Completada (parcial) |
| 3 — Integración IA | ⏳ Pendiente |
| 4 — Frontend público (CSS mobile-first) | ⏳ Pendiente |
| 5 — Optimización y deploy | ⏳ Pendiente |

Consultar `context.md` para el detalle completo de cada fase.

## Licencia

Proyecto privado — Loginco Corp. Todos los derechos reservados.
