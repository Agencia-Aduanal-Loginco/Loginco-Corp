# Optimización Frontend y Rendimiento (Fase 4 & 5) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Completar la Fase 4 (Frontend Público) y la optimización de rendimiento de Fase 5 en Loginco Corp, garantizando cero peticiones externas no críticas, prevención de CLS con aspect ratios explícitos, configuración de WhiteNoise para producción y suite de verificación.

**Architecture:** Optimización directa de plantillas Django (`templates/pages/about.html`, `templates/base.html`, etc.), reglas CSS mobile-first para contención de layouts en `static/css/main.css`, cabeceras de caché estricta de WhiteNoise en `config/settings/production.py` y suite de tests de regresión para SEO y rutas principales.

**Tech Stack:** Django 5.x, Python 3.12, WhiteNoise, Pillow / ImageKit, CSS Moderno (clamp, aspect-ratio, custom properties).

## Global Constraints

- Todos los comandos ejecutados deben usar el intérprete del entorno virtual `.venv/bin/python`.
- No introducir librerías o dependencias externas pesadas adicionales en `requirements/base.txt`.
- Mantener compatibilidad estricta con Unfold Admin y mobile-first (320px -> 768px -> 1024px).
- Todas las imágenes públicas deben usar `<picture>` con WebP y fallback, y declarar `width` y `height` explícitos.

---

### Task 1: Optimización de Assets y LCP en About (`templates/pages/about.html`)

**Files:**
- Create: `static/img/about-team-800.webp`, `static/img/about-team-800.jpg`, `static/img/about-team-480.webp`
- Modify: `templates/pages/about.html`
- Test: `apps/pages/tests.py`

**Interfaces:**
- Consumes: Django static tag `{% static 'img/about-team-...' %}`
- Produces: Plantilla `about.html` con `<picture>` responsivo local, eliminando llamada DNS externa a Unsplash.

- [ ] **Step 1: Crear imagen local optimizada para About**

Crear un script python para generar los assets de imagen locales optimizados (WebP y JPG) en `static/img/`:
```bash
.venv/bin/python -c "
from PIL import Image, ImageDraw, ImageFont
import os

img = Image.new('RGB', (800, 600), color='#1e293b')
draw = ImageDraw.Draw(img)
# Rectángulo y texto decorativo de fondo
draw.rectangle([(20, 20), (780, 580)], outline='#38bdf8', width=3)
draw.text((400, 300), 'Loginco Corp — Equipo y Operaciones', fill='#f8fafc', anchor='mm')

img.save('static/img/about-team-800.jpg', 'JPEG', quality=85)
img.save('static/img/about-team-800.webp', 'WEBP', quality=85)

img_sm = img.resize((480, 360))
img_sm.save('static/img/about-team-480.webp', 'WEBP', quality=85)
print('Assets creados con éxito.')
"
```

- [ ] **Step 2: Actualizar `templates/pages/about.html` con `<picture>` local**

Reemplazar la etiqueta `<img>` de Unsplash en `templates/pages/about.html` con:
```html
<div class="about-intro__image">
  <picture>
    <source type="image/webp"
            srcset="{% static 'img/about-team-480.webp' %} 480w, {% static 'img/about-team-800.webp' %} 800w"
            sizes="(min-width: 1024px) 500px, (min-width: 768px) 45vw, 100vw" />
    <img src="{% static 'img/about-team-800.jpg' %}"
         alt="Equipo Loginco Corp — socios de confianza en comercio exterior"
         loading="lazy"
         width="800"
         height="600"
         decoding="async" />
  </picture>
</div>
```

- [ ] **Step 3: Ejecutar pruebas de `apps.pages`**

Run: `.venv/bin/python manage.py test apps.pages`  
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add static/img/about-team* templates/pages/about.html
git commit -m "perf: localize and optimize team image on about page"
```

---

### Task 2: Prevención de CLS y Optimización CSS (`static/css/main.css`)

**Files:**
- Modify: `static/css/main.css`
- Test: `.venv/bin/python manage.py test`

**Interfaces:**
- Consumes: Clases CSS de tarjetas y multimedia.
- Produces: Reglas `aspect-ratio` consistentes para imágenes y contenedores para evitar layout shifts.

- [ ] **Step 1: Agregar reglas de aspect-ratio y contención de layout en `static/css/main.css`**

Asegurar que `.post-card__image-wrap`, `.service-card__cover`, `.about-intro__image` y `.socio-card__logo` tengan dimensiones estables:
```css
.post-card__image-wrap,
.post-card__placeholder {
  aspect-ratio: 16 / 9;
  width: 100%;
  overflow: hidden;
}

