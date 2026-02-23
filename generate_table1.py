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

# ── Employment Situation ───────────────────────────────────────────────────
EMP_COL = "Situación.ocupacional"
EMP_LABELS = {"Activo": "Employed", "Cesante": "Unemployed", "Inactivo": "Idle"}

add_row(
    "Employment Situation",
    f"Total (n={total_nonull(df, EMP_COL)})",
    total_nonull(men, EMP_COL),
    total_nonull(women, EMP_COL),
    total_nonull(controls, EMP_COL),
    total_nonull(cases, EMP_COL),
)
for val, label in EMP_LABELS.items():
    add_row(
        "",
        f"  {label}",
        n_only(men,      pl.col(EMP_COL) == val),
        n_only(women,    pl.col(EMP_COL) == val),
        n_only(controls, pl.col(EMP_COL) == val),
        n_only(cases,    pl.col(EMP_COL) == val),
    )

# ── Bloque: Clinical - Lifestyle ───────────────────────────────────────────
add_row("", "─── Clinical - Lifestyle ───", "", "", "", "")

# ── Weight ─────────────────────────────────────────────────────────────────
# peso has invalid entries (0.0 and 1.0) — filter to values > 30 kg
PESO_VALID = pl.col("peso") > 30

add_row(
    "Weight",
    mean_sd(df.filter(PESO_VALID)["peso"]),
    mean_sd(men.filter(PESO_VALID)["peso"]),
    mean_sd(women.filter(PESO_VALID)["peso"]),
    mean_sd(controls.filter(PESO_VALID)["peso"]),
    mean_sd(cases.filter(PESO_VALID)["peso"]),
)

# ── Height ─────────────────────────────────────────────────────────────────
add_row(
    "Height",
    mean_sd(df["Altura"].drop_nulls().cast(pl.Float64)),
    mean_sd(men["Altura"].drop_nulls().cast(pl.Float64)),
    mean_sd(women["Altura"].drop_nulls().cast(pl.Float64)),
    mean_sd(controls["Altura"].drop_nulls().cast(pl.Float64)),
    mean_sd(cases["Altura"].drop_nulls().cast(pl.Float64)),
)

# ── BMI ────────────────────────────────────────────────────────────────────
add_row(
    "BMI",
    mean_sd(df["IMC"]),
    mean_sd(men["IMC"]),
    mean_sd(women["IMC"]),
    mean_sd(controls["IMC"]),
    mean_sd(cases["IMC"]),
)

# ── Tobacco Consumption ────────────────────────────────────────────────────
TAB_COL = "tabaco"

add_row(
    "Tobacco Consumption",
    f"Total (n={total_nonull(df, TAB_COL)})",
    total_nonull(men, TAB_COL),
    total_nonull(women, TAB_COL),
    total_nonull(controls, TAB_COL),
    total_nonull(cases, TAB_COL),
)
for label, val in [("Yes", 1), ("No", 0)]:
    add_row(
        "",
        f"  {label}",
        n_only(men,      pl.col(TAB_COL) == val),
        n_only(women,    pl.col(TAB_COL) == val),
        n_only(controls, pl.col(TAB_COL) == val),
        n_only(cases,    pl.col(TAB_COL) == val),
    )

# ── Tobacco Daily Frequency ────────────────────────────────────────────────
# Source column: "Cigarros.diarios"
# Ordered high-to-low as in reference table
CIG_COL = "Cigarros.diarios"
CIG_LABELS = [
    ("31 o más",                                         "31 or more"),
    ("Entre 21 y 30",                                    "21 to 30"),
    ("Entre 11 y 20",                                    "11 to 20"),
    ("Entre 1 y 10",                                     "1 to 10"),
    ("Menos de 1 al día (menos de 7 a la semana)",       "Less than one"),
    ("0 al día",                                         "Never smoke"),
]

