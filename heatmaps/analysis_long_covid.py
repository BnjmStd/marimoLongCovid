import marimo

__generated_with = "0.19.6"
app = marimo.App(width="medium")


@app.cell
def _():
    import sys
    from pathlib import Path

    # Asegurar que la raíz del proyecto está en sys.path
    _root = str(Path("__file__").resolve().parent.parent)
    if _root not in sys.path:
        sys.path.insert(0, _root)

    import marimo as mo
    import polars as pl

    from modules import (
        load_long_covid,
        create_criterio_variables,
        plot_clusters_heatmap_by_diagnosis_week,
        plot_criterios_hospitalizacion_heatmap_agrupado_sexo,
    )

    # Funciones locales mejoradas con IDs de paciente
    from heatmap_utils import plot_heatmap_opcionC_con_ids, plot_heatmap_opcionC_arbol_ids, plot_clusters_heatmap_normalizado

    return (
        create_criterio_variables,
        load_long_covid,
        mo,
        pl,
        plot_clusters_heatmap_by_diagnosis_week,
        plot_clusters_heatmap_normalizado,
        plot_criterios_hospitalizacion_heatmap_agrupado_sexo,
        plot_heatmap_opcionC_con_ids,
        plot_heatmap_opcionC_arbol_ids,
    )


@app.cell
def _(mo):
    mo.md("""
    # Análisis Heatmaps — Long COVID Chile 2020-2021

    Notebook dedicado a los heatmaps seleccionados para iteración rápida:

    1. **Heatmap Opción C** — Criterios Long COVID agrupado por Hospitalización × Sexo
    2. **Heatmap Opción C + IDs** — Versión mejorada con identificadores de paciente
    2d. **Heatmap Opción C + Árbol** — Panel inferior con TODOS los IDs en texto vertical
    3. **Heatmap de Clusters** — Síntomas (ordenados por cluster) por semana de diagnóstico
    """)
    return


@app.cell
def _(mo):
    mo.md("""## 1. Cargar Dataset y Preparar Criterios""")
    return


@app.cell
def _(load_long_covid, create_criterio_variables, mo, pl):
    # Cargar dataset (ruta relativa al root del proyecto)
    df_raw = load_long_covid("datasets/longcovid_2020W13-2021W22.csv")
    df_con_criterios = create_criterio_variables(df_raw)

    mo.md(
        f"""
    **Dataset cargado:**
    - Registros: {len(df_con_criterios):,}
    - Columnas: {len(df_con_criterios.columns)}
    - Periodo: 2020W13 – 2021W22
    """
    )
    return (df_con_criterios,)


# ── Heatmap Opción C: Criterios × Hospitalización × Sexo ────────────────────


@app.cell
def _(mo):
    mo.md("""
    ---
    ## 2. Heatmap Opción C — Criterios Long COVID agrupado por Hospitalización y Sexo

    Pacientes ordenados como **Hosp-H → Hosp-M → No Hosp-H → No Hosp-M**.
    Dentro de cada subgrupo, los pacientes se ordenan por cumplimiento de criterios
    (C1 > C2 > C3 > C4 desc.), de forma que los que cumplen aparecen a la izquierda.

    **Codificación:** Azul oscuro = Cumple criterio | Rosa claro = No cumple
    """)
    return


@app.cell
def _(df_con_criterios, plot_criterios_hospitalizacion_heatmap_agrupado_sexo):
    fig_heatmap_opcionC = plot_criterios_hospitalizacion_heatmap_agrupado_sexo(
        df_con_criterios
    )
    fig_heatmap_opcionC
    return (fig_heatmap_opcionC,)


# ── Heatmap Opción C con IDs de paciente ─────────────────────────────────────


@app.cell
def _(mo):
    mo.md("""
    ---
    ## 2b. Heatmap Opción C — CON IDs de Paciente

    Versión mejorada que incluye `cod_participante` en el eje X inferior.
    Al hacer hover sobre cada celda se muestra el ID, posición, sexo, grupo y criterios.

    > **Nota:** Se muestran IDs representativos (1ro, último y cada ~50 pacientes por grupo).
    > Para la tabla completa paciente-a-paciente ver el archivo TXT generado.
    """)
    return


@app.cell
def _(df_con_criterios, plot_heatmap_opcionC_con_ids):
    fig_heatmap_opcionC_ids = plot_heatmap_opcionC_con_ids(df_con_criterios)
    fig_heatmap_opcionC_ids
    return (fig_heatmap_opcionC_ids,)