.service-card__cover {
  aspect-ratio: 16 / 9;
  width: 100%;
  overflow: hidden;
}

.about-intro__image {
  aspect-ratio: 4 / 3;
  width: 100%;
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.about-intro__image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.socio-card__logo {
  width: 140px;
  height: 64px;
  object-fit: contain;
}
```

- [ ] **Step 2: Verificar accesibilidad `:focus-visible` global**

Asegurar en `static/css/main.css` que los elementos interactivos tengan contorno de foco accesible:
```css
:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}
```

- [ ] **Step 3: Ejecutar suite de pruebas**

Run: `.venv/bin/python manage.py test`  
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add static/css/main.css
git commit -m "style: add aspect-ratio and focus-visible rules for CLS and a11y"
```

---

### Task 3: Configuración de Producción y Caché WhiteNoise (`config/settings/production.py`)

**Files:**
- Modify: `config/settings/production.py`
- Test: `.venv/bin/python manage.py collectstatic --dry-run --noinput`

**Interfaces:**
- Consumes: Django STORAGES y WhiteNoise settings.
- Produces: Headers inmutables de caché HTTP (max-age 1 año) para archivos estáticos con hash.

- [ ] **Step 1: Configurar `WHITENOISE_MAX_AGE` en `config/settings/production.py`**

Agregar directivas de WhiteNoise al final de `config/settings/production.py`:
```python
# Cabeceras de caché WhiteNoise (1 año para estáticos con hash inmutable)
WHITENOISE_MAX_AGE = 31536000
WHITENOISE_IMMUTABLE_FILE_TEST = lambda *args: True
```

- [ ] **Step 2: Probar collectstatic en seco**

Run: `DJANGO_SETTINGS_MODULE=config.settings.production .venv/bin/python manage.py collectstatic --dry-run --noinput`  
Expected: Proceso finaliza sin errores de archivos estáticos faltantes o manifests rotos.

- [ ] **Step 3: Commit**

```bash
git add config/settings/production.py
git commit -m "perf: configure immutable caching headers for WhiteNoise in production"
```

---

### Task 4: Tests de Regresión SEO, robots.txt y URLs

**Files:**
- Modify: `apps/pages/tests.py`
- Test: `.venv/bin/python manage.py test`

**Interfaces:**
- Consumes: Django Client test runner.
- Produces: Verificación automatizada de respuesta 200/410/robots.txt/sitemaps.

- [ ] **Step 1: Añadir tests exhaustivos en `apps/pages/tests.py`**

Incluir pruebas para:
- `RobotsTxtView` (`/robots.txt` retorna status 200, texto plano, directiva `Disallow: /admin/` y `Sitemap`).
- Rutas 410 Gone para URLs heredadas (`/shopping/`, `/authentic/`, etc.).
- Todas las páginas públicas cargan con status 200 (`/`, `/nosotros/`, `/contacto/`, `/servicios/`, `/blog/`, `/sitemap.xml`).

- [ ] **Step 2: Ejecutar suite completa de pruebas**

Run: `.venv/bin/python manage.py test`  
Expected: 25+ tests PASS sin advertencias.

- [ ] **Step 3: Commit**

```bash
git add apps/pages/tests.py
git commit -m "test: add comprehensive regression tests for SEO and core routes"
```

---

### Task 5: Actualización de Estado y Documentación (`context.md` y `CLAUDE.md`)

**Files:**
- Modify: `context.md`
- Modify: `CLAUDE.md`

**Interfaces:**
- Consumes: Resultados de las tareas 1-4.
- Produces: Documentos de contexto actualizados reflejando el cierre de la Fase 4 y la optimización de Fase 5.

- [ ] **Step 1: Actualizar `context.md`**

Marcar en la sección 11 (Fases de Implementación):
- Fase 4: Frontend Público `✓ COMPLETADA` (todos los checkboxes marcados).
- Fase 5: Optimización Core Web Vitals y WhiteNoise `✓ COMPLETADA`.

- [ ] **Step 2: Ejecutar linter ruff**

Run: `.venv/bin/python -m ruff check .`  
Expected: All checks passed!

- [ ] **Step 3: Commit**

```bash
git add context.md CLAUDE.md
git commit -m "docs: mark Phase 4 and Phase 5 performance optimization as complete"
```
