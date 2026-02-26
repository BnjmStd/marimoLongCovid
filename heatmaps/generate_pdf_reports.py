#!/usr/bin/env python3
"""
Generador de PDFs y tabla TXT para los Heatmaps seleccionados:
  1. Heatmap Opción C — Criterios Long COVID agrupado por Hospitalización × Sexo
  2. Heatmap Opción C con IDs — Versión mejorada con cod_participante
  3. Heatmap de Clusters — Síntomas por semana de diagnóstico
  4. Tabla TXT detalle paciente-a-paciente

Uso:
    cd marimoLongCovid          # ejecutar desde la raíz del proyecto
    python heatmaps/generate_pdf_reports.py
"""

import os
import sys
from pathlib import Path

# ── Asegurar que la raíz del proyecto y la carpeta heatmaps están en sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
HEATMAPS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(HEATMAPS_DIR))

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT

# Imports de módulos del proyecto
from modules import (
    load_data,
    create_criterio_variables,
    plot_clusters_heatmap_by_diagnosis_week,
    plot_criterios_hospitalizacion_heatmap_agrupado_sexo,
)

# Funciones locales mejoradas con IDs
from heatmap_utils import (
    plot_heatmap_opcionC_con_ids,
    plot_heatmap_opcionC_arbol_ids,
    plot_clusters_heatmap_normalizado,
)

# Generador de tabla TXT
from generate_table_opcionC import generate_txt_table

# ── Directorios de salida ───────────────────────────────────────────────────
OUTPUT_DIR = Path(__file__).resolve().parent / "pdf_reports"
OUTPUT_DIR.mkdir(exist_ok=True)

IMG_DIR = OUTPUT_DIR / "temp_images"
IMG_DIR.mkdir(exist_ok=True)


# ── Utilidades ──────────────────────────────────────────────────────────────

def clean_filename(title: str) -> str:
    """Limpia el título para usarlo como nombre de archivo."""
    import re
    cleaned = re.sub(r'[^\w\s-]', '', title)
    cleaned = re.sub(r'[-\s]+', '_', cleaned)
    return cleaned[:100]


def save_plotly_figure_as_image(
    fig, filename: str, width: int = 1200, height: int = 800
) -> str | None:
    """Guarda una figura de Plotly como imagen PNG."""
    img_path = IMG_DIR / f"{filename}.png"
    try:
        fig.write_image(str(img_path), width=width, height=height)
    except Exception as e:
        print(f"   ⚠️  kaleido falló, intentando orca: {e}")
        try:
            import plotly.io as pio
            pio.write_image(fig, str(img_path), format="png", width=width, height=height)
        except Exception as e2:
            print(f"   ❌ Error guardando imagen: {e2}")
            return None
    return str(img_path)


def create_pdf_report(
    title: str,
    interpretation: str,
    image_path: str,
    output_filename: str,
) -> None:
    """Crea un PDF con título + gráfico (imagen)."""
    pdf_path = OUTPUT_DIR / output_filename

    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=1 * inch,
        bottomMargin=0.75 * inch,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=16,
        textColor=HexColor("#2c3e50"),
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName="Helvetica-Bold",
    )

    normal_style = ParagraphStyle(
        "CustomNormal",
        parent=styles["Normal"],
        fontSize=11,
        leading=16,
        alignment=TA_LEFT,
        spaceAfter=12,
        fontName="Helvetica",
    )

    story = []
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 0.3 * inch))

    if image_path and os.path.exists(image_path):
        available_width = letter[0] - 1.5 * inch
        available_height = letter[1] - 2 * inch
        img = Image(
            image_path,
            width=available_width,
            height=available_height,
            kind="proportional",
        )
        story.append(img)
    else:
        story.append(Paragraph("<i>Imagen no disponible</i>", normal_style))

    doc.build(story)
    print(f"   ✅ PDF creado: {pdf_path.name}")


# ── Generación ──────────────────────────────────────────────────────────────

