# Especificación de Diseño: Optimización Frontend y Rendimiento (Fases 4 y 5)

**Fecha:** 2026-10-06  
**Proyecto:** Loginco Corp (`loginco.com.mx`)  
**Objetivo:** Completar la Fase 4 (Frontend Público) y la optimización de rendimiento de la Fase 5, asegurando métricas óptimas de Core Web Vitals, accesibilidad y SEO técnico.

---

## 1. Resumen y Alcance

Esta especificación cubre la optimización completa del frontend y la capa de entrega estática:
1. **Core Web Vitals**:
   - **LCP (Largest Contentful Paint)**: Auto-alojamiento de assets de imagen, preloads estratégicos, eliminación de peticiones externas no críticas.
   - **CLS (Cumulative Layout Shift)**: Asignación explícita de `aspect-ratio`, `width` y `height` en todas las imágenes y placeholders.
   - **FID / INP**: JavaScript ligero sin dependencias pesadas, ejecución asíncrona/pasiva de eventos de scroll y navegación.
2. **Caché y Entrega de Assets (Producción)**:
   - Configuración de WhiteNoise con `CompressedManifestStaticFilesStorage` y cabeceras de caché inmutables (`WHITENOISE_MAX_AGE = 31536000`).
3. **SEO Técnico y Accesibilidad**:
   - Servido estricto de `robots.txt` y sitemaps.
   - Verificación de metadatos Open Graph, Twitter Cards, canonical tags y Schema.org JSON-LD.
   - Accesibilidad WCAG AA: contraste, `focus-visible`, atributos ARIA en SVGs y menús.
4. **Documentación**:
   - Actualización de `context.md` y `CLAUDE.md` reflejando el cierre de la Fase 4 y la optimización de Fase 5.

---

## 2. Cambios Arquitectónicos y por Componente

### 2.1 Optimización de Assets y LCP
- **`templates/pages/about.html`**:
  - Reemplazar imagen remota de Unsplash por imagen local optimizada en `static/img/about-team.webp` / `about-team.jpg` con dimensiones explícitas.
  - Implementar etiqueta `<picture>` con WebP responsivo.
- **`templates/base.html`**:
  - Mantener preconnect a Google Fonts (`fonts.googleapis.com` y `fonts.gstatic.com`).
  - Carga asíncrona de fuentes vía truco `media="print" onload="this.media='all'"` con fallback `<noscript>`.
  - Iconos y favicons servidos localmente en formato SVG.
- **`templates/pages/home.html` y `templates/blog/post_detail.html`**:
  - Preload en `<head>` de imagen LCP correspondiente con `fetchpriority="high"`.

### 2.2 Eliminación de CLS (Dimensiones y Aspect-Ratio)
- **`static/css/main.css`**:
  - Aplicar regla `aspect-ratio: 16 / 9;` a `.post-card__image-wrap`, `.post-card__placeholder` y `.service-card__cover`.
  - Aplicar regla `aspect-ratio: 4 / 3;` a `.about-intro__image`.
  - Fijar tamaño explícito y `object-fit: contain;` para logos de socios comerciales en `.socio-card__logo`.
- **Templates**:
  - Verificar que todas las etiquetas `<img>` tengan atributos `width` y `height` acordes a sus proporciones intrínsecas.

### 2.3 Configuración de Producción y Caché
- **`config/settings/production.py`**:
  - Asegurar `WHITENOISE_MAX_AGE = 31536000` (1 año de caché para estáticos con hash manifest).
  - Mantener backend `whitenoise.storage.CompressedManifestStaticFilesStorage` en `STORAGES["staticfiles"]`.
- **`config/settings/base.py`**:
  - Mantener `CONTACT_EMAIL` y `DEFAULT_FROM_EMAIL` correctamente configurados.

### 2.4 SEO Técnico y Accesibilidad (a11y)
- **`apps/pages/views.py` & `apps/pages/urls.py`**:
  - `RobotsTxtView` sirviendo contenido dinámico con directiva `Disallow: /admin/` y declaración de `Sitemap: https://www.loginco.com.mx/sitemap.xml`.
- **Accesibilidad**:
  - Validar soporte de `:focus-visible` global para navegación por teclado.
  - Mantener enlace de salto de accesibilidad `<a href="#main-content" class="skip-link">` al inicio del `<body>`.
  - Atributos `aria-hidden="true"` en todos los SVGs decorativos y `aria-label` descriptivos en botones interactivos.

---

## 3. Plan de Pruebas y Validación

1. **Pruebas Automatizadas**:
   - Ejecución de suite de tests Django (`python manage.py test`) verificando que todas las vistas devuelvan código HTTP 200 y `robots.txt` devuelva contenido correcto.
2. **Validación de Estáticos (Collectstatic)**:
   - Ejecutar `python manage.py collectstatic --dry-run` para asegurar que el manifest de WhiteNoise no tenga referencias rotas a archivos faltantes.
3. **Auditoría de Sintaxis y Linting**:
   - `ruff check .` sin advertencias ni errores.

---

## 4. Estado de Documentación

Al completar la implementación:
- Actualizar `context.md`:
  - Fase 4: Cambiar de "parcial" a "COMPLETADA ✓".
  - Fase 5: Registrar optimizaciones de Core Web Vitals, WhiteNoise y assets como "COMPLETADA ✓".
