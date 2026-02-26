"""
Funciones de visualización mejoradas para los heatmaps.
Extienden las funciones de modules/visualizations.py con mejoras locales.
"""

from __future__ import annotations

from typing import Any, TypedDict

import plotly.graph_objects as go
import polars as pl


class HeatmapData(TypedDict):
    """Datos preparados para los heatmaps Opción C."""

    df_sorted: pl.DataFrame
    patient_ids: list[str]
    hosp_arr: Any  # NDArray from polars .to_numpy()
    sexo_arr: Any  # NDArray
    sum_arr: Any   # NDArray
    n_hosp_H: int
    n_hosp_M: int
    n_no_hosp_H: int
    n_no_hosp_M: int
    n_hosp: int
    n_total: int


# ── Utilidades compartidas ──────────────────────────────────────────────────

def _prepare_heatmap_data(df: pl.DataFrame) -> HeatmapData:
    """
    Prepara los datos para el heatmap Opción C: filtra, divide en 4 grupos,
    ordena y devuelve todo lo necesario para graficar.
    Reutilizado por ambas funciones de heatmap.
    """

    hosp_col = df["Hospitalización"]
    if hosp_col.dtype in (pl.Utf8, pl.String):
        df_h = df.with_columns(
            pl.when(pl.col("Hospitalización") == "1").then(1)
            .when(pl.col("Hospitalización") == "0").then(0)
            .otherwise(pl.lit(None)).cast(pl.Int32).alias("_hosp_num")
        )
    else:
        df_h = df.with_columns(
            pl.when(pl.col("Hospitalización") == 1).then(1)
            .when(pl.col("Hospitalización") == 0).then(0)
            .otherwise(pl.lit(None)).cast(pl.Int32).alias("_hosp_num")
        )
    df_h = df_h.filter(~pl.col("_hosp_num").is_null())

    def sort_by_criterios(sub: pl.DataFrame) -> pl.DataFrame:
        return sub.sort(
            ["criterio_1", "criterio_2", "criterio_3", "criterio_4"],
            descending=[True, True, True, True],
        )

    df_hosp_H    = sort_by_criterios(df_h.filter((pl.col("_hosp_num") == 1) & (pl.col("sexo") == 1)))
    df_hosp_M    = sort_by_criterios(df_h.filter((pl.col("_hosp_num") == 1) & (pl.col("sexo") == 2)))
    df_no_hosp_H = sort_by_criterios(df_h.filter((pl.col("_hosp_num") == 0) & (pl.col("sexo") == 1)))
    df_no_hosp_M = sort_by_criterios(df_h.filter((pl.col("_hosp_num") == 0) & (pl.col("sexo") == 2)))

    df_sorted = pl.concat([df_hosp_H, df_hosp_M, df_no_hosp_H, df_no_hosp_M])

    n_hosp_H    = df_hosp_H.height
    n_hosp_M    = df_hosp_M.height
    n_no_hosp_H = df_no_hosp_H.height
    n_no_hosp_M = df_no_hosp_M.height
    n_hosp      = n_hosp_H + n_hosp_M
    n_total     = df_sorted.height

    id_col = "cod_participante" if "cod_participante" in df_sorted.columns else "newCode"
    patient_ids = df_sorted[id_col].cast(pl.Utf8).to_list()

    hosp_arr = df_sorted["_hosp_num"].to_numpy()
    sexo_arr = df_sorted["sexo"].to_numpy()
    sum_arr  = (
        df_sorted["criterio_1"].cast(pl.Int32) +
        df_sorted["criterio_2"].cast(pl.Int32) +
        df_sorted["criterio_3"].cast(pl.Int32) +
        df_sorted["criterio_4"].cast(pl.Int32)
    ).to_numpy()

    return HeatmapData(
        df_sorted=df_sorted,
        patient_ids=patient_ids,
        hosp_arr=hosp_arr,
        sexo_arr=sexo_arr,
        sum_arr=sum_arr,
        n_hosp_H=n_hosp_H,
        n_hosp_M=n_hosp_M,
        n_no_hosp_H=n_no_hosp_H,
        n_no_hosp_M=n_no_hosp_M,
        n_hosp=n_hosp,
        n_total=n_total,
    )