def generate_heatmap_reports() -> None:
    """Genera los PDFs de los heatmaps seleccionados + tabla TXT."""
    print("=" * 70)
    print("GENERADOR DE REPORTES PDF — HEATMAPS LONG COVID")
    print("=" * 70)

    # 1. Cargar datos (ruta relativa a la raíz del proyecto)
    dataset_path = ROOT_DIR / "datasets" / "longcovid_2020W13-2021W22.csv"
    print(f"\n📊 Cargando datos desde {dataset_path} ...")
    df = load_data(str(dataset_path))
    df_con_criterios = create_criterio_variables(df)
    print(f"   ✅ {df_con_criterios.height:,} registros cargados")

    # 2. Generar tabla TXT
    print("\n📝 Generando tabla TXT detalle paciente-a-paciente...")
    try:
        txt_path = generate_txt_table()
        print(f"   ✅ Tabla TXT: {txt_path}")
    except Exception as e:
        print(f"   ❌ Error generando TXT: {e}")

    # 3. Definir reportes PDF
    reports = [
        # ── Heatmap Opción C (original) ──────────────────────────────────
        {
            "function": plot_criterios_hospitalizacion_heatmap_agrupado_sexo,
            "args": (df_con_criterios,),
            "title": "Heatmap Opcion C - Agrupado por Hospitalizacion y Sexo",
            "img_width": 1800,
            "img_height": 600,
            "interpretation": """
**Heatmap Opción C: Pacientes ordenados Hosp-H → Hosp-M → No Hosp-H → No Hosp-M**

**Estructura con encabezados de 2 niveles:**
- Nivel superior: "Hospitalizados" (fondo rosa) | "No hospitalizados" (fondo gris)
- Nivel inferior: "H" (azul) y "M" (fucsia) dentro de cada grupo
- 3 separadores verticales: H|M hosp, hosp|no_hosp, H|M no_hosp

**Codificación:**
- Azul oscuro (#2C3E7A): Cumple criterio | Rosa claro (#F4C2C2): No cumple
            """,
        },
        # ── Heatmap Opción C con IDs de paciente ────────────────────────
        {
            "function": plot_heatmap_opcionC_con_ids,
            "args": (df_con_criterios,),
            "title": "Heatmap Opcion C - Con IDs de Paciente",
            "img_width": 2000,
            "img_height": 700,
            "interpretation": """
**Heatmap Opción C mejorado: incluye cod_participante en eje X**

- Eje X muestra IDs representativos (1ro, último y cada ~50 pacientes por grupo)
- Hover muestra: ID, posición, sexo, hospitalización, criterios
- Consultar tabla TXT para el listado completo paciente-a-paciente
            """,
        },
        # ── Heatmap de Clusters por Semana de Diagnóstico ────────────────
        {
            "function": plot_clusters_heatmap_by_diagnosis_week,
            "args": (df_con_criterios,),
            "title": "Heatmap de Clusters por Semana de Diagnostico",
            "img_width": 1400,
            "img_height": 900,
            "interpretation": """
**Estructura:**
Eje X: Semana epidemiológica | Eje Y: Síntomas individuales (agrupados por cluster)

**Clusters:** AIRWAYS · COGNITIVE · GASTROINTESTINAL · MUSCULAR · RESPIRATORY · SMELL/TASTE

**Hallazgos clave:**
- Colores cálidos (amarillo) = mayor número de casos
- Colores fríos (azul) = menor número de casos
- Líneas blancas separan los clusters
            """,
        },
        # ── Heatmap Opción C con Árbol de IDs ───────────────────────────
        {
            "function": plot_heatmap_opcionC_arbol_ids,
            "args": (df_con_criterios,),
            "title": "Heatmap Opcion C - Arbol de IDs de Paciente",
            "img_width": 4000,
            "img_height": 1800,
            "interpretation": """
**Heatmap Opción C + panel inferior "árbol" con todos los cod_participante**

- Panel superior: Heatmap estándar (4 criterios × pacientes)
- Panel inferior: TODOS los IDs de paciente en texto vertical rotado 90°
- IDs coloreados: azul = Hombre (H), rosa = Mujer (M)
- Para ver todos los IDs con nitidez, abrir la imagen PNG directamente
- Separadores verticales conectan ambos paneles
            """,
        },
        # ── Heatmap de Clusters NORMALIZADO por semana ────────────────
        {
            "function": plot_clusters_heatmap_normalizado,
            "args": (df_con_criterios,),
            "title": "Heatmap Clusters Normalizado por Semana",
            "img_width": 1400,
            "img_height": 900,
            "interpretation": """
**Heatmap de síntomas (por cluster) × semana epidemiológica — NORMALIZADO**

- Cada celda = nº pacientes con síntoma / total pacientes de esa semana
- Valores entre 0% y 100% (proporciones)
- Permite comparar semanas con distinto nº de pacientes
- Escala Viridis: amarillo = alta proporción, azul oscuro = baja
- Líneas blancas separan los clusters
            """,
        },
    ]

    print(f"\n📝 Generando {len(reports)} reportes PDF...")
    print("-" * 70)

    for i, report in enumerate(reports, 1):
        print(f"\n{i}/{len(reports)} — {report['title']}")

        try:
            print("   🎨 Generando gráfico...")
            fig = report["function"](*report["args"])

            print("   💾 Guardando imagen temporal...")
            img_filename = clean_filename(report["title"])
            img_w = report.get("img_width", 1200)
            img_h = report.get("img_height", 800)
            img_path = save_plotly_figure_as_image(fig, img_filename, width=img_w, height=img_h)

            if img_path is None:
                print("   ⚠️  Saltando (no se pudo generar imagen)")
                continue

            print("   📄 Creando PDF...")
            pdf_filename = f"{clean_filename(report['title'])}.pdf"
            create_pdf_report(
                report["title"],
                report["interpretation"],
                img_path,
                pdf_filename,
            )

        except Exception as e:
            print(f"   ❌ Error: {e}")
            import traceback
            traceback.print_exc()
            continue

    print("\n" + "=" * 70)
    print("✅ PROCESO COMPLETADO")
    print("=" * 70)
    print(f"\n📁 PDFs generados en: {OUTPUT_DIR.absolute()}")
    print(f"🗑️  Imágenes temporales en: {IMG_DIR.absolute()}")
    print("=" * 70)


if __name__ == "__main__":
    generate_heatmap_reports()