add_row(
    "Tobacco Daily Frequency",
    f"Total (n={total_nonull(df, CIG_COL)})",
    total_nonull(men, CIG_COL),
    total_nonull(women, CIG_COL),
    total_nonull(controls, CIG_COL),
    total_nonull(cases, CIG_COL),
)
for raw_val, label in CIG_LABELS:
    add_row(
        "",
        f"  {label}",
        n_only(men,      pl.col(CIG_COL) == raw_val),
        n_only(women,    pl.col(CIG_COL) == raw_val),
        n_only(controls, pl.col(CIG_COL) == raw_val),
        n_only(cases,    pl.col(CIG_COL) == raw_val),
    )

# ── Alcohol Consumption ────────────────────────────────────────────────────
# Dataset has 5 frequency categories; the two weekly ones are combined
# into "2 or more times a week" to match the reference table structure.
ALC_COL = "Consumo.alcohol"
WEEKLY_VALS = ["Dos o tres veces a la semana", "Cuatro o más veces a la semana"]
ALC_LABELS = [
    (WEEKLY_VALS,                   "2 or more times a week"),
    (["Dos a cuatro veces al mes"], "2-4 times a month"),
    (["Una vez al mes o menos"],    "Once a month or less"),
    (["Nunca bebe"],                "Never drinks"),
]

add_row(
    "Alcohol Consumption",
    f"Total (n={total_nonull(df, ALC_COL)})",
    total_nonull(men, ALC_COL),
    total_nonull(women, ALC_COL),
    total_nonull(controls, ALC_COL),
    total_nonull(cases, ALC_COL),
)
for raw_vals, label in ALC_LABELS:
    add_row(
        "",
        f"  {label}",
        n_only(men,      pl.col(ALC_COL).is_in(raw_vals)),
        n_only(women,    pl.col(ALC_COL).is_in(raw_vals)),
        n_only(controls, pl.col(ALC_COL).is_in(raw_vals)),
        n_only(cases,    pl.col(ALC_COL).is_in(raw_vals)),
    )

# ── Bloque: COVID-19 ───────────────────────────────────────────────────────
add_row("", "─── COVID-19 ───", "", "", "", "")

# ── No. Symptoms ──────────────────────────────────────────────────────────
add_row(
    "No. Symptoms",
    mean_sd(df["Total_Sintomas"].cast(pl.Float64)),
    mean_sd(men["Total_Sintomas"].cast(pl.Float64)),
    mean_sd(women["Total_Sintomas"].cast(pl.Float64)),
    mean_sd(controls["Total_Sintomas"].cast(pl.Float64)),
    mean_sd(cases["Total_Sintomas"].cast(pl.Float64)),
)

# ── No. Pre-existing diseases ──────────────────────────────────────────────
add_row(
    "No. Pre-existing diseases",
    mean_sd(df["Total_Cond_pre"].cast(pl.Float64)),
    mean_sd(men["Total_Cond_pre"].cast(pl.Float64)),
    mean_sd(women["Total_Cond_pre"].cast(pl.Float64)),
    mean_sd(controls["Total_Cond_pre"].cast(pl.Float64)),
    mean_sd(cases["Total_Cond_pre"].cast(pl.Float64)),
)

# ── More than 5 Symptoms ───────────────────────────────────────────────────
# Mas_de_5: 0=No, 1=Yes — no nulls in dataset
M5_COL = "Mas_de_5"
add_row(
    "More than 5 Symptoms",
    f"Total (n={total_nonull(df, M5_COL)})",
    total_nonull(men, M5_COL),
    total_nonull(women, M5_COL),
    total_nonull(controls, M5_COL),
    total_nonull(cases, M5_COL),
)
for label, val in [("Yes", 1), ("No", 0)]:
    add_row(
        "",
        f"  {label}",
        n_only(men,      pl.col(M5_COL) == val),
        n_only(women,    pl.col(M5_COL) == val),
        n_only(controls, pl.col(M5_COL) == val),
        n_only(cases,    pl.col(M5_COL) == val),
    )

