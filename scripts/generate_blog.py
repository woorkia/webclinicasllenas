#!/usr/bin/env python3
"""
Auto-blog generator para Clínicas Llenas
Genera un artículo nuevo de SEO cada día usando Claude API
"""

import anthropic
import os
import json
import re
import random
from datetime import datetime
from pathlib import Path

# ─────────────────────────────────────────
# TEMAS DE BLOG DISPONIBLES
# Añade más según necesites
# ─────────────────────────────────────────
TOPICS = [
    # Automatización
    ("como-automatizar-recordatorios-citas-clinica", "automatización", "Cómo automatizar los recordatorios de citas en tu clínica privada"),
    ("sistema-agendamiento-online-clinicas-privadas", "automatización", "Sistema de agendamiento online para clínicas privadas: guía completa"),
    ("inteligencia-artificial-gestion-clinicas", "automatización", "Inteligencia artificial para la gestión de clínicas privadas en 2026"),
    ("automatizar-seguimiento-pacientes-clinica", "automatización", "Cómo automatizar el seguimiento de pacientes en tu clínica"),
    ("whatsapp-business-api-clinicas-dentales", "whatsapp", "WhatsApp Business API para clínicas dentales: todo lo que necesitas saber"),
    # No-shows
    ("estrategias-reducir-ausencias-clinica", "no-shows", "7 estrategias para reducir las ausencias en tu clínica dental"),
    ("politica-cancelacion-clinicas-dentales", "no-shows", "Política de cancelación para clínicas dentales: cómo implementarla sin perder pacientes"),
    ("lista-espera-clinica-dental-automatizada", "no-shows", "Lista de espera automatizada para clínicas dentales: llena los huecos vacíos"),
    # Pacientes
    ("fidelizar-pacientes-clinica-dental", "pacientes", "Cómo fidelizar pacientes en tu clínica dental y aumentar el LTV"),
    ("recuperar-pacientes-inactivos-clinica", "pacientes", "Cómo recuperar pacientes inactivos en tu clínica privada"),
    ("comunicacion-pacientes-clinica-digital", "pacientes", "Comunicación digital con pacientes: la guía para clínicas privadas"),
    ("onboarding-nuevos-pacientes-clinica", "pacientes", "Onboarding de nuevos pacientes: cómo dar la bienvenida perfecta en tu clínica"),
    # Gestión
    ("kpis-gestion-clinica-privada", "gestión", "Los 10 KPIs esenciales para gestionar tu clínica privada"),
    ("digitalizar-clinica-dental-paso-a-paso", "gestión", "Cómo digitalizar tu clínica dental paso a paso en 2026"),
    ("rentabilidad-clinica-dental-como-mejorarla", "gestión", "Rentabilidad de clínica dental: cómo mejorarla sin subir precios"),
    ("agenda-clinica-dental-optimizada", "gestión", "Agenda de clínica dental optimizada: reduce tiempos muertos y aumenta ingresos"),
    ("marketing-digital-clinicas-dentales-2026", "gestión", "Marketing digital para clínicas dentales en 2026: qué funciona de verdad"),
    # WhatsApp
    ("plantillas-whatsapp-clinicas-dentales", "whatsapp", "Plantillas de WhatsApp para clínicas dentales: 20 mensajes que convierten"),
    ("whatsapp-para-conseguir-resenas-google", "whatsapp", "Cómo usar WhatsApp para conseguir reseñas de Google en tu clínica"),
    ("chatbot-whatsapp-clinica-dental-configurar", "whatsapp", "Cómo configurar un chatbot de WhatsApp para tu clínica dental"),
]

def get_used_slugs():
    """Devuelve los slugs de artículos ya creados"""
    blog_dir = Path(__file__).parent.parent / "blog"
    used = set()
    for d in blog_dir.iterdir():
        if d.is_dir() and (d / "index.html").exists():
            used.add(d.name)
    return used

def pick_topic(used_slugs):
    """Elige un tema que todavía no exista"""
    available = [t for t in TOPICS if t[0] not in used_slugs]
    if not available:
        # Si se acabaron los temas, genera variaciones con ciudades
        cities = ["Madrid", "Barcelona", "Valencia", "Sevilla", "Málaga"]
        city = random.choice(cities)
        slug = f"clinica-dental-whatsapp-{city.lower()}-{datetime.now().year}"
        return (slug, "whatsapp", f"Automatización con WhatsApp para clínicas dentales en {city}")
    return random.choice(available)

