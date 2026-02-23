"""
generate_table2.py
==================
Genera la Tabla 2: comparación Long COVID (Controles vs Casos).

Columnas:   Variable | Average/Levels | Controls | Cases
Sin columnas de sexo. Incluye Blood Group y Rh en Clinical-Lifestyle.

Uso:
    python generate_table2.py
"""

import polars as pl
import pandas as pd
from pathlib import Path
from scipy import stats

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
# 2. DEFINIR GRUPOS
# ─────────────────────────────────────────────
controls = df.filter(pl.col("pheno_c19") == "CONTROL")
cases    = df.filter(pl.col("pheno_c19") == "CASO c19-GenoNET")

# ─────────────────────────────────────────────
# 3. HELPERS
# ─────────────────────────────────────────────

def mean_sd(series: pl.Series, decimals: int = 2) -> str:
    vals = series.drop_nulls()
    if len(vals) == 0:
        return "–"
    return f"{vals.mean():.{decimals}f} ({vals.std():.{decimals}f})"


def n_only(sub: pl.DataFrame, mask: pl.Expr) -> str:
    return str(sub.filter(mask).shape[0])


def total_nonull(sub: pl.DataFrame, col: str) -> str:
    return str(sub.filter(pl.col(col).is_not_null()).shape[0])


# ── Helpers p-value ────────────────────────────────────────────────────────

def fmt_p(p: float) -> str:
    """Formatea el p-value con marcadores de significancia."""
    if p < 0.001:
        return "<0.001***"
    elif p < 0.01:
        return f"{p:.3f}**"
    elif p < 0.05:
        return f"{p:.3f}*"
    else:
        return f"{p:.3f}"


def pval_continuous(col: str) -> str:
    """Mann-Whitney U (dos colas) para variables continuas."""
    a = controls[col].drop_nulls().cast(pl.Float64).to_numpy()
    b = cases[col].drop_nulls().cast(pl.Float64).to_numpy()
    if len(a) < 5 or len(b) < 5:
        return "–"
    result = stats.mannwhitneyu(a, b, alternative="two-sided")
    return fmt_p(float(result.pvalue))


def pval_cat(contingency: list[list[int]]) -> str:
    """Chi-cuadrado sobre tabla de contingencia precalculada."""
    table = [row for row in contingency if sum(row) > 0]
    if len(table) < 2:
        return "–"
    chi2_result = stats.chi2_contingency(table)
    return fmt_p(float(chi2_result[1]))  # type: ignore[arg-type]


def build_ct_int(col: str, vals: list) -> list[list[int]]:
    """Tabla de contingencia Control/Caso para valores enteros."""
    return [
        [controls.filter(pl.col(col) == v).shape[0],
         cases.filter(pl.col(col) == v).shape[0]]
        for v in vals
    ]


def build_ct_str(col: str, vals: list) -> list[list[int]]:
    """Tabla de contingencia Control/Caso para valores string."""
    return [
        [controls.filter(pl.col(col) == v).shape[0],
         cases.filter(pl.col(col) == v).shape[0]]
        for v in vals
    ]


def build_ct_isin(col: str, groups: list[list[str]]) -> list[list[int]]:
    """Tabla de contingencia para grupos combinados (is_in)."""
    return [
        [controls.filter(pl.col(col).is_in(g)).shape[0],
         cases.filter(pl.col(col).is_in(g)).shape[0]]
        for g in groups
    ]


# ─────────────────────────────────────────────
# 4. CONSTRUCCIÓN FILA A FILA
# ─────────────────────────────────────────────

rows: list[dict] = []

def add_row(variable: str, avg_levels: str, controls_val: str, cases_val: str,
            p_value: str = "") -> None:
    rows.append({
        "Variable":         variable,
        "Average / Levels": avg_levels,
        "Controls":         controls_val,
        "Cases":            cases_val,
        "p-value":          p_value,
    })


# ── Bloque: Socio-Demographic ──────────────────────────────────────────────
add_row("", "─── Socio-Demographic ───", "", "")

# ── Age ───────────────────────────────────────────────────────────────────
add_row(
    "Age",
    mean_sd(df["edad_entrevistado"]),
    mean_sd(controls["edad_entrevistado"]),
    mean_sd(cases["edad_entrevistado"]),
    pval_continuous("edad_entrevistado"),
)

