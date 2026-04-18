#!/usr/bin/env python3
"""
Auto-blog generator para Clínicas Llenas
Genera 5 artículos SEO al día usando Claude API con enlaces internos
"""

import anthropic
import os
import re
import random
from datetime import datetime
from pathlib import Path

# ─────────────────────────────────────────
# BANCO DE TEMAS — añade más según necesites
# (slug, categoría, título)
# ─────────────────────────────────────────
TOPICS = [
    # AUTOMATIZACIÓN
    ("como-automatizar-recordatorios-citas-clinica", "automatización", "Cómo automatizar los recordatorios de citas en tu clínica privada"),
    ("sistema-agendamiento-online-clinicas-privadas", "automatización", "Sistema de agendamiento online para clínicas privadas: guía completa"),
    ("inteligencia-artificial-gestion-clinicas", "automatización", "Inteligencia artificial para la gestión de clínicas privadas en 2026"),
    ("automatizar-seguimiento-pacientes-clinica", "automatización", "Cómo automatizar el seguimiento de pacientes en tu clínica"),
    ("automatizacion-facturacion-clinica-dental", "automatización", "Automatización de facturación en clínicas dentales: ahorra 10 horas a la semana"),
    ("flujos-trabajo-automatizados-clinica", "automatización", "Flujos de trabajo automatizados para clínicas: de la cita al pago sin intervención manual"),
    ("clinica-dental-24-horas-con-whatsapp", "automatización", "Cómo tu clínica puede atender pacientes 24 horas sin contratar más personal"),
    ("automatizar-consentimientos-informados-digitales", "automatización", "Automatizar consentimientos informados digitales en tu clínica dental"),
    ("presupuestos-automaticos-clinica-dental", "automatización", "Presupuestos automáticos para clínicas dentales: cierra más tratamientos sin esfuerzo"),
    ("integracion-whatsapp-software-clinica", "automatización", "Cómo integrar WhatsApp con el software de gestión de tu clínica"),
    # NO-SHOWS
    ("estrategias-reducir-ausencias-clinica", "no-shows", "7 estrategias probadas para reducir las ausencias en tu clínica dental"),
    ("politica-cancelacion-clinicas-dentales", "no-shows", "Política de cancelación para clínicas dentales: cómo implementarla sin perder pacientes"),
    ("lista-espera-clinica-dental-automatizada", "no-shows", "Lista de espera automatizada para clínicas dentales: llena los huecos vacíos"),
    ("coste-real-no-show-clinica-dental", "no-shows", "El coste real de un no-show en tu clínica dental: cuánto dinero pierdes realmente"),
    ("confirmacion-citas-whatsapp-reducir-no-shows", "no-shows", "Confirmación de citas por WhatsApp: cómo reducir no-shows un 52% en 30 días"),
    ("por-que-los-pacientes-no-confirman-cita", "no-shows", "Por qué los pacientes no confirman su cita y cómo solucionarlo"),
    ("doble-confirmacion-citas-clinica", "no-shows", "Sistema de doble confirmación de citas para clínicas: paso a paso"),
    ("recordatorio-whatsapp-72-horas-cita", "no-shows", "El recordatorio de WhatsApp 72 horas antes que elimina los no-shows"),
    # PACIENTES
    ("fidelizar-pacientes-clinica-dental", "pacientes", "Cómo fidelizar pacientes en tu clínica dental y aumentar el valor de vida"),
    ("recuperar-pacientes-inactivos-clinica", "pacientes", "Cómo recuperar pacientes inactivos en tu clínica privada con WhatsApp"),
    ("comunicacion-pacientes-clinica-digital", "pacientes", "Comunicación digital con pacientes: la guía completa para clínicas privadas"),
    ("onboarding-nuevos-pacientes-clinica", "pacientes", "Onboarding de nuevos pacientes: cómo dar la bienvenida perfecta en tu clínica"),
    ("experiencia-paciente-clinica-dental", "pacientes", "Experiencia del paciente en clínica dental: los 7 momentos clave que debes automatizar"),
    ("encuestas-satisfaccion-clinica-dental", "pacientes", "Encuestas de satisfacción para clínicas dentales: cómo y cuándo enviarlas por WhatsApp"),
    ("captacion-pacientes-clinica-dental-2026", "pacientes", "Captación de pacientes para clínicas dentales en 2026: las 5 estrategias que funcionan"),
    ("programa-referidos-clinica-dental", "pacientes", "Programa de referidos para clínicas dentales: cómo conseguir pacientes sin gastar en publicidad"),
    ("segmentacion-pacientes-clinica-dental", "pacientes", "Segmentación de pacientes en clínicas dentales: cómo personalizar la comunicación"),
    ("pacientes-vip-clinica-dental-estrategia", "pacientes", "Pacientes VIP en clínicas dentales: cómo identificarlos y fidelizarlos"),
    # GESTIÓN
    ("kpis-gestion-clinica-privada", "gestión", "Los 10 KPIs esenciales para gestionar tu clínica privada como un negocio rentable"),
    ("digitalizar-clinica-dental-paso-a-paso", "gestión", "Cómo digitalizar tu clínica dental paso a paso en 2026"),
    ("rentabilidad-clinica-dental-como-mejorarla", "gestión", "Rentabilidad de clínica dental: cómo mejorarla sin subir precios"),
    ("agenda-clinica-dental-optimizada", "gestión", "Agenda de clínica dental optimizada: reduce tiempos muertos y aumenta ingresos"),
    ("marketing-digital-clinicas-dentales-2026", "gestión", "Marketing digital para clínicas dentales en 2026: qué funciona de verdad"),
    ("errores-gestion-clinica-dental", "gestión", "Los 8 errores de gestión que están hundiendo la rentabilidad de tu clínica dental"),
    ("software-clinica-dental-cual-elegir", "gestión", "Software para clínicas dentales en 2026: cómo elegir el que mejor se adapta a ti"),
    ("clinica-dental-sin-secretaria-es-posible", "gestión", "Clínica dental sin secretaria a jornada completa: ¿es posible en 2026?"),
    ("como-escalar-clinica-dental-privada", "gestión", "Cómo escalar tu clínica dental privada de 1 a 3 sillones sin caos"),
    ("precio-tratamientos-clinica-dental-estrategia", "gestión", "Estrategia de precios para clínicas dentales: cómo posicionarte sin perder pacientes"),
    ("turnos-espera-clinica-dental-optimizar", "gestión", "Cómo optimizar los tiempos de espera en tu clínica dental"),
    # WHATSAPP
    ("whatsapp-business-api-clinicas-dentales", "whatsapp", "WhatsApp Business API para clínicas dentales: todo lo que necesitas saber"),
    ("plantillas-whatsapp-clinicas-dentales", "whatsapp", "20 plantillas de WhatsApp para clínicas dentales que convierten"),
    ("whatsapp-para-conseguir-resenas-google", "whatsapp", "Cómo usar WhatsApp para conseguir reseñas de Google en tu clínica"),
    ("chatbot-whatsapp-clinica-dental-configurar", "whatsapp", "Cómo configurar un chatbot de WhatsApp para tu clínica dental sin programar"),
    ("whatsapp-marketing-clinica-dental-legal", "whatsapp", "WhatsApp Marketing para clínicas dentales: cómo hacerlo legal y efectivo"),
    ("diferencia-whatsapp-business-api-clinica", "whatsapp", "WhatsApp Business vs WhatsApp Business API: cuál necesita tu clínica"),
    ("mensajes-bienvenida-whatsapp-clinica", "whatsapp", "Mensajes de bienvenida por WhatsApp para clínicas: ejemplos que funcionan"),
    ("whatsapp-para-presupuestos-clinica-dental", "whatsapp", "Cómo enviar presupuestos por WhatsApp en tu clínica dental y cerrar más casos"),
    ("automatizar-respuestas-whatsapp-clinica", "whatsapp", "Automatizar respuestas de WhatsApp en tu clínica: guía completa 2026"),
    ("whatsapp-cobros-pagos-clinica-dental", "whatsapp", "WhatsApp para gestionar cobros y pagos en clínicas dentales"),
]

