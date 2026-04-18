#!/usr/bin/env python3
"""
Auto-blog generator para Clínicas Llenas
Genera 5 artículos SEO al día usando Claude API con enlaces internos.

IMPORTANTE: Este script usa el artículo original (pacientes-dormidos-como-reactivarlos)
como PLANTILLA LITERAL. Claude solo genera el contenido del cuerpo — la estructura,
tipografía, navbar, hero, footer, sidebar... son idénticos al artículo de referencia.
"""

import anthropic
import os
import re
import json
import random
from datetime import datetime
from pathlib import Path

# ─────────────────────────────────────────
# BANCO DE TEMAS
# (slug, categoría, título, categoría_label_mostrado)
# ─────────────────────────────────────────
TOPICS = [
    # AUTOMATIZACIÓN
    ("como-automatizar-recordatorios-citas-clinica", "automatización", "Cómo automatizar los recordatorios de citas en tu clínica privada", "Automatización"),
    ("sistema-agendamiento-online-clinicas-privadas", "automatización", "Sistema de agendamiento online para clínicas privadas: guía completa", "Automatización"),
    ("inteligencia-artificial-gestion-clinicas", "automatización", "Inteligencia artificial para la gestión de clínicas privadas en 2026", "Automatización"),
    ("automatizar-seguimiento-pacientes-clinica", "automatización", "Cómo automatizar el seguimiento de pacientes en tu clínica", "Automatización"),
    ("automatizacion-facturacion-clinica-dental", "automatización", "Automatización de facturación en clínicas dentales: ahorra 10 horas a la semana", "Automatización"),
    ("flujos-trabajo-automatizados-clinica", "automatización", "Flujos de trabajo automatizados para clínicas: de la cita al pago sin intervención manual", "Automatización"),
    ("clinica-dental-24-horas-con-whatsapp", "automatización", "Cómo tu clínica puede atender pacientes 24 horas sin contratar más personal", "Automatización"),
    ("automatizar-consentimientos-informados-digitales", "automatización", "Automatizar consentimientos informados digitales en tu clínica dental", "Automatización"),
    ("presupuestos-automaticos-clinica-dental", "automatización", "Presupuestos automáticos para clínicas dentales: cierra más tratamientos sin esfuerzo", "Automatización"),
    ("integracion-whatsapp-software-clinica", "automatización", "Cómo integrar WhatsApp con el software de gestión de tu clínica", "Automatización"),
    # NO-SHOWS
    ("estrategias-reducir-ausencias-clinica", "no-shows", "7 estrategias probadas para reducir las ausencias en tu clínica dental", "Reducción de no-shows"),
    ("politica-cancelacion-clinicas-dentales", "no-shows", "Política de cancelación para clínicas dentales: cómo implementarla sin perder pacientes", "Reducción de no-shows"),
    ("lista-espera-clinica-dental-automatizada", "no-shows", "Lista de espera automatizada para clínicas dentales: llena los huecos vacíos", "Reducción de no-shows"),
    ("coste-real-no-show-clinica-dental", "no-shows", "El coste real de un no-show en tu clínica dental: cuánto dinero pierdes realmente", "Reducción de no-shows"),
    ("confirmacion-citas-whatsapp-reducir-no-shows", "no-shows", "Confirmación de citas por WhatsApp: cómo reducir no-shows un 52% en 30 días", "Reducción de no-shows"),
    ("por-que-los-pacientes-no-confirman-cita", "no-shows", "Por qué los pacientes no confirman su cita y cómo solucionarlo", "Reducción de no-shows"),
    ("doble-confirmacion-citas-clinica", "no-shows", "Sistema de doble confirmación de citas para clínicas: paso a paso", "Reducción de no-shows"),
    ("recordatorio-whatsapp-72-horas-cita", "no-shows", "El recordatorio de WhatsApp 72 horas antes que elimina los no-shows", "Reducción de no-shows"),
    # PACIENTES
    ("fidelizar-pacientes-clinica-dental", "pacientes", "Cómo fidelizar pacientes en tu clínica dental y aumentar el valor de vida", "Fidelización de pacientes"),
    ("recuperar-pacientes-inactivos-clinica", "pacientes", "Cómo recuperar pacientes inactivos en tu clínica privada con WhatsApp", "Reactivación de pacientes"),
    ("comunicacion-pacientes-clinica-digital", "pacientes", "Comunicación digital con pacientes: la guía completa para clínicas privadas", "Comunicación paciente"),
    ("onboarding-nuevos-pacientes-clinica", "pacientes", "Onboarding de nuevos pacientes: cómo dar la bienvenida perfecta en tu clínica", "Onboarding pacientes"),
    ("experiencia-paciente-clinica-dental", "pacientes", "Experiencia del paciente en clínica dental: los 7 momentos clave que debes automatizar", "Experiencia paciente"),
    ("encuestas-satisfaccion-clinica-dental", "pacientes", "Encuestas de satisfacción para clínicas dentales: cómo y cuándo enviarlas por WhatsApp", "Satisfacción paciente"),
    ("captacion-pacientes-clinica-dental-2026", "pacientes", "Captación de pacientes para clínicas dentales en 2026: las 5 estrategias que funcionan", "Captación pacientes"),
    ("programa-referidos-clinica-dental", "pacientes", "Programa de referidos para clínicas dentales: cómo conseguir pacientes sin gastar en publicidad", "Referidos"),
    ("segmentacion-pacientes-clinica-dental", "pacientes", "Segmentación de pacientes en clínicas dentales: cómo personalizar la comunicación", "Segmentación"),
    ("pacientes-vip-clinica-dental-estrategia", "pacientes", "Pacientes VIP en clínicas dentales: cómo identificarlos y fidelizarlos", "Pacientes VIP"),
    # GESTIÓN
    ("kpis-gestion-clinica-privada", "gestión", "Los 10 KPIs esenciales para gestionar tu clínica privada como un negocio rentable", "Gestión de clínicas"),
    ("digitalizar-clinica-dental-paso-a-paso", "gestión", "Cómo digitalizar tu clínica dental paso a paso en 2026", "Gestión de clínicas"),
    ("rentabilidad-clinica-dental-como-mejorarla", "gestión", "Rentabilidad de clínica dental: cómo mejorarla sin subir precios", "Gestión de clínicas"),
    ("agenda-clinica-dental-optimizada", "gestión", "Agenda de clínica dental optimizada: reduce tiempos muertos y aumenta ingresos", "Gestión de clínicas"),
    ("marketing-digital-clinicas-dentales-2026", "gestión", "Marketing digital para clínicas dentales en 2026: qué funciona de verdad", "Marketing"),
    ("errores-gestion-clinica-dental", "gestión", "Los 8 errores de gestión que están hundiendo la rentabilidad de tu clínica dental", "Gestión de clínicas"),
    ("software-clinica-dental-cual-elegir", "gestión", "Software para clínicas dentales en 2026: cómo elegir el que mejor se adapta a ti", "Software"),
    ("clinica-dental-sin-secretaria-es-posible", "gestión", "Clínica dental sin secretaria a jornada completa: ¿es posible en 2026?", "Gestión de clínicas"),
    ("como-escalar-clinica-dental-privada", "gestión", "Cómo escalar tu clínica dental privada de 1 a 3 sillones sin caos", "Gestión de clínicas"),
    ("precio-tratamientos-clinica-dental-estrategia", "gestión", "Estrategia de precios para clínicas dentales: cómo posicionarte sin perder pacientes", "Precios"),
    ("turnos-espera-clinica-dental-optimizar", "gestión", "Cómo optimizar los tiempos de espera en tu clínica dental", "Gestión de clínicas"),
    # WHATSAPP
    ("whatsapp-business-api-clinicas-dentales", "whatsapp", "WhatsApp Business API para clínicas dentales: todo lo que necesitas saber", "WhatsApp"),
    ("plantillas-whatsapp-clinicas-dentales", "whatsapp", "20 plantillas de WhatsApp para clínicas dentales que convierten", "WhatsApp"),
    ("whatsapp-para-conseguir-resenas-google", "whatsapp", "Cómo usar WhatsApp para conseguir reseñas de Google en tu clínica", "WhatsApp"),
    ("chatbot-whatsapp-clinica-dental-configurar", "whatsapp", "Cómo configurar un chatbot de WhatsApp para tu clínica dental sin programar", "WhatsApp"),
    ("whatsapp-marketing-clinica-dental-legal", "whatsapp", "WhatsApp Marketing para clínicas dentales: cómo hacerlo legal y efectivo", "WhatsApp"),
    ("diferencia-whatsapp-business-api-clinica", "whatsapp", "WhatsApp Business vs WhatsApp Business API: cuál necesita tu clínica", "WhatsApp"),
    ("mensajes-bienvenida-whatsapp-clinica", "whatsapp", "Mensajes de bienvenida por WhatsApp para clínicas: ejemplos que funcionan", "WhatsApp"),
    ("whatsapp-para-presupuestos-clinica-dental", "whatsapp", "Cómo enviar presupuestos por WhatsApp en tu clínica dental y cerrar más casos", "WhatsApp"),
    ("automatizar-respuestas-whatsapp-clinica", "whatsapp", "Automatizar respuestas de WhatsApp en tu clínica: guía completa 2026", "WhatsApp"),
    ("whatsapp-cobros-pagos-clinica-dental", "whatsapp", "WhatsApp para gestionar cobros y pagos en clínicas dentales", "WhatsApp"),
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

CAT_IMAGES = {
    "automatización": "img-confirmacion-citas.svg",
    "whatsapp": "img-whatsapp-business.svg",
    "no-shows": "img-no-shows.svg",
    "pacientes": "img-pacientes.svg",
    "gestión": "img-citas-online.svg",
}


# ─────────────────────────────────────────
# PLANTILLA LITERAL — basada en el artículo
# /blog/pacientes-dormidos-como-reactivarlos/
# Solo se sustituyen placeholders {{var}}.
# ─────────────────────────────────────────
TEMPLATE = r"""<!DOCTYPE html>
<html lang="es" dir="ltr">
<head>
<!-- Google Tag Manager -->
<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
})(window,document,'script','dataLayer','GTM-MDXZ4PDM');</script>
<!-- End Google Tag Manager -->
<meta charset="UTF-8">
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<title>{{meta_title}} | Clínicas Llenas</title>
<meta name="description" content="{{meta_description}}">
<meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1">
<link rel="canonical" href="https://www.clinicasllenas.com/blog/{{slug}}/">
<link rel="alternate" hreflang="es" href="https://www.clinicasllenas.com/blog/{{slug}}/">
<link rel="alternate" hreflang="x-default" href="https://www.clinicasllenas.com/blog/{{slug}}/">
<meta property="og:type" content="article">
<meta property="og:url" content="https://www.clinicasllenas.com/blog/{{slug}}/">
<meta property="og:title" content="{{meta_title}}">
<meta property="og:description" content="{{meta_description}}">
<meta property="og:image" content="https://www.clinicasllenas.com/og-image.svg">
<meta property="og:image:type" content="image/svg+xml">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:site_name" content="Clínicas Llenas">
<meta property="article:published_time" content="{{iso_date}}">
<meta property="article:modified_time" content="{{iso_date}}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{{meta_title}}">
<meta name="twitter:image" content="https://www.clinicasllenas.com/og-image.svg">
<meta name="twitter:description" content="{{meta_description}}">
<link rel="icon" type="image/x-icon" href="/favicon.ico">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">
<link rel="icon" type="image/png" sizes="192x192" href="/favicon-192.png">
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="apple-touch-icon" href="/favicon-192.png">
<link rel="manifest" href="/site.webmanifest">
<meta name="theme-color" content="#1E3A5F">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@300;400;500&display=swap">
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "@id": "https://www.clinicasllenas.com/blog/{{slug}}/#article",
  "headline": "{{h1}}",
  "description": "{{meta_description}}",
  "image": "https://www.clinicasllenas.com/og-image.svg",
  "datePublished": "{{iso_date}}",
  "dateModified": "{{iso_date}}",
  "author": { "@type": "Organization", "name": "Clínicas Llenas", "url": "https://clinicasllenas.com" },
  "publisher": { "@type": "Organization", "name": "Clínicas Llenas", "logo": { "@type": "ImageObject", "url": "https://www.clinicasllenas.com/logo.png" } },
  "mainEntityOfPage": { "@type": "WebPage", "@id": "https://www.clinicasllenas.com/blog/{{slug}}/" },
  "keywords": {{keywords_json}},
  "articleSection": "{{category_label}}",
  "inLanguage": "es-ES"
}
</script>
<style>
*,*::before,*::after{margin:0;padding:0;box-sizing:border-box}
:root{--ink:#0D1B2A;--blue:#2563EB;--blue-mid:#1E4FC9;--blue-dim:rgba(37,99,235,0.1);--emerald:#10B981;--emerald-dim:rgba(16,185,129,0.12);--surface:#F8FAFC;--border:rgba(15,23,42,0.08);--muted:#64748B;--muted-2:#94A3B8;--font-display:'Plus Jakarta Sans',system-ui,sans-serif;--font-body:'Inter',system-ui,sans-serif;--r-sm:12px;--r-md:18px;--r-lg:24px;--r-xl:32px;--r-pill:100px;--shadow-sm:0 1px 3px rgba(0,0,0,.06);--shadow-md:0 4px 16px rgba(0,0,0,.07);--shadow-lg:0 16px 48px rgba(0,0,0,.1)}
html{scroll-behavior:smooth}body{font-family:var(--font-body);color:var(--ink);background:#fff;line-height:1.6;-webkit-font-smoothing:antialiased}a{text-decoration:none;color:inherit}
.nav{position:fixed;top:16px;left:50%;transform:translateX(-50%);z-index:100;width:calc(100% - 32px);max-width:1200px}
.nav-inner{background:rgba(255,255,255,0.92);backdrop-filter:blur(24px);border:1px solid var(--border);border-radius:var(--r-pill);padding:0 24px;display:flex;align-items:center;justify-content:space-between;height:60px;box-shadow:var(--shadow-sm)}
.nav.scrolled .nav-inner{box-shadow:var(--shadow-md)}
.nav-logo img{height:90px;width:auto;display:block;margin:-17px 0;}
.nav-links{display:flex;gap:1.5rem;align-items:center}
.nav-links a{font-size:14px;font-weight:500;color:var(--muted);transition:color .2s}
.nav-links a:hover,.nav-links a.active{color:var(--ink)}
.nav-cta{background:var(--ink);color:#fff;border:none;border-radius:var(--r-pill);padding:10px 22px;font-family:var(--font-display);font-size:13.5px;font-weight:700;cursor:pointer;transition:background .2s}
.nav-cta:hover{background:var(--blue)}
@media(max-width:860px){.nav-links{display:none}}
.article-hero{background:var(--surface);padding:120px 2rem 60px;position:relative;overflow:hidden}
.article-hero::before{content:'';position:absolute;inset:0;background:radial-gradient(ellipse 700px 400px at 50% 0%,rgba(37,99,235,0.06) 0%,transparent 70%)}
.article-hero-inner{max-width:760px;margin:0 auto;position:relative}
.article-breadcrumb{display:flex;align-items:center;gap:8px;margin-bottom:1.5rem;font-size:13px;color:var(--muted)}
.article-breadcrumb a{color:var(--muted);transition:color .2s}.article-breadcrumb a:hover{color:var(--blue)}
.article-breadcrumb svg{width:14px;height:14px;fill:var(--muted-2)}
.article-cat{display:inline-flex;align-items:center;gap:6px;background:rgba(99,102,241,0.1);border-radius:var(--r-pill);padding:4px 14px;margin-bottom:1rem}
.article-cat span{font-size:11px;font-weight:700;color:#6366F1;text-transform:uppercase;letter-spacing:.05em}
.article-hero h1{font-family:var(--font-display);font-size:clamp(1.8rem,3.5vw,2.75rem);font-weight:800;color:var(--ink);line-height:1.2;margin-bottom:1rem}
.article-meta{display:flex;align-items:center;gap:1.5rem;flex-wrap:wrap;margin-bottom:2rem}
.article-meta-item{display:flex;align-items:center;gap:6px;font-size:13px;color:var(--muted)}
.article-meta-item svg{width:15px;height:15px;fill:var(--muted-2)}
.article-meta-item strong{color:var(--ink);font-weight:600}
.article-excerpt{font-size:17px;color:var(--muted);line-height:1.7;padding:1.25rem 1.5rem;background:#fff;border-left:3px solid #6366F1;border-radius:0 var(--r-sm) var(--r-sm) 0;box-shadow:var(--shadow-sm)}
.article-hero-img{width:100%;max-width:760px;margin:2rem auto 0;border-radius:var(--r-xl);overflow:hidden;box-shadow:var(--shadow-lg)}
.article-hero-img img{width:100%;height:360px;object-fit:cover;display:block}
.article-layout{max-width:1100px;margin:0 auto;padding:4rem 2rem 6rem;display:grid;grid-template-columns:1fr 300px;gap:4rem;align-items:start}
.article-content h2{font-family:var(--font-display);font-size:1.5rem;font-weight:700;color:var(--ink);margin:2.5rem 0 1rem;line-height:1.3}
.article-content h3{font-family:var(--font-display);font-size:1.15rem;font-weight:700;color:var(--ink);margin:2rem 0 .75rem}
.article-content p{font-size:16px;color:#334155;line-height:1.8;margin-bottom:1.25rem}
.article-content ul{margin:1rem 0 1.5rem 1.5rem}
.article-content li{font-size:16px;color:#334155;line-height:1.7;margin-bottom:.5rem}
.article-content strong{color:var(--ink);font-weight:600}
.article-content a{color:var(--blue);text-decoration:underline;text-decoration-thickness:1px;text-underline-offset:3px}
.callout{padding:1.25rem 1.5rem;border-radius:var(--r-md);margin:2rem 0}
.callout-blue{background:var(--blue-dim);border:1px solid rgba(37,99,235,0.15)}
.callout-purple{background:rgba(99,102,241,0.08);border:1px solid rgba(99,102,241,0.2)}
.callout-green{background:var(--emerald-dim);border:1px solid rgba(16,185,129,0.2)}
.callout-title{font-family:var(--font-display);font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:.05em;margin-bottom:.5rem}
.callout-blue .callout-title{color:var(--blue)}.callout-green .callout-title{color:#059669}.callout-purple .callout-title{color:#6366F1}
.callout p{font-size:14.5px;color:var(--ink);margin:0;line-height:1.65}
.stat-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;margin:2rem 0}
.stat-box{background:#fff;border:1px solid var(--border);border-radius:var(--r-lg);padding:1.25rem;text-align:center;box-shadow:var(--shadow-sm)}
.stat-box-num{font-family:var(--font-display);font-size:2rem;font-weight:800;color:#6366F1;display:block;line-height:1}
.stat-box-label{font-size:12.5px;color:var(--muted);margin-top:.35rem;line-height:1.4}
.steps{display:flex;flex-direction:column;gap:1.5rem;margin:2rem 0}
.step{display:flex;gap:1rem;align-items:flex-start}
.step-num{width:36px;height:36px;border-radius:50%;background:linear-gradient(135deg,#6366F1,#4F46E5);color:#fff;display:flex;align-items:center;justify-content:center;font-family:var(--font-display);font-weight:800;font-size:14px;flex-shrink:0;margin-top:2px}
.step-body{}
.step-body strong{display:block;font-family:var(--font-display);font-size:15px;font-weight:700;color:var(--ink);margin-bottom:.35rem}
.step-body p{font-size:14.5px;color:var(--muted);margin:0;line-height:1.6}
.article-cta{background:linear-gradient(135deg,#0D1B2A 0%,#1E3A5F 100%);border-radius:var(--r-xl);padding:2.5rem;text-align:center;margin:3rem 0;position:relative;overflow:hidden}
.article-cta::before{content:'';position:absolute;inset:0;background:radial-gradient(ellipse 400px 300px at 50% 0%,rgba(37,99,235,0.3) 0%,transparent 70%)}
.article-cta-inner{position:relative}
.article-cta h3{font-family:var(--font-display);font-size:1.4rem;font-weight:800;color:#fff;margin-bottom:.6rem}
.article-cta p{color:#94A3B8;font-size:14.5px;margin-bottom:1.5rem}
.article-cta-btn{display:inline-flex;align-items:center;gap:10px;background:var(--blue);color:#fff !important;border:none;border-radius:var(--r-pill);padding:15px 32px;font-family:var(--font-display);font-weight:700;font-size:15px;cursor:pointer;transition:all .2s;text-decoration:none;box-shadow:0 8px 24px rgba(37,99,235,0.4);white-space:nowrap}
.article-cta-btn:hover{background:var(--blue-mid)}
.sidebar-toc{background:#fff;border:1px solid var(--border);border-radius:var(--r-xl);padding:1.5rem;position:sticky;top:90px;box-shadow:var(--shadow-sm)}
.sidebar-toc h4{font-family:var(--font-display);font-size:13px;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:.06em;margin-bottom:1rem}
.toc-list{list-style:none;display:flex;flex-direction:column;gap:2px}
.toc-list a{display:block;font-size:13.5px;color:var(--muted);padding:6px 10px;border-radius:var(--r-sm);transition:all .2s;line-height:1.4}
.toc-list a:hover{color:var(--blue);background:var(--blue-dim)}
.sidebar-related{margin-top:1.5rem;background:#fff;border:1px solid var(--border);border-radius:var(--r-xl);padding:1.5rem;box-shadow:var(--shadow-sm)}
.sidebar-related h4{font-family:var(--font-display);font-size:13px;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:.06em;margin-bottom:1rem}
.related-item{display:flex;flex-direction:column;gap:4px;padding:10px 0;border-bottom:1px solid var(--border)}
.related-item:last-child{border-bottom:none;padding-bottom:0}
.related-item a{font-size:13.5px;font-weight:600;color:var(--ink);line-height:1.35;transition:color .2s}
.related-item a:hover{color:var(--blue)}
.related-item span{font-size:12px;color:var(--muted-2)}
.article-author{display:flex;gap:1rem;align-items:flex-start;background:var(--surface);border-radius:var(--r-xl);padding:1.5rem;margin-top:3rem;border:1px solid var(--border)}
.author-av{width:48px;height:48px;border-radius:50%;background:var(--blue-dim);display:flex;align-items:center;justify-content:center;font-family:var(--font-display);font-weight:800;color:var(--blue);font-size:14px;flex-shrink:0}
.author-info strong{display:block;font-family:var(--font-display);font-weight:700;color:var(--ink);margin-bottom:.2rem}
.author-info p{font-size:13.5px;color:var(--muted);margin:0;line-height:1.5}
.footer{background:#08101A;padding:2rem}
.footer-inner{max-width:1200px;margin:0 auto;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:1rem}
.footer-copy{font-size:12px;color:#334155}
.footer-links{display:flex;gap:1.5rem}
.footer-links a{font-size:12px;color:#334155;transition:color .2s}
.footer-links a:hover{color:#64748B}
@media(max-width:900px){.article-layout{grid-template-columns:1fr}.article-sidebar{display:none}.stat-grid{grid-template-columns:1fr 1fr}}
@media(max-width:540px){.stat-grid{grid-template-columns:1fr}.article-hero{padding:100px 1.5rem 40px}}
</style>
</head>
<body>
<!-- Google Tag Manager (noscript) -->
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-MDXZ4PDM"
height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
<!-- End Google Tag Manager (noscript) -->

<nav class="nav" id="nav">
  <div class="nav-inner">
    <a href="/" class="nav-logo" aria-label="Clínicas Llenas">
      <img src="/logo.png" alt="Clínicas Llenas" fetchpriority="high">
    </a>
    <div class="nav-links">
      <a href="/#problema">Problema</a>
      <a href="/#proceso">Proceso</a>
      <a href="/#modulos">Módulos</a>
      <a href="/#resultados">Resultados</a>
      <a href="/#precios">Precios</a>
      <a href="/blog/" class="active">Blog</a>
    </div>
    <button class="nav-cta" onclick="window.location.href='/#contacto'">Diagnóstico gratis</button>
  </div>
</nav>

<header class="article-hero">
  <div class="article-hero-inner">
    <nav class="article-breadcrumb" aria-label="Breadcrumb">
      <a href="/">Inicio</a>
      <svg viewBox="0 0 20 20"><path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd"/></svg>
      <a href="/blog/">Blog</a>
      <svg viewBox="0 0 20 20"><path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd"/></svg>
      <span>{{breadcrumb}}</span>
    </nav>
    <div class="article-cat"><span>{{category_label}}</span></div>
    <h1>{{h1}}</h1>
    <div class="article-meta">
      <div class="article-meta-item">
        <svg viewBox="0 0 20 20"><path fill-rule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clip-rule="evenodd"/></svg>
        <span>{{date_readable}}</span>
      </div>
      <div class="article-meta-item">
        <svg viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.5 2.5a1 1 0 001.414-1.414L11 9.586V6z" clip-rule="evenodd"/></svg>
        <span>{{read_time}} minutos de lectura</span>
      </div>
      <div class="article-meta-item">
        <svg viewBox="0 0 20 20"><path d="M9 6a3 3 0 11-6 0 3 3 0 016 0zM17 6a3 3 0 11-6 0 3 3 0 016 0zM12.93 17c.046-.327.07-.66.07-1a6.97 6.97 0 00-1.5-4.33A5 5 0 0119 16v1h-6.07zM6 11a5 5 0 015 5v1H1v-1a5 5 0 015-5z"/></svg>
        <span>Por <strong>Equipo Clínicas Llenas</strong></span>
      </div>
    </div>
    <div class="article-excerpt">
      {{excerpt}}
    </div>
    <div class="article-hero-img">
      <img src="/blog/{{hero_image}}" alt="{{h1}}" loading="eager">
    </div>
  </div>
</header>

<div class="article-layout">
  <article class="article-content">

{{body_content}}

    <div style="margin:2rem 0;padding:1.25rem 1.5rem;background:linear-gradient(135deg,#EFF6FF,#F0FDF4);border:1px solid #BFDBFE;border-radius:14px;display:flex;align-items:center;gap:1rem;flex-wrap:wrap">
      <div style="flex:1;min-width:200px">
        <p style="margin:0 0 4px;font-size:14px;font-weight:700;color:#0D1B2A">👀 Míralo en acción</p>
        <p style="margin:0;font-size:13px;color:#475569;line-height:1.5">Explora la demo interactiva con el flujo real de WhatsApp para cada módulo.</p>
      </div>
      <a href="/demo/" style="display:inline-flex;align-items:center;gap:6px;background:#2563EB;color:#fff;text-decoration:none;border-radius:50px;padding:10px 22px;font-weight:700;font-size:13px;white-space:nowrap;transition:background .2s" onmouseover="this.style.background='#1D4ED8'" onmouseout="this.style.background='#2563EB'">Ver demo interactiva →</a>
    </div>

    <div class="article-author">
      <div class="author-av">CL</div>
      <div class="author-info">
        <strong>Equipo Clínicas Llenas</strong>
        <p>Ayudamos a clínicas privadas en España a automatizar su gestión con WhatsApp. Más de 87 clínicas confían en nosotros para reducir no-shows, reactivar pacientes y crecer sin contratar más personal.</p>
      </div>
    </div>
  </article>

  <aside class="article-sidebar">
    <div class="sidebar-toc">
      <h4>En este artículo</h4>
      <ul class="toc-list">
{{toc_items}}
      </ul>
    </div>
    <div class="sidebar-related">
      <h4>Artículos relacionados</h4>
{{related_items}}
    </div>
  </aside>
</div>

<footer class="footer">
  <div class="footer-inner">
    <span class="footer-copy">© 2026 Clínicas Llenas · Todos los derechos reservados</span>
    <nav class="footer-links">
      <a href="/">Inicio</a><a href="/blog/">Blog</a><a href="/privacidad">Privacidad</a>
    </nav>
  </div>
</footer>
<script>
const nav=document.getElementById('nav');
window.addEventListener('scroll',()=>nav.classList.toggle('scrolled',window.scrollY>40),{passive:true});
</script>

<!-- WhatsApp Float -->
<a href="https://wa.me/34628044918?text=Hola,%20quiero%20información%20sobre%20Clínicas%20Llenas"
   target="_blank" rel="noopener" aria-label="Contactar por WhatsApp"
   style="position:fixed;bottom:1.5rem;right:1.5rem;z-index:9998;
          width:56px;height:56px;border-radius:50%;
          background:#25D366;box-shadow:0 4px 20px rgba(37,211,102,0.45);
          display:flex;align-items:center;justify-content:center;
          transition:transform .2s,box-shadow .2s;text-decoration:none;"
   onmouseover="this.style.transform='scale(1.1)';this.style.boxShadow='0 6px 28px rgba(37,211,102,0.6)'"
   onmouseout="this.style.transform='scale(1)';this.style.boxShadow='0 4px 20px rgba(37,211,102,0.45)'">
  <svg xmlns="http://www.w3.org/2000/svg" width="30" height="30" viewBox="0 0 24 24" fill="white">
    <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
  </svg>
</a>

<!-- Cookie Banner -->
<div id="cookie-banner" role="dialog" aria-label="Gestión de cookies" aria-live="polite" style="
  display:none;
  position:fixed; bottom:1.5rem; left:50%; transform:translateX(-50%);
  z-index:9999;
  background:#fff;
  border:1px solid #e2e8f0;
  border-radius:16px;
  box-shadow:0 8px 40px rgba(15,23,42,0.14);
  padding:1.5rem 1.75rem;
  max-width:580px; width:calc(100% - 3rem);
  font-family:'Inter',sans-serif;
">
  <div style="display:flex;align-items:flex-start;gap:1rem;">
    <span style="font-size:22px;flex-shrink:0;">🍪</span>
    <div style="flex:1;">
      <p style="font-size:14px;font-weight:600;color:#0f172a;margin:0 0 4px;">Este sitio usa cookies</p>
      <p style="font-size:13px;color:#64748b;margin:0 0 1rem;line-height:1.5;">
        Usamos cookies técnicas (necesarias) y analíticas (Google Analytics) para mejorar tu experiencia.
        <a href="/cookies" style="color:#2563eb;text-decoration:underline;" target="_blank">Más información</a>
      </p>
      <div style="display:flex;gap:0.6rem;flex-wrap:wrap;">
        <button id="cookie-accept-all" style="
          background:#2563eb;color:#fff;border:none;border-radius:8px;
          padding:8px 18px;font-size:13px;font-weight:600;cursor:pointer;
          font-family:inherit;transition:background .2s;
        ">Aceptar todo</button>
        <button id="cookie-accept-essential" style="
          background:#f1f5f9;color:#334155;border:1px solid #e2e8f0;border-radius:8px;
          padding:8px 18px;font-size:13px;font-weight:500;cursor:pointer;
          font-family:inherit;transition:background .2s;
        ">Solo esenciales</button>
        <a href="/cookies" style="
          display:inline-flex;align-items:center;
          padding:8px 14px;font-size:13px;color:#64748b;
          font-family:inherit;text-decoration:none;
        ">Configurar</a>
      </div>
    </div>
  </div>
</div>

<script>
(function() {
  var COOKIE_KEY = 'cl_cookie_consent';
  var banner = document.getElementById('cookie-banner');
  function setCookie(name, value, days) {
    var d = new Date();
    d.setTime(d.getTime() + days * 24 * 60 * 60 * 1000);
    document.cookie = name + '=' + value + ';expires=' + d.toUTCString() + ';path=/;SameSite=Lax';
  }
  function getCookie(name) {
    var v = document.cookie.match('(^|;) ?' + name + '=([^;]*)(;|$)');
    return v ? v[2] : null;
  }
  function hideBanner() { banner.style.display = 'none'; }
  function showBanner() { banner.style.display = 'block'; }
  if (!getCookie(COOKIE_KEY)) { setTimeout(showBanner, 800); }
  document.getElementById('cookie-accept-all').addEventListener('click', function() {
    setCookie(COOKIE_KEY, 'all', 365); hideBanner();
  });
  document.getElementById('cookie-accept-essential').addEventListener('click', function() {
    setCookie(COOKIE_KEY, 'essential', 365); hideBanner();
  });
})();
</script>

</body>
</html>
"""


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
            try:
                html = (d / "index.html").read_text(encoding="utf-8")
                m = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.DOTALL)
                if m:
                    title = re.sub(r'<[^>]+>', '', m.group(1)).strip()
                    articles[d.name] = title
            except Exception:
                pass
    return articles