def generate_article(slug, category, title):
    """Genera el artículo completo usando Claude"""
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    today = datetime.now().strftime("%Y-%m-%d")
    today_readable = datetime.now().strftime("%-d de %B de %Y").replace(
        "January","enero").replace("February","febrero").replace("March","marzo").replace(
        "April","abril").replace("May","mayo").replace("June","junio").replace(
        "July","julio").replace("August","agosto").replace("September","septiembre").replace(
        "October","octubre").replace("November","noviembre").replace("December","diciembre")

    prompt = f"""Eres el redactor SEO de Clínicas Llenas, una empresa española B2B SaaS que ayuda a clínicas privadas a automatizar su gestión mediante WhatsApp.

Escribe un artículo de blog completo en HTML para el slug /{slug}/ con el título: "{title}"

INSTRUCCIONES ESTRICTAS:
- El artículo debe tener entre 1200 y 1800 palabras
- Está dirigido a dueños/directores de clínicas dentales privadas en España
- Tono: profesional pero cercano, directo, con datos reales
- Incluye al menos 5 subtítulos H2, 2 H3
- Incluye al menos una lista numerada o con viñetas
- Menciona "Clínicas Llenas" de forma natural 2-3 veces como solución
- Incluye estadísticas y datos concretos (puedes inventar datos realistas del sector)
- Termina con un CTA hacia /demo/ o /#contacto
- Categoría SEO: {category}
- Fecha: {today_readable}

Devuelve SOLO el HTML completo de la página, usando exactamente esta estructura:

<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
  <title>[TITULO SEO - max 60 chars] | Clínicas Llenas</title>
  <meta name="description" content="[DESCRIPCION SEO 150-160 chars]">
  <meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1">
  <link rel="canonical" href="https://clinicasllenas.com/blog/{slug}/">
  <link rel="alternate" hreflang="es" href="https://clinicasllenas.com/blog/{slug}/">
  <link rel="alternate" hreflang="x-default" href="https://clinicasllenas.com/blog/{slug}/">
  <!-- Open Graph -->
  <meta property="og:title" content="[TITULO OG]">
  <meta property="og:description" content="[DESC OG]">
  <meta property="og:url" content="https://clinicasllenas.com/blog/{slug}/">
  <meta property="og:type" content="article">
  <meta property="og:image" content="https://clinicasllenas.com/blog/img-{category}.svg">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:type" content="image/svg+xml">
  <meta property="og:locale" content="es_ES">
  <meta property="og:site_name" content="Clínicas Llenas">
  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="[TITULO TWITTER]">
  <meta name="twitter:description" content="[DESC TWITTER]">
  <meta name="twitter:image" content="https://clinicasllenas.com/blog/img-{category}.svg">
  <!-- Schema -->
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "BlogPosting",
    "headline": "{title}",
    "description": "[DESCRIPCION]",
    "image": "https://clinicasllenas.com/blog/img-{category}.svg",
    "datePublished": "{today}",
    "dateModified": "{today}",
    "author": {{"@type": "Organization", "name": "Clínicas Llenas"}},
    "publisher": {{"@type": "Organization", "name": "Clínicas Llenas", "logo": {{"@type": "ImageObject", "url": "https://clinicasllenas.com/logo.png"}}}},
    "mainEntityOfPage": {{"@type": "WebPage", "@id": "https://clinicasllenas.com/blog/{slug}/"}}
  }}
  </script>
  <!-- GTM -->
  <script>(function(w,d,s,l,i){{w[l]=w[l]||[];w[l].push({{'gtm.start':new Date().getTime(),event:'gtm.js'}});var f=d.getElementsByTagName(s)[0],j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src='https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);}})(window,document,'script','dataLayer','GTM-MDXZ4PDM');</script>
  <style>
    *{{box-sizing:border-box;margin:0;padding:0}}
    body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;color:#1a202c;line-height:1.7;background:#fff}}
    .nav{{display:flex;justify-content:space-between;align-items:center;padding:1rem 2rem;background:#fff;border-bottom:1px solid #e2e8f0;position:sticky;top:0;z-index:100}}
    .nav-logo{{font-weight:700;font-size:1.1rem;color:#1a202c;text-decoration:none}}
    .nav-cta{{background:#2563EB;color:#fff;padding:.5rem 1.25rem;border-radius:9999px;text-decoration:none;font-size:.9rem;font-weight:600}}
    .article-hero{{background:linear-gradient(135deg,#EFF6FF,#F0FDF4);padding:3rem 1.5rem 2rem;text-align:center}}
    .article-hero .cat{{display:inline-block;background:#DBEAFE;color:#1D4ED8;padding:.25rem .75rem;border-radius:9999px;font-size:.8rem;font-weight:600;letter-spacing:.05em;text-transform:uppercase;margin-bottom:1rem}}
    .article-hero h1{{font-size:clamp(1.6rem,4vw,2.4rem);font-weight:800;color:#0F172A;max-width:800px;margin:0 auto 1rem;line-height:1.3}}
    .article-hero .meta{{color:#64748B;font-size:.9rem}}
    .article-img{{width:100%;max-width:860px;height:260px;margin:0 auto;display:block;object-fit:cover;border-radius:0 0 12px 12px}}
    .article-body{{max-width:760px;margin:0 auto;padding:2.5rem 1.5rem}}
    .article-body h2{{font-size:1.5rem;font-weight:700;color:#0F172A;margin:2.5rem 0 1rem;line-height:1.3}}
    .article-body h3{{font-size:1.2rem;font-weight:600;color:#1E293B;margin:2rem 0 .75rem}}
    .article-body p{{margin-bottom:1.25rem;color:#374151;font-size:1.05rem}}
    .article-body ul,ol{{margin:1rem 0 1.5rem 1.5rem}}
    .article-body li{{margin-bottom:.5rem;color:#374151}}
    .article-body strong{{color:#0F172A}}
    .article-body blockquote{{border-left:4px solid #2563EB;padding:.75rem 1.25rem;background:#EFF6FF;margin:1.5rem 0;border-radius:0 8px 8px 0;color:#1E40AF;font-style:italic}}
    .demo-banner{{margin:2rem 0;padding:1.25rem 1.5rem;background:linear-gradient(135deg,#EFF6FF,#F0FDF4);border:1px solid #BFDBFE;border-radius:14px;display:flex;align-items:center;gap:1rem;flex-wrap:wrap}}
    .demo-banner p{{margin:0;flex:1;font-weight:600;color:#1E3A5F;min-width:200px}}
    .demo-banner a{{background:#2563EB;color:#fff;padding:.6rem 1.25rem;border-radius:9999px;text-decoration:none;font-weight:600;font-size:.9rem;white-space:nowrap}}
    .article-author{{display:flex;align-items:center;gap:1rem;padding:1.5rem;background:#F8FAFC;border-radius:12px;margin-top:2.5rem}}
    .author-avatar{{width:52px;height:52px;border-radius:50%;background:linear-gradient(135deg,#2563EB,#16A34A);display:flex;align-items:center;justify-content:center;color:#fff;font-weight:700;font-size:1.1rem;flex-shrink:0}}
    .author-info p{{margin:0;font-size:.9rem;color:#64748B}}
    .author-info strong{{color:#0F172A}}
    .breadcrumb{{padding:.75rem 1.5rem;background:#F8FAFC;font-size:.85rem}}
    .breadcrumb a{{color:#2563EB;text-decoration:none}}
    .breadcrumb span{{color:#94A3B8;margin:0 .4rem}}
    .footer{{background:#0F172A;color:#94A3B8;text-align:center;padding:2rem 1.5rem;font-size:.85rem;margin-top:4rem}}
    .footer a{{color:#94A3B8;text-decoration:none}}
    @media(max-width:640px){{.nav{{padding:.75rem 1rem}}.article-hero{{padding:2rem 1rem 1.5rem}}.article-body{{padding:1.5rem 1rem}}}}
  </style>
</head>
<body>
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-MDXZ4PDM" height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>

<nav class="nav">
  <a href="/" class="nav-logo">Clínicas<span style="color:#2563EB">Llenas</span></a>
  <a href="/#contacto" class="nav-cta">Diagnóstico gratis</a>
</nav>

<div class="breadcrumb">
  <a href="/">Inicio</a><span>›</span><a href="/blog/">Blog</a><span>›</span>{title}
</div>

[AQUI VA EL HERO Y TODO EL CONTENIDO DEL ARTÍCULO]

<footer class="footer">
  <p>© 2026 Clínicas Llenas · <a href="/privacidad/">Privacidad</a> · <a href="/cookies/">Cookies</a> · <a href="/terminos/">Términos</a></p>
  <p style="margin-top:.5rem">Automatización WhatsApp para clínicas privadas en España</p>
</footer>

<!-- Cookie banner -->
<div id="cookie-banner" style="display:none;position:fixed;bottom:0;left:0;right:0;background:#1e293b;color:#e2e8f0;padding:1rem 1.5rem;z-index:9999;display:flex;flex-wrap:wrap;align-items:center;gap:1rem;justify-content:space-between">
  <p style="margin:0;font-size:.875rem;flex:1;min-width:200px">Usamos cookies para mejorar tu experiencia. <a href="/cookies/" style="color:#60a5fa">Más info</a></p>
  <div style="display:flex;gap:.5rem;flex-shrink:0">
    <button onclick="setCookie('rejected')" style="padding:.5rem 1rem;border-radius:6px;border:1px solid #475569;background:transparent;color:#e2e8f0;cursor:pointer;font-size:.875rem">Rechazar</button>
    <button onclick="setCookie('accepted')" style="padding:.5rem 1rem;border-radius:6px;background:#2563EB;color:#fff;border:none;cursor:pointer;font-size:.875rem;font-weight:600">Aceptar</button>
  </div>
</div>
<script>
  function setCookie(v){{document.cookie='cl_cookie_consent='+v+';path=/;max-age='+(365*24*3600);document.getElementById('cookie-banner').style.display='none'}}
  if(!document.cookie.includes('cl_cookie_consent')){{document.getElementById('cookie-banner').style.display='flex'}}
</script>
</body>
</html>

Escribe el artículo completo, sustituyendo [AQUI VA EL HERO Y TODO EL CONTENIDO DEL ARTÍCULO] y todos los placeholders entre corchetes. El artículo debe estar completamente escrito, sin placeholders."""

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=8000,
        messages=[{"role": "user", "content": prompt}]
    )

    return message.content[0].text