# Mapeo slug → título para enlaces internos (artículos ya publicados)
EXISTING_ARTICLES = {
    "como-reducir-no-shows-clinica-dental": "Cómo reducir los no-shows en tu clínica dental un 50% con WhatsApp",
    "recordatorios-automaticos-whatsapp-clinicas": "Recordatorios automáticos de citas para clínicas: guía completa 2026",
    "aumentar-resenas-google-clinica-dental": "Cómo conseguir más reseñas en Google para tu clínica dental",
    "software-gestion-clinicas-privadas": "Software de gestión para clínicas privadas: comparativa 2026",
    "automatizar-confirmacion-citas-whatsapp": "Automatizar la confirmación de citas por WhatsApp en tu clínica",
    "clinica-dental-sin-recepcionista": "Clínica dental sin recepcionista: cómo funciona la automatización total",
    "como-conseguir-pacientes-nuevos-clinica": "Cómo conseguir pacientes nuevos para tu clínica dental en 2026",
    "pacientes-dormidos-como-reactivarlos": "Pacientes dormidos: cómo reactivarlos con WhatsApp",
    "reducir-cancelaciones-clinica-dental": "Reducir cancelaciones en clínica dental: 6 técnicas efectivas",
    "marketing-dental-sin-publicidad": "Marketing dental sin publicidad de pago: las estrategias que funcionan",
    "whatsapp-business-clinicas-dentales": "WhatsApp Business para clínicas dentales: guía de uso",
    "whatsapp-vs-email-clinicas": "WhatsApp vs Email para clínicas: qué canal convierte más",
    "gestion-citas-online-clinicas": "Gestión de citas online para clínicas: todo lo que necesitas saber",
    "consentimientos-informados-digitales-clinicas": "Consentimientos informados digitales en clínicas: ventajas y cómo implementarlos",
    "aumentar-facturacion-clinica-dental": "Cómo aumentar la facturación de tu clínica dental con automatización",
    "como-conseguir-resenas-google-clinica": "Cómo conseguir reseñas de Google para tu clínica dental paso a paso",
}