def pick_topics(used_slugs, count=5):
    """Elige N temas que no existan aún"""
    available = [t for t in TOPICS if t[0] not in used_slugs]
    random.shuffle(available)
    chosen = available[:count]
    while len(chosen) < count:
        cities = ["Madrid", "Barcelona", "Valencia", "Sevilla", "Málaga", "Bilbao", "Zaragoza"]
        city = random.choice(cities)
        year = datetime.now().year
        slug = f"automatizacion-clinica-dental-{city.lower()}-{year}-{len(chosen)}"
        chosen.append((slug, "automatización", f"Automatización para clínicas dentales en {city}: guía {year}", "Automatización"))
    return chosen


def get_cat_image(category):
    return CAT_IMAGES.get(category, "img-recordatorios.svg")


def generate_body_content(slug, category, category_label, title, published_articles):
    """
    Llama a Claude para generar SOLO el contenido del cuerpo del artículo
    (entre <article class="article-content"> y el banner "Míralo en acción")
    y los metadatos. Devuelve un dict con todas las piezas.
    """
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    related = [(s, t) for s, t in published_articles.items() if s != slug]
    random.shuffle(related)
    internal_links_context = "\n".join([f'- /blog/{s}/ → "{t}"' for s, t in related[:12]])

    prompt = f"""Eres el redactor SEO jefe de Clínicas Llenas, empresa B2B SaaS española que automatiza la gestión de clínicas privadas mediante WhatsApp.

Tienes que escribir un artículo de blog. El HTML que envuelve el artículo (navbar, hero, sidebar, footer, cookie banner, WhatsApp float) está YA HECHO y es fijo — solo tienes que generar los campos de contenido.

DATOS DEL ARTÍCULO:
- URL: https://clinicasllenas.com/blog/{slug}/
- Título H1: "{title}"
- Categoría: {category_label}

DEVUELVE EXACTAMENTE UN OBJETO JSON (sin ``` ni texto adicional) con estas claves:

{{
  "meta_title": "Título SEO max 60 chars (sin '| Clínicas Llenas', se añade después)",
  "meta_description": "Descripción SEO 150-160 chars con keyword principal",
  "excerpt": "Párrafo de entrada de 2-3 líneas que resume el artículo. Texto plano, NO HTML. Se muestra en un blockquote destacado.",
  "breadcrumb": "2-3 palabras para el breadcrumb (ej: 'Pacientes dormidos')",
  "read_time": 7,
  "keywords": ["keyword1", "keyword2", "keyword3"],
  "toc": [
    {{"id": "slug-de-seccion-1", "label": "Texto corto"}},
    {{"id": "slug-de-seccion-2", "label": "Texto corto"}}
  ],
  "body_html": "HTML COMPLETO del cuerpo del artículo"
}}

━━━ INSTRUCCIONES PARA body_html ━━━

El body_html DEBE:
- Empezar directamente con <h2 id="..."> (no <article>, no <div>, no contenedor)
- Tener entre 1.500 y 2.000 palabras
- Contener MÍNIMO 5 secciones <h2> con id="..." que coincida con los items del toc
- Al menos 1 sección puede tener <h3>
- Párrafos cortos (<p>), listas con <ul><li>, negritas con <strong>
- Incluir AL MENOS UN bloque .stat-grid con 3 .stat-box (estadísticas del sector)
- Incluir AL MENOS 2 .callout (usar clases callout-blue, callout-purple o callout-green) con estructura:
  <div class="callout callout-blue"><div class="callout-title">Título</div><p>Contenido</p></div>
- Incluir AL MENOS UN bloque .steps con 3-4 .step numerados (como el original)
- Incluir UN bloque .article-cta (caja oscura con CTA) antes de la conclusión con enlace a /#contacto
- Terminar con un <h2 id="conclusion">Conclusión</h2> y 2 párrafos finales
- Incluir 4-6 enlaces internos naturales usando estas URLs (texto ancla variado, NO el título exacto):
{internal_links_context}

CLASES CSS DISPONIBLES (ya están en el CSS, úsalas con el HTML indicado):

1. STAT GRID — 3 estadísticas:
<div class="stat-grid">
  <div class="stat-box"><span class="stat-box-num">40%</span><div class="stat-box-label">Texto corto</div></div>
  <div class="stat-box"><span class="stat-box-num">7x</span><div class="stat-box-label">Texto corto</div></div>
  <div class="stat-box"><span class="stat-box-num">34%</span><div class="stat-box-label">Texto corto</div></div>
</div>

2. CALLOUT — caja destacada:
<div class="callout callout-purple">
  <div class="callout-title">Título corto</div>
  <p>Texto del callout</p>
</div>

3. STEPS — pasos numerados:
<div class="steps">
  <div class="step"><div class="step-num">1</div><div class="step-body"><strong>Título paso</strong><p>Descripción del paso</p></div></div>
  <div class="step"><div class="step-num">2</div><div class="step-body"><strong>Título paso</strong><p>Descripción del paso</p></div></div>
</div>

4. CTA FINAL dentro del artículo:
<div class="article-cta">
  <div class="article-cta-inner">
    <h3>Pregunta potente relacionada con el tema</h3>
    <p>Frase corta que explique el valor.</p>
    <a href="/#contacto" class="article-cta-btn">Texto del botón →</a>
  </div>
</div>

SEO:
- Keyword principal en el primer párrafo y en al menos 2 H2
- Variaciones semánticas a lo largo del texto
- Párrafos cortos (3-4 líneas máx.) para mobile
- Datos concretos del sector salud privada España (odontología, fisio, estética)
- Tono: profesional, cercano, data-driven. No corporativo frío.

EL TOC debe coincidir EXACTAMENTE con los id="..." de los H2 del body_html.

DEVUELVE SOLO EL JSON, SIN MARKDOWN, SIN ``` , SIN TEXTO EXTRA."""

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=12000,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = message.content[0].text.strip()
    # Limpiar posibles code fences
    if raw.startswith("```json"):
        raw = raw[7:]
    if raw.startswith("```"):
        raw = raw[3:]
    if raw.endswith("```"):
        raw = raw[:-3]
    raw = raw.strip()

    data = json.loads(raw)
    return data


