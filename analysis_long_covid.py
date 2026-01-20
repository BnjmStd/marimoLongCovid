import marimo

__generated_with = "0.19.4"
app = marimo.App(width="medium")


@app.cell
def __():
    import marimo as mo
    import polars as pl

    from modules import (
        load_long_covid,
        create_criterio_variables,
        count_by_criterio,
        create_descriptive_table,
        plot_long_covid_by_variable,
        plot_clusters_analysis,
        create_table_1,
    )

    return (
        count_by_criterio,
        create_criterio_variables,
        create_descriptive_table,
        create_table_1,
        load_long_covid,
        mo,
        pl,
        plot_clusters_analysis,
        plot_long_covid_by_variable,
    )


@app.cell
def __(mo):
    mo.md(
        """
    # Análisis Long COVID - Chile 2020-2021
    
    ## Tareas del análisis:
    1. Dataset truncado (variantes y long COVID) - generar estadísticas
    2. Variables de criterio (1-4)
    3. Variantes: barplot apilado por semana epidemiológica (11 linajes) + curva casos Chile
    4. Long COVID por semana epidemiológica por diferentes variables
    5. Análisis de clusters y secuelas
    6. Tabla 1 descriptiva
    7. Figura metodológica
    """
    )
    return


@app.cell
def __(mo):
    mo.md("## 1. Cargar Dataset y Generar Estadísticas")
    return


@app.cell
def __(load_long_covid, mo):
    # Cargar dataset
    df_long_covid = load_long_covid("datasets/longcovid_2020W13-2021W22.csv")

    mo.md(
        f"""
    **Dataset Long COVID cargado:**
    - Registros: {len(df_long_covid):,}
    - Columnas: {len(df_long_covid.columns)}
    - Periodo: 2020W13 - 2021W22
    """
    )
    return (df_long_covid,)


@app.cell
def __(mo):
    mo.md("## 2. Crear Variables de Criterio por fenotipos long covid (1-4)")
    return


@app.cell
def __(mo):
    mo.md("### 2.1. Criterio 1 (longCOVID, fenotipo muy general)\n")
    return


@app.cell
def __(mo):
    mo.md("### 2.2. Criterio 2 (Síntomas recurrentes)\n")
    return


@app.cell
def __(mo):
    mo.md("## 2.3. Criterio 3 (Cluster)")
    return


@app.cell
def __(mo):
    mo.md("## 2.4. Criterio 4 (Secuelas)")
    return


@app.cell
def __(mo):
    mo.md("## 3. Variantes: Barplot Apilado por Semana Epidemiológica")
    return


@app.cell
def __(mo):
    mo.md("## 4. Long COVID por Semana Epidemiológica")
    return


@app.cell
def __(mo):
    mo.md("### 4.1. Por variable longCOVID")
    return


@app.cell
def __(mo):
    mo.md("### 4.2. Por síntomas recurrentes")
    return


@app.cell
def __(mo):
    mo.md("### 4.3. Por pertenencia a cluster")
    return


@app.cell
def __(mo):
    mo.md("### 4.4. Por secuelas")
    return


@app.cell
def __(mo):
    mo.md("## 5. Análisis de Clusters y Secuelas")
    return


@app.cell
def __(mo):
    mo.md("## 6. Tabla 1: Descriptiva")
    return


@app.cell
def __(mo):
    mo.md("## 7. Figura Metodológica")
    return


if __name__ == "__main__":
    app.run()