def get_used_slugs():
    """Devuelve los slugs de artículos ya creados"""
    blog_dir = Path(__file__).parent.parent / "blog"
    used = set()
    for d in blog_dir.iterdir():
        if d.is_dir() and (d / "index.html").exists():
            used.add(d.name)
    return used

def get_all_published_articles():
    """Devuelve dict slug→título de todos los artículos publicados"""
    blog_dir = Path(__file__).parent.parent / "blog"
    articles = dict(EXISTING_ARTICLES)
    for d in blog_dir.iterdir():
        if d.is_dir() and (d / "index.html").exists():
            # Intentar extraer el título del HTML
            try:
                html = (d / "index.html").read_text(encoding="utf-8")
                m = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.DOTALL)
                if m:
                    title = re.sub(r'<[^>]+>', '', m.group(1)).strip()
                    articles[d.name] = title
            except:
                pass
    return articles

def pick_topics(used_slugs, count=5):
    """Elige N temas que no existan aún"""
    available = [t for t in TOPICS if t[0] not in used_slugs]
    random.shuffle(available)
    chosen = available[:count]
    # Si no hay suficientes, generar variaciones
    while len(chosen) < count:
        cities = ["Madrid", "Barcelona", "Valencia", "Sevilla", "Málaga", "Bilbao", "Zaragoza"]
        city = random.choice(cities)
        year = datetime.now().year
        slug = f"automatizacion-clinica-dental-{city.lower()}-{year}-{len(chosen)}"
        chosen.append((slug, "automatización", f"Automatización para clínicas dentales en {city}: guía {year}"))
    return chosen

