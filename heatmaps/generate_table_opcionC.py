#!/usr/bin/env python3
"""
Genera una tabla TXT con el detalle paciente-a-paciente del Heatmap Opción C.

Salida: heatmaps/output/tabla_opcionC_por_sexo.txt

Estructura de la tabla:
  - Un bloque por cada subgrupo (Hosp-H, Hosp-M, NoHosp-H, NoHosp-M)
  - Columnas: N° | cod_participante | C1 | C2 | C3 | C4 | Total
  - Totales parciales y generales al final

Uso:
    python heatmaps/generate_table_opcionC.py
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

import polars as pl
from modules import load_data, create_criterio_variables

# ── Directorio de salida ────────────────────────────────────────────────────
OUTPUT_DIR = Path(__file__).resolve().parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


def _prepare_data(df: pl.DataFrame):
    """Replica exactamente la lógica de agrupación/ordenación del heatmap Opción C."""

    # 1. Preparar _hosp_num
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

    # 2. Dividir y ordenar exactamente igual que el heatmap
    def sort_by_criterios(sub: pl.DataFrame) -> pl.DataFrame:
        return sub.sort(
            ["criterio_1", "criterio_2", "criterio_3", "criterio_4"],
            descending=[True, True, True, True],
        )

    groups = {
        "Hospitalizados — Hombres (H)": sort_by_criterios(
            df_h.filter((pl.col("_hosp_num") == 1) & (pl.col("sexo") == 1))
        ),
        "Hospitalizados — Mujeres (M)": sort_by_criterios(
            df_h.filter((pl.col("_hosp_num") == 1) & (pl.col("sexo") == 2))
        ),
        "No hospitalizados — Hombres (H)": sort_by_criterios(
            df_h.filter((pl.col("_hosp_num") == 0) & (pl.col("sexo") == 1))
        ),
        "No hospitalizados — Mujeres (M)": sort_by_criterios(
            df_h.filter((pl.col("_hosp_num") == 0) & (pl.col("sexo") == 2))
        ),
    }
    return groups


def _mark(val) -> str:
    """Devuelve X si cumple criterio, - si no."""
    return "X" if int(val) == 1 else "-"


def generate_txt_table() -> str:
    """Genera la tabla TXT y la guarda en disco. Devuelve la ruta del archivo."""

    # ── Cargar datos ─────────────────────────────────────────────────────────
    dataset_path = ROOT_DIR / "datasets" / "longcovid_2020W13-2021W22.csv"
    df = load_data(str(dataset_path))
    df_con_criterios = create_criterio_variables(df)
    groups = _prepare_data(df_con_criterios)

    lines: list[str] = []
    sep = "=" * 90

    lines.append(sep)
    lines.append("TABLA DETALLE HEATMAP OPCIÓN C — CRITERIOS LONG COVID POR PACIENTE")
    lines.append("Ordenado: Hosp-H → Hosp-M → NoHosp-H → NoHosp-M")
    lines.append("Dentro de cada grupo: orden descendente por C1 > C2 > C3 > C4")
    lines.append(sep)
    lines.append("")

    # Contadores globales para resumen final
    grand_totals = {}  # {grupo_label: {criterio: count}}
    grand_n = {}       # {grupo_label: int}
    global_idx = 0     # Índice continuo (posición en heatmap)

    for group_label, df_group in groups.items():
        n = df_group.height
        grand_n[group_label] = n
        grand_totals[group_label] = {c: 0 for c in range(1, 5)}

        lines.append(f"┌{'─' * 88}┐")
        lines.append(f"│  {group_label:<50s}  (n = {n}){' ' * (30 - len(str(n)))}│")
        lines.append(f"├{'─' * 88}┤")
        lines.append(
            f"│ {'N°':>5s} │ {'Pos.Heatmap':>11s} │ {'cod_participante':>18s} │"
            f" {'C1':^4s}│ {'C2':^4s}│ {'C3':^4s}│ {'C4':^4s}│ {'Total':>5s} │"
        )
        lines.append(f"├{'─' * 88}┤")

        for local_i in range(n):
            global_idx += 1
            row = df_group.row(local_i, named=True)
            cod = str(row.get("cod_participante", row.get("newCode", "?")))
            c1 = int(row["criterio_1"])
            c2 = int(row["criterio_2"])
            c3 = int(row["criterio_3"])
            c4 = int(row["criterio_4"])
            total = c1 + c2 + c3 + c4

            grand_totals[group_label][1] += c1
            grand_totals[group_label][2] += c2
            grand_totals[group_label][3] += c3
            grand_totals[group_label][4] += c4

            lines.append(
                f"│ {local_i + 1:>5d} │ {global_idx:>11d} │ {cod:>18s} │"
                f"  {_mark(c1):^3s}│  {_mark(c2):^3s}│  {_mark(c3):^3s}│  {_mark(c4):^3s}│ {total:>5d} │"
            )

        lines.append(f"└{'─' * 88}┘")
        lines.append("")

    # ── Resumen de totales ───────────────────────────────────────────────────
    lines.append(sep)
    lines.append("RESUMEN DE TOTALES POR GRUPO Y CRITERIO")
    lines.append(sep)
    lines.append("")
    lines.append(f"{'Grupo':<42s} │ {'n':>5s} │ {'C1':>5s} │ {'C2':>5s} │ {'C3':>5s} │ {'C4':>5s} │")
    lines.append(f"{'─' * 42}─┼{'─' * 7}┼{'─' * 7}┼{'─' * 7}┼{'─' * 7}┼{'─' * 7}┤")

    for group_label in groups:
        n = grand_n[group_label]
        t = grand_totals[group_label]
        lines.append(
            f"{group_label:<42s} │ {n:>5d} │ {t[1]:>5d} │ {t[2]:>5d} │ {t[3]:>5d} │ {t[4]:>5d} │"
        )

    # Subtotales por sexo
    lines.append(f"{'─' * 42}─┼{'─' * 7}┼{'─' * 7}┼{'─' * 7}┼{'─' * 7}┼{'─' * 7}┤")

    # Hombres
    h_labels = [l for l in groups if "Hombres" in l]
    n_h = sum(grand_n[l] for l in h_labels)
    t_h = {c: sum(grand_totals[l][c] for l in h_labels) for c in range(1, 5)}
    lines.append(
        f"{'TOTAL HOMBRES (H)':<42s} │ {n_h:>5d} │ {t_h[1]:>5d} │ {t_h[2]:>5d} │ {t_h[3]:>5d} │ {t_h[4]:>5d} │"
    )

    # Mujeres
    m_labels = [l for l in groups if "Mujeres" in l]
    n_m = sum(grand_n[l] for l in m_labels)
    t_m = {c: sum(grand_totals[l][c] for l in m_labels) for c in range(1, 5)}
    lines.append(
        f"{'TOTAL MUJERES (M)':<42s} │ {n_m:>5d} │ {t_m[1]:>5d} │ {t_m[2]:>5d} │ {t_m[3]:>5d} │ {t_m[4]:>5d} │"
    )

    lines.append(f"{'─' * 42}─┼{'─' * 7}┼{'─' * 7}┼{'─' * 7}┼{'─' * 7}┼{'─' * 7}┤")

    # Gran total
    n_all = n_h + n_m
    t_all = {c: t_h[c] + t_m[c] for c in range(1, 5)}
    lines.append(
        f"{'GRAN TOTAL':<42s} │ {n_all:>5d} │ {t_all[1]:>5d} │ {t_all[2]:>5d} │ {t_all[3]:>5d} │ {t_all[4]:>5d} │"
    )

    lines.append("")

    # ── Porcentajes ──────────────────────────────────────────────────────────
    lines.append(sep)
    lines.append("PORCENTAJE QUE CUMPLE CADA CRITERIO (por grupo)")
    lines.append(sep)
    lines.append("")
    lines.append(f"{'Grupo':<42s} │ {'C1 %':>6s} │ {'C2 %':>6s} │ {'C3 %':>6s} │ {'C4 %':>6s} │")
    lines.append(f"{'─' * 42}─┼{'─' * 8}┼{'─' * 8}┼{'─' * 8}┼{'─' * 8}┤")

    for group_label in groups:
        n = grand_n[group_label]
        t = grand_totals[group_label]
        pcts = {c: (t[c] / n * 100) if n > 0 else 0 for c in range(1, 5)}
        lines.append(
            f"{group_label:<42s} │ {pcts[1]:>5.1f}% │ {pcts[2]:>5.1f}% │ {pcts[3]:>5.1f}% │ {pcts[4]:>5.1f}% │"
        )

    lines.append(f"{'─' * 42}─┼{'─' * 8}┼{'─' * 8}┼{'─' * 8}┼{'─' * 8}┤")
    pct_h = {c: (t_h[c] / n_h * 100) if n_h > 0 else 0 for c in range(1, 5)}
    pct_m = {c: (t_m[c] / n_m * 100) if n_m > 0 else 0 for c in range(1, 5)}
    pct_a = {c: (t_all[c] / n_all * 100) if n_all > 0 else 0 for c in range(1, 5)}
    lines.append(
        f"{'TOTAL HOMBRES (H)':<42s} │ {pct_h[1]:>5.1f}% │ {pct_h[2]:>5.1f}% │ {pct_h[3]:>5.1f}% │ {pct_h[4]:>5.1f}% │"
    )
    lines.append(
        f"{'TOTAL MUJERES (M)':<42s} │ {pct_m[1]:>5.1f}% │ {pct_m[2]:>5.1f}% │ {pct_m[3]:>5.1f}% │ {pct_m[4]:>5.1f}% │"
    )
    lines.append(f"{'─' * 42}─┼{'─' * 8}┼{'─' * 8}┼{'─' * 8}┼{'─' * 8}┤")
    lines.append(
        f"{'GRAN TOTAL':<42s} │ {pct_a[1]:>5.1f}% │ {pct_a[2]:>5.1f}% │ {pct_a[3]:>5.1f}% │ {pct_a[4]:>5.1f}% │"
    )

    # ── Criterios compartidos ────────────────────────────────────────────────
    lines.append("")
    lines.append(sep)
    lines.append("CRITERIOS COMPARTIDOS (pacientes que cumplen múltiples criterios simultáneamente)")
    lines.append(sep)
    lines.append("")

    from itertools import combinations as _combs

    all_combos: list[tuple[int, ...]] = []
    for r in range(2, 5):
        all_combos.extend(_combs(range(1, 5), r))
    # (1,2) (1,3) (1,4) (2,3) (2,4) (3,4) (1,2,3) (1,2,4) (1,3,4) (2,3,4) (1,2,3,4)

    combo_header = (
        f"{'Combinación':<24s}│{'Hosp-H':>8s}│{'Hosp-M':>8s}"
        f"│{'NoHos-H':>8s}│{'NoHos-M':>8s}│{'Total':>8s}│{'%Total':>8s}│"
    )
    combo_sep_line = (
        f"{'─' * 24}┼{'─' * 8}┼{'─' * 8}┼{'─' * 8}┼{'─' * 8}┼{'─' * 8}┼{'─' * 8}┤"
    )

    lines.append(combo_header)
    lines.append(combo_sep_line)

    for combo in all_combos:
        label = " ∩ ".join(f"C{c}" for c in combo)
        row_line = f"{label:<24s}"
        combo_total = 0
        for _gl, df_g in groups.items():
            filt = pl.col(f"criterio_{combo[0]}") == 1
            for c in combo[1:]:
                filt = filt & (pl.col(f"criterio_{c}") == 1)
            cnt = df_g.filter(filt).height
            combo_total += cnt
            row_line += f"│{cnt:>8d}"
        pct_c = combo_total / n_all * 100 if n_all > 0 else 0
        row_line += f"│{combo_total:>8d}│{pct_c:>7.1f}%│"
        lines.append(row_line)

    # ── Distribución por número de criterios cumplidos ───────────────────────
    lines.append("")
    lines.append(sep)
    lines.append("DISTRIBUCIÓN POR NÚMERO DE CRITERIOS CUMPLIDOS")
    lines.append(sep)
    lines.append("")

    lines.append(combo_header)
    lines.append(combo_sep_line)

    for num_c in range(5):  # 0, 1, 2, 3, 4
        label = f"{num_c} criterios" if num_c != 1 else "1 criterio"
        row_line = f"{label:<24s}"
        dist_total = 0
        for _gl, df_g in groups.items():
            cnt = df_g.with_columns(
                (
                    pl.col("criterio_1").cast(pl.Int32)
                    + pl.col("criterio_2").cast(pl.Int32)
                    + pl.col("criterio_3").cast(pl.Int32)
                    + pl.col("criterio_4").cast(pl.Int32)
                ).alias("_sum_c")
            ).filter(pl.col("_sum_c") == num_c).height
            dist_total += cnt
            row_line += f"│{cnt:>8d}"
        pct_d = dist_total / n_all * 100 if n_all > 0 else 0
        row_line += f"│{dist_total:>8d}│{pct_d:>7.1f}%│"
        lines.append(row_line)

    lines.append("")
    lines.append(sep)
    lines.append("X = Cumple criterio   |   - = No cumple criterio")
    lines.append("Pos.Heatmap = posición del paciente en el eje X del gráfico Opción C")
    lines.append(sep)

    # ── Escribir archivo ─────────────────────────────────────────────────────
    txt = "\n".join(lines)
    out_path = OUTPUT_DIR / "tabla_opcionC_por_sexo.txt"
    out_path.write_text(txt, encoding="utf-8")
    print(f"✅ Tabla guardada en: {out_path}")
    return str(out_path)


if __name__ == "__main__":
    generate_txt_table()
