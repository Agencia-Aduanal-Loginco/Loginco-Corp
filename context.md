# Loginco Corp — Plataforma Comercial Principal
> Documento de planificación e implementación
> Creado: 2026-03-31
> Última actualización: 2026-04-08
> Estado: En desarrollo — Fase 1 ✓, Fase 2 ✓, Fase 3 ✓, Fase 4 ✓ (parcial), Fase 5 pendiente

---

## 1. Visión General

**Dominio:** `loginco.com.mx`
**Slogan:** "Cero estrés, aduanal"
**Propósito:** Hub comercial que centraliza y comercializa los tres servicios de Loginco:

| Servicio | Dominio | Descripción |
|---|---|---|
| Agencia Aduanal | agencia-aduanal.loginco.com.mx | Trámites y gestión aduanal |
| Bodega & Patio | bodega-patio.loginco.com.mx | Almacenaje y patio de maniobras |
| Transporte | transporte.loginco.com.mx | Servicio de transporte de carga |

### Objetivos principales
- Posicionar `loginco.com.mx` como la cara comercial de todo el grupo
- CMS centralizado para publicar contenido SEO en los tres sub-sitios
- Generación de contenido asistida por IA (Claude API de Anthropic)
- Experiencia 100% mobile-first
- Soporte para imágenes y video

---

## 2. Stack Tecnológico

| Capa | Tecnología | Notas |
|---|---|---|
| Lenguaje | Python 3.12+ | |
| Framework | Django 5.x | |
| Base de datos | SQLite (dev) / PostgreSQL 16+ (prod) | Dev usa SQLite por simplicidad |
| ORM / Migraciones | Django ORM | |
| Editor WYSIWYG | TipTap (vía JS bundle) | Bundle en `static/js/tiptap-bundle.js` ✓; widget `TiptapWidget` en `apps/blog/widgets.py` ✓ |
| IA / Contenido | DigitalOcean AI Platform (`llama3.3-70b-instruct`) | Cliente en `apps/ai_assistant/client.py` ✓ — OpenAI-compatible endpoint vía SDK `openai` |
| Media (imágenes) | django-imagekit + Pillow | WebP lazy via `ImageSpecField`; pre-generación en signal `post_save` |
| Media (video) | Campo `video_file` + `video_embed_url` | Subida directa o embed externo (YouTube/Vimeo) |
| Almacenamiento estático | WhiteNoise (dev y prod) | S3-compatible configurable en producción |
| CSS / UI Admin | Unfold | Tema moderno, responsive, azul cielo como color primario |
| Servidor WSGI | Gunicorn | |
| Proxy reverso | Nginx | |
| Caché | locmem (dev) / DB backend (prod) | Sin Redis |
| Tareas programadas | django-apscheduler | Job `publish_scheduled_posts` cada minuto; scheduler en `apps/core/scheduler.py` |
| SEO | django-meta + sitemap nativo | Open Graph, Twitter Card, JSON-LD en `base.html` |
| Variables de entorno | python-decouple | |
| Debug (dev) | django-debug-toolbar | Solo en desarrollo |
| Linting | ruff | `ruff check .` / `ruff format .` |
| Idioma | Español (es-MX) / America/Mexico_City | |

---

## 3. Estructura del Proyecto Django

