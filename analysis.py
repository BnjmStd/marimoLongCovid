import marimo

__generated_with = "0.19.4"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import polars as pl
    import plotly.express as px
    import plotly.graph_objects as go
    print("Librerías importadas: marimo, polars, plotly.express, plotly.graph_objects")
    return mo, pl, px


@app.cell
def _(mo):
    mo.md("""
    # Long COVID - Análisis de Datos

    Este es un notebook reactivo de Marimo con Polars y Plotly.

    ## Stack Moderno:
    - **Polars**: 10-100x más rápido que Pandas
    - **Plotly**: Gráficos interactivos
    - **Marimo**: Notebooks reactivos
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## 1. Cargar Datos
    """)
    return


@app.cell
def _(pl):
    # Ejemplo: Crear un DataFrame de demostración
    # Reemplaza esto con tu archivo CSV/Parquet:
    # df = pl.read_csv("data/tu_archivo.csv")
    # df = pl.read_parquet("data/tu_archivo.parquet")

    df = pl.DataFrame({
        "fecha": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"],
        "pacientes": [120, 135, 128, 142, 156],
        "sintomas": ["fatiga", "tos", "fatiga", "dolor", "fatiga"],
        "severidad": [7.5, 6.2, 8.1, 5.5, 7.8]
    }).with_columns(
        pl.col("fecha").str.to_date()
    )

    df
    return (df,)


@app.cell
def _(df, mo):
    mo.md(f"""
    ## 2. Exploración Rápida

    **Total de registros:** {len(df):,}

    **Columnas:** {', '.join(df.columns)}
    """)
    return


@app.cell
def _(df, pl):
    # Estadísticas descriptivas con Polars
    stats = df.select([
        pl.col("pacientes").mean().alias("promedio_pacientes"),
        pl.col("severidad").mean().alias("severidad_promedio"),
        pl.col("severidad").max().alias("severidad_max")
    ])

    stats
    return


@app.cell
def _(mo):
    mo.md("""
    ## 3. Visualizaciones
    """)
    return


@app.cell
def _(df, px):
    # Gráfico de línea interactivo
    fig_linea = px.line(
        df.to_pandas(),  # Plotly usa pandas, pero conversión es rápida
        x="fecha",
        y="pacientes",
        title="Evolución de Pacientes",
        markers=True,
        template="plotly_white"
    )

    fig_linea.update_layout(
        xaxis_title="Fecha",
        yaxis_title="Número de Pacientes",
        hovermode="x unified"
    )

    fig_linea
    return


@app.cell
def _(df, pl, px):
    # Gráfico de barras por síntoma
    sintomas_count = df.group_by("sintomas").agg(
        pl.count().alias("frecuencia")
    ).sort("frecuencia", descending=True)

    fig_barras = px.bar(
        sintomas_count.to_pandas(),
        x="sintomas",
        y="frecuencia",
        title="Frecuencia de Síntomas",
        template="plotly_white",
        color="frecuencia",
        color_continuous_scale="Blues"
    )

    fig_barras
    return


@app.cell
def _(df, px):
    # Scatter plot de severidad
    fig_scatter = px.scatter(
        df.to_pandas(),
        x="fecha",
        y="severidad",
        size="pacientes",
        color="sintomas",
        title="Severidad vs Fecha (tamaño = pacientes)",
        template="plotly_white",
        hover_data=["pacientes"]
    )

    fig_scatter
    return


@app.cell
def _(mo):
    mo.md("""
    ## 4. Agregaciones con Polars

    Polars es extremadamente rápido para operaciones groupby y agregaciones.
    """)
    return


@app.cell
def _(df, pl):
    # Análisis por síntoma
    analisis = df.group_by("sintomas").agg([
        pl.count().alias("n_casos"),
        pl.col("severidad").mean().alias("severidad_promedio"),
        pl.col("pacientes").sum().alias("total_pacientes")
    ]).sort("severidad_promedio", descending=True)

    analisis
    return


@app.cell
def _(mo):
    mo.md("""
    ---

    ## 💡 Siguientes Pasos:

    1. **Carga tus datos reales**: Reemplaza el DataFrame de ejemplo
    2. **Explora**: Marimo recalcula automáticamente cuando cambias código
    3. **Añade más celdas**: Click en el botón + para agregar análisis
    4. **Exporta**: Usa `marimo export analysis.py` para HTML estático

    ### Comandos útiles:
    ```python
    # Leer CSV
    df = pl.read_csv("data/archivo.csv")

    # Leer Parquet (muy rápido)
    df = pl.read_parquet("data/archivo.parquet")

    # Leer Excel
    df = pl.read_excel("data/archivo.xlsx")
    ```
    """)
    return


if __name__ == "__main__":
    app.run()