# ── Sex ───────────────────────────────────────────────────────────────────
SEX_COL = "sexo"
add_row(
    "Sex",
    f"Total (n={total_nonull(df, SEX_COL)})",
    total_nonull(controls, SEX_COL),
    total_nonull(cases, SEX_COL),
    pval_cat(build_ct_int(SEX_COL, [1, 2])),
)
for label, val in [("Male", 1), ("Female", 2)]:
    add_row("", f"  {label}",
            n_only(controls, pl.col(SEX_COL) == val),
            n_only(cases,    pl.col(SEX_COL) == val))

# ── Ethnicity ─────────────────────────────────────────────────────────────
ETH_COL = "desc_pueblo_orig"
ETHNICITY_ORDER = [
    "Afrodescendiente", "Atacameño", "Aymara", "Colla",
    "Diaguita", "Kawésqar", "Mapuche", "Quechua",
    "Rapa Nui", "Yámana", "Ninguna", "Otro",
]
eth_unique = df.filter(pl.col(ETH_COL).is_not_null())[ETH_COL].unique().to_list()
ordered_eth = [e for e in ETHNICITY_ORDER if e in eth_unique]
ordered_eth += [e for e in sorted(eth_unique) if e not in ETHNICITY_ORDER]
add_row(
    "Ethnicity",
    f"Total (n={total_nonull(df, ETH_COL)})",
    total_nonull(controls, ETH_COL),
    total_nonull(cases, ETH_COL),
    pval_cat(build_ct_str(ETH_COL, ordered_eth)),
)
for eth in ordered_eth:
    add_row("", f"  {eth}",
            n_only(controls, pl.col(ETH_COL) == eth),
            n_only(cases,    pl.col(ETH_COL) == eth))

# ── Ancestry AMR ──────────────────────────────────────────────────────────
df_amr       = df.with_columns((pl.col("AYM") + pl.col("MAP")).alias("AMR"))
controls_amr = controls.with_columns((pl.col("AYM") + pl.col("MAP")).alias("AMR"))
cases_amr    = cases.with_columns((pl.col("AYM") + pl.col("MAP")).alias("AMR"))
_amr_ctrl = controls_amr["AMR"].drop_nulls().cast(pl.Float64).to_numpy()
_amr_case = cases_amr["AMR"].drop_nulls().cast(pl.Float64).to_numpy()
_p_amr = fmt_p(float(stats.mannwhitneyu(_amr_ctrl, _amr_case, alternative="two-sided").pvalue))
add_row(
    "Ancestry AMR",
    mean_sd(df_amr["AMR"]),
    mean_sd(controls_amr["AMR"]),
    mean_sd(cases_amr["AMR"]),
    _p_amr,
)

# ── Ancestry AFR ──────────────────────────────────────────────────────────
add_row(
    "Ancestry AFR",
    mean_sd(df["AFR"], decimals=2),
    mean_sd(controls["AFR"], decimals=2),
    mean_sd(cases["AFR"], decimals=2),
    pval_continuous("AFR"),
)

# ── Ancestry EUR ──────────────────────────────────────────────────────────
add_row(
    "Ancestry EUR",
    mean_sd(df["EUR"], decimals=2),
    mean_sd(controls["EUR"], decimals=2),
    mean_sd(cases["EUR"], decimals=2),
    pval_continuous("EUR"),
)

# ── Ancestry MAP ──────────────────────────────────────────────────────────
add_row(
    "Ancestry MAP",
    mean_sd(df["MAP"], decimals=2),
    mean_sd(controls["MAP"], decimals=2),
    mean_sd(cases["MAP"], decimals=2),
    pval_continuous("MAP"),
)

# ── Ancestry AYM ──────────────────────────────────────────────────────────
add_row(
    "Ancestry AYM",
    mean_sd(df["AYM"], decimals=2),
    mean_sd(controls["AYM"], decimals=2),
    mean_sd(cases["AYM"], decimals=2),
    pval_continuous("AYM"),
)

# ── Population Density ────────────────────────────────────────────────────
add_row(
    "Population Density",
    mean_sd(df["Densidad"]),
    mean_sd(controls["Densidad"]),
    mean_sd(cases["Densidad"]),
    pval_continuous("Densidad"),
)

# ── Geographic Location ───────────────────────────────────────────────────
GEO_COL = "Macrozona"
GEO_LABELS = {1: "North", 2: "Center", 3: "Center South", 4: "South", 5: "Austral"}
add_row(
    "Geographic Location",
    f"Total (n={total_nonull(df, GEO_COL)})",
    total_nonull(controls, GEO_COL),
    total_nonull(cases, GEO_COL),
    pval_cat(build_ct_int(GEO_COL, list(GEO_LABELS.keys()))),
)
for val, label in GEO_LABELS.items():
    add_row("", f"  {label}",
            n_only(controls, pl.col(GEO_COL) == val),
            n_only(cases,    pl.col(GEO_COL) == val))