```
loginco/                          # Directorio raíz del proyecto
├── config/                       # Configuración del proyecto Django
│   ├── settings/
│   │   ├── base.py               # Configuración base compartida ✓
│   │   ├── development.py        # SQLite + debug_toolbar + cache locmem ✓
│   │   └── production.py         # PostgreSQL via psycopg[binary] ✓
│   ├── urls.py                   # Rutas principales + sitemaps registrados ✓
│   ├── wsgi.py                   ✓
│   └── asgi.py                   ✓
├── apps/
│   ├── core/                     # TimeStampedModel abstracto + scheduler APScheduler ✓
│   │   ├── models.py             # TimeStampedModel ✓
│   │   └── scheduler.py          # get_scheduler() + start_scheduler() + jobs registrados ✓
│   ├── pages/                    # HomeView, AboutView, ContactView ✓
│   │   ├── views.py              # TemplateView genéricas ✓
│   │   └── urls.py               ✓
│   ├── services/                 # Página índice de servicios ✓
│   │   ├── views.py              ✓
│   │   └── urls.py               ✓
│   ├── blog/                     # CMS principal ✓
│   │   ├── models.py             # Post, Category, Tag, SiteTarget ✓
│   │   ├── admin.py              # Admin Unfold enriquecido (sin TipTap aún) ✓
│   │   ├── views.py              # PostListView, PostDetailView, CategoryDetailView ✓
│   │   ├── jobs.py               # publish_scheduled_posts (APScheduler) ✓
│   │   ├── sitemaps.py           # PostSitemap, CategorySitemap ✓
│   │   └── urls.py               ✓
│   ├── media_manager/            # Gestión centralizada de imágenes y videos ✓
│   │   ├── models.py             # MediaFile con ImageSpecField WebP ✓
│   │   ├── signals.py            # pre_generate_webp_specs en post_save ✓
│   │   └── admin.py              # MediaFileAdmin — miniatura en list, preview en detalle ✓
│   ├── seo/                      # SEOMixin abstracto + sitemaps estáticos ✓
│   │   ├── models.py             # SEOMixin ✓
│   │   └── sitemaps.py           # StaticViewSitemap ✓
│   └── ai_assistant/             # **Fase 3 — completada** ✓
│       ├── views.py              # GenerateContentView — lógica completa con rate limiting ✓
│       ├── urls.py               # /admin/ai/generate/ ✓
│       ├── client.py             # Cliente DO Gradient singleton (llama3.3-70b-instruct, OpenAI SDK) ✓
│       ├── prompts.py            # Biblioteca de prompts por tipo (full_post, meta_only, excerpt, improve, alt_text) ✓
│       ├── models.py             # AIGenerationLog — registro de generaciones con tokens ✓
│       └── admin.py              # AIGenerationLogAdmin (solo lectura) ✓
├── templates/
│   ├── base.html                 # SEO completo: meta, OG, Twitter, JSON-LD ✓
│   ├── admin/
│   │   └── blog/post/
│   │       └── change_form.html  # Preview SEO en tiempo real (snippet Google) + contadores ✓
│   ├── pages/
│   │   ├── home.html             # Hero + cards + blog reciente; <picture> + srcset ✓
│   │   ├── about.html            # JSON-LD Organization ✓
│   │   └── contact.html          # JSON-LD ContactPage ✓
│   ├── blog/
│   │   ├── post_list.html        # <picture> + loading="lazy" ✓
│   │   ├── post_detail.html      # <picture> + fetchpriority="high" + JSON-LD BlogPosting ✓
│   │   └── category_detail.html  # <picture> + loading="lazy" ✓
│   └── services/
│       └── index.html            # JSON-LD ItemList (3 servicios) ✓
├── static/
│   ├── css/
│   │   ├── main.css              # Sistema de diseño completo — 1800+ líneas, mobile-first ✓
│   │   └── tiptap-editor.css     # Estilos del editor TipTap en el admin ✓
│   ├── js/
│   │   ├── tiptap-bundle.js      # Bundle minificado del editor TipTap ✓
│   │   └── ai-assistant.js       # Modal + AJAX para el asistente IA en el admin ✓
│   └── img/                      # Logotipos e isotipo Loginco Corp ✓
├── media/                        # Archivos subidos (ignorado en git)
├── requirements/
│   ├── base.txt                  ✓
│   ├── development.txt           # -r base.txt + ruff + django-debug-toolbar ✓
│   └── production.txt            # -r base.txt + psycopg[binary] ✓
├── .env.example
├── manage.py
├── Dockerfile                    ✓
├── docker-compose.yml            ✓
├── docker-compose.prod.yml       ✓
├── nginx.conf                    ✓
└── js_src/                       # Fuentes TipTap (node_modules + tiptap-editor.js) ✓
```

---

## 4. Modelos de Base de Datos (Estado Actual)

