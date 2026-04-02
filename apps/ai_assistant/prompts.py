"""
Biblioteca de prompts estructurados para el asistente IA de Loginco Corp.

Tono de marca:
- Profesional, confiable y cercano (no robótico ni genérico)
- Audiencia: importadores/exportadores mexicanos y empresas logísticas
- Idioma: español (es-MX), con terminología aduanal mexicana
- Siempre orientado a valor real para el lector
"""

# ---------------------------------------------------------------------------
# Contexto de marca compartido (inyectado en todos los system prompts)
# ---------------------------------------------------------------------------

_BRAND_CONTEXT = """
Eres el redactor de contenido especializado de Loginco Corp, una empresa mexicana
líder en servicios de comercio exterior. Loginco Corp agrupa tres servicios:

1. **Agencia Aduanal** (agencia-aduanal.loginco.com.mx): Asesoría y gestión integral
   de trámites aduanales ante el SAT y la Aduana Mexicana.
2. **Bodega & Patio** (bodega-patio.loginco.com.mx): Almacenaje en depósito fiscal,
   patio de maniobras y manejo de mercancías de importación/exportación.
3. **Transporte** (transporte.loginco.com.mx): Transporte de carga para mercancías
   de comercio exterior a lo largo de México.

**Slogan:** "Cero estrés, aduanal"

**Tono de escritura:**
- Profesional y confiable, pero cercano (habla de "tú" al lector)
- Claro y directo: sin jerga innecesaria, pero con terminología aduanal correcta
- Orientado a beneficios reales del lector (importador/exportador mexicano)
- Nunca genérico ni "de relleno" — cada párrafo debe aportar valor

**Terminología mexicana a usar correctamente:**
pedimento, despacho aduanal, agente aduanal, SAT, VUCEM, fracción arancelaria,
COVE, e-document, DODA, rectificación, depósito fiscal, regímenes aduaneros,
NOM, regulaciones y restricciones no arancelarias (RRNA).
""".strip()

_RESPONSE_FORMAT_INSTRUCTION = (
    "Responde ÚNICAMENTE con JSON válido, sin texto adicional, sin markdown, sin bloques de código."
)

# ---------------------------------------------------------------------------
# Builder principal
# ---------------------------------------------------------------------------


def build_prompt(generation_type: str, context: dict) -> tuple[str, str]:
    """
    Construye el par (system_prompt, user_prompt) para el tipo de generación dado.

    Args:
        generation_type: Uno de 'full_post', 'meta_only', 'excerpt', 'improve', 'alt_text'.
        context: Diccionario con los campos requeridos para cada tipo (ver docstring de cada builder).

    Returns:
        Tupla (system_prompt, user_prompt) lista para enviar a la API.

    Raises:
        ValueError: Si generation_type no está soportado.
    """
    builders = {
        "full_post": _build_full_post,
        "meta_only": _build_meta_only,
        "excerpt": _build_excerpt,
        "improve": _build_improve,
        "alt_text": _build_alt_text,
    }
    builder = builders.get(generation_type)
    if builder is None:
        raise ValueError(
            f"Tipo de generación '{generation_type}' no soportado. "
            f"Tipos válidos: {', '.join(builders.keys())}"
        )
    return builder(context)


# ---------------------------------------------------------------------------
# Builders por tipo
# ---------------------------------------------------------------------------


def _build_full_post(context: dict) -> tuple[str, str]:
    """
    Genera un artículo completo con cuerpo HTML, metadatos SEO y excerpt.

    context keys:
        title (str): Título del artículo.
        site_target_name (str): Nombre del sub-sitio (ej. "Agencia Aduanal").
        site_target_slug (str): Slug del sub-sitio (ej. "agencia-aduanal").
        category (str, opcional): Nombre de la categoría.
        keywords (str, opcional): Keywords adicionales separadas por comas.
        word_count (int, opcional): Longitud objetivo en palabras (default 1000).
    """
    title = context.get("title", "")
    site_target_name = context.get("site_target_name", "Loginco Corp")
    category = context.get("category", "")
    keywords = context.get("keywords", "")
    word_count = context.get("word_count", 1000)

    system = f"""{_BRAND_CONTEXT}

{_RESPONSE_FORMAT_INSTRUCTION}

El JSON de respuesta debe tener exactamente esta estructura:
{{
  "body": "<HTML del artículo con etiquetas H2, H3, H4, párrafos <p>, listas <ul>/<ol>. Sin <html>, <head>, <body> ni <h1>>",
  "meta_title": "<Título SEO, máximo 60 caracteres>",
  "meta_description": "<Descripción SEO, máximo 160 caracteres, incluye CTA>",
  "excerpt": "<Resumen del artículo, máximo 280 caracteres>"
}}"""

    category_line = f"\n- Categoría: {category}" if category else ""
    keywords_line = f"\n- Keywords adicionales: {keywords}" if keywords else ""

    user = f"""Redacta un artículo de blog completo para el sitio de **{site_target_name}** de Loginco Corp.

**Datos del artículo:**
- Título: {title}
- Sub-sitio destino: {site_target_name}{category_line}{keywords_line}
- Longitud objetivo: aproximadamente {word_count} palabras

**Requisitos del contenido:**
- Estructura con H2 principales, H3 subsecciones y H4 cuando sea necesario
- Párrafos cortos (máx 4 líneas) para fácil lectura en móvil
- Al menos una lista <ul> o <ol> con puntos clave o pasos
- Orientado a importadores/exportadores mexicanos
- Termina con un párrafo de cierre que invite al lector a contactar a Loginco
- El meta_title debe incluir la keyword principal y ser atractivo para el SERP
- La meta_description debe incluir un CTA claro en menos de 160 caracteres
- El excerpt es el gancho inicial del artículo (máx 280 caracteres)

Genera el JSON ahora:"""

    return system, user