# ── Education Level ───────────────────────────────────────────────────────
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
    total_nonull(controls, EDU_COL),
    total_nonull(cases, EDU_COL),
    pval_cat(build_ct_int(EDU_COL, list(EDU_LABELS.keys()))),
)
for val, label in EDU_LABELS.items():
    add_row("", f"  {label}",
            n_only(controls, pl.col(EDU_COL) == val),
            n_only(cases,    pl.col(EDU_COL) == val))

# ── Healthcare System ─────────────────────────────────────────────────────
HS_COL = "Tipo_Salud"
HS_LABELS = {1: "Public", 2: "Private"}
add_row(
    "Healthcare System",
    f"Total (n={total_nonull(df, HS_COL)})",
    total_nonull(controls, HS_COL),
    total_nonull(cases, HS_COL),
    pval_cat(build_ct_int(HS_COL, list(HS_LABELS.keys()))),
)
for val, label in HS_LABELS.items():
    add_row("", f"  {label}",
            n_only(controls, pl.col(HS_COL) == val),
            n_only(cases,    pl.col(HS_COL) == val))

# ── Employment Situation ──────────────────────────────────────────────────
EMP_COL = "Situación.ocupacional"
EMP_LABELS = {"Activo": "Employed", "Cesante": "Unemployed", "Inactivo": "Idle"}
add_row(
    "Employment Situation",
    f"Total (n={total_nonull(df, EMP_COL)})",
    total_nonull(controls, EMP_COL),
    total_nonull(cases, EMP_COL),
    pval_cat(build_ct_str(EMP_COL, list(EMP_LABELS.keys()))),
)
for val, label in EMP_LABELS.items():
    add_row("", f"  {label}",
            n_only(controls, pl.col(EMP_COL) == val),
            n_only(cases,    pl.col(EMP_COL) == val))

# ── Bloque: Clinical - Lifestyle ───────────────────────────────────────────
add_row("", "─── Clinical - Lifestyle ───", "", "")

# ── Weight ────────────────────────────────────────────────────────────────
PESO_VALID = pl.col("peso") > 30
_ctrl_peso = controls.filter(PESO_VALID)["peso"].drop_nulls().to_numpy()
_case_peso = cases.filter(PESO_VALID)["peso"].drop_nulls().to_numpy()
_peso_result = stats.mannwhitneyu(_ctrl_peso, _case_peso, alternative="two-sided")
_p_peso = float(_peso_result.pvalue)
add_row(
    "Weight",
    mean_sd(df.filter(PESO_VALID)["peso"]),
    mean_sd(controls.filter(PESO_VALID)["peso"]),
    mean_sd(cases.filter(PESO_VALID)["peso"]),
    fmt_p(_p_peso),
)

# ── Height ────────────────────────────────────────────────────────────────
add_row(
    "Height",
    mean_sd(df["Altura"].drop_nulls().cast(pl.Float64)),
    mean_sd(controls["Altura"].drop_nulls().cast(pl.Float64)),
    mean_sd(cases["Altura"].drop_nulls().cast(pl.Float64)),
    pval_continuous("Altura"),
)

# ── BMI ───────────────────────────────────────────────────────────────────
add_row(
    "BMI",
    mean_sd(df["IMC"]),
    mean_sd(controls["IMC"]),
    mean_sd(cases["IMC"]),
    pval_continuous("IMC"),
)

# ── Blood Group ───────────────────────────────────────────────────────────
BG_COL = "Grupo.Sanguíneo"
BG_LABELS = ["O", "A", "B", "AB"]
add_row(
    "Blood Group",
    f"Total (n={total_nonull(df, BG_COL)})",
    total_nonull(controls, BG_COL),
    total_nonull(cases, BG_COL),
    pval_cat(build_ct_str(BG_COL, BG_LABELS)),
)
for val in BG_LABELS:
    add_row("", f"  {val}",
            n_only(controls, pl.col(BG_COL) == val),
            n_only(cases,    pl.col(BG_COL) == val))

