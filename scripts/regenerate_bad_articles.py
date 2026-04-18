#!/usr/bin/env python3
"""
Regenera los artículos que se crearon con el prompt viejo y quedaron
con estructura/tipografía rota. Usa la nueva plantilla literal.

Ejecutar via GitHub Actions con workflow_dispatch.

Uso:
  python regenerate_bad_articles.py           # regenera TODOS los BAD_SLUGS
  python regenerate_bad_articles.py 1         # regenera solo el primero (test)
  python regenerate_bad_articles.py 3         # regenera los 3 primeros
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Añadir el directorio al path para poder importar generate_blog
sys.path.insert(0, str(Path(__file__).parent))

from generate_blog import (
    TOPICS,
    build_article_html,
    get_all_published_articles,
    get_cat_image,
    update_blog_index,
    update_sitemap,
)

# Los 10 artículos generados mal que hay que regenerar
BAD_SLUGS = [
    "automatizar-respuestas-whatsapp-clinica",
    "chatbot-whatsapp-clinica-dental-configurar",
    "como-escalar-clinica-dental-privada",
    "coste-real-no-show-clinica-dental",
    "fidelizar-pacientes-clinica-dental",
    "flujos-trabajo-automatizados-clinica",
    "integracion-whatsapp-software-clinica",
    "presupuestos-automaticos-clinica-dental",
    "segmentacion-pacientes-clinica-dental",
    "turnos-espera-clinica-dental-optimizar",
]


def find_topic(slug):
    for t in TOPICS:
        if t[0] == slug:
            return t
    return None


def main():
    # Determinar cuántos artículos regenerar
    # 1. arg CLI, 2. env var COUNT, 3. todos
    count = None
    if len(sys.argv) > 1:
        try:
            count = int(sys.argv[1])
        except ValueError:
            pass
    if count is None and os.environ.get("COUNT"):
        try:
            count = int(os.environ["COUNT"])
        except ValueError:
            pass

    slugs_to_regen = BAD_SLUGS if count is None else BAD_SLUGS[:count]

    print(f"🔄 Regenerando {len(slugs_to_regen)} artículo(s) con plantilla correcta")
    if count is not None:
        print(f"   (modo test: solo los {count} primero(s))")
    today = datetime.now()

    # Obtener publicados — EXCLUYENDO los que vamos a regenerar
    # para que sus contenidos no se contaminen entre sí con enlaces rotos
    all_published = get_all_published_articles()
    # Mantenemos sus títulos "limpios" del TOPICS, no los rotos
    for slug in BAD_SLUGS:
        topic = find_topic(slug)
        if topic:
            all_published[slug] = topic[2]

    meses_abbr = {1: "Ene", 2: "Feb", 3: "Mar", 4: "Abr", 5: "May", 6: "Jun",
                  7: "Jul", 8: "Ago", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dic"}
    today_str = f"{today.day} {meses_abbr[today.month]} {today.year}"

    regenerated = []
    total = len(slugs_to_regen)

    for i, slug in enumerate(slugs_to_regen, 1):
        topic = find_topic(slug)
        if not topic:
            print(f"   ⚠️ [{i}/{total}] Slug {slug} no está en TOPICS, saltando")
            continue

        slug, category, title, category_label = topic
        print(f"\n📝 [{i}/{total}] Regenerando: {title}")

        try:
            published_without_self = {s: t for s, t in all_published.items() if s != slug}

            html, data = build_article_html(
                slug, category, category_label, title, published_without_self, today
            )

            article_dir = Path(__file__).parent.parent / "blog" / slug
            article_dir.mkdir(parents=True, exist_ok=True)
            (article_dir / "index.html").write_text(html, encoding="utf-8")
            print(f"   ✅ Creado blog/{slug}/index.html")

            description = data.get("meta_description") or f"Guía sobre {title.lower()} para clínicas privadas en España."
            update_blog_index(slug, category, title, description, today_str)
            print(f"   ✅ Card añadida al blog index")

            regenerated.append(slug)

        except Exception as e:
            print(f"   ❌ Error regenerando {slug}: {e}")

    if regenerated:
        update_sitemap(regenerated)
        print(f"\n✅ Sitemap actualizado con {len(regenerated)} URLs")

    print(f"\n🎉 Regenerados {len(regenerated)}/{total} artículos con plantilla correcta")


if __name__ == "__main__":
    main()
