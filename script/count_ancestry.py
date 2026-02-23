#!/usr/bin/env python3
"""
Determina la ANCESTRÍA DOMINANTE de cada participante a partir de las
proporciones EUR, EAS, AFR, AYM, MAP y cuenta cuántos hay en cada grupo.

Uso: python count_ancestry.py [ruta/al/csv]
Si no se indica ruta, usa ../datasets/longcovid_2020W13-2021W22.csv
"""
import sys
from pathlib import Path
import csv

PROP_COLS = ["EUR", "EAS", "AFR", "AYM", "MAP"]


def main():
    p = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("../datasets/longcovid_2020W13-2021W22.csv")
    if not p.exists():
        print(f"ERROR: CSV no encontrado: {p.resolve()}")
        sys.exit(1)

    dominant_counts: dict[str, int] = {}
    sin_datos = 0
    total_rows = 0

    with p.open(newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []

        available = [c for c in PROP_COLS if c in fieldnames]
        missing   = [c for c in PROP_COLS if c not in fieldnames]
        if missing:
            print(f"AVISO: columnas no encontradas: {missing}")
        if not available:
            print("ERROR: ninguna columna de proporciones ancestrales disponible.")
            sys.exit(1)

        for r in reader:
            total_rows += 1
            props = {}
            for col in available:
                raw = r.get(col, "").strip()
                try:
                    props[col] = float(raw)
                except (ValueError, TypeError):
                    pass

            if props:
                dominant = max(props, key=lambda k: props[k])
                dominant_counts[dominant] = dominant_counts.get(dominant, 0) + 1
            else:
                sin_datos += 1

    print(f"\nTotal participantes : {total_rows}")
    print(f"Sin datos genéticos : {sin_datos}")
    print(f"\n=== Ancestría dominante (columnas: {available}) ===")
    print(f"{'Grupo':<8} {'n':>7}  {'%':>6}")
    print("-" * 28)
    for col in available:
        count = dominant_counts.get(col, 0)
        pct = count / (total_rows - sin_datos) * 100 if (total_rows - sin_datos) > 0 else 0
        print(f"  {col:<6} {count:>7}  ({pct:>5.1f}%)")
    print("-" * 28)
    con_datos = total_rows - sin_datos
    print(f"  {'TOTAL':<6} {con_datos:>7}  (100.0%)")


if __name__ == '__main__':
    main()