def _build_meta_only(context: dict) -> tuple[str, str]:
    """
    Genera solo meta_title y meta_description a partir de un título y cuerpo.

    context keys:
        title (str): Título del artículo.
        body_text (str): Texto plano del cuerpo (primeros ~500 caracteres).
        site_target_name (str): Nombre del sub-sitio.
    """
    title = context.get("title", "")
    body_text = context.get("body_text", "")[:500]
    site_target_name = context.get("site_target_name", "Loginco Corp")

    system = f"""{_BRAND_CONTEXT}

{_RESPONSE_FORMAT_INSTRUCTION}

El JSON de respuesta debe tener exactamente esta estructura:
{{
  "meta_title": "<Título SEO, máximo 60 caracteres, incluye keyword principal>",
  "meta_description": "<Descripción SEO, máximo 160 caracteres, incluye CTA>"
}}"""

    user = f"""Genera los metadatos SEO optimizados para este artículo de {site_target_name} — Loginco Corp.

**Título del artículo:** {title}

**Extracto del contenido:**
{body_text}

**Requisitos:**
- meta_title: máximo 60 caracteres, incluye la keyword principal, atractivo para el SERP
- meta_description: máximo 160 caracteres, resume el valor del artículo e incluye un CTA
- Ambos en español (es-MX)

Genera el JSON ahora:"""

    return system, user


def _build_excerpt(context: dict) -> tuple[str, str]:
    """
    Genera un excerpt/resumen corto del artículo.

    context keys:
        title (str): Título del artículo.
        body_text (str): Texto plano del cuerpo (primeros ~300 caracteres).
    """
    title = context.get("title", "")
    body_text = context.get("body_text", "")[:300]

    system = f"""{_BRAND_CONTEXT}

{_RESPONSE_FORMAT_INSTRUCTION}

El JSON de respuesta debe tener exactamente esta estructura:
{{
  "excerpt": "<Resumen del artículo, máximo 280 caracteres, en español (es-MX)>"
}}"""

    user = f"""Genera un excerpt (resumen) atractivo para este artículo del blog de Loginco Corp.

**Título:** {title}

**Inicio del contenido:**
{body_text}

**Requisitos:**
- Máximo 280 caracteres
- Debe enganchar al lector y resumir el valor del artículo
- Tono cercano y profesional, en español (es-MX)
- No termines con "..." — escribe una oración completa

Genera el JSON ahora:"""

    return system, user


def _build_improve(context: dict) -> tuple[str, str]:
    """
    Mejora un cuerpo de artículo HTML existente.

    context keys:
        body (str): HTML actual del artículo.
        site_target_name (str): Nombre del sub-sitio.
    """
    body = context.get("body", "")
    site_target_name = context.get("site_target_name", "Loginco Corp")

    system = f"""{_BRAND_CONTEXT}

{_RESPONSE_FORMAT_INSTRUCTION}

El JSON de respuesta debe tener exactamente esta estructura:
{{
  "body": "<HTML mejorado del artículo. Mantén las etiquetas HTML existentes (H2, H3, H4, p, ul, ol). Sin <html>, <head> ni <body>>"
}}"""

    user = f"""Mejora el siguiente artículo HTML para el blog de {site_target_name} — Loginco Corp.

**HTML actual:**
{body}

**Qué mejorar:**
- Claridad y fluidez de la redacción
- Coherencia de tono (profesional, cercano, en español es-MX)
- Terminología aduanal correcta y específica
- Párrafos muy largos: divídelos en párrafos más cortos
- Enriquece con detalles prácticos si el contenido es muy genérico
- Mantén toda la estructura HTML (H2, H3, H4, listas)
- No cambies el tema ni la intención del artículo original
- Asegura que el cierre invite al lector a contactar a Loginco

Genera el JSON ahora:"""

    return system, user


def _build_alt_text(context: dict) -> tuple[str, str]:
    """
    Genera texto alternativo (alt text) para una imagen.

    context keys:
        image_title (str): Título o nombre del archivo de la imagen.
        image_context (str): Contexto sobre la imagen (descripción, artículo relacionado, etc.).
    """
    image_title = context.get("image_title", "")
    image_context = context.get("image_context", "")

    system = f"""{_BRAND_CONTEXT}

{_RESPONSE_FORMAT_INSTRUCTION}

El JSON de respuesta debe tener exactamente esta estructura:
{{
  "alt_text": "<Texto alternativo descriptivo, máximo 120 caracteres, en español (es-MX)>"
}}"""

    user = f"""Genera un texto alternativo (alt text) SEO-friendly para una imagen de Loginco Corp.

**Título o nombre de la imagen:** {image_title}
**Contexto adicional:** {image_context}

**Requisitos:**
- Máximo 120 caracteres
- Descriptivo y específico (no genérico)
- Incluye la keyword principal si es natural
- En español (es-MX)
- No empieces con "Imagen de" o "Foto de"

Genera el JSON ahora:"""

    return system, user