def update_blog_index(slug, category, title, description):
    """Añade el nuevo artículo al índice del blog"""
    blog_index = Path(__file__).parent.parent / "blog" / "index.html"
    content = blog_index.read_text(encoding="utf-8")

    today = datetime.now().strftime("%-d %b %Y").replace(
        "Jan","Ene").replace("Feb","Feb").replace("Mar","Mar").replace(
        "Apr","Abr").replace("May","May").replace("Jun","Jun").replace(
        "Jul","Jul").replace("Aug","Ago").replace("Sep","Sep").replace(
        "Oct","Oct").replace("Nov","Nov").replace("Dec","Dic")

    cat_colors = {
        "automatización": ("DBEAFE","1D4ED8"),
        "whatsapp": ("D1FAE5","065F46"),
        "no-shows": ("FEF3C7","92400E"),
        "pacientes": ("FCE7F3","9D174D"),
        "gestión": ("EDE9FE","5B21B6"),
    }
    bg, fg = cat_colors.get(category, ("F1F5F9","334155"))

    new_card = f"""
      <article class="blog-card" data-cat="{category}">
        <a href="/blog/{slug}/">
          <div class="blog-card-img" style="background:linear-gradient(135deg,#EFF6FF,#F0FDF4);display:flex;align-items:center;justify-content:center;height:180px">
            <img src="/blog/img-{category}.svg" alt="{title}" style="height:120px;width:auto" loading="lazy">
          </div>
        </a>
        <div class="blog-card-body">
          <span class="blog-cat" style="background:#{bg};color:#{fg}">{category.upper()}</span>
          <h2><a href="/blog/{slug}/">{title}</a></h2>
          <p>{description}</p>
          <div class="blog-card-footer">
            <span style="font-size:.8rem;color:#94A3B8">{today}</span>
            <a href="/blog/{slug}/" class="blog-read-more">Leer artículo →</a>
          </div>
        </div>
      </article>"""

    # Insertar después del opening del blog-grid
    insert_after = '<div class="blog-grid" id="blog-grid">'
    content = content.replace(insert_after, insert_after + new_card, 1)
    blog_index.write_text(content, encoding="utf-8")