### 4.1 Modelo SEO Base (`apps/seo/models.py`) ✓

```python
class SEOMixin(models.Model):
    """Mixin abstracto para cualquier modelo con necesidades SEO."""
    meta_title       = models.CharField(max_length=70, blank=True)
    meta_description = models.TextField(max_length=160, blank=True)
    meta_keywords    = models.CharField(max_length=255, blank=True)
    og_title         = models.CharField(max_length=95, blank=True)
    og_description   = models.TextField(max_length=200, blank=True)
    # NOTA: og_image FK a MediaFile NO implementado — se omitió del diseño original
    canonical_url    = models.URLField(blank=True)
    no_index         = models.BooleanField(default=False)
    schema_markup    = models.JSONField(default=dict, blank=True)  # JSON-LD

    # Métodos helper:
    # get_effective_meta_title() → meta_title o fallback a title
    # get_effective_og_title()   → og_title o meta_title
    # get_effective_og_description() → og_description o meta_description

    class Meta:
        abstract = True
```

> **Decisión:** `og_image` no es un campo del modelo. Las templates usan `featured_image` del Post directamente.

### 4.2 Modelo base con timestamps (`apps/core/models.py`) ✓

```python
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True
```

### 4.3 Publicaciones CMS (`apps/blog/models.py`) ✓

```python
class SiteTarget(models.Model):
    name        = models.CharField(max_length=100)
    domain      = models.URLField()         # URL completa, ej: https://agencia-aduanal.loginco.com.mx
    slug        = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    is_active   = models.BooleanField(default=True)

class Category(TimeStampedModel):
    name         = models.CharField(max_length=100)
    slug         = models.SlugField(unique=True)
    description  = models.TextField(blank=True)
    site_targets = models.ManyToManyField(SiteTarget, blank=True)

    def get_absolute_url(self):
        return reverse("blog:category", kwargs={"slug": self.slug})

class Tag(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)

class Post(SEOMixin, TimeStampedModel):
    # STATUS_DRAFT | STATUS_SCHEDULED | STATUS_PUBLISHED
    title          = models.CharField(max_length=200)
    slug           = models.SlugField(unique=True, max_length=220)
    excerpt        = models.TextField(max_length=300)
    body           = models.TextField()           # HTML de TipTap
    featured_image = models.ForeignKey('media_manager.MediaFile', null=True, blank=True,
                                       on_delete=SET_NULL, limit_choices_to={"file_type": "image"})
    video_url      = models.URLField(blank=True)  # Embed externo (YouTube/Vimeo)
    category       = models.ForeignKey(Category, on_delete=PROTECT)
    tags           = models.ManyToManyField(Tag, blank=True)
    site_targets   = models.ManyToManyField(SiteTarget)
    status         = models.CharField(choices=[draft, scheduled, published], default=draft, db_index=True)
    published_at   = models.DateTimeField(null=True, blank=True)
    author         = models.ForeignKey(AUTH_USER_MODEL, on_delete=PROTECT)
    ai_generated   = models.BooleanField(default=False)
    reading_time   = models.PositiveSmallIntegerField(default=0)  # Auto-calculado en save()
    # created_at / updated_at heredados de TimeStampedModel

    # save() auto-calcula reading_time (200 palabras/min)
    # save() establece published_at=now() al publicar si está vacío
```

### 4.4 Media Manager (`apps/media_manager/models.py`) ✓

```python
class MediaFile(TimeStampedModel):
    file_type       = models.CharField(choices=[image, video], db_index=True)
    image           = models.ImageField(upload_to='media/images/%Y/%m/')   # Solo imágenes
    video_file      = models.FileField(upload_to='media/videos/%Y/%m/')    # Video subido directo
    video_embed_url = models.URLField(blank=True)                          # YouTube/Vimeo
    title           = models.CharField(max_length=200)
    alt_text        = models.CharField(max_length=200, blank=True)
    caption         = models.TextField(blank=True)
    width           = models.PositiveIntegerField(null=True)   # Auto-poblado en save()
    height          = models.PositiveIntegerField(null=True)
    file_size       = models.PositiveIntegerField(null=True)
    uploaded_by     = models.ForeignKey(AUTH_USER_MODEL, null=True)

    # Specs WebP generadas por imagekit (lazy) — pre-generadas en signal post_save:
    image_thumb_webp = ImageSpecField(source='image', ResizeToFit(400,300),  WEBP, q85)
    image_md_webp    = ImageSpecField(source='image', ResizeToFit(800,600),  WEBP, q85)
    image_lg_webp    = ImageSpecField(source='image', ResizeToFit(1280,960), WEBP, q85)
```