# ── Severe Infection ───────────────────────────────────────────────────────
# Severo: 0=No, 1=Yes — no nulls in dataset
SEV_COL = "Severo"
add_row(
    "Severe Infection",
    f"Total (n={total_nonull(df, SEV_COL)})",
    total_nonull(men, SEV_COL),
    total_nonull(women, SEV_COL),
    total_nonull(controls, SEV_COL),
    total_nonull(cases, SEV_COL),
)
for label, val in [("Yes", 1), ("No", 0)]:
    add_row(
        "",
        f"  {label}",
        n_only(men,      pl.col(SEV_COL) == val),
        n_only(women,    pl.col(SEV_COL) == val),
        n_only(controls, pl.col(SEV_COL) == val),
        n_only(cases,    pl.col(SEV_COL) == val),
    )

# ── Recovered ─────────────────────────────────────────────────────────────
# recuperado_3m: 1=Yes, 2=No; 8 nulls
REC_COL = "recuperado_3m"
add_row(
    "Recovered",
    f"Total (n={total_nonull(df, REC_COL)})",
    total_nonull(men, REC_COL),
    total_nonull(women, REC_COL),
    total_nonull(controls, REC_COL),
    total_nonull(cases, REC_COL),
)
for label, val in [("Yes", 1), ("No", 2)]:
    add_row(
        "",
        f"  {label}",
        n_only(men,      pl.col(REC_COL) == val),
        n_only(women,    pl.col(REC_COL) == val),
        n_only(controls, pl.col(REC_COL) == val),
        n_only(cases,    pl.col(REC_COL) == val),
    )

# ── Health problems that limit daily activities ────────────────────────────
# problemas_3m: 1=Yes, 2=No, 3=NS/NR (treated as neither Yes nor No, but
# counted in Total). 5 nulls.
PROB_COL = "problemas_3m"
add_row(
    "Health problems that limit daily activities",
    f"Total (n={total_nonull(df, PROB_COL)})",
    total_nonull(men, PROB_COL),
    total_nonull(women, PROB_COL),
    total_nonull(controls, PROB_COL),
    total_nonull(cases, PROB_COL),
)
for label, val in [("Yes", 1), ("No", 2)]:
    add_row(
        "",
        f"  {label}",
        n_only(men,      pl.col(PROB_COL) == val),
        n_only(women,    pl.col(PROB_COL) == val),
        n_only(controls, pl.col(PROB_COL) == val),
        n_only(cases,    pl.col(PROB_COL) == val),
    )

# ── Need someone to help regularly ────────────────────────────────────────
# ayuda_3m: 1=Yes, 2=No, 3=NS/NR (treated as neither, counted in Total).
# 5 nulls.
AYU_COL = "ayuda_3m"
add_row(
    "Need someone to help regularly",
    f"Total (n={total_nonull(df, AYU_COL)})",
    total_nonull(men, AYU_COL),
    total_nonull(women, AYU_COL),
    total_nonull(controls, AYU_COL),
    total_nonull(cases, AYU_COL),
)
for label, val in [("Yes", 1), ("No", 2)]:
    add_row(
        "",
        f"  {label}",
        n_only(men,      pl.col(AYU_COL) == val),
        n_only(women,    pl.col(AYU_COL) == val),
        n_only(controls, pl.col(AYU_COL) == val),
        n_only(cases,    pl.col(AYU_COL) == val),
    )

# ── Health problems that require to stay at home ───────────────────────────
# casa_3m: 1=Yes, 2=No, 3=NS/NR (treated as neither, counted in Total).
# 4 nulls.
CASA_COL = "casa_3m"
add_row(
    "Health problems that require to stay at home",
    f"Total (n={total_nonull(df, CASA_COL)})",
    total_nonull(men, CASA_COL),
    total_nonull(women, CASA_COL),
    total_nonull(controls, CASA_COL),
    total_nonull(cases, CASA_COL),
)
for label, val in [("Yes", 1), ("No", 2)]:
    add_row(
        "",
        f"  {label}",
        n_only(men,      pl.col(CASA_COL) == val),
        n_only(women,    pl.col(CASA_COL) == val),
        n_only(controls, pl.col(CASA_COL) == val),
        n_only(cases,    pl.col(CASA_COL) == val),
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
