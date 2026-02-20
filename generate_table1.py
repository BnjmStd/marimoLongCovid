"""
generate_table1.py
==================
Genera la Tabla 1 sociodemográfica del análisis Long COVID.

Columnas:   Variable | Average/Levels | Men | Women | Controls | Cases
p-values:   pendientes (se agregarán al exportar a Word con python-docx)

Uso:
    python generate_table1.py
"""

import polars as pl
import pandas as pd
import numpy as np
from pathlib import Path

# ─────────────────────────────────────────────
# 1. CARGAR DATOS
# ─────────────────────────────────────────────
DATASET = Path("datasets/longcovid_2020W13-2021W22.csv")

df = pl.read_csv(
    DATASET,
    null_values=["NA", "N/A", ""],
    infer_schema_length=10000,
)

# ─────────────────────────────────────────────
# 2. DEFINIR GRUPOS PRINCIPALES
# ─────────────────────────────────────────────
# Sexo
men     = df.filter(pl.col("sexo") == 1)
women   = df.filter(pl.col("sexo") == 2)

# Long COVID
controls = df.filter(pl.col("pheno_c19") == "CONTROL")
cases    = df.filter(pl.col("pheno_c19") == "CASO c19-GenoNET")

GROUPS = {
    "Overall":  df,
    "Men":      men,
    "Women":    women,
    "Controls": controls,
    "Cases":    cases,
}

# ─────────────────────────────────────────────
# 3. HELPERS
# ─────────────────────────────────────────────

def mean_sd(series: pl.Series, decimals: int = 2) -> str:
    """Devuelve 'mean (SD)' como string."""
    vals = series.drop_nulls()
    if len(vals) == 0:
        return "–"
    m = vals.mean()
    s = vals.std()
    return f"{m:.{decimals}f} ({s:.{decimals}f})"


def n_pct(sub: pl.DataFrame, mask: pl.Expr, decimals: int = 1) -> str:
    """
    Cuenta filas que cumplen mask dentro de sub y devuelve 'n (%)'.
    El porcentaje es relativo al total no-nulo del grupo.
    """
    total = sub.filter(mask.is_not_null()).shape[0]
    n = sub.filter(mask).shape[0]
    if total == 0:
        return "0"
    pct = 100 * n / total
    return f"{n} ({pct:.{decimals}f}%)"


def n_only(sub: pl.DataFrame, mask: pl.Expr) -> str:
    """Sólo el conteo, sin porcentaje."""
    return str(sub.filter(mask).shape[0])


def total_nonull(sub: pl.DataFrame, col: str) -> str:
    return str(sub.filter(pl.col(col).is_not_null()).shape[0])


# ─────────────────────────────────────────────
# 4. CONSTRUCCIÓN FILA A FILA
# ─────────────────────────────────────────────

rows: list[dict] = []

def add_row(variable: str, avg_levels: str,
            men: str, women: str, controls: str, cases: str) -> None:
    rows.append({
        "Variable":          variable,
        "Average / Levels":  avg_levels,
        "Men":               men,
        "Women":             women,
        "Controls":          controls,
        "Cases":             cases,
    })


# ── Bloque: Socio-Demographic ───────────────────────────────────────────────
add_row("", "─── Socio-Demographic ───", "", "", "", "")

# ── Age ─────────────────────────────────────────────────────────────────────
add_row(
    "Age",
    mean_sd(df["edad_entrevistado"]),
    mean_sd(men["edad_entrevistado"]),
    mean_sd(women["edad_entrevistado"]),
    mean_sd(controls["edad_entrevistado"]),
    mean_sd(cases["edad_entrevistado"]),
)

# ── Sex ─────────────────────────────────────────────────────────────────────
SEX_COL = "sexo"

add_row(
    "Sex",
    f"Total (n={total_nonull(df, SEX_COL)})",
    total_nonull(men, SEX_COL),
    total_nonull(women, SEX_COL),
    total_nonull(controls, SEX_COL),
    total_nonull(cases, SEX_COL),
)
for label, val in [("Male", 1), ("Female", 2)]:
    add_row(
        "",
        f"  {label}",
        n_only(men,      pl.col(SEX_COL) == val),
        n_only(women,    pl.col(SEX_COL) == val),
        n_only(controls, pl.col(SEX_COL) == val),
        n_only(cases,    pl.col(SEX_COL) == val),
    )

# ── Ethnicity ────────────────────────────────────────────────────────────────
ETH_COL = "desc_pueblo_orig"
eth_total = df.filter(pl.col(ETH_COL).is_not_null())

# Orden de categorías (sigue el de la imagen de referencia)
ETHNICITY_ORDER = [
    "Afrodescendiente", "Atacameño", "Aymara", "Colla",
    "Diaguita", "Kawésqar", "Mapuche", "Quechua",
    "Rapa Nui", "Yámana", "Ninguna", "Otro",
]

add_row(
    "Ethnicity",
    f"Total (n={total_nonull(df, ETH_COL)})",
    total_nonull(men, ETH_COL),
    total_nonull(women, ETH_COL),
    total_nonull(controls, ETH_COL),
    total_nonull(cases, ETH_COL),
)

# Categorías reales en el dataset
eth_unique = (
    df.filter(pl.col(ETH_COL).is_not_null())
    [ETH_COL]
    .unique()
    .to_list()
)
# Mostrar en orden de referencia + cualquier valor extra
ordered_eth = [e for e in ETHNICITY_ORDER if e in eth_unique]
ordered_eth += [e for e in sorted(eth_unique) if e not in ETHNICITY_ORDER]

for eth in ordered_eth:
    add_row(
        "",
        f"  {eth}",
        n_only(men,      pl.col(ETH_COL) == eth),
        n_only(women,    pl.col(ETH_COL) == eth),
        n_only(controls, pl.col(ETH_COL) == eth),
        n_only(cases,    pl.col(ETH_COL) == eth),
    )