# ── Rh Group ──────────────────────────────────────────────────────────────
RH_COL = "Grupo.Rh"
RH_VALS = ["Rh +", "Rh -"]
add_row(
    "Rh Group",
    f"Total (n={total_nonull(df, RH_COL)})",
    total_nonull(controls, RH_COL),
    total_nonull(cases, RH_COL),
    pval_cat(build_ct_str(RH_COL, RH_VALS)),
)
for val in RH_VALS:
    add_row("", f"  {val}",
            n_only(controls, pl.col(RH_COL) == val),
            n_only(cases,    pl.col(RH_COL) == val))

# ── Tobacco Consumption ───────────────────────────────────────────────────
TAB_COL = "tabaco"
add_row(
    "Tobacco Consumption",
    f"Total (n={total_nonull(df, TAB_COL)})",
    total_nonull(controls, TAB_COL),
    total_nonull(cases, TAB_COL),
    pval_cat(build_ct_int(TAB_COL, [1, 0])),
)
for label, val in [("Yes", 1), ("No", 0)]:
    add_row("", f"  {label}",
            n_only(controls, pl.col(TAB_COL) == val),
            n_only(cases,    pl.col(TAB_COL) == val))

# ── Tobacco Daily Frequency ───────────────────────────────────────────────
CIG_COL = "Cigarros.diarios"
CIG_RAW  = [
    "31 o más", "Entre 21 y 30", "Entre 11 y 20",
    "Entre 1 y 10", "Menos de 1 al día (menos de 7 a la semana)", "0 al día",
]
CIG_LABELS = [
    ("31 o más",                                   "31 or more"),
    ("Entre 21 y 30",                              "21 to 30"),
    ("Entre 11 y 20",                              "11 to 20"),
    ("Entre 1 y 10",                               "1 to 10"),
    ("Menos de 1 al día (menos de 7 a la semana)", "Less than one"),
    ("0 al día",                                   "Never smoke"),
]
add_row(
    "Tobacco Daily Frequency",
    f"Total (n={total_nonull(df, CIG_COL)})",
    total_nonull(controls, CIG_COL),
    total_nonull(cases, CIG_COL),
    pval_cat(build_ct_str(CIG_COL, CIG_RAW)),
)
for raw_val, label in CIG_LABELS:
    add_row("", f"  {label}",
            n_only(controls, pl.col(CIG_COL) == raw_val),
            n_only(cases,    pl.col(CIG_COL) == raw_val))

# ── Alcohol Consumption ───────────────────────────────────────────────────
ALC_COL = "Consumo.alcohol"
WEEKLY_VALS = ["Dos o tres veces a la semana", "Cuatro o más veces a la semana"]
ALC_GROUPS = [
    WEEKLY_VALS,
    ["Dos a cuatro veces al mes"],
    ["Una vez al mes o menos"],
    ["Nunca bebe"],
]
ALC_LABELS = [
    "2 or more times a week",
    "2-4 times a month",
    "Once a month or less",
    "Never drinks",
]
add_row(
    "Alcohol Consumption",
    f"Total (n={total_nonull(df, ALC_COL)})",
    total_nonull(controls, ALC_COL),
    total_nonull(cases, ALC_COL),
    pval_cat(build_ct_isin(ALC_COL, ALC_GROUPS)),
)
for group_vals, label in zip(ALC_GROUPS, ALC_LABELS):
    add_row("", f"  {label}",
            n_only(controls, pl.col(ALC_COL).is_in(group_vals)),
            n_only(cases,    pl.col(ALC_COL).is_in(group_vals)))

# ── Bloque: COVID-19 ──────────────────────────────────────────────────────
add_row("", "─── COVID-19 ───", "", "")

# ── No. Symptoms ─────────────────────────────────────────────────────────
add_row(
    "No. Symptoms",
    mean_sd(df["Total_Sintomas"].cast(pl.Float64)),
    mean_sd(controls["Total_Sintomas"].cast(pl.Float64)),
    mean_sd(cases["Total_Sintomas"].cast(pl.Float64)),
    pval_continuous("Total_Sintomas"),
)

# ── No. Pre-existing diseases ─────────────────────────────────────────────
add_row(
    "No. Pre-existing diseases",
    mean_sd(df["Total_Cond_pre"].cast(pl.Float64)),
    mean_sd(controls["Total_Cond_pre"].cast(pl.Float64)),
    mean_sd(cases["Total_Cond_pre"].cast(pl.Float64)),
    pval_continuous("Total_Cond_pre"),
)