def build_article_html(slug, category, category_label, title, published_articles, today):
    """Genera el HTML final aplicando la plantilla literal"""
    data = generate_body_content(slug, category, category_label, title, published_articles)

    # Fecha legible en español
    meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
             "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    date_readable = f"{today.day} {meses[today.month - 1]} {today.year}"
    iso_date = today.strftime("%Y-%m-%dT09:00:00+02:00")

    # TOC items
    toc_html = "\n".join([
        f'        <li><a href="#{item["id"]}">{item["label"]}</a></li>'
        for item in data.get("toc", [])
    ])

    # Related items — elegir 2 artículos relacionados
    related_pool = [(s, t) for s, t in published_articles.items() if s != slug]
    random.shuffle(related_pool)
    related_sel = related_pool[:2]
    related_html = "\n".join([
        f'''      <div class="related-item">
        <a href="/blog/{s}/">{t}</a>
        <span>{random.randint(5, 9)} min lectura</span>
      </div>'''
        for s, t in related_sel
    ])

    # Keywords JSON
    keywords_json = json.dumps(data.get("keywords", [title.lower()]), ensure_ascii=False)

    # Substituciones
    replacements = {
        "{{slug}}": slug,
        "{{meta_title}}": data.get("meta_title", title)[:60],
        "{{meta_description}}": data.get("meta_description", "")[:160],
        "{{h1}}": title,
        "{{breadcrumb}}": data.get("breadcrumb", category_label),
        "{{category_label}}": category_label,
        "{{excerpt}}": data.get("excerpt", ""),
        "{{hero_image}}": get_cat_image(category),
        "{{date_readable}}": date_readable,
        "{{iso_date}}": iso_date,
        "{{read_time}}": str(data.get("read_time", 7)),
        "{{keywords_json}}": keywords_json,
        "{{body_content}}": data.get("body_html", ""),
        "{{toc_items}}": toc_html,
        "{{related_items}}": related_html,
    }

    html = TEMPLATE
    for k, v in replacements.items():
        html = html.replace(k, str(v))

    return html, data