# ── Ancestry AMR (AYM + MAP) ───────────────────────────────────────────────
# AMR ≈ Aymara + Mapuche ancestry proportions
df_amr       = df.with_columns((pl.col("AYM") + pl.col("MAP")).alias("AMR"))
men_amr      = men.with_columns((pl.col("AYM") + pl.col("MAP")).alias("AMR"))
women_amr    = women.with_columns((pl.col("AYM") + pl.col("MAP")).alias("AMR"))
controls_amr = controls.with_columns((pl.col("AYM") + pl.col("MAP")).alias("AMR"))
cases_amr    = cases.with_columns((pl.col("AYM") + pl.col("MAP")).alias("AMR"))

add_row(
    "Ancestry AMR",
    mean_sd(df_amr["AMR"]),
    mean_sd(men_amr["AMR"]),
    mean_sd(women_amr["AMR"]),
    mean_sd(controls_amr["AMR"]),
    mean_sd(cases_amr["AMR"]),
)

# ── Ancestry AFR ───────────────────────────────────────────────────────────
add_row(
    "Ancestry AFR",
    mean_sd(df["AFR"], decimals=2),
    mean_sd(men["AFR"], decimals=2),
    mean_sd(women["AFR"], decimals=2),
    mean_sd(controls["AFR"], decimals=2),
    mean_sd(cases["AFR"], decimals=2),
)

# ── Population Density ─────────────────────────────────────────────────────
add_row(
    "Population Density",
    mean_sd(df["Densidad"]),
    mean_sd(men["Densidad"]),
    mean_sd(women["Densidad"]),
    mean_sd(controls["Densidad"]),
    mean_sd(cases["Densidad"]),
)

# ── Geographic Location (Macrozona) ────────────────────────────────────────
GEO_COL = "Macrozona"
GEO_LABELS = {1: "North", 2: "Center", 3: "Center South", 4: "South", 5: "Austral"}

add_row(
    "Geographic Location",
    f"Total (n={total_nonull(df, GEO_COL)})",
    total_nonull(men, GEO_COL),
    total_nonull(women, GEO_COL),
    total_nonull(controls, GEO_COL),
    total_nonull(cases, GEO_COL),
)
for val, label in GEO_LABELS.items():
    add_row(
        "",
        f"  {label}",
        n_only(men,      pl.col(GEO_COL) == val),
        n_only(women,    pl.col(GEO_COL) == val),
        n_only(controls, pl.col(GEO_COL) == val),
        n_only(cases,    pl.col(GEO_COL) == val),
    )

# ── Education Level ────────────────────────────────────────────────────────
EDU_COL = "Educacion"
EDU_LABELS = {
    0: "Elementary School or Lower Level",
    1: "High School",
    2: "Professional Technician",
    3: "University",
}

add_row(
    "Education Level",
    f"Total (n={total_nonull(df, EDU_COL)})",
    total_nonull(men, EDU_COL),
    total_nonull(women, EDU_COL),
    total_nonull(controls, EDU_COL),
    total_nonull(cases, EDU_COL),
)
for val, label in EDU_LABELS.items():
    add_row(
        "",
        f"  {label}",
        n_only(men,      pl.col(EDU_COL) == val),
        n_only(women,    pl.col(EDU_COL) == val),
        n_only(controls, pl.col(EDU_COL) == val),
        n_only(cases,    pl.col(EDU_COL) == val),
    )

# ── Healthcare System ──────────────────────────────────────────────────────
HS_COL = "Tipo_Salud"
HS_LABELS = {1: "Public", 2: "Private"}

add_row(
    "Healthcare System",
    f"Total (n={total_nonull(df, HS_COL)})",
    total_nonull(men, HS_COL),
    total_nonull(women, HS_COL),
    total_nonull(controls, HS_COL),
    total_nonull(cases, HS_COL),
)
for val, label in HS_LABELS.items():
    add_row(
        "",
        f"  {label}",
        n_only(men,      pl.col(HS_COL) == val),
        n_only(women,    pl.col(HS_COL) == val),
        n_only(controls, pl.col(HS_COL) == val),
        n_only(cases,    pl.col(HS_COL) == val),
    )

# ─────────────────────────────────────────────
# 5. CONSTRUIR DATAFRAME FINAL
# ─────────────────────────────────────────────
table1 = pd.DataFrame(rows)

# ─────────────────────────────────────────────
# 6. MOSTRAR EN CONSOLA
# ─────────────────────────────────────────────
pd.set_option("display.max_rows", 200)
pd.set_option("display.max_colwidth", 50)
pd.set_option("display.width", 160)

print("\n")
print("=" * 160)
print("TABLE 1 — Sociodemographic Characteristics")
print(f"         Sex Comparison  |  LongCOVID Comparison")
print(f"         (p-values pending — to be added via python-docx)")
print("=" * 160)
print(table1.to_string(index=False))
print("=" * 160)

# Group totals summary
n_total    = df.shape[0]
n_men      = men.shape[0]
n_women    = women.shape[0]
n_controls = controls.shape[0]
n_cases    = cases.shape[0]

print(f"\nSample sizes → Total: {n_total} | Men: {n_men} | Women: {n_women} "
      f"| Controls: {n_controls} | Cases: {n_cases}")

# ─────────────────────────────────────────────
# 7. GUARDAR CSV (para uso posterior con python-docx)
# ─────────────────────────────────────────────
OUT_CSV = Path("pdf_reports/table1_sociodemographic.csv")
OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
table1.to_csv(OUT_CSV, index=False)
print(f"\nTabla guardada en: {OUT_CSV}")