def update_sitemap(slug):
    """Añade la nueva URL al sitemap"""
    sitemap = Path(__file__).parent.parent / "sitemap.xml"
    content = sitemap.read_text(encoding="utf-8")
    today = datetime.now().strftime("%Y-%m-%d")

    new_url = f"""  <url>
    <loc>https://clinicasllenas.com/blog/{slug}/</loc>
    <lastmod>{today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>"""

    content = content.replace("</urlset>", new_url + "\n</urlset>")
    sitemap.write_text(content, encoding="utf-8")

def main():
    used = get_used_slugs()
    slug, category, title = pick_topic(used)

    print(f"📝 Generando artículo: {title}")
    print(f"   Slug: /blog/{slug}/")
    print(f"   Categoría: {category}")

    # Generar HTML
    html = generate_article(slug, category, title)

    # Guardar artículo
    article_dir = Path(__file__).parent.parent / "blog" / slug
    article_dir.mkdir(parents=True, exist_ok=True)
    (article_dir / "index.html").write_text(html, encoding="utf-8")
    print(f"✅ Artículo guardado en blog/{slug}/index.html")

    # Extraer descripción del HTML para el índice
    desc_match = re.search(r'meta name="description" content="([^"]+)"', html)
    description = desc_match.group(1) if desc_match else f"Guía completa sobre {title.lower()} para clínicas privadas en España."

    # Actualizar índice del blog
    update_blog_index(slug, category, title, description[:120] + "...")
    print("✅ Blog index actualizado")

    # Actualizar sitemap
    update_sitemap(slug)
    print("✅ Sitemap actualizado")

    print(f"\n🎉 Artículo publicado: https://clinicasllenas.com/blog/{slug}/")

    # Output para GitHub Actions
    print(f"\n::set-output name=article_slug::{slug}")
    print(f"::set-output name=article_title::{title}")

if __name__ == "__main__":
    main()