> **Diferencia vs diseño original:** Se usan dos campos separados (`image`, `video_file`) en lugar de un único `file = FileField`. El campo `webp_version` del diseño fue reemplazado por tres `ImageSpecField` de imagekit.

---

## 5. CMS — Django Admin Enriquecido

### 5.1 Estado actual del Admin

| Componente | Estado | Notas |
|---|---|---|
| Tema visual Unfold | ✓ Implementado | Color primario azul Loginco (#3434b0); navegación lateral configurada |
| Registro de modelos | ✓ Implementado | SiteTarget, Category, Tag, Post con fieldsets completos |
| Editor TipTap | ✓ Implementado | Bundle en `static/js/tiptap-bundle.js`; `TiptapWidget` en `apps/blog/widgets.py` |
| Asistente IA | ✓ Implementado | DO Gradient (llama3.3-70b-instruct); modal JS en `ai-assistant.js`; log en `AIGenerationLog` |
| Preview SEO | ✓ Implementado | Snippet Google en `templates/admin/blog/post/change_form.html` |
| Admin MediaFile | ✓ Implementado | `media_manager/admin.py` con miniatura, dimensiones, preview |
| Admin AIGenerationLog | ✓ Implementado | Solo lectura; registra modelo, tokens, usuario, éxito/error |
| Programación posts | ✓ Implementado | APScheduler job cada minuto publica scheduled → published |

### 5.2 Configuración Unfold actual (`config/settings/base.py`)

- `SITE_TITLE`: "Loginco Corp"
- `BORDER_RADIUS`: 6px
- Color `primary`: azul cielo (sky-500: `14 165 233`)
- Sidebar con secciones: Contenido / Media / Sistema
- Incluye link a tareas programadas (django_apscheduler)

### 5.3 Flujo del Asistente IA (diseño — Fase 3)

```
[Admin: formulario de Post]
    ↓
[Usuario llena: Título, Categoría, Sitio destino]
    ↓
[Clic "Generar contenido con IA"]
    ↓
[AJAX POST → /admin/ai/generate/]
    ↓
[ai_assistant/views.py → Anthropic SDK]   ← Pendiente implementar
    ↓
[Prompt estructurado: título + servicio + longitud + keywords + tono]
    ↓
[Respuesta: body HTML + meta_title + meta_description + excerpt]
    ↓
[Inyectar en campos del formulario via JS]
```

---

## 6. Estrategia SEO

### 6.1 SEO On-Page — implementado en `templates/base.html` ✓

- `<title>` dinámico: `object.get_effective_meta_title()` con fallback
- `<meta name="description">` desde `object.meta_description`
- `<meta name="keywords">` condicional
- `<meta name="robots">` controlado por `object.no_index`
- `<link rel="canonical">` desde `object.canonical_url`
- Open Graph: `og:title`, `og:description`, `og:image`, `og:type`, `og:locale`, `og:site_name`
- Twitter Card: `summary_large_image`
- JSON-LD: bloque `{% block schema_markup %}` con `object.schema_markup|safe`

### 6.2 SEO Técnico ✓

- Sitemaps registrados en `config/urls.py`:
  - `sitemap.xml` (index con `StaticViewSitemap` + `PostSitemap` + `CategorySitemap`)
- `robots.txt` — **pendiente** (no implementado)
- `PostSitemap`, `CategorySitemap` en `apps/blog/sitemaps.py`
- `StaticViewSitemap` en `apps/seo/sitemaps.py`

### 6.3 Métricas SEO en Admin — pendientes

- Contador de caracteres meta description
- Preview snippet Google
- Indicador densidad keyword

---

## 7. Diseño Mobile-First

### 7.1 Estado actual

- Templates HTML estructuradas (semántica correcta con `<header>`, `<main>`, `<footer>`, `<nav>`) ✓
- **CSS implementado** — `static/css/main.css` (1800+ líneas), custom properties, mobile-first ✓
- `static/css/tiptap-editor.css` — estilos del editor en el admin ✓
- Breakpoints 320px → 768px → 1024px implementados ✓
- Tipografía fluida con `clamp()` ✓
- Paleta: azul Loginco `#3434b0` (primario), naranja `#f97316` (acento), marinero `#0d0d3c` (footer)

### 7.2 Performance Targets (Lighthouse) — objetivo

| Métrica | Target |
|---|---|
| Performance | ≥ 90 |
| Accessibility | ≥ 95 |
| Best Practices | ≥ 95 |
| SEO | 100 |
| LCP | < 2.5s |
| CLS | < 0.1 |
| FID / INP | < 200ms |

### 7.3 Optimización de imágenes — implementado ✓

- `ImageSpecField` genera WebP en tres tamaños (thumb 400px, md 800px, lg 1280px) ✓
- Signal `post_save` en `media_manager/signals.py` pre-genera los tres specs al subir ✓
- `fetchpriority="high"` en imagen hero de `post_detail.html` ✓
- `loading="lazy"` en todas las imágenes de listados y home ✓
- `<picture>` con `<source type="image/webp">` en home, blog, category ✓

---

## 8. Arquitectura de URLs

```
/                          → pages:home (HomeView)
/nosotros/                 → pages:about
/contacto/                 → pages:contact
/servicios/                → services:index
/blog/                     → blog:post_list
/blog/<slug>/              → blog:post_detail
/blog/categoria/<slug>/    → blog:category
/sitemap.xml               → sitemap index
/admin/                    → Django Admin (Unfold)
/admin/ai/generate/        → ai_assistant:generate (stub 501)
/__debug__/                → debug_toolbar (solo dev)
```

---

## 9. Integración IA (Fase 3 — completada con DigitalOcean AI Platform)

> **Cambio arquitectónico:** Se migró de Groq a **DigitalOcean AI Platform (Gradient)**.
> Endpoint OpenAI-compatible: `https://inference.do-ai.run/v1/`. Cliente activo usa `DO_MODEL_ACCESS_KEY`.
> Ventaja: mismo endpoint soporta modelos OSS (Llama, Qwen, Mistral) y comerciales (Claude, GPT).

### 9.1 Configuración actual

```python
# apps/ai_assistant/client.py  ✓
import openai
DO_INFERENCE_URL = "https://inference.do-ai.run/v1/"
MODEL = "llama3.3-70b-instruct"
MAX_TOKENS = 4096
# Singleton lazy — falla con ImproperlyConfigured si DO_MODEL_ACCESS_KEY no está configurada
```

### 9.2 Tipos de generación planeados

| Tipo | Descripción |
|---|---|
| `full_post` | Cuerpo completo + metadatos SEO |
| `meta_only` | Solo meta_title y meta_description |
| `excerpt` | Resumen/excerpt |
| `improve` | Mejora texto existente |
| `alt_text` | Alt text para imágenes |

### 9.3 Estado actual

- `apps/ai_assistant/views.py` — `GenerateContentView` completa: validación, rate limiting (3/sesión), log ✓
- `apps/ai_assistant/urls.py` — ruta `/admin/ai/generate/` registrada ✓
- `apps/ai_assistant/client.py` — cliente DO Gradient singleton con `generate(system, user)` → `(text, input_tokens, output_tokens)` ✓
- `apps/ai_assistant/prompts.py` — `build_prompt(generation_type, context)` con los 5 tipos ✓
- `apps/ai_assistant/models.py` — `AIGenerationLog` registra cada generación ✓
- `apps/ai_assistant/admin.py` — admin solo lectura para `AIGenerationLog` ✓
- `static/js/ai-assistant.js` — modal vanilla JS + AJAX en el admin ✓

### 9.4 Parámetros de prompt (diseño)

- Tono: profesional, confiable, cercano
- Audiencia: importadores/exportadores mexicanos, empresas logísticas
- Longitud: 800–1500 palabras para posts completos
- Idioma: español (es-MX), terminología aduanal mexicana
- Rate limiting: máx 3 generaciones/sesión sin confirmación

---

## 10. Variables de Entorno

```env
# Django
DJANGO_SECRET_KEY=
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=loginco.com.mx,www.loginco.com.mx

# Base de datos (producción — PostgreSQL)
DATABASE_URL=postgres://user:password@localhost:5432/loginco_db

# IA — DigitalOcean AI Platform (Gradient)
DO_MODEL_ACCESS_KEY=

# Media Storage (producción — S3-compatible, opcional)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=
AWS_S3_ENDPOINT_URL=

# Email
EMAIL_HOST=
EMAIL_PORT=
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=

# Cloudflare Stream (opcional para video)
CLOUDFLARE_ACCOUNT_ID=
CLOUDFLARE_STREAM_TOKEN=
```

> En **desarrollo** el setting `DJANGO_SETTINGS_MODULE=config.settings.development` usa SQLite y no requiere `DATABASE_URL`.

---

## 11. Fases de Implementación

### Fase 1 — Fundación ✓ COMPLETADA

- [x] Setup proyecto Django + estructura de apps
- [x] Docker Compose + Dockerfile para desarrollo local
- [x] Modelos base: `SEOMixin`, `TimeStampedModel`, `MediaFile`, `SiteTarget`
- [x] `django-imagekit` con `ImageSpecField` para WebP (3 tamaños)
- [x] Signal `post_save` pre-genera specs WebP
- [x] `APScheduler` configurado en `apps/core/scheduler.py`
- [x] Django Admin con Unfold (tema, colores, navegación lateral)
- [x] Settings split: `base.py` / `development.py` (SQLite) / `production.py` (PostgreSQL)

### Fase 2 — CMS Core ✓ COMPLETADA

- [x] Modelos `Post`, `Category`, `Tag` completos con todas las relaciones
- [x] Admin `PostAdmin` con fieldsets (Contenido / Clasificación / Publicación / SEO / Info)
- [x] Admin `CategoryAdmin`, `TagAdmin`, `SiteTargetAdmin`
- [x] Admin `MediaFileAdmin` con miniatura, dimensiones y preview (`media_manager/admin.py`)
- [x] Editor TipTap en el admin — `TiptapWidget` en `apps/blog/widgets.py`, bundle en `static/js/`
- [x] Job APScheduler `publish_scheduled_posts` (cada minuto)
- [x] `PostSitemap`, `CategorySitemap`, `StaticViewSitemap` registrados
- [x] Vistas `PostListView`, `PostDetailView`, `CategoryDetailView`
- [x] Templates: `base.html` (SEO completo), blog, pages, services
- [x] Preview SEO en tiempo real (snippet Google en `templates/admin/blog/post/change_form.html`)
- [x] URLs configuradas
- [ ] **Pendiente:** `robots.txt`

### Fase 3 — Integración IA ✓ COMPLETADA

- [x] `apps/ai_assistant/client.py` — cliente DO Gradient (`llama3.3-70b-instruct`, OpenAI SDK)
- [x] `apps/ai_assistant/prompts.py` — prompts por tipo (full_post, meta_only, excerpt, improve, alt_text)
- [x] `GenerateContentView` con validación, rate limiting (3/sesión) y manejo de errores
- [x] UI del asistente en el admin — `static/js/ai-assistant.js` (modal vanilla JS + AJAX)
- [x] Log de generaciones — modelo `AIGenerationLog` + admin solo lectura
- [x] `apps/ai_assistant/admin.py` — `AIGenerationLogAdmin`

### Fase 4 — Frontend Público ✓ COMPLETADA (parcial)

- [x] CSS mobile-first con custom properties — `static/css/main.css` (1800+ líneas)
- [x] Estilos completos: `base.html`, home, blog, servicios, about, contact
- [x] `<picture>` con `<source type="image/webp">` en todas las templates de contenido
- [x] `loading="lazy"` en imágenes de listados
- [x] `fetchpriority="high"` en imagen hero de `post_detail.html`
- [x] Schema.org JSON-LD por tipo: BlogPosting, Organization, ContactPage, ItemList
- [x] Tipografía fluida con `clamp()`
- [ ] **Pendiente:** `robots.txt`
- [ ] **Pendiente:** Auditoría Lighthouse / Core Web Vitals

### Fase 5 — Optimización y Deploy ✗ PENDIENTE

- [x] `Dockerfile` y `docker-compose.yml` para desarrollo
- [x] `docker-compose.prod.yml` y `nginx.conf` preparados
- [ ] `robots.txt` (pendiente en todas las fases anteriores)
- [ ] Optimización Core Web Vitals / Auditoría Lighthouse
- [ ] CI/CD básico
- [ ] Tests unitarios e integración
- [ ] Deploy en producción (VPS / DigitalOcean — por decidir)

---

## 12. Dependencias Python

```txt
# requirements/base.txt
django>=5.1,<6.0
python-decouple>=3.8
pillow>=10.4
django-imagekit>=5.0
django-apscheduler>=0.6
openai>=1.50
django-unfold>=0.40
django-meta>=2.4
whitenoise>=6.7
gunicorn>=22.0

# requirements/development.txt
-r base.txt
ruff>=0.4
django-debug-toolbar>=4.4

# requirements/production.txt
-r base.txt
psycopg[binary]>=3.2
```

---

## 13. Decisiones de Diseño y Justificaciones

| Decisión | Alternativa descartada | Razón |
|---|---|---|
| Django Admin + Unfold | Wagtail | Menor curva de aprendizaje, más rápido de implementar |
| TipTap | CKEditor / Quill | Más moderno, mejor output HTML limpio, extensible |
| Unfold | django-jazzmin | Mejor soporte mobile en el admin, mantenimiento activo |
| DO AI Platform | Groq / Anthropic directo | Endpoint único para OSS + comerciales; integrable con hosting DO; OpenAI-compatible |
| SQLite (dev) | PostgreSQL en dev | Simplifica el setup local; prod usa PostgreSQL |
| PostgreSQL (prod) | MySQL | Full-text search nativo, JSONField, mejor soporte Django |
| django-apscheduler | Celery + Redis | Sin dependencia externa de Redis; jobs en PostgreSQL |
| `ImageSpecField` (imagekit) | APScheduler job de resize | Generación lazy + pre-calentado via signal; más simple |
| `image` + `video_file` separados | Único `FileField` | Mayor claridad semántica; imagekit requiere `ImageField` |
| Signal `post_save` para WebP | Job periódico | Pre-genera specs inmediatamente al subir, sin esperar |
| `og_image` omitido en SEOMixin | FK a MediaFile | Templates usan `featured_image` del Post directamente |

---

## 14. Preguntas Pendientes / Decisiones Futuras

- [ ] ¿Se necesita autenticación de usuarios públicos (portal de clientes)?
- [ ] ¿Los sub-sitios consumirán el contenido vía API REST o estarán integrados en el mismo proyecto Django?
- [ ] ¿Hay preferencia de hosting? (VPS, DigitalOcean, AWS, Render)
- [ ] ¿Se necesita formulario de contacto con integración CRM/email marketing?
- [ ] ¿Cuál es el proceso de aprobación de contenido? (¿un editor revisa antes de publicar?)
- [ ] ¿Se necesita Google Analytics / Tag Manager integrado?
- [ ] ¿Los videos son propios (subir al servidor) o embeds externos (YouTube/Vimeo)?
- [ ] ¿Se agrega `og_image` como FK en `SEOMixin` o se deja que cada template use `featured_image`?
- [ ] ¿TipTap se compila localmente o se obtiene desde CDN/npm?

---

*Documento mantenido en: `/home/tony/Developer/WebLoginco/Loginco Corp/context.md`*