def _build_z_and_hover(data: HeatmapData, include_ids: bool = True) -> tuple[list[list[int]], list[list[str]]]:
    """Construye z_matrix y hover_main para el heatmap."""
    criterios = [1, 2, 3, 4]
    n_total = data["n_total"]
    df_sorted = data["df_sorted"]
    patient_ids = data["patient_ids"]
    hosp_arr = data["hosp_arr"]
    sexo_arr = data["sexo_arr"]
    sum_arr = data["sum_arr"]

    z_matrix = []
    hover_main = []
    for crit in criterios:
        crit_arr = df_sorted[f"criterio_{crit}"].to_numpy()
        row, rh = [], []
        for i in range(n_total):
            v = int(crit_arr[i])
            sx = "H" if sexo_arr[i] == 1 else "M"
            hs = "Hospitalizado" if hosp_arr[i] == 1 else "No hospitalizado"
            row.append(v)
            id_line = f"<b>ID: {patient_ids[i]}</b><br>" if include_ids else ""
            rh.append(
                f"{id_line}"
                f"Pos: {i+1}/{n_total}<br>"
                f"Sexo: {sx}<br>{hs}<br>"
                f"Criterios: {int(sum_arr[i])}/4<br>"
                f"C{crit}: {'<b>Cumple ✓</b>' if v else 'No cumple ✗'}"
            )
        z_matrix.append(row)
        hover_main.append(rh)
    return z_matrix, hover_main


def _add_header_annotations(fig: go.Figure, data: HeatmapData, header2_y: float = 1.04, header1_y: float = 1.18, xref: str = "x") -> None:
    """Agrega los encabezados de 2 niveles (Hosp/NoHosp × H/M) a la figura."""
    n_hosp_H = data["n_hosp_H"]
    n_hosp_M = data["n_hosp_M"]
    n_no_hosp_H = data["n_no_hosp_H"]
    n_no_hosp_M = data["n_no_hosp_M"]
    n_hosp = data["n_hosp"]

    cx_hosp_H    = (n_hosp_H - 1) / 2
    cx_hosp_M    = n_hosp_H + (n_hosp_M - 1) / 2
    cx_hosp      = (n_hosp - 1) / 2
    cx_no_hosp_H = n_hosp + (n_no_hosp_H - 1) / 2
    cx_no_hosp_M = n_hosp + n_no_hosp_H + (n_no_hosp_M - 1) / 2
    cx_no_hosp   = n_hosp + (n_no_hosp_H + n_no_hosp_M - 1) / 2

    for cx_sub, label, bg in [
        (cx_hosp_H, "H", "#2980b9"),
        (cx_hosp_M, "M", "#c0397a"),
        (cx_no_hosp_H, "H", "#2980b9"),
        (cx_no_hosp_M, "M", "#c0397a"),
    ]:
        fig.add_annotation(
            x=cx_sub, y=header2_y,
            xref=xref, yref="paper",
            text=f"<b>{label}</b>",
            showarrow=False,
            font=dict(color="white", size=13, family="Arial Black"),
            bgcolor=bg, borderpad=4,
            xanchor="center", yanchor="bottom",
        )

    for cx_grp, label, bg, fc in [
        (cx_hosp, "Hospitalizados", "#e8a0a8", "#7B1A2A"),
        (cx_no_hosp, "No hospitalizados", "#d0d0d0", "#3A3A3A"),
    ]:
        fig.add_annotation(
            x=cx_grp, y=header1_y,
            xref=xref, yref="paper",
            text=f"<b>{label}</b>",
            showarrow=False,
            font=dict(color=fc, size=13, family="Arial"),
            bgcolor=bg, borderpad=5,
            xanchor="center", yanchor="bottom",
        )