def generate_article(slug, category, title, published_articles):
    """Genera el artículo completo usando Claude con enlaces internos"""
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    today = datetime.now().strftime("%Y-%m-%d")
    today_readable = datetime.now().strftime("%-d de %B de %Y")
    # Traducir mes al español
    meses = {"January":"enero","February":"febrero","March":"marzo","April":"abril",
             "May":"mayo","June":"junio","July":"julio","August":"agosto",
             "September":"septiembre","October":"octubre","November":"noviembre","December":"diciembre"}
    for en, es in meses.items():
        today_readable = today_readable.replace(en, es)

    # Preparar lista de artículos relacionados para enlaces internos
    # Filtramos el propio artículo y elegimos los más relevantes
    related = [(s, t) for s, t in published_articles.items() if s != slug]
    random.shuffle(related)
    internal_links_context = "\n".join([f'- /blog/{s}/ → "{t}"' for s, t in related[:12]])

    cat_colors = {
        "automatización": ("DBEAFE","1D4ED8"),
        "whatsapp": ("D1FAE5","065F46"),
        "no-shows": ("FEF3C7","92400E"),
        "pacientes": ("FCE7F3","9D174D"),
        "gestión": ("EDE9FE","5B21B6"),
    }
    bg, fg = cat_colors.get(category, ("F1F5F9","334155"))

    prompt = f"""Eres el redactor SEO jefe de Clínicas Llenas, empresa B2B SaaS española que automatiza la gestión de clínicas privadas mediante WhatsApp.

Escribe un artículo de blog COMPLETO con HTML para la URL: https://clinicasllenas.com/blog/{slug}/
Título: "{title}"
Categoría: {category}
Fecha: {today_readable}

━━━ REQUISITOS SEO OBLIGATORIOS ━━━

ESTRUCTURA:
- 1.500 a 2.000 palabras de contenido real
- H1: el título exacto (ya aparece en el hero, no lo repitas en el body)
- Mínimo 6 subtítulos H2 con palabras clave long-tail incluidas
- Mínimo 2 subtítulos H3 dentro de algún H2
- 1 lista numerada y 1 lista con viñetas (bullets)
- 1 tabla comparativa o de datos
- 1 blockquote con estadística o cita relevante del sector

SEO ON-PAGE:
- Keyword principal "{title}" en el primer párrafo
- Variaciones semánticas de la keyword a lo largo del texto
- Densidad natural — no relleno, texto que aporte valor real
- Párrafos cortos (máx. 4 líneas) para legibilidad mobile
- Datos y estadísticas concretas del sector odontología/salud privada España

ENLACES INTERNOS (MUY IMPORTANTE):
Incluye 4-6 enlaces internos naturales a otros artículos del blog.
Usa exactamente estas URLs y textos ancla variados (no repitas el título exacto):

{internal_links_context}

Ejemplo de enlace interno: <a href="/blog/como-reducir-no-shows-clinica-dental/">reducir las ausencias en consulta</a>

CTA FINAL:
Termina con una sección "¿Listo para automatizar tu clínica?" con dos botones:
- Primario → /demo/ "Ver demo interactiva"
- Secundario → /#contacto "Pedir diagnóstico gratis"

━━━ ESTRUCTURA HTML EXACTA A DEVOLVER ━━━

Devuelve SOLO el HTML completo sin explicaciones. Usa esta plantilla:

<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
  <title>[TITULO SEO máx 60 chars] | Clínicas Llenas</title>
  <meta name="description" content="[DESCRIPCIÓN 150-160 chars con keyword principal]">
  <meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1">
  <link rel="canonical" href="https://clinicasllenas.com/blog/{slug}/">
  <link rel="alternate" hreflang="es" href="https://clinicasllenas.com/blog/{slug}/">
  <link rel="alternate" hreflang="x-default" href="https://clinicasllenas.com/blog/{slug}/">
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
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="[TITULO TWITTER]">
  <meta name="twitter:description" content="[DESC TWITTER]">
  <meta name="twitter:image" content="https://clinicasllenas.com/blog/img-{category}.svg">
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "BlogPosting",
    "headline": "{title}",
    "description": "[DESCRIPCIÓN]",
    "image": "https://clinicasllenas.com/blog/img-{category}.svg",
    "datePublished": "{today}",
    "dateModified": "{today}",
    "author": {{"@type": "Organization", "name": "Clínicas Llenas", "url": "https://clinicasllenas.com"}},
    "publisher": {{"@type": "Organization", "name": "Clínicas Llenas", "logo": {{"@type": "ImageObject", "url": "https://clinicasllenas.com/logo.png"}}}},
    "mainEntityOfPage": {{"@type": "WebPage", "@id": "https://clinicasllenas.com/blog/{slug}/"}},
    "keywords": "[KEYWORDS separadas por coma]",
    "articleSection": "{category}"
  }}
  </script>
  <script>(function(w,d,s,l,i){{w[l]=w[l]||[];w[l].push({{'gtm.start':new Date().getTime(),event:'gtm.js'}});var f=d.getElementsByTagName(s)[0],j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src='https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);}})(window,document,'script','dataLayer','GTM-MDXZ4PDM');</script>
  <style>
    *{{box-sizing:border-box;margin:0;padding:0}}
    body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;color:#1a202c;line-height:1.7;background:#fff}}
    .nav{{display:flex;justify-content:space-between;align-items:center;padding:1rem 2rem;background:#fff;border-bottom:1px solid #e2e8f0;position:sticky;top:0;z-index:100}}
    .nav-logo{{font-weight:700;font-size:1.1rem;color:#1a202c;text-decoration:none}}
    .nav-cta{{background:#2563EB;color:#fff;padding:.5rem 1.25rem;border-radius:9999px;text-decoration:none;font-size:.9rem;font-weight:600}}
    .article-hero{{background:linear-gradient(135deg,#EFF6FF,#F0FDF4);padding:3rem 1.5rem 2rem;text-align:center}}
    .article-hero .cat{{display:inline-block;background:#{bg};color:#{fg};padding:.25rem .75rem;border-radius:9999px;font-size:.8rem;font-weight:600;letter-spacing:.05em;text-transform:uppercase;margin-bottom:1rem}}
    .article-hero h1{{font-size:clamp(1.6rem,4vw,2.4rem);font-weight:800;color:#0F172A;max-width:820px;margin:0 auto 1rem;line-height:1.25}}
    .article-hero .meta{{color:#64748B;font-size:.9rem;display:flex;justify-content:center;gap:1.5rem;flex-wrap:wrap}}
    .article-hero .meta span{{display:flex;align-items:center;gap:.3rem}}
    .article-img-wrap{{max-width:860px;margin:0 auto;overflow:hidden;border-radius:0 0 16px 16px}}
    .article-img-wrap img{{width:100%;height:240px;object-fit:cover;display:block}}
    .breadcrumb{{max-width:860px;margin:1.5rem auto 0;padding:0 1.5rem;font-size:.85rem;color:#94A3B8}}
    .breadcrumb a{{color:#2563EB;text-decoration:none}}
    .breadcrumb span{{margin:0 .4rem}}
    .article-layout{{max-width:860px;margin:0 auto;padding:2rem 1.5rem;display:grid;grid-template-columns:1fr 260px;gap:3rem;align-items:start}}
    .article-body h2{{font-size:1.45rem;font-weight:700;color:#0F172A;margin:2.5rem 0 .9rem;line-height:1.3}}
    .article-body h3{{font-size:1.15rem;font-weight:600;color:#1E293B;margin:1.75rem 0 .6rem}}
    .article-body p{{margin-bottom:1.2rem;color:#374151;font-size:1.02rem}}
    .article-body ul,.article-body ol{{margin:1rem 0 1.5rem 1.5rem}}
    .article-body li{{margin-bottom:.6rem;color:#374151;font-size:1.02rem}}
    .article-body strong{{color:#0F172A}}
    .article-body a{{color:#2563EB;text-decoration:underline;text-decoration-color:rgba(37,99,235,.3)}}
    .article-body a:hover{{text-decoration-color:#2563EB}}
    .article-body blockquote{{border-left:4px solid #2563EB;padding:1rem 1.25rem;background:#EFF6FF;margin:1.75rem 0;border-radius:0 8px 8px 0;color:#1E40AF;font-style:italic;font-size:1.05rem}}
    .article-body table{{width:100%;border-collapse:collapse;margin:1.5rem 0;font-size:.95rem}}
    .article-body th{{background:#1E293B;color:#fff;padding:.6rem .9rem;text-align:left;font-weight:600}}
    .article-body td{{padding:.6rem .9rem;border-bottom:1px solid #E2E8F0;color:#374151}}
    .article-body tr:nth-child(even) td{{background:#F8FAFC}}
    .demo-banner{{margin:2.5rem 0;padding:1.5rem;background:linear-gradient(135deg,#EFF6FF,#F0FDF4);border:1px solid #BFDBFE;border-radius:16px}}
    .demo-banner h3{{font-size:1.15rem;font-weight:700;color:#1E3A5F;margin-bottom:.5rem}}
    .demo-banner p{{color:#475569;margin-bottom:1rem;font-size:.95rem}}
    .demo-banner .cta-btns{{display:flex;gap:.75rem;flex-wrap:wrap}}
    .demo-banner .btn-primary{{background:#2563EB;color:#fff;padding:.65rem 1.35rem;border-radius:9999px;text-decoration:none;font-weight:600;font-size:.9rem}}
    .demo-banner .btn-secondary{{background:#fff;color:#2563EB;padding:.65rem 1.35rem;border-radius:9999px;text-decoration:none;font-weight:600;font-size:.9rem;border:1.5px solid #2563EB}}
    .sidebar{{position:sticky;top:80px}}
    .sidebar-box{{background:#F8FAFC;border-radius:14px;padding:1.25rem;margin-bottom:1.5rem}}
    .sidebar-box h4{{font-size:.9rem;font-weight:700;color:#0F172A;margin-bottom:.9rem;text-transform:uppercase;letter-spacing:.05em}}
    .sidebar-box ul{{list-style:none;margin:0;padding:0}}
    .sidebar-box ul li{{margin-bottom:.6rem;font-size:.88rem}}
    .sidebar-box ul li a{{color:#2563EB;text-decoration:none;line-height:1.4}}
    .sidebar-box ul li a:hover{{text-decoration:underline}}
    .sidebar-cta{{background:linear-gradient(135deg,#1E3A5F,#2563EB);color:#fff;border-radius:14px;padding:1.5rem;text-align:center}}
    .sidebar-cta p{{color:rgba(255,255,255,.85);font-size:.9rem;margin:.5rem 0 1rem}}
    .sidebar-cta a{{display:block;background:#fff;color:#1E3A5F;padding:.65rem;border-radius:9999px;font-weight:700;font-size:.9rem;text-decoration:none}}
    .article-author{{display:flex;align-items:center;gap:1rem;padding:1.25rem;background:#F8FAFC;border-radius:12px;margin-top:2rem;border:1px solid #E2E8F0}}
    .author-avatar{{width:48px;height:48px;border-radius:50%;background:linear-gradient(135deg,#2563EB,#16A34A);display:flex;align-items:center;justify-content:center;color:#fff;font-weight:700;flex-shrink:0}}
    .author-info p{{margin:0;font-size:.85rem;color:#64748B}}
    .related-articles{{max-width:860px;margin:3rem auto 0;padding:0 1.5rem 3rem}}
    .related-articles h3{{font-size:1.2rem;font-weight:700;color:#0F172A;margin-bottom:1.25rem}}
    .related-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem}}
    .related-card{{background:#F8FAFC;border-radius:12px;padding:1.1rem;border:1px solid #E2E8F0;text-decoration:none;display:block;transition:box-shadow .2s}}
    .related-card:hover{{box-shadow:0 4px 16px rgba(0,0,0,.08)}}
    .related-card .rc-cat{{font-size:.75rem;font-weight:600;color:#2563EB;margin-bottom:.4rem;text-transform:uppercase}}
    .related-card p{{font-size:.88rem;font-weight:600;color:#0F172A;line-height:1.4;margin:0}}
    .footer{{background:#0F172A;color:#94A3B8;text-align:center;padding:2rem 1.5rem;font-size:.85rem;margin-top:2rem}}
    .footer a{{color:#94A3B8;text-decoration:none}}
    @media(max-width:768px){{
      .article-layout{{grid-template-columns:1fr;gap:1.5rem}}
      .sidebar{{position:static}}
      .related-grid{{grid-template-columns:1fr}}
      .nav{{padding:.75rem 1rem}}
      .article-hero{{padding:2rem 1rem 1.5rem}}
    }}
  </style>
</head>
<body>
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-MDXZ4PDM" height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>

<nav class="nav">
  <a href="/" class="nav-logo">Clínicas<span style="color:#2563EB">Llenas</span></a>
  <a href="/#contacto" class="nav-cta">Diagnóstico gratis</a>
</nav>

[AQUÍ VA TODO EL CONTENIDO: hero section, breadcrumb, article-layout con article-body y sidebar, related-articles, article-author, y el CTA final]

<footer class="footer">
  <p>© 2026 Clínicas Llenas · <a href="/privacidad/">Privacidad</a> · <a href="/cookies/">Cookies</a> · <a href="/terminos/">Términos</a></p>
  <p style="margin-top:.5rem">Automatización WhatsApp para clínicas privadas en España</p>
</footer>

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

IMPORTANTE: Devuelve el HTML completo y funcional. Sustituye [AQUÍ VA TODO EL CONTENIDO] con el contenido real del artículo. No dejes ningún placeholder entre corchetes."""

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=10000,
        messages=[{"role": "user", "content": prompt}]
    )

    return message.content[0].text