def update_blog_index(slug, category, title, description, today_str):
    """Añade el nuevo artículo al índice del blog"""
    blog_index = Path(__file__).parent.parent / "blog" / "index.html"
    content = blog_index.read_text(encoding="utf-8")

    cat_colors = {
        "automatización": ("DBEAFE", "1D4ED8"),
        "whatsapp": ("D1FAE5", "065F46"),
        "no-shows": ("FEF3C7", "92400E"),
        "pacientes": ("FCE7F3", "9D174D"),
        "gestión": ("EDE9FE", "5B21B6"),
    }
    bg, fg = cat_colors.get(category, ("F1F5F9", "334155"))

    new_card = f"""
      <article class="blog-card" data-cat="{category}">
        <a href="/blog/{slug}/">
          <div class="blog-card-img" style="background:linear-gradient(135deg,#EFF6FF,#F0FDF4);display:flex;align-items:center;justify-content:center;height:180px">
            <img src="/blog/{get_cat_image(category)}" alt="{title}" style="height:120px;width:auto" loading="lazy">
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
    today = datetime.now()

    meses_abbr = {1: "Ene", 2: "Feb", 3: "Mar", 4: "Abr", 5: "May", 6: "Jun",
                  7: "Jul", 8: "Ago", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dic"}
    today_str = f"{today.day} {meses_abbr[today.month]} {today.year}"

    generated_slugs = []

    for i, (slug, category, title, category_label) in enumerate(topics, 1):
        print(f"\n📝 [{i}/5] Generando: {title}")

        try:
            html, data = build_article_html(slug, category, category_label, title, published, today)

            article_dir = Path(__file__).parent.parent / "blog" / slug
            article_dir.mkdir(parents=True, exist_ok=True)
            (article_dir / "index.html").write_text(html, encoding="utf-8")
            print(f"   ✅ Guardado en blog/{slug}/")

            description = data.get("meta_description") or f"Guía sobre {title.lower()} para clínicas privadas en España."

            update_blog_index(slug, category, title, description, today_str)
            print(f"   ✅ Añadido al índice del blog")

            published[slug] = title
            generated_slugs.append(slug)

        except Exception as e:
            print(f"   ❌ Error generando {slug}: {e}")

    if generated_slugs:
        update_sitemap(generated_slugs)
        print(f"\n✅ Sitemap actualizado con {len(generated_slugs)} nuevas URLs")

    print(f"\n🎉 Completado: {len(generated_slugs)}/5 artículos publicados")
    for slug in generated_slugs:
        print(f"   → https://clinicasllenas.com/blog/{slug}/")


if __name__ == "__main__":
    main()
