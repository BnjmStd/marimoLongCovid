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

import re
import sys
from pathlib import Path

# ── Asegurar que la raíz del proyecto y la carpeta heatmaps están en sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
HEATMAPS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(HEATMAPS_DIR))

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
    plot_clusters_heatmap_normalizado_sin_numeros,
    plot_clusters_heatmap_normalizado_sin_nulos,
    plot_clusters_individuales_by_week,
)

# Generador de tabla TXT
from generate_table_opcionC import generate_txt_table

# ── Directorios de salida ───────────────────────────────────────────────────
OUTPUT_DIR = Path(__file__).resolve().parent / "pdf_reports"
OUTPUT_DIR.mkdir(exist_ok=True)


# ── Utilidades ──────────────────────────────────────────────────────────────


def clean_filename(title: str) -> str:
    """Limpia el título para usarlo como nombre de archivo."""
    cleaned = re.sub(r'[^\w\s-]', '', title)
    cleaned = re.sub(r'[-\s]+', '_', cleaned)
    return cleaned[:100]


def save_plotly_as_vector_pdf(
    fig,
    output_path: Path,
    width: int = 1400,
    height: int = 900,
) -> bool:
    """
    Guarda una figura Plotly directamente como **PDF vectorial** usando kaleido.
    No requiere reportlab ni imágenes temporales PNG.
    """
    try:
        fig.write_image(str(output_path), format="pdf", width=width, height=height)
        return True
    except Exception as e:
        print(f"   ❌ Error generando PDF vectorial: {e}")
        import traceback
        traceback.print_exc()
        return False


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
        # ── Heatmap Normalizado — síntomas figura paper (sin nulos) ──────
        {
            "function": plot_clusters_heatmap_normalizado_sin_nulos,
            "args": (df_con_criterios,),
            "title": "Heatmap Normalizado - Sintomas Figura Paper (sin nulos)",
            "img_width": 1400,
            "img_height": 900,
            "interpretation": """
**Heatmap de síntomas (figura del paper) × semana — NORMALIZADO sin nulos**

Síntomas replicados exactamente desde la figura de referencia.
Denominador corregido: se excluyen NULLs por columna y semana.
            """,
        },
        # ── Heatmap Normalizado por semana — SIN números en celda ────────
        {
            "function": plot_clusters_heatmap_normalizado_sin_numeros,
            "args": (df_con_criterios,),
            "title": "Heatmap Clusters Normalizado por Semana Sin Numeros",
            "img_width": 1400,
            "img_height": 900,
            "interpretation": """
**Heatmap de síntomas (por cluster) × semana epidemiológica — NORMALIZADO**

Idéntico al heatmap normalizado estándar pero sin mostrar el conteo n
dentro de cada celda (versión limpia para publicación / PDF vectorial).
            """,
        },
        # ── Barplot clusters individuales por semana ──────────────────────
        {
            "function": plot_clusters_individuales_by_week,
            "args": (df_con_criterios,),
            "title": "Clusters Individuales por Semana Epidemiologica",
            "img_width": 1400,
            "img_height": 600,
            "interpretation": """
**Barplot apilado por semana — Clusters Individuales Long COVID**

Barras = pertenencias a clusters (multi-conteo, un paciente puede pertenecer
a varios clusters simultáneamente).
Línea negra punteada (eje derecho) = N pacientes únicos por semana.
            """,
        },
    ]

    print(f"\n📝 Generando {len(reports)} PDFs vectoriales...")
    print("-" * 70)

    generated, failed = [], []
    for i, report in enumerate(reports, 1):
        title = report["title"]
        print(f"\n{i}/{len(reports)} — {title}")

        try:
            print("   🎨 Generando gráfico...")
            fig = report["function"](*report["args"])

            pdf_filename = f"{clean_filename(title)}.pdf"
            pdf_path = OUTPUT_DIR / pdf_filename
            w = report.get("img_width", 1400)
            h = report.get("img_height", 900)

            print("   📄 Guardando PDF vectorial...")
            ok = save_plotly_as_vector_pdf(fig, pdf_path, width=w, height=h)
            if ok:
                print(f"   ✅ {pdf_filename}")
                generated.append(pdf_filename)
            else:
                failed.append(title)

        except Exception as e:
            print(f"   ❌ Error: {e}")
            import traceback
            traceback.print_exc()
            failed.append(title)
            continue

    print("\n" + "=" * 70)
    print("✅ PROCESO COMPLETADO")
    print("=" * 70)
    print(f"\n📁 PDFs vectoriales en: {OUTPUT_DIR.absolute()}")
    print(f"   Generados: {len(generated)} | Fallidos: {len(failed)}")
    if failed:
        print("   Fallidos:", failed)
    print("=" * 70)


if __name__ == "__main__":
    generate_heatmap_reports()