def update_blog_index(slug, category, title, description, today_str):
    """Añade el nuevo artículo al índice del blog"""
    blog_index = Path(__file__).parent.parent / "blog" / "index.html"
    content = blog_index.read_text(encoding="utf-8")

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
          <p>{description[:130]}...</p>
          <div class="blog-card-footer">
            <span style="font-size:.8rem;color:#94A3B8">{today_str}</span>
            <a href="/blog/{slug}/" class="blog-read-more">Leer artículo →</a>
          </div>
        </div>
      </article>"""

    insert_after = '<!-- Artículos generados automáticamente -->'
    if insert_after in content:
        content = content.replace(insert_after, insert_after + new_card, 1)
        blog_index.write_text(content, encoding="utf-8")
        return True
    return False

def update_sitemap(slugs):
    """Añade las nuevas URLs al sitemap"""
    sitemap = Path(__file__).parent.parent / "sitemap.xml"
    content = sitemap.read_text(encoding="utf-8")
    today = datetime.now().strftime("%Y-%m-%d")

    new_urls = ""
    for slug in slugs:
        if f"/blog/{slug}/" not in content:
            new_urls += f"""  <url>
    <loc>https://clinicasllenas.com/blog/{slug}/</loc>
    <lastmod>{today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>\n"""

    if new_urls:
        content = content.replace("</urlset>", new_urls + "</urlset>")
        sitemap.write_text(content, encoding="utf-8")

def main():
    print(f"🚀 Iniciando generación de 5 artículos — {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    used = get_used_slugs()
    published = get_all_published_articles()
    topics = pick_topics(used, count=5)

    today_str = datetime.now().strftime("%-d %b %Y").replace(
        "Jan","Ene").replace("Feb","Feb").replace("Mar","Mar").replace(
        "Apr","Abr").replace("May","May").replace("Jun","Jun").replace(
        "Jul","Jul").replace("Aug","Ago").replace("Sep","Sep").replace(
        "Oct","Oct").replace("Nov","Nov").replace("Dec","Dic")

    generated_slugs = []

    for i, (slug, category, title) in enumerate(topics, 1):
        print(f"\n📝 [{i}/5] Generando: {title}")

        try:
            # Generar HTML
            html = generate_article(slug, category, title, published)

            # Guardar artículo
            article_dir = Path(__file__).parent.parent / "blog" / slug
            article_dir.mkdir(parents=True, exist_ok=True)
            (article_dir / "index.html").write_text(html, encoding="utf-8")
            print(f"   ✅ Guardado en blog/{slug}/")

            # Extraer descripción del meta
            desc_match = re.search(r'meta name="description" content="([^"]+)"', html)
            description = desc_match.group(1) if desc_match else f"Guía sobre {title.lower()} para clínicas privadas en España."

            # Añadir al índice
            update_blog_index(slug, category, title, description, today_str)
            print(f"   ✅ Añadido al índice del blog")

            # Añadir a publicados para que los siguientes artículos del día puedan enlazarlo
            published[slug] = title
            generated_slugs.append(slug)

        except Exception as e:
            print(f"   ❌ Error generando {slug}: {e}")

    # Actualizar sitemap con todos los nuevos artículos
    if generated_slugs:
        update_sitemap(generated_slugs)
        print(f"\n✅ Sitemap actualizado con {len(generated_slugs)} nuevas URLs")

    print(f"\n🎉 Completado: {len(generated_slugs)}/5 artículos publicados")
    for slug in generated_slugs:
        print(f"   → https://clinicasllenas.com/blog/{slug}/")

if __name__ == "__main__":
    main()