# ── More than 5 Symptoms ──────────────────────────────────────────────────
M5_COL = "Mas_de_5"
add_row(
    "More than 5 Symptoms",
    f"Total (n={total_nonull(df, M5_COL)})",
    total_nonull(controls, M5_COL),
    total_nonull(cases, M5_COL),
    pval_cat(build_ct_int(M5_COL, [1, 0])),
)
for label, val in [("Yes", 1), ("No", 0)]:
    add_row("", f"  {label}",
            n_only(controls, pl.col(M5_COL) == val),
            n_only(cases,    pl.col(M5_COL) == val))

# ── Severe Infection ──────────────────────────────────────────────────────
SEV_COL = "Severo"
add_row(
    "Severe Infection",
    f"Total (n={total_nonull(df, SEV_COL)})",
    total_nonull(controls, SEV_COL),
    total_nonull(cases, SEV_COL),
    pval_cat(build_ct_int(SEV_COL, [1, 0])),
)
for label, val in [("Yes", 1), ("No", 0)]:
    add_row("", f"  {label}",
            n_only(controls, pl.col(SEV_COL) == val),
            n_only(cases,    pl.col(SEV_COL) == val))

# ── Recovered ────────────────────────────────────────────────────────────
REC_COL = "recuperado_3m"
add_row(
    "Recovered",
    f"Total (n={total_nonull(df, REC_COL)})",
    total_nonull(controls, REC_COL),
    total_nonull(cases, REC_COL),
    pval_cat(build_ct_int(REC_COL, [1, 2])),
)
for label, val in [("Yes", 1), ("No", 2)]:
    add_row("", f"  {label}",
            n_only(controls, pl.col(REC_COL) == val),
            n_only(cases,    pl.col(REC_COL) == val))

# ── Health problems that limit daily activities ───────────────────────────
PROB_COL = "problemas_3m"
add_row(
    "Health problems that limit daily activities",
    f"Total (n={total_nonull(df, PROB_COL)})",
    total_nonull(controls, PROB_COL),
    total_nonull(cases, PROB_COL),
    pval_cat(build_ct_int(PROB_COL, [1, 2])),
)
for label, val in [("Yes", 1), ("No", 2)]:
    add_row("", f"  {label}",
            n_only(controls, pl.col(PROB_COL) == val),
            n_only(cases,    pl.col(PROB_COL) == val))

# ── Need someone to help regularly ───────────────────────────────────────
AYU_COL = "ayuda_3m"
add_row(
    "Need someone to help regularly",
    f"Total (n={total_nonull(df, AYU_COL)})",
    total_nonull(controls, AYU_COL),
    total_nonull(cases, AYU_COL),
    pval_cat(build_ct_int(AYU_COL, [1, 2])),
)
for label, val in [("Yes", 1), ("No", 2)]:
    add_row("", f"  {label}",
            n_only(controls, pl.col(AYU_COL) == val),
            n_only(cases,    pl.col(AYU_COL) == val))

# ── Health problems that require to stay at home ──────────────────────────
CASA_COL = "casa_3m"
add_row(
    "Health problems that require to stay at home",
    f"Total (n={total_nonull(df, CASA_COL)})",
    total_nonull(controls, CASA_COL),
    total_nonull(cases, CASA_COL),
    pval_cat(build_ct_int(CASA_COL, [1, 2])),
)
for label, val in [("Yes", 1), ("No", 2)]:
    add_row("", f"  {label}",
            n_only(controls, pl.col(CASA_COL) == val),
            n_only(cases,    pl.col(CASA_COL) == val))

# ─────────────────────────────────────────────
# 5. CONSTRUIR DATAFRAME FINAL
# ─────────────────────────────────────────────
table2 = pd.DataFrame(rows)

# ─────────────────────────────────────────────
# 6. MOSTRAR EN CONSOLA
# ─────────────────────────────────────────────
pd.set_option("display.max_rows", 200)
pd.set_option("display.max_colwidth", 50)
pd.set_option("display.width", 120)

print("\n")
print("=" * 120)
print("TABLE 2 — Long COVID Comparison (Controls vs Cases)")
print(f"         Mann-Whitney U (continuous) | Chi-square (categorical)")
print("=" * 120)
print(table2.to_string(index=False))
print("=" * 120)

n_total    = df.shape[0]
n_controls = controls.shape[0]
n_cases    = cases.shape[0]
print(f"\nSample sizes → Total: {n_total} | Controls: {n_controls} | Cases: {n_cases}")

# ─────────────────────────────────────────────
# 7. GUARDAR CSV
# ─────────────────────────────────────────────
OUT_CSV = Path("pdf_reports/table2_longcovid.csv")
OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
table2.to_csv(OUT_CSV, index=False)
print(f"\nTabla guardada en: {OUT_CSV}")