# ── Heatmap Opción C con ÁRBOL de IDs ────────────────────────────────────────


@app.cell
def _(mo):
    mo.md("""
    ---
    ## 2d. Heatmap Opción C — ÁRBOL de IDs de Paciente

    Panel superior: heatmap estándar (4 criterios × pacientes).  
    Panel inferior: **TODOS** los `cod_participante` en texto vertical rotado 90°.

    - IDs en **azul** = Hombre (H), en **rosa** = Mujer (M)
    - Separadores verticales conectan ambos paneles
    - Para ver cada ID con nitidez, exportar a PNG con ancho ≥ 4000px
    """)
    return


@app.cell
def _(df_con_criterios, plot_heatmap_opcionC_arbol_ids):
    fig_heatmap_arbol = plot_heatmap_opcionC_arbol_ids(df_con_criterios)
    fig_heatmap_arbol
    return (fig_heatmap_arbol,)


# ── Tabla detalle TXT ────────────────────────────────────────────────────────


@app.cell
def _(mo):
    mo.md("""
    ---
    ## 2c. Tabla Detalle Paciente-a-Paciente

    Resumen de criterios por grupo (datos del TXT).

    > Ejecuta `python heatmaps/generate_table_opcionC.py` para generar el archivo completo.
    """)
    return


@app.cell
def _(df_con_criterios, mo, pl):
    from generate_table_opcionC import _prepare_data

    groups = _prepare_data(df_con_criterios)

    # Mostrar resumen en el notebook
    resumen_lines = []
    for group_label, df_group in groups.items():
        n = df_group.height
        c1 = df_group.filter(pl.col("criterio_1") == 1).height
        c2 = df_group.filter(pl.col("criterio_2") == 1).height
        c3 = df_group.filter(pl.col("criterio_3") == 1).height
        c4 = df_group.filter(pl.col("criterio_4") == 1).height
        resumen_lines.append(
            f"| {group_label} | {n} | {c1} ({c1/n*100:.1f}%) | {c2} ({c2/n*100:.1f}%) | {c3} ({c3/n*100:.1f}%) | {c4} ({c4/n*100:.1f}%) |"
        )

    mo.md(
        "### Resumen por grupo\n\n"
        "| Grupo | n | C1 | C2 | C3 | C4 |\n"
        "|-------|---|----|----|----|----|---|\n"
        + "\n".join(resumen_lines)
    )
    return


# ── Heatmap de Clusters por Semana de Diagnóstico ───────────────────────────


@app.cell
def _(mo):
    mo.md("""
    ---
    ## 3. Heatmap de Clusters por Semana de Diagnóstico

    Muestra la prevalencia de cada **síntoma individual** (agrupado por cluster)
    a lo largo de las semanas epidemiológicas.

    **Clusters:** AIRWAYS · COGNITIVE · GASTROINTESTINAL · MUSCULAR · RESPIRATORY · SMELL/TASTE

    **Color (Viridis):** Amarillo/verde = mayor n° de casos · Azul oscuro = menor n° de casos
    """)
    return


@app.cell
def _(df_con_criterios, plot_clusters_heatmap_by_diagnosis_week):
    fig_heatmap_clusters = plot_clusters_heatmap_by_diagnosis_week(df_con_criterios)
    fig_heatmap_clusters
    return (fig_heatmap_clusters,)


@app.cell
def _(mo):
    mo.md("""
    **Interpretación:**
    - **Eje X**: Semana epidemiológica (semana de diagnóstico COVID)
    - **Eje Y**: Síntomas individuales ≥3 meses, agrupados por cluster
    - Líneas blancas separan los clusters
    - Permite identificar patrones temporales y clusters predominantes en cada período
    """)
    return


# ── Heatmap de Clusters NORMALIZADO ────────────────────────────────────────


@app.cell
def _(mo):
    mo.md("""
    ---
    ## 4. Heatmap de Clusters NORMALIZADO por Semana

    Mismos síntomas y clusters que el anterior, pero cada celda muestra la
    **proporción** de pacientes con ese síntoma respecto al total de pacientes
    de esa semana.

    > celda = nº pacientes con síntoma / total pacientes de esa semana

    Esto permite comparar semanas con distinto número de pacientes sin que
    las semanas más pobladas dominen visualmente.
    """)
    return


@app.cell
def _(df_con_criterios, plot_clusters_heatmap_normalizado):
    fig_clusters_norm = plot_clusters_heatmap_normalizado(df_con_criterios)
    fig_clusters_norm
    return (fig_clusters_norm,)


if __name__ == "__main__":
    app.run()