# ── Heatmap Opción C con IDs en tick labels (versión simple) ─────────────────

def plot_heatmap_opcionC_con_ids(df: pl.DataFrame) -> go.Figure:
    """
    Heatmap Opción C con IDs de paciente como tick labels en el eje X.
    Muestra IDs representativos (1ro, último y cada ~50 pacientes por grupo).
    """
    data = _prepare_heatmap_data(df)
    z_matrix, hover_main = _build_z_and_hover(data, include_ids=True)

    criterios = [1, 2, 3, 4]
    criterio_names = {1: "Criterio 1", 2: "Criterio 2", 3: "Criterio 3", 4: "Criterio 4"}
    criterio_colors = {1: "#3498db", 2: "#e74c3c", 3: "#f39c12", 4: "#9b59b6"}

    colorscale = [
        [0.0, "#F4C2C2"], [0.5, "#F4C2C2"],
        [0.5, "#2C3E7A"], [1.0, "#2C3E7A"],
    ]

    fig = go.Figure(data=go.Heatmap(
        z=z_matrix, zmin=0, zmax=1,
        colorscale=colorscale, showscale=False,
        hoverongaps=False, hoverinfo="text", text=hover_main,
        xgap=0.3, ygap=2,
    ))

    # Separadores verticales
    n_hosp_H = data["n_hosp_H"]
    n_hosp = data["n_hosp"]
    n_no_hosp_H = data["n_no_hosp_H"]
    for x_div in [n_hosp_H - 0.5, n_hosp - 0.5, n_hosp + n_no_hosp_H - 0.5]:
        fig.add_vline(x=x_div, line_width=2, line_color="#333333", line_dash="solid")

    # Eje Y
    fig.update_yaxes(
        tickvals=list(range(4)),
        ticktext=[criterio_names[c] for c in criterios],
        showgrid=False, autorange="reversed",
    )

    # Eje X — IDs representativos
    patient_ids = data["patient_ids"]
    n_total = data["n_total"]
    tick_vals, tick_texts = [], []
    groups_info = [
        (0, n_hosp_H), (n_hosp_H, n_hosp),
        (n_hosp, n_hosp + n_no_hosp_H), (n_hosp + n_no_hosp_H, n_total),
    ]
    for start, end in groups_info:
        gs = end - start
        if gs == 0:
            continue
        tick_vals.append(start)
        tick_texts.append(patient_ids[start])
        if gs > 1:
            tick_vals.append(end - 1)
            tick_texts.append(patient_ids[end - 1])
        step = max(1, gs // 6)
        for pos in range(start + step, end - 1, step):
            tick_vals.append(pos)
            tick_texts.append(patient_ids[pos])

    fig.update_xaxes(
        tickvals=tick_vals, ticktext=tick_texts, tickangle=-90,
        tickfont=dict(size=6, family="Courier New"),
        showgrid=False, zeroline=False, title="cod_participante (ID paciente)",
    )

    _add_header_annotations(fig, data)

    # Etiquetas de criterio en margen izquierdo
    for ci, crit in enumerate(criterios):
        fig.add_annotation(
            x=-0.04, y=ci, xref="paper", yref="y",
            text=f"<b>{criterio_names[crit]}</b>",
            showarrow=False, xanchor="center", textangle=-90,
            font=dict(color="white", size=10),
            bgcolor=criterio_colors[crit], borderpad=3,
        )

    # Leyenda manual
    for col, lbl in [("#2C3E7A", "Cumple criterio"), ("#F4C2C2", "No cumple"),
                      ("#2980b9", "Hombre (H)"), ("#c0397a", "Mujer (M)")]:
        fig.add_trace(go.Scatter(x=[None], y=[None], mode="markers",
                                  marker=dict(size=12, color=col, symbol="square"),
                                  name=lbl, showlegend=True))

    # Conteos
    n_hosp_M = data["n_hosp_M"]
    n_no_hosp_M = data["n_no_hosp_M"]
    fig.add_annotation(
        x=0.5, y=-0.18, xref="paper", yref="paper",
        text=(f"Hospitalizados: {n_hosp_H} H + {n_hosp_M} M = {n_hosp}  |  "
              f"No hospitalizados: {n_no_hosp_H} H + {n_no_hosp_M} M = {n_no_hosp_H + n_no_hosp_M}"),
        showarrow=False, font=dict(size=9, color="#555"), xanchor="center",
    )

    fig.update_layout(
        title=None, template="plotly_white", plot_bgcolor="white",
        height=600, width=1400, margin=dict(l=130, r=40, t=100, b=180),
        legend=dict(orientation="h", yanchor="bottom", y=-0.30, xanchor="center", x=0.5),
    )
    return fig


# ── Heatmap Opción C con ÁRBOL de IDs debajo ────────────────────────────────

def plot_heatmap_opcionC_arbol_ids(df: pl.DataFrame) -> go.Figure:
    """
    Heatmap Opción C con TODOS los IDs de paciente visibles en el eje X.

    Cada paciente tiene su ``cod_participante`` como tick label rotado -90°
    con una "ramita" (tick mark exterior) que lo conecta visualmente al
    heatmap.  Diseñado para exportar a PNG con ancho ≥ 4000 px.
    """
    data = _prepare_heatmap_data(df)
    z_matrix, hover_main = _build_z_and_hover(data, include_ids=True)

    criterios = [1, 2, 3, 4]
    criterio_names = {1: "Criterio 1", 2: "Criterio 2", 3: "Criterio 3", 4: "Criterio 4"}
    criterio_colors = {1: "#3498db", 2: "#e74c3c", 3: "#f39c12", 4: "#9b59b6"}

    n_hosp_H = data["n_hosp_H"]
    n_hosp_M = data["n_hosp_M"]
    n_no_hosp_H = data["n_no_hosp_H"]
    n_no_hosp_M = data["n_no_hosp_M"]
    n_hosp = data["n_hosp"]
    n_total = data["n_total"]
    patient_ids = data["patient_ids"]

    colorscale = [
        [0.0, "#F4C2C2"], [0.5, "#F4C2C2"],
        [0.5, "#2C3E7A"], [1.0, "#2C3E7A"],
    ]

    fig = go.Figure(data=go.Heatmap(
        z=z_matrix, zmin=0, zmax=1,
        colorscale=colorscale, showscale=False,
        hoverongaps=False, hoverinfo="text", text=hover_main,
        xgap=0.3, ygap=2,
    ))

    # ── Separadores verticales ───────────────────────────────────────────────
    # H|M dentro de cada grupo (finos)
    for x_div in [n_hosp_H - 0.5, n_hosp + n_no_hosp_H - 0.5]:
        fig.add_vline(x=x_div, line_width=1.5, line_color="#333333", line_dash="solid")
    # Hospitalizados | No hospitalizados (grueso y negro)
    fig.add_vline(x=n_hosp - 0.5, line_width=5, line_color="black", line_dash="solid")

    # ── Eje Y ────────────────────────────────────────────────────────────────
    fig.update_yaxes(
        tickvals=list(range(4)),
        ticktext=[criterio_names[c] for c in criterios],
        showgrid=False, autorange="reversed",
    )

    # ── Eje X — TODOS los IDs con "ramitas" (ticks outside) ──────────────────
    fig.update_xaxes(
        tickvals=list(range(n_total)),
        ticktext=patient_ids,
        tickangle=-90,
        tickfont=dict(size=3, family="Courier New"),
        ticks="outside",
        ticklen=12,
        tickwidth=0.3,
        tickcolor="#aaa",
        showgrid=False,
        zeroline=False,
    )

    # ── Encabezados de 2 niveles ─────────────────────────────────────────────
    _add_header_annotations(fig, data)

    # ── Etiquetas de criterio en margen izquierdo ────────────────────────────
    for ci, crit in enumerate(criterios):
        fig.add_annotation(
            x=-0.02, y=ci, xref="paper", yref="y",
            text=f"<b>{criterio_names[crit]}</b>",
            showarrow=False, xanchor="center", textangle=-90,
            font=dict(color="white", size=10),
            bgcolor=criterio_colors[crit], borderpad=3,
        )

    # ── Leyenda manual ───────────────────────────────────────────────────────
    for col, lbl in [("#2C3E7A", "Cumple criterio"), ("#F4C2C2", "No cumple"),
                      ("#2980b9", "Hombre (H)"), ("#c0397a", "Mujer (M)")]:
        fig.add_trace(go.Scatter(x=[None], y=[None], mode="markers",
                                  marker=dict(size=12, color=col, symbol="square"),
                                  name=lbl, showlegend=True))

    # ── Conteos ──────────────────────────────────────────────────────────────
    fig.add_annotation(
        x=0.5, y=-0.08, xref="paper", yref="paper",
        text=(
            f"Hospitalizados: {n_hosp_H} H + {n_hosp_M} M = {n_hosp}  |  "
            f"No hospitalizados: {n_no_hosp_H} H + {n_no_hosp_M} M = "
            f"{n_no_hosp_H + n_no_hosp_M}  |  Total: {n_total}"
        ),
        showarrow=False, font=dict(size=9, color="#555"), xanchor="center",
    )

    # ── Layout ───────────────────────────────────────────────────────────────
    fig.update_layout(
        title=None,
        template="plotly_white",
        plot_bgcolor="white",
        height=1200,
        width=4000,
        margin=dict(l=130, r=40, t=170, b=350),
        legend=dict(orientation="h", yanchor="bottom", y=-0.20,
                    xanchor="center", x=0.5),
    )
    return fig


# ── Heatmap de Clusters normalizado por semana ──────────────────────────────

# Definición canónica de síntomas × clusters (reutilizable)
_SINTOMAS_POR_CLUSTER: list[tuple[str, str, str]] = [
    # AIRWAYS
    ("congestion_3m",      "Nasal congestion",   "AIRWAYS"),
    ("tos_3m",             "Cough",              "AIRWAYS"),
    ("",                   "Phlegm",             "AIRWAYS"),
    ("do_garganta_3m",     "Sore throat",        "AIRWAYS"),
    # COGNITIVE
    ("depresion_3m",       "Depression/Anxiety",  "COGNITIVE"),
    ("memoria_3m",         "Memory impairment",  "COGNITIVE"),
    ("do_cabeza_3m",       "Headache",           "COGNITIVE"),
    ("somnolencia_3m",     "Drowsiness",         "COGNITIVE"),
    # GASTROINTESTINAL
    ("do_abdominal_3m",    "Abdominal pain",     "GASTROINTESTINAL"),
    ("nausea_3m",          "Nausea",             "GASTROINTESTINAL"),
    ("hin_piernas_3m",     "Edema (swollen legs)","GASTROINTESTINAL"),
    ("diarrea_3m",         "Diarrhea",           "GASTROINTESTINAL"),
    ("pe_peso_3m",         "Weight loss",        "GASTROINTESTINAL"),
    ("apetito_3m",         "Change in appetite", "GASTROINTESTINAL"),
    # MUSCULAR
    ("do_musculos_3m",     "Muscle pain",        "MUSCULAR"),
    ("do_articulacion_3m", "Joint pain",         "MUSCULAR"),
    ("pes_piernas_3m",     "Legs feel heavy",    "MUSCULAR"),
    # RESPIRATORY
    ("fa_aliento_3m",      "Shortness of breath","RESPIRATORY"),
    ("fatiga_3m",          "Fatigue",            "RESPIRATORY"),
    ("do_pecho_3m",        "Chest pain",         "RESPIRATORY"),
    ("di_respirar_3m",     "Breathing difficulty","RESPIRATORY"),
    # SMELL/TASTE
    ("pe_olfato_3m",       "Anosmia",            "SMELL/TASTE"),
    ("ca_olfato_3m",       "Change in smell",    "SMELL/TASTE"),
    ("pe_gusto_3m",        "Ageusia",            "SMELL/TASTE"),
    ("ca_gusto_3m",        "Change in taste",    "SMELL/TASTE"),
]


def plot_clusters_heatmap_normalizado(df: pl.DataFrame) -> go.Figure:
    """
    Heatmap de síntomas (por cluster) × semana epidemiológica, **normalizado**.

    Cada celda = n_pacientes_con_síntoma / n_total_pacientes_en_esa_semana.
    Valor entre 0 y 1 (mostrado como porcentaje en hover).

    Permite comparar semanas con distinto número de pacientes sin que las
    semanas con más casos dominen visualmente el heatmap.
    """
    all_weeks: list[str] = sorted(
        df.select("yearweek").unique().to_series().to_list()
    )

    # Pre-calcular n total de pacientes por semana (denominador)
    patients_per_week: dict[str, int] = {}
    for week in all_weeks:
        patients_per_week[week] = df.filter(pl.col("yearweek") == week).height

    # Construir matrices
    heatmap_z: list[list[float]] = []          # valores normalizados
    heatmap_text: list[list[str]] = []         # hover text
    symptom_labels: list[str] = []
    cluster_boundaries: list[int] = []

    current_cluster: str | None = None
    row_idx = 0

    for var_col, label, cluster in _SINTOMAS_POR_CLUSTER:
        if cluster != current_cluster:
            if current_cluster is not None:
                cluster_boundaries.append(row_idx)
            current_cluster = cluster

        symptom_labels.append(label)

        if not var_col or var_col not in df.columns:
            heatmap_z.append([0.0] * len(all_weeks))
            heatmap_text.append([""] * len(all_weeks))
            row_idx += 1
            continue

        row_z: list[float] = []
        row_t: list[str] = []
        for week in all_weeks:
            n_total = patients_per_week[week]
            n_symptom = df.filter(
                (pl.col("yearweek") == week) & (pl.col(var_col) == 1)
            ).height
            prop = n_symptom / n_total if n_total > 0 else 0.0
            row_z.append(round(prop, 4))
            row_t.append(
                f"Week: {week}<br>"
                f"Symptom: {label}<br>"
                f"Cases: {n_symptom} / {n_total}<br>"
                f"<b>Proportion: {prop:.1%}</b>"
            )
        heatmap_z.append(row_z)
        heatmap_text.append(row_t)
        row_idx += 1

    # ── Figura ───────────────────────────────────────────────────────────────
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_z,
        x=all_weeks,
        y=symptom_labels,
        colorscale="Viridis",
        zmin=0, zmax=1,
        colorbar=dict(
            title="Proportion",
            tickformat=".0%",
            tickvals=[0, 0.25, 0.50, 0.75, 1.0],
        ),
        hoverongaps=False,
        hoverinfo="text",
        text=heatmap_text,
    ))

    # Separadores entre clusters
    shapes = []
    for boundary_idx in cluster_boundaries:
        shapes.append(dict(
            type="line",
            x0=-0.5, x1=len(all_weeks) - 0.5,
            y0=boundary_idx - 0.5, y1=boundary_idx - 0.5,
            line=dict(color="white", width=2),
        ))

    fig.update_layout(
        title="Symptoms at ≥3 months by Week of Diagnosis (normalized by week N)",
        xaxis_title="Epidemiological Week",
        yaxis_title="Symptoms (grouped by cluster)",
        template="plotly_white",
        height=800,
        width=1400,
        xaxis=dict(type="category", tickangle=-45, side="bottom"),
        yaxis=dict(side="left", autorange="reversed", tickfont=dict(size=10)),
        shapes=shapes,
    )

    return fig
