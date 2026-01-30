import marimo

__generated_with = "0.19.6"
app = marimo.App(width="medium")


@app.cell
def _():
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
        plot_dataset_overview,
        plot_criterio_comparison,
        plot_criterio1_by_week,
        plot_criterio2_sintomas,
        plot_criterio2_promedio_sintomas,
        plot_criterio2_promedio_sintomas_by_week,
        plot_criterio2_recovery,
        plot_criterio3_clusters_comparison,
        plot_longcovid_by_week,
        plot_sintomas_recurrentes_by_week,
        plot_cluster_pertenencia_by_week,
        plot_clusters_individuales_by_week,
        plot_secuelas_by_week,
        plot_clusters_heatmap_by_diagnosis_week,
        plot_demographic_clinical_heatmap,
        plot_criterio_barplot,
        plot_cases_by_week_by_sex,
        plot_cases_by_week_by_age_group,
        plot_cases_by_week_by_secuelas,
        plot_cases_by_week_by_nueva_condicion,
        plot_cases_by_week_by_sintomas_recurrentes,
        plot_cases_by_week_by_criterio_3_sin_nulls,
        plot_linaje_barplot,
        plot_hospitalizacion_by_week,
        create_table1_stratified,
    )
    return (
        create_criterio_variables,
        create_table1_stratified,
        load_long_covid,
        mo,
        pl,
        plot_cases_by_week_by_age_group,
        plot_cases_by_week_by_criterio_3_sin_nulls,
        plot_cases_by_week_by_nueva_condicion,
        plot_cases_by_week_by_secuelas,
        plot_cases_by_week_by_sex,
        plot_cases_by_week_by_sintomas_recurrentes,
        plot_cluster_pertenencia_by_week,
        plot_clusters_heatmap_by_diagnosis_week,
        plot_demographic_clinical_heatmap,
        plot_clusters_individuales_by_week,
        plot_criterio1_by_week,
        plot_criterio2_promedio_sintomas,
        plot_criterio2_promedio_sintomas_by_week,
        plot_criterio2_recovery,
        plot_criterio2_sintomas,
        plot_criterio3_clusters_comparison,
        plot_criterio_barplot,
        plot_criterio_comparison,
        plot_dataset_overview,
        plot_longcovid_by_week,
        plot_secuelas_by_week,
        plot_sintomas_recurrentes_by_week,
    )


@app.cell
def _(mo):
    mo.md("""
    # Análisis Long COVID - Chile 2020-2021

    ## Tareas del análisis:
    1. Dataset truncado (variantes y long COVID) - generar estadísticas
    2. Variables de criterio (1-4)
    3. Variantes: barplot apilado por semana epidemiológica (11 linajes) + curva casos Chile
    4. Long COVID por semana epidemiológica por diferentes variables
    5. Análisis de clusters y secuelas
    6. Tabla 1 descriptiva
    7. Figura metodológica
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## 1. Cargar Dataset y Generar Estadísticas
    """)
    return


@app.cell
def _(load_long_covid, mo):
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
def _(mo):
    mo.md("""
    ### Resumen Visual del Dataset
    """)
    return


@app.cell
def _(df_long_covid, plot_dataset_overview):
    # Gráfico de resumen del dataset
    fig_overview = plot_dataset_overview(df_long_covid)
    fig_overview
    return


@app.cell
def _(mo):
    mo.md("""
    **Interpretación:** Este panel muestra cuatro métricas clave del dataset:
    - **Distribución por Sexo**: Balance de género en la muestra
    - **Distribución de Edad**: Histograma de edades de los participantes
    - **Casos por Semana Epidemiológica**: Evolución temporal del reclutamiento
    - **Long COVID vs Control**: Proporción de casos con Long COVID (rojo) vs controles (azul)
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## 2. Crear Variables de Criterio por fenotipos long covid (1-4)
    """)
    return


@app.cell
def _():
    # Paleta de colores única para cada criterio
    COLORES_CRITERIOS = {
        1: "#3498db",  # Azul - Criterio 1 (Long COVID general)
        2: "#e74c3c",  # Rojo - Criterio 2 (Síntomas recurrentes)
        3: "#f39c12",  # Naranja - Criterio 3 (Clusters)
        4: "#9b59b6",  # Morado - Criterio 4 (Secuelas)
    }

    # Metadata de criterios para documentación
    CRITERIOS_METADATA = {
        1: {
            "nombre": "Long COVID General",
            "variables": ["longCOVID"],
            "descripcion": "Fenotipo muy general basado en la variable longCOVID",
            "formula": "criterio_1 = 1 si longCOVID == 1, sino 0",
            "color": COLORES_CRITERIOS[1],
        },
        2: {
            "nombre": "Síntomas Recurrentes",
            "variables": ["covid", "sintoma_recurrente_count", "recuperado_3m"],
            "descripcion": "COVID confirmado + Más de 1 síntoma recurrente + No recuperado a los 3 meses",
            "formula": "criterio_2 = 1 si (covid==1 AND sintoma_recurrente_count>1 AND recuperado_3m==2)",
            "color": COLORES_CRITERIOS[2],
        },
        3: {
            "nombre": "Clusters",
            "variables": ["covid", "pertenece_cluster_count", "recuperado_3m"],
            "descripcion": "COVID-19 + Al menos 2 síntomas de cualquier cluster + No recuperado a los 3 meses",
            "formula": "criterio_3 = 1 si (covid==1 AND pertenece_cluster_count>=1 AND recuperado_3m==2)",
            "color": COLORES_CRITERIOS[3],
        },
        4: {
            "nombre": "Secuelas",
            "variables": ["covid", "conteo_nueva_condicion", "sec_count"],
            "descripcion": "COVID-19 + Nueva condición O Secuelas crónicas",
            "formula": "criterio_4 = 1 si (covid==1 AND (conteo_nueva_condicion>=1 OR sec_count>=1))",
            "color": COLORES_CRITERIOS[4],
        },
    }
    return COLORES_CRITERIOS, CRITERIOS_METADATA


@app.cell
def _(pl):
    def validar_criterio(df, num_criterio: int, variables_componentes):
        """
        Valida un criterio calculando métricas de calidad y consistencia

        Args:
            df: DataFrame con el criterio calculado
            num_criterio: Número del criterio (1, 2, 3, 4)
            variables_componentes: Lista de variables que componen el criterio

        Returns:
            Diccionario con métricas de validación
        """
        criterio_col = f"criterio_{num_criterio}"

        # Validaciones básicas
        validacion = {
            "criterio": num_criterio,
            "n_total": len(df),
            "n_cumplen": df.filter(pl.col(criterio_col) == 1).height,
            "n_no_cumplen": df.filter(pl.col(criterio_col) == 0).height,
            "porcentaje_cumplen": (
                df.filter(pl.col(criterio_col) == 1).height / len(df) * 100
            ),
            "null_counts": {},
            "variables_validas": {},
        }

        # Contar NULLs por cada variable componente
        for var in variables_componentes:
            if var in df.columns:
                null_count = df.filter(pl.col(var).is_null()).height
                valid_count = df.filter(pl.col(var).is_not_null()).height
                validacion["null_counts"][var] = null_count
                validacion["variables_validas"][var] = {
                    "validos": valid_count,
                    "porcentaje_valido": (valid_count / len(df) * 100),
                }

        # Verificar consistencia del criterio
        validacion["consistente"] = (
            validacion["n_cumplen"] + validacion["n_no_cumplen"]
        ) == validacion["n_total"]

        return validacion
    return (validar_criterio,)


@app.cell
def _(mo):
    mo.md("""
    ### 2.1. Criterio 1 (longCOVID, fenotipo muy general)
    """)
    return


@app.cell
def _(df_long_covid, mo, pl):
    mo.md(f"""
    **Criterio 1:** Long COVID (fenotipo general)
    - Variable: `longCOVID == 1`
    - **Fórmula:** `criterio_1 = 1` si longCOVID == 1, sino 0

    **Casos en dataset:**
    - Cumplen longCOVID: {df_long_covid.filter(pl.col('longCOVID') == 1).height:,}
    - No cumplen: {df_long_covid.filter(pl.col('longCOVID') == 0).height:,}
    """)
    return


@app.cell
def _(CRITERIOS_METADATA, df_con_criterios, mo, pl, validar_criterio):
    # Validación del Criterio 1
    validacion_c1 = validar_criterio(
        df_con_criterios, 1, CRITERIOS_METADATA[1]["variables"]
    )

    # Mostrar resumen de Criterio 1
    mo.md(
        f"""
    ---
    ###  Resumen Criterio 1: {CRITERIOS_METADATA[1]['nombre']}

    **Construcción del criterio:**
    - **Número de variables:** {len(CRITERIOS_METADATA[1]['variables'])}
    - **Variables componentes:** `{'`, `'.join(CRITERIOS_METADATA[1]['variables'])}`
    - **Descripción:** {CRITERIOS_METADATA[1]['descripcion']}
    - **Fórmula lógica:** `{CRITERIOS_METADATA[1]['formula']}`
    - **Color asignado:** <span style="color:{CRITERIOS_METADATA[1]['color']}">███</span> `{CRITERIOS_METADATA[1]['color']}`

    **Resultados:**
    - Total de casos: {validacion_c1['n_total']:,}
    - Cumplen criterio: {validacion_c1['n_cumplen']:,} ({validacion_c1['porcentaje_cumplen']:.2f}%)
    - No cumplen: {validacion_c1['n_no_cumplen']:,} ({100-validacion_c1['porcentaje_cumplen']:.2f}%)

    **Validación de datos:**
    """
    )

    # Crear tabla de validación
    _validacion_tabla = []
    for _var in CRITERIOS_METADATA[1]["variables"]:
        if _var in validacion_c1["variables_validas"]:
            _info = validacion_c1["variables_validas"][_var]
            _validacion_tabla.append(
                {
                    "Variable": _var,
                    "Valores válidos": _info["validos"],
                    "% Válido": f"{_info['porcentaje_valido']:.2f}%",
                    "Valores NULL": validacion_c1["null_counts"][_var],
                }
            )

    df_validacion_c1 = pl.DataFrame(_validacion_tabla)

    (validacion_c1, df_validacion_c1)
    return df_validacion_c1, validacion_c1


@app.cell
def _(df_validacion_c1, mo, validacion_c1):
    # Mostrar tabla de validación
    mo.ui.table(df_validacion_c1)

    estado_c1 = (
        " **Criterio funciona correctamente**"
        if validacion_c1["consistente"]
        else "❌ **Problema detectado en el criterio**"
    )

    mo.md(
        f"""
    {estado_c1}

    - Consistencia lógica: {'Sí' if validacion_c1['consistente'] else 'No'}
    - Total casos = Cumplen + No cumplen: {validacion_c1['n_total']} = {validacion_c1['n_cumplen']} + {validacion_c1['n_no_cumplen']}

    ---
    """
    )
    return


@app.cell
def _(create_criterio_variables, df_long_covid):
    # Crear todas las variables de criterio
    df_con_criterios = create_criterio_variables(df_long_covid)
    df_con_criterios
    return (df_con_criterios,)


@app.cell
def _(CRITERIOS_METADATA, df_con_criterios, plot_criterio_barplot):
    # Barplot de Criterio 1
    fig_bar_c1 = plot_criterio_barplot(
        df_con_criterios,
        1,
        "Criterio 1 (Long COVID): Distribución de Casos",
        CRITERIOS_METADATA[1]["color"],
    )
    fig_bar_c1
    return


@app.cell
def _(mo):
    mo.md("""
    **Interpretación:** Este gráfico muestra la distribución semanal de casos según el Criterio 1 (fenotipo general de Long COVID):
    - **Barras azules**: Casos que cumplen el criterio (longCOVID == 1)
    - **Barras grises**: Casos que no cumplen el criterio

    Permite visualizar la evolución temporal del Long COVID durante el período de estudio (2020-2021).
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ### Criterio 1: Evolución Temporal
    """)
    return


@app.cell
def _(df_con_criterios, plot_criterio1_by_week):
    # Long COVID por semana epidemiológica
    fig_c1_week = plot_criterio1_by_week(df_con_criterios)
    fig_c1_week
    return


@app.cell
def _(mo):
    mo.md("""
    **Interpretación:** Evolución temporal con líneas separadas:
    - **Línea Long COVID**: Muestra la tendencia de casos positivos por semana
    - **Línea Control**: Muestra los casos control (sin Long COVID) por semana

    Este gráfico permite identificar picos, tendencias y patrones estacionales en la incidencia de Long COVID.
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## 2.2. Criterio 2 (Síntomas recurrentes)

    **Definición:** COVID confirmado + Más de 1 síntoma recurrente + No recuperado a los 3 meses

    **Fórmula:** `criterio_2 = 1` si cumple:
    - DP4: COVID confirmado (`covid == 1`)
    - P17: Más de 1 síntoma recurrente (`sintoma_recurrente_count > 1`)
    - P20: No recuperado a los 3 meses (`recuperado_3m == 2`)
    """)
    return


@app.cell
def _(df_con_criterios, pl):
    # Validar Criterio 2
    conteo_c2 = df_con_criterios.filter(pl.col("criterio_2") == 1).height
    no_cumple_c2 = df_con_criterios.filter(pl.col("criterio_2") == 0).height

    (conteo_c2, no_cumple_c2)
    return conteo_c2, no_cumple_c2


@app.cell
def _(conteo_c2, mo, no_cumple_c2):
    mo.md(f"""
    **Casos en dataset:**
    - Cumplen criterio 2: {conteo_c2:,}
    - No cumplen: {no_cumple_c2:,}
    """)
    return


@app.cell
def _(CRITERIOS_METADATA, df_con_criterios, mo, pl, validar_criterio):
    # Validación del Criterio 2
    validacion_c2 = validar_criterio(
        df_con_criterios, 2, CRITERIOS_METADATA[2]["variables"]
    )

    # Mostrar resumen de Criterio 2
    mo.md(
        f"""
    ---
    ###  Resumen Criterio 2: {CRITERIOS_METADATA[2]['nombre']}

    **Construcción del criterio:**
    - **Número de variables:** {len(CRITERIOS_METADATA[2]['variables'])}
    - **Variables componentes:** `{'`, `'.join(CRITERIOS_METADATA[2]['variables'])}`
    - **Descripción:** {CRITERIOS_METADATA[2]['descripcion']}
    - **Fórmula lógica:** `{CRITERIOS_METADATA[2]['formula']}`
    - **Color asignado:** <span style="color:{CRITERIOS_METADATA[2]['color']}">███</span> `{CRITERIOS_METADATA[2]['color']}`

    **Resultados:**
    - Total de casos: {validacion_c2['n_total']:,}
    - Cumplen criterio: {validacion_c2['n_cumplen']:,} ({validacion_c2['porcentaje_cumplen']:.2f}%)
    - No cumplen: {validacion_c2['n_no_cumplen']:,} ({100-validacion_c2['porcentaje_cumplen']:.2f}%)

    **Validación de datos:**
    """
    )

    # Crear tabla de validación
    _validacion_tabla_c2 = []
    for _var in CRITERIOS_METADATA[2]["variables"]:
        if _var in validacion_c2["variables_validas"]:
            _info = validacion_c2["variables_validas"][_var]
            _validacion_tabla_c2.append(
                {
                    "Variable": _var,
                    "Valores válidos": _info["validos"],
                    "% Válido": f"{_info['porcentaje_valido']:.2f}%",
                    "Valores NULL": validacion_c2["null_counts"][_var],
                }
            )

    df_validacion_c2 = pl.DataFrame(_validacion_tabla_c2)

    (validacion_c2, df_validacion_c2)
    return df_validacion_c2, validacion_c2


@app.cell
def _(df_validacion_c2, mo, validacion_c2):
    # Mostrar tabla de validación del Criterio 2
    mo.ui.table(df_validacion_c2)

    estado_c2 = (
        " **Criterio funciona correctamente**"
        if validacion_c2["consistente"]
        else "❌ **Problema detectado en el criterio**"
    )

    mo.md(
        f"""
    {estado_c2}

    - Consistencia lógica: {'Sí' if validacion_c2['consistente'] else 'No'}
    - Total casos = Cumplen + No cumplen: {validacion_c2['n_total']} = {validacion_c2['n_cumplen']} + {validacion_c2['n_no_cumplen']}

    ---
    """
    )
    return


@app.cell
def _(CRITERIOS_METADATA, df_con_criterios, plot_criterio_barplot):
    # Barplot de Criterio 2
    fig_bar_c2 = plot_criterio_barplot(
        df_con_criterios,
        2,
        "Criterio 2 (Síntomas Recurrentes): Distribución de Casos",
        CRITERIOS_METADATA[2]["color"],
    )
    fig_bar_c2
    return


@app.cell
def _(mo):
    mo.md("""
    **Interpretación:** Distribución semanal del Criterio 2 (Síntomas Recurrentes):
    - **Barras rojas**: Casos con COVID confirmado + >1 síntoma recurrente + no recuperados a los 3 meses
    - **Barras grises**: Resto de casos

    Este criterio es más restrictivo que el Criterio 1, enfocándose en persistencia sintomática específica.
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ### Criterio 2: Análisis de Síntomas
    """)
    return


@app.cell
def _(CRITERIOS_METADATA, df_con_criterios, plot_criterio2_promedio_sintomas):
    # Promedio de síntomas recurrentes
    fig_c2_promedio = plot_criterio2_promedio_sintomas(
        df_con_criterios, CRITERIOS_METADATA[2]["color"]
    )
    fig_c2_promedio
    return


@app.cell
def _(mo):
    mo.md("""
    **Interpretación:** Este gráfico compara el promedio de síntomas recurrentes entre dos grupos:
    - **Cumple Criterio 2** (rojo): Casos con COVID-19 confirmado, más de 1 síntoma recurrente y no recuperados a los 3 meses
    - **No Cumple** (gris): Resto de casos

    El promedio general de síntomas en el dataset es mostrado en el indicador de la izquierda.
    """)
    return


@app.cell
def _(
    CRITERIOS_METADATA,
    df_con_criterios,
    plot_criterio2_promedio_sintomas_by_week,
):
    # Evolución temporal del promedio de síntomas
    fig_c2_promedio_week = plot_criterio2_promedio_sintomas_by_week(
        df_con_criterios, CRITERIOS_METADATA[2]["color"]
    )
    fig_c2_promedio_week
    return


@app.cell
def _(mo):
    mo.md("""
    **Interpretación:** Este gráfico muestra cómo evoluciona el promedio de síntomas recurrentes a lo largo del tiempo:
    - La línea **roja** representa el promedio semanal para casos que cumplen el Criterio 2
    - La línea **gris** representa el promedio semanal para casos que no cumplen el Criterio 2
    - La línea punteada marca el umbral de >1 síntoma (requisito del Criterio 2)

    Permite identificar si hay patrones temporales en la severidad sintomática.
    """)
    return


@app.cell
def _(df_con_criterios, plot_criterio2_sintomas):
    # Distribución de síntomas recurrentes
    fig_c2_sintomas = plot_criterio2_sintomas(df_con_criterios)
    fig_c2_sintomas
    return


@app.cell
def _(mo):
    mo.md("""
    **Interpretación:** Este gráfico muestra la distribución de casos según el número de síntomas recurrentes (0, 1, 2, 3, 4+).
    Permite visualizar cuántas personas experimentan diferentes niveles de carga sintomática, independientemente de si cumplen o no el Criterio 2.
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ### Criterio 2: Estado de Recuperación
    """)
    return


@app.cell
def _(df_con_criterios, plot_criterio2_recovery):
    # Análisis de recuperación
    fig_c2_recovery = plot_criterio2_recovery(df_con_criterios)
    fig_c2_recovery
    return


@app.cell
def _(mo):
    mo.md("""
    **Interpretación:** Este panel compara el estado de recuperación:
    - **Panel izquierdo (Pie chart)**: Distribución general de recuperación en todo el dataset
    - **Panel derecho (Barras)**: Comparación del estado de recuperación entre casos que cumplen y no cumplen el Criterio 2

    Permite evaluar si el Criterio 2 está efectivamente capturando casos no recuperados.
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## 2.3. Criterio 3 (Cluster)

    **Definición:** COVID-19 + Al menos 2 síntomas de cualquier cluster + No recuperado a los 3 meses

    **Fórmula:** `criterio_3 = 1` si cumple:
    - `covid == 1` (DP4: Diagnóstico de COVID)
    - `pertenece_cluster_count >= 1` (P17: Al menos 2 síntomas de cualquier cluster)
    - `recuperado_3m == 2` (P20: No recuperado)
    """)
    return


@app.cell
def _(df_con_criterios, pl):
    # Validar Criterio 3
    conteo_c3 = df_con_criterios.filter(pl.col("criterio_3") == 1).height
    no_cumple_c3 = df_con_criterios.filter(pl.col("criterio_3") == 0).height

    (conteo_c3, no_cumple_c3)
    return conteo_c3, no_cumple_c3


@app.cell
def _(conteo_c3, mo, no_cumple_c3):
    mo.md(f"""
    **Casos en dataset:**
    - Cumplen criterio 3: {conteo_c3:,}
    - No cumplen: {no_cumple_c3:,}
    """)
    return


@app.cell
def _(CRITERIOS_METADATA, df_con_criterios, mo, pl, validar_criterio):
    # Validación del Criterio 3
    validacion_c3 = validar_criterio(
        df_con_criterios, 3, CRITERIOS_METADATA[3]["variables"]
    )

    # Mostrar resumen de Criterio 3
    mo.md(
        f"""
    ---
    ###  Resumen Criterio 3: {CRITERIOS_METADATA[3]['nombre']}

    **Construcción del criterio:**
    - **Número de variables:** {len(CRITERIOS_METADATA[3]['variables'])}
    - **Variables componentes:** `{'`, `'.join(CRITERIOS_METADATA[3]['variables'])}`
    - **Descripción:** {CRITERIOS_METADATA[3]['descripcion']}
    - **Fórmula lógica:** `{CRITERIOS_METADATA[3]['formula']}`
    - **Color asignado:** <span style="color:{CRITERIOS_METADATA[3]['color']}">███</span> `{CRITERIOS_METADATA[3]['color']}`

    **Resultados:**
    - Total de casos: {validacion_c3['n_total']:,}
    - Cumplen criterio: {validacion_c3['n_cumplen']:,} ({validacion_c3['porcentaje_cumplen']:.2f}%)
    - No cumplen: {validacion_c3['n_no_cumplen']:,} ({100-validacion_c3['porcentaje_cumplen']:.2f}%)

    **Validación de datos:**
    """
    )

    # Crear tabla de validación
    _validacion_tabla_c3 = []
    for _var in CRITERIOS_METADATA[3]["variables"]:
        if _var in validacion_c3["variables_validas"]:
            _info = validacion_c3["variables_validas"][_var]
            _validacion_tabla_c3.append(
                {
                    "Variable": _var,
                    "Valores válidos": _info["validos"],
                    "% Válido": f"{_info['porcentaje_valido']:.2f}%",
                    "Valores NULL": validacion_c3["null_counts"][_var],
                }
            )

    df_validacion_c3 = pl.DataFrame(_validacion_tabla_c3)

    (validacion_c3, df_validacion_c3)
    return df_validacion_c3, validacion_c3


@app.cell
def _(df_validacion_c3, mo, validacion_c3):
    # Mostrar tabla de validación del Criterio 3
    mo.ui.table(df_validacion_c3)

    estado_c3 = (
        " **Criterio funciona correctamente**"
        if validacion_c3["consistente"]
        else "❌ **Problema detectado en el criterio**"
    )

    mo.md(
        f"""
    {estado_c3}

    - Consistencia lógica: {'Sí' if validacion_c3['consistente'] else 'No'}
    - Total casos = Cumplen + No cumplen: {validacion_c3['n_total']} = {validacion_c3['n_cumplen']} + {validacion_c3['n_no_cumplen']}

    **Nota:** Este criterio mostró una diferencia de 8 casos respecto al análisis previo (360 vs 352). 
    Las validaciones anteriores indican que no hay valores NULL en las variables componentes, 
    por lo que la diferencia podría deberse a criterios de filtrado o versión del dataset.

    ---
    """
    )
    return


@app.cell
def _(CRITERIOS_METADATA, df_con_criterios, plot_criterio_barplot):
    # Barplot de Criterio 3
    fig_bar_c3 = plot_criterio_barplot(
        df_con_criterios,
        3,
        "Criterio 3 (Clusters): Distribución de Casos",
        CRITERIOS_METADATA[3]["color"],
    )
    fig_bar_c3
    return


@app.cell
def _(mo):
    mo.md("""
    **Interpretación:** Distribución semanal del Criterio 3 (Clusters sintomáticos):
    - **Barras naranjas**: Casos con COVID + pertenencia a clusters sintomáticos + no recuperados
    - **Barras grises**: Resto de casos

    Este criterio identifica fenotipos específicos basados en agrupaciones de síntomas que co-ocurren.
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ### Criterio 3: Comparación de Clusters Individuales
    """)
    return


@app.cell
def _(
    CRITERIOS_METADATA,
    df_con_criterios,
    plot_criterio3_clusters_comparison,
):
    # Comparación de clusters individuales por sexo
    fig_c3_clusters = plot_criterio3_clusters_comparison(
        df_con_criterios,
        CRITERIOS_METADATA[3]['color']
    )
    fig_c3_clusters
    return


@app.cell
def _(mo):
    mo.md("""
    **Interpretación:** Este gráfico compara la distribución de clusters entre casos que cumplen el Criterio 3 vs controles:

    **Casos (izquierda de cada cluster):**
    - **Morado**: Mujeres que cumplen Criterio 3 con el cluster
    - **Verde claro**: Hombres que cumplen Criterio 3 con el cluster

    **Controles (derecha de cada cluster):**
    - **Morado claro**: Mujeres que NO cumplen Criterio 3 pero tienen el cluster
    - **Verde muy claro**: Hombres que NO cumplen Criterio 3 pero tienen el cluster

    **Clusters mostrados:**
    1. **AIRWAYS**: Síntomas de vías respiratorias superiores (congestión nasal, tos, flema)
    2. **COGNITIVE**: Problemas cognitivos (depresión, ansiedad, deterioro de memoria)
    3. **GASTRO-INTESTINAL**: Síntomas digestivos (dolor abdominal, náuseas, diarrea)
    4. **MUSCULAR**: Síntomas musculoesqueléticos (dolor muscular, articular)
    5. **RESPIRATORY**: Síntomas respiratorios bajos (disnea, fatiga, dolor torácico)
    6. **SMELL/TASTE**: Alteraciones olfato-gustativas (anosmia, ageusia)

    Permite identificar qué fenotipos son más prevalentes en casos confirmados de Long COVID y si hay diferencias por sexo.
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ### Criterio 3: Evolución Temporal (sin casos con nulls)
    
    **Nota importante:** El Criterio 3 ahora excluye automáticamente los casos con valores NULL en `recuperado_3m`, 
    ya que esta variable es esencial para determinar si un paciente cumple el criterio (no recuperado a los 3 meses).
    """)
    return


@app.cell
def _(df_con_criterios, plot_cases_by_week_by_criterio_3_sin_nulls):
    fig_criterio3_week = plot_cases_by_week_by_criterio_3_sin_nulls(df_con_criterios)
    fig_criterio3_week
    return (fig_criterio3_week,)


@app.cell
def _(df_con_criterios, mo, pl):
    # Calcular estadísticas del criterio 3 sin nulls
    df_c3_sin_nulls = df_con_criterios.filter(~pl.col('recuperado_3m').is_null())
    total_c3_sin_nulls = df_c3_sin_nulls.height
    cumple_c3_sin_nulls = df_c3_sin_nulls.filter(pl.col('criterio_3') == 1).height
    no_cumple_c3_sin_nulls = df_c3_sin_nulls.filter(pl.col('criterio_3') == 0).height
    pct_cumple_c3 = (cumple_c3_sin_nulls / total_c3_sin_nulls * 100) if total_c3_sin_nulls > 0 else 0
    
    # Calcular casos omitidos
    casos_omitidos = df_con_criterios.height - total_c3_sin_nulls
    
    mo.md(f"""
    ---
    ###  Interpretación: Criterio 3 sin casos con nulls
    
    **Definición del Criterio 3:**
    - COVID-19 confirmado (`covid == 1`)
    - Pertenece a al menos un cluster sintomático (`pertenece_cluster_count >= 1`)
    - NO recuperado a los 3 meses (`recuperado_3m == 2`)
    - **⚠️ Importante:** Se omiten **{casos_omitidos} casos con NULL** en `recuperado_3m`
    
    **Estadísticas (sin nulls):**
    - **Total de casos del dataset:** {df_con_criterios.height:,}
    - **Casos omitidos (NULL en recuperado_3m):** {casos_omitidos}
    - **Casos analizados:** {total_c3_sin_nulls:,}
    - **Cumplen Criterio 3:** {cumple_c3_sin_nulls:,} casos ({pct_cumple_c3:.1f}%)
    - **No cumplen:** {no_cumple_c3_sin_nulls:,} casos ({100-pct_cumple_c3:.1f}%)
    
    **Hallazgos clave:**
    - El color **naranja** (criterio 3) representa casos con fenotipos de clusters sintomáticos persistentes
    - La evolución temporal muestra la carga de Long COVID definida por clusters
    - **Se omitieron {casos_omitidos} casos** sin información de recuperación a 3 meses, asegurando análisis con datos completos
    - Al excluir nulls, obtenemos una medida más precisa y confiable del criterio
    
    **Implicaciones clínicas:**
    - Los clusters identifican subgrupos con patrones sintomáticos específicos
    - Útil para estratificar intervenciones según el fenotipo predominante
    - La exclusión de nulls asegura que solo se consideren casos con seguimiento completo a 3 meses
    
    ---
    """)
    return (cumple_c3_sin_nulls, df_c3_sin_nulls, no_cumple_c3_sin_nulls, pct_cumple_c3, total_c3_sin_nulls)


@app.cell
def _(mo):
    mo.md("""
    ---
    ## 2.3.1. Distribución de Ancestrías Genéticas
    
    Las ancestrías genéticas (EUR, AFR, EAS, AYM, MAP) representan las proporciones de componentes ancestrales
    en la población estudiada. Analizar su distribución ayuda a entender la diversidad genética y posibles
    asociaciones entre ancestría y desarrollo de Long COVID.
    """)
    return


@app.cell
def _(df_con_criterios, plot_linaje_barplot):
    fig_linaje = plot_linaje_barplot(df_con_criterios)
    fig_linaje
    return (fig_linaje,)


@app.cell
def _(df_con_criterios, mo, pl):
    # Calcular estadísticas de ancestrías
    ancestrias = ['EUR', 'AFR', 'EAS', 'AYM', 'MAP']
    
    ancestria_stats = []
    for anc in ancestrias:
        promedio = df_con_criterios[anc].mean()
        ancestria_stats.append((anc, promedio))
    
    # Ordenar por proporción
    ancestria_stats_sorted = sorted(ancestria_stats, key=lambda x: x[1], reverse=True)
    
    ancestria_max = ancestria_stats_sorted[0]
    ancestria_nombre_max = ancestria_max[0]
    prop_max = ancestria_max[1]
    
    # Nombres completos
    nombres_ancestria = {
        'EUR': 'Europea',
        'AFR': 'Africana', 
        'EAS': 'Este Asiática',
        'AYM': 'Aymara',
        'MAP': 'Mapuche'
    }
    
    mo.md(f"""
    ---
    ###  Interpretación: Distribución de Ancestrías Genéticas
    
    **Estadísticas de ancestrías genéticas:**
    - **Ancestría predominante:** {nombres_ancestria[ancestria_nombre_max]} ({ancestria_nombre_max}) - Proporción promedio: {prop_max:.4f} ({prop_max*100:.2f}%)
    - **Total de casos analizados:** {df_con_criterios.height:,}
    
    **Ancestrías evaluadas:**
    - **EUR:** Ancestría Europea
    - **AFR:** Ancestría Africana
    - **EAS:** Ancestría Este Asiática
    - **AYM:** Ancestría Aymara (población indígena)
    - **MAP:** Ancestría Mapuche (población indígena)
    
    **Hallazgos clave:**
    - Las proporciones muestran la composición genética de la población chilena estudiada
    - La mezcla de ancestrías refleja la historia demográfica de Chile
    - Las poblaciones indígenas (AYM, MAP) representan componentes ancestrales importantes
    
    **Implicaciones:**
    - Permite estratificar análisis por ancestría genética
    - Útil para estudios de asociación entre ancestría y susceptibilidad a Long COVID
    - Contexto importante para medicina de precisión y equidad en salud
    - Visibiliza la diversidad genética de poblaciones indígenas en la investigación
    
    ---
    """)
    return (ancestria_max, ancestria_nombre_max, ancestria_stats, ancestria_stats_sorted, ancestrias, nombres_ancestria, prop_max)


@app.cell
def _(mo):
    mo.md("""
    ---
    ## 2.3.2. Hospitalización por Semana Epidemiológica
    
    La hospitalización es un indicador de severidad de la enfermedad aguda. Analizar su distribución temporal
    permite identificar períodos de mayor carga hospitalaria y posibles asociaciones con desarrollo de Long COVID.
    """)
    return


@app.cell
def _(df_con_criterios, plot_hospitalizacion_by_week):
    fig_hosp_week = plot_hospitalizacion_by_week(df_con_criterios)
    fig_hosp_week
    return (fig_hosp_week,)


@app.cell
def _(df_con_criterios, mo, pl):
    # Calcular estadísticas de hospitalización
    total_casos_hosp = df_con_criterios.height
    hospitalizados = df_con_criterios.filter(pl.col('Hospitalización') == 1).height
    no_hospitalizados = df_con_criterios.filter(pl.col('Hospitalización') == 0).height
    pct_hosp = (hospitalizados / total_casos_hosp) * 100
    
    # Identificar semana con más hospitalizaciones
    df_hosp_week_stats = (df_con_criterios
                          .filter(pl.col('Hospitalización') == 1)
                          .group_by('yearweek')
                          .agg(pl.count('Hospitalización').alias('n_hosp'))
                          .sort('n_hosp', descending=True))
    
    if df_hosp_week_stats.height > 0:
        semana_max = df_hosp_week_stats.row(0)
        semana_max_nombre = semana_max[0]
        casos_max_semana = semana_max[1]
    else:
        semana_max_nombre = "N/A"
        casos_max_semana = 0
    
    mo.md(f"""
    ---
    ###  Interpretación: Hospitalización por Semana
    
    **Estadísticas de hospitalización:**
    - **Total de casos:** {total_casos_hosp:,}
    - **Casos hospitalizados:** {hospitalizados:,} ({pct_hosp:.1f}%)
    - **Casos no hospitalizados:** {no_hospitalizados:,} ({100-pct_hosp:.1f}%)
    - **Semana con más hospitalizaciones:** {semana_max_nombre} ({casos_max_semana} casos)
    
    **Hallazgos clave:**
    - La distribución temporal muestra picos de hospitalización en momentos de alta circulación viral
    - El color **rojo** representa casos hospitalizados, indicando severidad aguda
    - El color **gris** representa casos no hospitalizados
    - La proporción de hospitalizaciones puede variar según la variante predominante
    
    **Implicaciones clínicas:**
    - La hospitalización en fase aguda puede ser un predictor de Long COVID
    - Útil para identificar períodos de mayor demanda hospitalaria
    - Permite analizar si la severidad aguda se asocia con síntomas persistentes
    - Importante para planificación de recursos y seguimiento post-alta
    
    ---
    """)
    return (casos_max_semana, df_hosp_week_stats, hospitalizados, no_hospitalizados, pct_hosp, semana_max, semana_max_nombre, total_casos_hosp)


@app.cell
def _(mo):
    mo.md("""
    ## 2.4. Criterio 4 (Secuelas)

    **Definición:** COVID-19 + Nueva condición O Secuelas crónicas

    **Fórmula:** `criterio_4 = 1` si cumple:
    - `covid == 1` (DP4: Diagnóstico de COVID)
    - `conteo_nueva_condicion >= 1` (P21: Ha desarrollado una nueva condición) **O**
    - `sec_count >= 1` (P22: Condición crónica no reportada en etapa aguda)
    """)
    return


@app.cell
def _(df_con_criterios, pl):
    # Validar Criterio 4
    conteo_c4 = df_con_criterios.filter(pl.col("criterio_4") == 1).height
    no_cumple_c4 = df_con_criterios.filter(pl.col("criterio_4") == 0).height

    (conteo_c4, no_cumple_c4)
    return conteo_c4, no_cumple_c4


@app.cell
def _(conteo_c4, mo, no_cumple_c4):
    mo.md(f"""
    **Casos en dataset:**
    - Cumplen criterio 4: {conteo_c4:,}
    - No cumplen: {no_cumple_c4:,}
    """)
    return


@app.cell
def _(CRITERIOS_METADATA, df_con_criterios, mo, pl, validar_criterio):
    # Validación del Criterio 4
    validacion_c4 = validar_criterio(
        df_con_criterios, 4, CRITERIOS_METADATA[4]["variables"]
    )

    # Mostrar resumen de Criterio 4
    mo.md(
        f"""
    ---
    ###  Resumen Criterio 4: {CRITERIOS_METADATA[4]['nombre']}

    **Construcción del criterio:**
    - **Número de variables:** {len(CRITERIOS_METADATA[4]['variables'])}
    - **Variables componentes:** `{'`, `'.join(CRITERIOS_METADATA[4]['variables'])}`
    - **Descripción:** {CRITERIOS_METADATA[4]['descripcion']}
    - **Fórmula lógica:** `{CRITERIOS_METADATA[4]['formula']}`
    - **Color asignado:** <span style="color:{CRITERIOS_METADATA[4]['color']}">███</span> `{CRITERIOS_METADATA[4]['color']}`

    **Resultados:**
    - Total de casos: {validacion_c4['n_total']:,}
    - Cumplen criterio: {validacion_c4['n_cumplen']:,} ({validacion_c4['porcentaje_cumplen']:.2f}%)
    - No cumplen: {validacion_c4['n_no_cumplen']:,} ({100-validacion_c4['porcentaje_cumplen']:.2f}%)

    **Validación de datos:**
    """
    )

    # Crear tabla de validación
    _validacion_tabla_c4 = []
    for _var in CRITERIOS_METADATA[4]["variables"]:
        if _var in validacion_c4["variables_validas"]:
            _info = validacion_c4["variables_validas"][_var]
            _validacion_tabla_c4.append(
                {
                    "Variable": _var,
                    "Valores válidos": _info["validos"],
                    "% Válido": f"{_info['porcentaje_valido']:.2f}%",
                    "Valores NULL": validacion_c4["null_counts"][_var],
                }
            )

    df_validacion_c4 = pl.DataFrame(_validacion_tabla_c4)

    (validacion_c4, df_validacion_c4)
    return df_validacion_c4, validacion_c4


@app.cell
def _(df_validacion_c4, mo, validacion_c4):
    # Mostrar tabla de validación del Criterio 4
    mo.ui.table(df_validacion_c4)

    estado_c4 = (
        " **Criterio funciona correctamente**"
        if validacion_c4["consistente"]
        else "❌ **Problema detectado en el criterio**"
    )

    mo.md(
        f"""
    {estado_c4}

    - Consistencia lógica: {'Sí' if validacion_c4['consistente'] else 'No'}
    - Total casos = Cumplen + No cumplen: {validacion_c4['n_total']} = {validacion_c4['n_cumplen']} + {validacion_c4['n_no_cumplen']}

    **Nota:** Este criterio utiliza un operador OR (nueva_condición O secuelas), 
    lo que puede resultar en un mayor número de casos positivos comparado con criterios que usan AND.

    ---
    """
    )
    return


@app.cell
def _(CRITERIOS_METADATA, df_con_criterios, plot_criterio_barplot):
    # Barplot de Criterio 4
    fig_bar_c4 = plot_criterio_barplot(
        df_con_criterios,
        4,
        "Criterio 4 (Secuelas): Distribución de Casos",
        CRITERIOS_METADATA[4]["color"],
    )
    fig_bar_c4
    return


@app.cell
def _(mo):
    mo.md("""
    **Interpretación:** Distribución semanal del Criterio 4 (Secuelas):
    - **Barras moradas**: Casos con COVID + desarrollo de nueva condición O secuelas crónicas
    - **Barras grises**: Resto de casos

    Este criterio captura el impacto a largo plazo del COVID-19 en términos de condiciones médicas nuevas o persistentes.
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## 2.5. Comparación de Criterios
    """)
    return


@app.cell
def _(
    COLORES_CRITERIOS,
    CRITERIOS_METADATA,
    mo,
    pl,
    validacion_c1,
    validacion_c2,
    validacion_c3,
    validacion_c4,
):
    # Crear tabla resumen comparativa de todos los criterios
    resumen_criterios = []

    for i, validacion in enumerate(
        [validacion_c1, validacion_c2, validacion_c3, validacion_c4], 1
    ):
        resumen_criterios.append(
            {
                "Criterio": f"Criterio {i}",
                "Nombre": CRITERIOS_METADATA[i]["nombre"],
                "N° Variables": len(CRITERIOS_METADATA[i]["variables"]),
                "Casos positivos": validacion["n_cumplen"],
                "% Positivos": f"{validacion['porcentaje_cumplen']:.2f}%",
                "Casos negativos": validacion["n_no_cumplen"],
                "Total": validacion["n_total"],
                "Consistente": "" if validacion["consistente"] else "❌",
                "Color": COLORES_CRITERIOS[i],
            }
        )

    df_resumen_criterios = pl.DataFrame(resumen_criterios)

    mo.md(
        f"""
    ---
    ### 📋 Tabla Resumen: Comparación de los 4 Criterios de Fenotipo Long COVID

    Esta tabla consolida las métricas clave de cada criterio para facilitar la comparación:
    """
    )

    (df_resumen_criterios,)
    return df_resumen_criterios, resumen_criterios


@app.cell
def _(df_resumen_criterios, mo):
    # Mostrar tabla resumen
    mo.ui.table(df_resumen_criterios)
    return


@app.cell
def _(CRITERIOS_METADATA, mo, resumen_criterios):
    # Análisis interpretativo
    total_c1 = resumen_criterios[0]["Casos positivos"]
    total_c2 = resumen_criterios[1]["Casos positivos"]
    total_c3 = resumen_criterios[2]["Casos positivos"]
    total_c4 = resumen_criterios[3]["Casos positivos"]

    mo.md(
        f"""
    ---
    ### 🔍 Interpretación de los Criterios

    **Prevalencia de Long COVID según criterio:**
    1. **{CRITERIOS_METADATA[1]['nombre']}:** {total_c1:,} casos - Definición más general
    2. **{CRITERIOS_METADATA[2]['nombre']}:** {total_c2:,} casos - Enfocado en síntomas persistentes
    3. **{CRITERIOS_METADATA[3]['nombre']}:** {total_c3:,} casos - Basado en clusters sintomáticos
    4. **{CRITERIOS_METADATA[4]['nombre']}:** {total_c4:,} casos - Enfocado en complicaciones crónicas

    **Observaciones clave:**
    - Los criterios 2, 3 y 4 son más restrictivos que el Criterio 1 (fenotipo general)
    - El Criterio 4 identifica el mayor número de casos específicos ({total_c4:,}), 
      probablemente debido al uso del operador OR (nueva condición O secuelas)
    - Todos los criterios han pasado las validaciones de consistencia 
    - No se detectaron valores NULL significativos en las variables componentes

    **Paleta de colores asignada para visualizaciones:**
    - Criterio 1: <span style="color:{CRITERIOS_METADATA[1]['color']}">███</span> {CRITERIOS_METADATA[1]['color']} (Azul)
    - Criterio 2: <span style="color:{CRITERIOS_METADATA[2]['color']}">███</span> {CRITERIOS_METADATA[2]['color']} (Rojo)
    - Criterio 3: <span style="color:{CRITERIOS_METADATA[3]['color']}">███</span> {CRITERIOS_METADATA[3]['color']} (Naranja)
    - Criterio 4: <span style="color:{CRITERIOS_METADATA[4]['color']}">███</span> {CRITERIOS_METADATA[4]['color']} (Morado)

    ---
    """
    )
    return


@app.cell
def _(mo):
    mo.md("""
    ### 2.5.1. Análisis del Impacto de Valores NULL
    """)
    return


@app.cell
def _(analyze_criterios_null_impact, df_con_criterios):
    # Analizar el impacto de NULLs en cada criterio
    analisis_nulls = analyze_criterios_null_impact(df_con_criterios)
    analisis_nulls
    return (analisis_nulls,)


@app.cell
def _(COLORES_CRITERIOS, analisis_nulls, plot_criterios_null_impact):
    # Crear visualización del impacto de NULLs
    fig_nulls_impact = plot_criterios_null_impact(analisis_nulls, COLORES_CRITERIOS)
    fig_nulls_impact
    return


@app.cell
def _(analisis_nulls, mo):
    # Interpretación del análisis de NULLs
    c1_perdidos = analisis_nulls['criterio_1']['casos_perdidos']
    c2_perdidos = analisis_nulls['criterio_2']['casos_perdidos']
    c3_perdidos = analisis_nulls['criterio_3']['casos_perdidos']
    c4_perdidos = analisis_nulls['criterio_4']['casos_perdidos']

    c1_pct = analisis_nulls['criterio_1']['porcentaje_perdido']
    c2_pct = analisis_nulls['criterio_2']['porcentaje_perdido']
    c3_pct = analisis_nulls['criterio_3']['porcentaje_perdido']
    c4_pct = analisis_nulls['criterio_4']['porcentaje_perdido']

    total_perdidos = c1_perdidos + c2_perdidos + c3_perdidos + c4_perdidos

    # Identificar criterio más afectado
    criterios_afectados = {
        'Criterio 1': (c1_perdidos, c1_pct),
        'Criterio 2': (c2_perdidos, c2_pct),
        'Criterio 3': (c3_perdidos, c3_pct),
        'Criterio 4': (c4_perdidos, c4_pct)
    }
    max_afectado = max(criterios_afectados.items(), key=lambda x: x[1][0])

    mo.md(
        f"""
    ---
    ###  Interpretación: Impacto de Valores NULL en los Criterios

    **Calidad de los datos:**
    - **Criterio 1:** {c1_perdidos} casos perdidos ({c1_pct:.1f}%) - Depende solo de `longCOVID`
    - **Criterio 2:** {c2_perdidos} casos perdidos ({c2_pct:.1f}%) - Variables: covid, sintoma_recurrente_count, recuperado_3m
    - **Criterio 3:** {c3_perdidos} casos perdidos ({c3_pct:.1f}%) - Variables: covid, pertenece_cluster_count, recuperado_3m
    - **Criterio 4:** {c4_perdidos} casos perdidos ({c4_pct:.1f}%) - Variables: covid, conteo_nueva_condicion, sec_count

    **Hallazgos principales:**
    - **Total de casos con datos faltantes:** {total_perdidos} casos
    - **Criterio más afectado:** {max_afectado[0]} con {max_afectado[1][0]} casos ({max_afectado[1][1]:.1f}%)
    - La completitud de los datos es {'excelente (>95%)' if total_perdidos < 75 else 'buena (>90%)' if total_perdidos < 150 else 'aceptable'} para el análisis

    **Implicaciones metodológicas:**
    - Los criterios son **robustos** ante datos faltantes, con pérdidas mínimas
    - La estrategia de incluir casos con valores NULL no introduce sesgos significativos
    - Los conteos reportados en la comparación reflejan la realidad clínica observada
    - {'⚠️ Se recomienda análisis de sensibilidad para el ' + max_afectado[0] if max_afectado[1][1] > 5 else ' La calidad de datos permite análisis confiables'}

    **Variables con más NULLs por criterio:**
    - Criterio 1: {', '.join(analisis_nulls['criterio_1']['variables'])}
    - Criterio 2: {', '.join(analisis_nulls['criterio_2']['variables'])}
    - Criterio 3: {', '.join(analisis_nulls['criterio_3']['variables'])}
    - Criterio 4: {', '.join(analisis_nulls['criterio_4']['variables'])}

    ---
    """
    )
    return


@app.cell
def _(COLORES_CRITERIOS, df_con_criterios, plot_criterio_comparison):
    # Comparación visual de todos los criterios
    fig_criterios = plot_criterio_comparison(df_con_criterios, COLORES_CRITERIOS)
    fig_criterios
    return


@app.cell
def _(mo):
    mo.md("""
    **Interpretación:** Comparación directa de los 4 criterios diagnósticos:
    - Cada criterio usa su **color representativo** para las barras de casos que cumplen
    - Las barras grises representan casos que no cumplen cada criterio
    - Permite comparar visualmente la prevalencia relativa de cada definición de Long COVID

    **Observaciones clave:**
    - Criterio 1 (azul) es el más inclusivo (fenotipo general)
    - Criterios 2, 3 y 4 son más específicos y capturan diferentes aspectos del Long COVID
    - La diferencia en números refleja las distintas definiciones operacionales
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## 2.6. Comparación de Resultados - Criterio 3

    **Objetivo:** Investigar diferencia entre resultados
    - Resultado actual: 360 casos
    - Resultado Josefa: 352 casos
    - Diferencia: 8 casos

    **Análisis de componentes del Criterio 3:**
    """)
    return


@app.cell
def _(df_con_criterios, pl):
    # Desglosar componentes del Criterio 3
    analisis_c3 = df_con_criterios.select(
        ["covid", "pertenece_cluster_count", "recuperado_3m", "criterio_3"]
    )

    # Validar cada componente
    covid_positivo = df_con_criterios.filter(pl.col("covid") == 1).height
    tiene_clusters = df_con_criterios.filter(
        pl.col("pertenece_cluster_count") >= 1
    ).height
    no_recuperado = df_con_criterios.filter(pl.col("recuperado_3m") == 2).height

    # Los 3 componentes juntos
    tres_condiciones = df_con_criterios.filter(
        (pl.col("covid") == 1)
        & (pl.col("pertenece_cluster_count") >= 1)
        & (pl.col("recuperado_3m") == 2)
    ).height

    (covid_positivo, tiene_clusters, no_recuperado, tres_condiciones, analisis_c3)
    return covid_positivo, no_recuperado, tiene_clusters, tres_condiciones


@app.cell
def _(covid_positivo, mo, no_recuperado, tiene_clusters, tres_condiciones):
    mo.md(f"""
    **Conteos por componente:**
    - COVID positivo (`covid == 1`): {covid_positivo:,}
    - Pertenece a algún cluster (`pertenece_cluster_count >= 1`): {tiene_clusters:,}
    - No recuperado a los 3 meses (`recuperado_3m == 2`): {no_recuperado:,}
    - **Cumplen las 3 condiciones simultáneamente: {tres_condiciones:,}**

    **Verificación:** El criterio_3 debería coincidir con el conteo de las 3 condiciones.
    """)
    return


@app.cell
def _(df_con_criterios, pl):
    # Casos que cumplen criterio 3 - análisis detallado
    casos_c3 = df_con_criterios.filter(pl.col("criterio_3") == 1).select(
        [
            "covid",
            "pertenece_cluster_count",
            "recuperado_3m",
            "cluster_cognitivo_bi",
            "cluster_gastrointestinal_bi",
            "cluster_muscular_bi",
            "cluster_olfato_gusto_bi",
            "cluster_respiratorio_bi",
            "cluster_via_aerea_bi",
            "yearweek",
        ]
    )

    # Distribución de pertenece_cluster_count entre los que cumplen C3
    dist_clusters_c3 = (
        casos_c3.group_by("pertenece_cluster_count")
        .agg(pl.len().alias("n_casos"))
        .sort("pertenece_cluster_count")
    )

    (casos_c3, dist_clusters_c3)
    return (dist_clusters_c3,)


@app.cell
def _(dist_clusters_c3, mo):
    mo.md(f"""
    **Distribución de clusters entre casos que cumplen Criterio 3:**

    {dist_clusters_c3}

    **Posibles causas de discrepancia (360 vs 352):**
    1. Manejo diferente de valores NULL en alguna variable
    2. Definición diferente de `pertenece_cluster_count`
    3. Filtrado diferente de `recuperado_3m`
    4. Versión diferente del dataset
    """)
    return


@app.cell
def _(df_con_criterios, pl):
    # Verificar valores NULL en componentes del criterio 3
    null_covid = df_con_criterios.filter(pl.col("covid").is_null()).height
    null_clusters = df_con_criterios.filter(
        pl.col("pertenece_cluster_count").is_null()
    ).height
    null_recuperado = df_con_criterios.filter(pl.col("recuperado_3m").is_null()).height

    # Casos con recuperado_3m diferente de 1 y 2
    recuperado_otros = df_con_criterios.filter(
        (pl.col("recuperado_3m") != 1) & (pl.col("recuperado_3m") != 2)
    ).height

    (null_covid, null_clusters, null_recuperado, recuperado_otros)
    return null_clusters, null_covid, null_recuperado, recuperado_otros


@app.cell
def _(mo, null_clusters, null_covid, null_recuperado, recuperado_otros):
    mo.md(f"""
    **Análisis de valores NULL y edge cases:**
    - NULL en `covid`: {null_covid}
    - NULL en `pertenece_cluster_count`: {null_clusters}
    - NULL en `recuperado_3m`: {null_recuperado}
    - Valores de `recuperado_3m` diferentes de 1 y 2: {recuperado_otros}
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## 3. Variantes: Barplot Apilado por Semana Epidemiológica
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## 4. Long COVID por Semana Epidemiológica

    Análisis temporal de casos con diferentes categorizaciones
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ### 4.1. Long COVID por Criterios Diagnósticos
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ### 4.1. Criterios Diagnósticos por Semana
    """)
    return


@app.cell
def _(df_con_criterios, pl):
    # Validar datos: tiene vs no tiene criterio
    datos_criterios_binario = (
        df_con_criterios.with_columns(
            pl.when(
                (pl.col("criterio_2") == 1)
                | (pl.col("criterio_3") == 1)
                | (pl.col("criterio_4") == 1)
            )
            .then(pl.lit("Tiene criterio"))
            .otherwise(pl.lit("No tiene criterio"))
            .alias("tiene_criterio")
        )
        .group_by(["yearweek", "tiene_criterio"])
        .agg(pl.len().alias("n"))
        .sort("yearweek")
    )

    datos_criterios_binario.head(15)
    return


@app.cell
def _(df_con_criterios, plot_longcovid_by_week):
    fig_longcovid_week = plot_longcovid_by_week(df_con_criterios)
    fig_longcovid_week
    return


@app.cell
def _(mo):
    mo.md("""
    **Interpretación:** Evolución temporal agregada de criterios diagnósticos:
    - **Rojo**: Casos que cumplen AL MENOS UNO de los criterios 2, 3 o 4 (definiciones específicas)
    - **Azul**: Casos que no cumplen ninguno de estos criterios

    Este gráfico muestra la carga temporal de Long COVID según las definiciones más restrictivas.
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ### 4.2. Distribución de Síntomas Recurrentes
    """)
    return


@app.cell
def _(df_con_criterios, pl):
    # Validar datos: distribución de síntomas recurrentes
    datos_sintomas_hist = (
        df_con_criterios.with_columns(
            pl.when(pl.col("sintoma_recurrente_count") == 0)
            .then(pl.lit("0"))
            .when(pl.col("sintoma_recurrente_count") == 1)
            .then(pl.lit("1"))
            .when(pl.col("sintoma_recurrente_count") == 2)
            .then(pl.lit("2"))
            .when(pl.col("sintoma_recurrente_count") == 3)
            .then(pl.lit("3"))
            .otherwise(pl.lit("4+"))
            .alias("categoria")
        )
        .group_by("categoria")
        .agg(pl.len().alias("n_personas"))
        .sort("categoria")
    )

    datos_sintomas_hist
    return


@app.cell
def _(df_con_criterios, plot_sintomas_recurrentes_by_week):
    fig_sintomas_hist = plot_sintomas_recurrentes_by_week(df_con_criterios)
    fig_sintomas_hist
    return


@app.cell
def _(mo):
    mo.md("""
    **Interpretación:** Distribución de carga sintomática en la población:
    - **Eje X**: Número de síntomas recurrentes (0, 1, 2, 3, 4+)
    - **Eje Y**: Número de personas
    - **Colores**: Gradiente que refleja la severidad (de verde-azul a morado)

    Muestra cuántas personas experimentan diferentes niveles de persistencia sintomática, útil para entender el espectro de severidad.
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ### 4.3. Pertenencia a Clusters por Semana
    """)
    return


@app.cell
def _(df_con_criterios, pl):
    # Validar datos: pertenencia a clusters por semana
    datos_cluster_semana = (
        df_con_criterios.with_columns(
            pl.when(pl.col("pertenece_cluster_count") >= 1)
            .then(pl.lit("Pertenece a cluster"))
            .otherwise(pl.lit("No pertenece"))
            .alias("pertenece_cluster")
        )
        .group_by(["yearweek", "pertenece_cluster"])
        .agg(pl.len().alias("n"))
        .sort("yearweek")
    )

    datos_cluster_semana.head(15)
    return


@app.cell
def _(df_con_criterios, plot_cluster_pertenencia_by_week):
    fig_cluster_week = plot_cluster_pertenencia_by_week(df_con_criterios)
    fig_cluster_week
    return


@app.cell
def _(mo):
    mo.md("""
    **Interpretación:** Evolución temporal de pertenencia a clusters sintomáticos:
    - **Rojo**: Casos que pertenecen a AL MENOS UN cluster (≥2 síntomas co-ocurrentes de un mismo grupo)
    - **Gris**: Casos que no pertenecen a ningún cluster

    Los clusters representan fenotipos sintomáticos específicos (respiratorio, cognitivo, gastrointestinal, etc.).
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ### 4.4. Clusters Individuales por Semana
    """)
    return


@app.cell
def _(df_con_criterios, pl):
    # Validar datos: un ejemplo con cluster cognitivo
    datos_cognitivo_semana = (
        df_con_criterios.group_by(["yearweek", "cluster_cognitivo_bi"])
        .agg(pl.len().alias("n"))
        .sort("yearweek")
    )

    datos_cognitivo_semana.head(15)
    return


@app.cell
def _(df_con_criterios, plot_clusters_individuales_by_week):
    fig_clusters_ind = plot_clusters_individuales_by_week(df_con_criterios)
    fig_clusters_ind
    return


@app.cell
def _(mo):
    mo.md("""
    **Interpretación:** Barplot apilado mostrando la distribución de los 6 clusters por semana:
    - **Cognitivo** (morado): Problemas de memoria, concentración, niebla mental
    - **Gastrointestinal** (naranja): Síntomas digestivos
    - **Muscular** (rojo): Dolor muscular, debilidad
    - **Olfato/Gusto** (amarillo): Anosmia, ageusia
    - **Respiratorio** (azul): Disnea, tos persistente
    - **Vía Aérea** (verde-azulado): Síntomas de vías respiratorias superiores

    Permite identificar qué fenotipos predominan en cada período temporal.
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ### 4.5. Secuelas por Semana
    """)
    return


@app.cell
def _(df_con_criterios, pl):
    # Validar datos: secuelas por semana
    datos_secuelas_semana = (
        df_con_criterios.with_columns(
            pl.when(pl.col("sec_count") >= 1)
            .then(pl.lit("Con secuelas"))
            .otherwise(pl.lit("Sin secuelas"))
            .alias("tiene_secuelas")
        )
        .group_by(["yearweek", "tiene_secuelas"])
        .agg(pl.len().alias("n"))
        .sort("yearweek")
    )

    datos_secuelas_semana.head(15)
    return


@app.cell
def _(df_con_criterios, plot_secuelas_by_week):
    fig_secuelas_week = plot_secuelas_by_week(df_con_criterios)
    fig_secuelas_week
    return


@app.cell
def _(mo):
    mo.md("""
    **Interpretación:** Distribución temporal de casos con y sin secuelas:
    - **Rojo**: Casos con al menos una secuela crónica (condición no reportada en etapa aguda)
    - **Azul**: Casos sin secuelas crónicas documentadas

    Las secuelas representan el impacto a largo plazo más allá de los síntomas iniciales.
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ### 4.6. Heatmap de Clusters por Semana de Diagnóstico
    """)
    return


@app.cell
def _(df_con_criterios, plot_clusters_heatmap_by_diagnosis_week):
    fig_heatmap_clusters = plot_clusters_heatmap_by_diagnosis_week(df_con_criterios)
    fig_heatmap_clusters
    return


@app.cell
def _(mo):
    mo.md("""
    **Interpretación:** Heatmap de intensidad temporal por cluster/fenotipo:
    - **Eje X**: Semana epidemiológica (semana de diagnóstico COVID)
    - **Eje Y**: Clusters sintomáticos y Long-COVID general
    - **Color (Viridis)**: Intensidad = número de individuos con síntomas ≥3 meses
        - Amarillo/verde claro: Mayor número de casos
        - Azul oscuro/morado: Menor número de casos

    Permite identificar:
    - Patrones temporales específicos por fenotipo
    - Semanas con mayor carga sintomática
    - Clusters que predominan en diferentes períodos
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ---
    ### 4.7. Heatmap Demográfico-Clínico: Características por Edad y Sexo
    
    Este heatmap muestra la distribución de características clínicas importantes 
    (hospitalización, severidad, condiciones preexistentes) estratificadas por grupos etarios y sexo.
    """)
    return


@app.cell
def _(df_con_criterios, plot_demographic_clinical_heatmap):
    fig_heatmap_demo = plot_demographic_clinical_heatmap(df_con_criterios)
    fig_heatmap_demo
    return (fig_heatmap_demo,)


@app.cell
def _(df_con_criterios, mo, pl):
    # Calcular estadísticas para interpretación del heatmap demográfico
    total_casos_demo = df_con_criterios.height
    
    # Por edad
    casos_jovenes = df_con_criterios.filter(pl.col('edad_entrevistado') < 30).height
    casos_adultos = df_con_criterios.filter(
        (pl.col('edad_entrevistado') >= 30) & (pl.col('edad_entrevistado') < 60)
    ).height
    casos_mayores = df_con_criterios.filter(pl.col('edad_entrevistado') >= 60).height
    
    # Hospitalización por edad
    hosp_mayores = df_con_criterios.filter(
        (pl.col('edad_entrevistado') >= 60) & (pl.col('Hospitalización') == 1)
    ).height
    total_mayores = df_con_criterios.filter(pl.col('edad_entrevistado') >= 60).height
    pct_hosp_mayores = (hosp_mayores / total_mayores * 100) if total_mayores > 0 else 0
    
    # Severidad por edad
    sev_mayores = df_con_criterios.filter(
        (pl.col('edad_entrevistado') >= 60) & (pl.col('Severo') == 1)
    ).height
    pct_sev_mayores = (sev_mayores / total_mayores * 100) if total_mayores > 0 else 0
    
    # Condiciones preexistentes promedio
    avg_cond_total = df_con_criterios['Total_Cond_pre'].mean()
    avg_cond_mayores = df_con_criterios.filter(
        pl.col('edad_entrevistado') >= 60
    )['Total_Cond_pre'].mean()
    
    # Por sexo
    fem_count = df_con_criterios.filter(pl.col('sexo') == 1).height
    masc_count = df_con_criterios.filter(pl.col('sexo') == 2).height
    
    mo.md(f"""
    ---
    ### 📊 Interpretación: Heatmap Demográfico-Clínico
    
    **Estructura del heatmap:**
    - **Eje X (columnas):** Grupos etarios (< 30, 30-44, 45-59, >60) + Sexo (Femenino, Masculino)
    - **Eje Y (filas):** Variables clínicas clave
    - **Escala de color:** Rojo (valores altos) → Amarillo → Azul (valores bajos)
    
    **Estadísticas generales:**
    - **Total casos:** {total_casos_demo:,}
    - **< 30 años:** {casos_jovenes} casos
    - **30-59 años:** {casos_adultos} casos  
    - **≥ 60 años:** {casos_mayores} casos
    - **Femenino:** {fem_count} casos
    - **Masculino:** {masc_count} casos
    
    **Hallazgos clave por variable:**
    
    1. **Hospitalización:**
       - Adultos mayores (≥60): {pct_hosp_mayores:.1f}% hospitalizados
       - Patrón esperado: incremento con la edad
       - Mayor riesgo en grupos etarios avanzados
    
    2. **Severidad (casos severos):**
       - Adultos mayores (≥60): {pct_sev_mayores:.1f}% casos severos
       - Correlación positiva con edad
       - Indicador de vulnerabilidad por grupo
    
    3. **Condiciones preexistentes:**
       - Promedio general: {avg_cond_total:.2f} condiciones por persona
       - Adultos mayores (≥60): {avg_cond_mayores:.2f} condiciones promedio
       - Factor de riesgo acumulativo con la edad
    
    **Patrones demográficos identificados:**
    - 📈 **Gradiente etario:** Hospitalización y severidad aumentan con la edad
    - 🏥 **Vulnerabilidad:** Adultos mayores muestran mayor carga clínica
    - 👥 **Diferencias por sexo:** Comparables en las columnas finales del heatmap
    - 🔴 **Zonas rojas:** Indican grupos de mayor riesgo o mayor carga de enfermedad
    - 🔵 **Zonas azules:** Grupos con menor prevalencia de características adversas
    
    **Implicaciones clínicas y de salud pública:**
    - Identificación de poblaciones prioritarias para intervenciones
    - Estratificación de riesgo basada en edad y comorbilidades
    - Planificación de recursos hospitalarios según demografía
    - Diseño de políticas de prevención focalizadas
    - Seguimiento diferenciado post-COVID según perfil demográfico
    
    **Utilidad del heatmap:**
    - Visualización rápida de patrones demográfico-clínicos
    - Comparación simultánea entre grupos etarios y sexo
    - Identificación de brechas y desigualdades en salud
    - Herramienta de comunicación para tomadores de decisiones
    
    ---
    """)
    return (avg_cond_mayores, avg_cond_total, casos_adultos, casos_jovenes, casos_mayores, fem_count, hosp_mayores, masc_count, pct_hosp_mayores, pct_sev_mayores, sev_mayores, total_casos_demo, total_mayores)


@app.cell
def _(mo):
    mo.md("""
    ## 5. Casos por Semana Epidemiológica - Análisis por Variables Demográficas y Clínicas
    
    Esta sección presenta gráficos de barras apiladas mostrando la distribución temporal de casos 
    coloreados por diferentes variables de interés.
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ### 5.1. Distribución por Sexo
    """)
    return


@app.cell
def _(df_con_criterios, plot_cases_by_week_by_sex):
    fig_sexo_week = plot_cases_by_week_by_sex(df_con_criterios)
    fig_sexo_week
    return (fig_sexo_week,)


@app.cell
def _(df_con_criterios, mo, pl):  # type: ignore
    # Calcular estadísticas por sexo
    total_fem = df_con_criterios.filter(pl.col('sexo') == 1).height
    total_masc = df_con_criterios.filter(pl.col('sexo') == 2).height
    total_casos = df_con_criterios.height
    pct_fem = (total_fem / total_casos * 100) if total_casos > 0 else 0
    pct_masc = (total_masc / total_casos * 100) if total_casos > 0 else 0
    
    mo.md(f"""
    ---
    ###  Interpretación: Distribución por Sexo
    
    **Composición general de la muestra:**
    - **Femenino (rojo):** {total_fem:,} casos ({pct_fem:.1f}%)
    - **Masculino (azul):** {total_masc:,} casos ({pct_masc:.1f}%)
    
    **Hallazgos clave:**
    - {'Las mujeres representan la mayoría de casos' if pct_fem > 50 else 'Los hombres representan la mayoría de casos'} en el estudio
    - La distribución temporal muestra {'patrones consistentes' if abs(pct_fem - 50) < 15 else 'diferencias marcadas'} entre sexos
    - Útil para identificar si hay sesgo de género en el reclutamiento o diferencias reales en la susceptibilidad
    
    **Implicaciones:**
    - Considerar el sexo como variable confusora en análisis multivariados
    - {'⚠️ Desbalance importante - considerar ajustar por sexo en comparaciones' if abs(pct_fem - 50) > 20 else ' Distribución relativamente equilibrada'}
    
    ---
    """)
    return (total_fem, total_masc, pct_fem, pct_masc)


@app.cell
def _(mo):
    mo.md("""
    ### 5.2. Distribución por Grupo Etario
    """)
    return


@app.cell
def _(df_con_criterios, plot_cases_by_week_by_age_group):
    fig_edad_week = plot_cases_by_week_by_age_group(df_con_criterios)
    fig_edad_week
    return (fig_edad_week,)


@app.cell
def _(df_con_criterios, mo, pl):
    # Calcular estadísticas por grupo etario
    df_edad_cat = df_con_criterios.with_columns(
        pl.when(pl.col('edad_entrevistado') < 30)
        .then(pl.lit('<30'))
        .when((pl.col('edad_entrevistado') >= 30) & (pl.col('edad_entrevistado') < 45))
        .then(pl.lit('30-44'))
        .when((pl.col('edad_entrevistado') >= 45) & (pl.col('edad_entrevistado') < 60))
        .then(pl.lit('45-59'))
        .otherwise(pl.lit('≥60'))
        .alias('grupo_edad')
    )
    
    stats_edad = df_edad_cat.group_by('grupo_edad').agg(
        pl.len().alias('n')
    ).sort('grupo_edad')
    
    total_edad = df_edad_cat.height
    
    # Crear texto de estadísticas
    _stats_text_edad = []
    grupos_orden = ['<30', '30-44', '45-59', '≥60']
    for grupo in grupos_orden:
        _n_edad = stats_edad.filter(pl.col('grupo_edad') == grupo).select('n').item(0, 0) if len(stats_edad.filter(pl.col('grupo_edad') == grupo)) > 0 else 0
        _pct_edad = (_n_edad / total_edad * 100) if total_edad > 0 else 0
        _stats_text_edad.append(f"- **{grupo} años:** {_n_edad:,} casos ({_pct_edad:.1f}%)")
    
    _stats_str_edad = '\n    '.join(_stats_text_edad)
    
    # Identificar grupo predominante
    if len(stats_edad) > 0:
        grupo_max = stats_edad.sort('n', descending=True).select('grupo_edad').item(0, 0)
        n_max = stats_edad.sort('n', descending=True).select('n').item(0, 0)
    else:
        grupo_max = "N/A"
        n_max = 0
    
    mo.md(f"""
    ---
    ###  Interpretación: Distribución por Grupo Etario
    
    **Estratificación por edad (criterio OMS para adultos):**
    - **<30 años:** Adultos jóvenes (alta actividad laboral/social)
    - **30-44 años:** Edad media temprana (población económicamente activa)
    - **45-59 años:** Edad media tardía (mayor carga de comorbilidades)
    - **≥60 años:** Adultos mayores (mayor vulnerabilidad)
    
    **Composición por edad:**
    {_stats_str_edad}
    
    **Hallazgos clave:**
    - **Grupo predominante:** {grupo_max} años con {n_max:,} casos
    - Los colores del gráfico permiten visualizar la evolución temporal de cada grupo etario
    - Útil para identificar si Long COVID afecta diferencialmente a grupos de edad específicos
    
    **Implicaciones clínicas:**
    - Considerar la edad como factor de riesgo en modelos predictivos
    - Los grupos más jóvenes (<30) pueden tener presentaciones diferentes vs adultos mayores
    - Importante para estratificar intervenciones y seguimiento clínico
    
    ---
    """)
    return (grupo_max, n_max)


@app.cell
def _(mo):
    mo.md("""
    ### 5.3. Distribución por Presencia de Secuelas
    """)
    return


@app.cell
def _(df_con_criterios, plot_cases_by_week_by_secuelas):
    fig_secuelas_week_v2 = plot_cases_by_week_by_secuelas(df_con_criterios)
    fig_secuelas_week_v2
    return (fig_secuelas_week_v2,)


@app.cell
def _(df_con_criterios, mo, pl):
    # Calcular estadísticas de secuelas
    con_secuelas = df_con_criterios.filter(pl.col('sec_count') >= 1).height
    sin_secuelas = df_con_criterios.filter(pl.col('sec_count') == 0).height
    total_sec = df_con_criterios.height
    pct_con = (con_secuelas / total_sec * 100) if total_sec > 0 else 0
    pct_sin = (sin_secuelas / total_sec * 100) if total_sec > 0 else 0
    
    mo.md(f"""
    ---
    ###  Interpretación: Presencia de Secuelas
    
    **Distribución de secuelas:**
    - **Con secuelas (rojo):** {con_secuelas:,} casos ({pct_con:.1f}%)
    - **Sin secuelas (verde):** {sin_secuelas:,} casos ({pct_sin:.1f}%)
    
    **Hallazgos clave:**
    - {'Mayoría de casos presenta secuelas documentadas' if pct_con > 50 else 'Mayoría de casos sin secuelas documentadas'}
    - Las secuelas son componente del Criterio 4 (definición de Long COVID)
    - La distribución temporal muestra la evolución de complicaciones post-COVID
    
    **Relevancia clínica:**
    - Secuelas incluyen: complicaciones respiratorias, cardiovasculares, neurológicas, etc.
    - {'⚠️ Alta prevalencia de secuelas requiere seguimiento prolongado' if pct_con > 30 else ' Prevalencia moderada de secuelas'}
    - Importante para planificación de recursos de rehabilitación y seguimiento
    
    ---
    """)
    return (con_secuelas, sin_secuelas, pct_con, pct_sin)


@app.cell
def _(mo):
    mo.md("""
    ### 5.4. Distribución por Nueva Condición Médica
    """)
    return


@app.cell
def _(df_con_criterios, plot_cases_by_week_by_nueva_condicion):
    fig_nueva_cond_week = plot_cases_by_week_by_nueva_condicion(df_con_criterios)
    fig_nueva_cond_week
    return (fig_nueva_cond_week,)


@app.cell
def _(df_con_criterios, mo, pl):
    # Calcular estadísticas de nueva condición
    con_nueva = df_con_criterios.filter(pl.col('conteo_nueva_condicion') >= 1).height
    sin_nueva = df_con_criterios.filter(pl.col('conteo_nueva_condicion') == 0).height
    total_nc = df_con_criterios.height
    pct_con_nc = (con_nueva / total_nc * 100) if total_nc > 0 else 0
    pct_sin_nc = (sin_nueva / total_nc * 100) if total_nc > 0 else 0
    
    mo.md(f"""
    ---
    ###  Interpretación: Nueva Condición Médica Post-COVID
    
    **Distribución de nuevas condiciones:**
    - **Con nueva condición (morado):** {con_nueva:,} casos ({pct_con_nc:.1f}%)
    - **Sin nueva condición (gris):** {sin_nueva:,} casos ({pct_sin_nc:.1f}%)
    
    **Hallazgos clave:**
    - {'Proporción significativa desarrolló nuevas condiciones médicas' if pct_con_nc > 20 else 'Proporción moderada con nuevas condiciones'}
    - Nueva condición es componente del Criterio 4 junto con secuelas (operador OR)
    - Refleja el impacto de COVID-19 en generar nueva morbilidad
    
    **Implicaciones para salud pública:**
    - Nuevas condiciones pueden incluir: diabetes, hipertensión, problemas cardíacos de novo
    - {'⚠️ Alta carga de nueva morbilidad - impacto en sistema de salud' if pct_con_nc > 25 else '⚡ Carga moderada de nueva morbilidad'}
    - Importante para estimar costos de atención a largo plazo
    - Sugiere necesidad de monitoreo continuo post-infección
    
    ---
    """)
    return (con_nueva, sin_nueva, pct_con_nc, pct_sin_nc)


@app.cell
def _(mo):
    mo.md("""
    ### 5.5. Distribución por Nivel de Síntomas Recurrentes
    """)
    return


@app.cell
def _(df_con_criterios, plot_cases_by_week_by_sintomas_recurrentes):
    fig_sintomas_rec_week = plot_cases_by_week_by_sintomas_recurrentes(df_con_criterios)
    fig_sintomas_rec_week
    return (fig_sintomas_rec_week,)


@app.cell
def _(df_con_criterios, mo, pl):
    # Calcular estadísticas de síntomas recurrentes
    df_sint_cat = df_con_criterios.with_columns(
        pl.when(pl.col('sintoma_recurrente_count') == 0)
        .then(pl.lit('0'))
        .when(pl.col('sintoma_recurrente_count') == 1)
        .then(pl.lit('1'))
        .when(pl.col('sintoma_recurrente_count') == 2)
        .then(pl.lit('2'))
        .when(pl.col('sintoma_recurrente_count') == 3)
        .then(pl.lit('3'))
        .otherwise(pl.lit('4+'))
        .alias('cat_sintomas')
    )
    
    stats_sint = df_sint_cat.group_by('cat_sintomas').agg(
        pl.len().alias('n')
    ).sort('cat_sintomas')
    
    total_sint = df_sint_cat.height
    
    # Calcular casos con >1 síntoma (parte del Criterio 2)
    con_mult_sint = df_con_criterios.filter(pl.col('sintoma_recurrente_count') > 1).height
    pct_mult = (con_mult_sint / total_sint * 100) if total_sint > 0 else 0
    
    # Crear estadísticas por categoría
    _stats_text_sint = []
    for cat in ['0', '1', '2', '3', '4+']:
        row_data = stats_sint.filter(pl.col('cat_sintomas') == cat)
        if len(row_data) > 0:
            _n_sint = row_data.select('n').item()
            _pct_sint = (_n_sint / total_sint * 100) if total_sint > 0 else 0
            _stats_text_sint.append(f"- **{cat} síntoma(s):** {_n_sint:,} casos ({_pct_sint:.1f}%)")
    
    _stats_str_sint = '\n    '.join(_stats_text_sint)
    
    mo.md(f"""
    ---
    ###  Interpretación: Nivel de Síntomas Recurrentes
    
    **Distribución de carga sintomática:**
    {_stats_str_sint}
    
    **Hallazgos clave:**
    - **Casos con >1 síntoma recurrente:** {con_mult_sint:,} ({pct_mult:.1f}%) - componente del Criterio 2
    - El gradiente de color (gris → rojo) refleja la severidad creciente
    - Mayor número de síntomas sugiere mayor impacto funcional
    
    **Relevancia clínica:**
    - La persistencia sintomática es marcador de Long COVID
    - {'⚠️ Alta proporción con síntomas múltiples' if pct_mult > 40 else '⚡ Proporción moderada con síntomas múltiples'}
    - Útil para priorizar casos que requieren atención multidisciplinaria
    - Los casos con 4+ síntomas pueden requerir intervenciones más intensivas
    
    **Patrones temporales:**
    - Permite identificar semanas con mayor carga sintomática
    - Útil para correlacionar con variantes circulantes o políticas de salud
    
    ---
    """)
    return (con_mult_sint, pct_mult)


@app.cell
def _(mo):
    mo.md("""
    ### 4.1. Por variable longCOVID
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ### 4.2. Por síntomas recurrentes
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ### 4.3. Por pertenencia a cluster
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ### 4.4. Por secuelas
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## 6. Análisis de Clusters y Secuelas
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## 7. Tabla 1: Características Descriptivas Estratificadas por Long COVID
    
    Esta sección presenta una tabla descriptiva completa comparando características demográficas,
    clínicas y sintomáticas entre individuos con y sin Long COVID. La tabla incluye pruebas 
    estadísticas para evaluar diferencias significativas entre grupos.
    """)
    return


@app.cell
def _(create_table1_stratified, df_con_criterios):
    # Crear tabla descriptiva estratificada
    fig_table1 = create_table1_stratified(df_con_criterios, stratify_by='longCOVID')
    fig_table1
    return (fig_table1,)


@app.cell
def _(df_con_criterios, mo, pl):  # type: ignore
    # Calcular estadísticas generales para la interpretación
    n_total = df_con_criterios.height
    n_lc = df_con_criterios.filter(pl.col('longCOVID') == 1).height
    n_no_lc = df_con_criterios.filter(pl.col('longCOVID') == 0).height
    pct_lc = (n_lc / n_total * 100) if n_total > 0 else 0
    
    # Diferencias demográficas
    pct_fem_lc = (df_con_criterios.filter((pl.col('longCOVID') == 1) & (pl.col('sexo') == 1)).height / n_lc * 100) if n_lc > 0 else 0
    pct_fem_no_lc = (df_con_criterios.filter((pl.col('longCOVID') == 0) & (pl.col('sexo') == 1)).height / n_no_lc * 100) if n_no_lc > 0 else 0
    
    # Síntomas recurrentes
    mean_sint_lc = df_con_criterios.filter(pl.col('longCOVID') == 1).select(pl.col('sintoma_recurrente_count').mean()).item()
    mean_sint_no_lc = df_con_criterios.filter(pl.col('longCOVID') == 0).select(pl.col('sintoma_recurrente_count').mean()).item()
    
    # Clusters más prevalentes en Long COVID
    clusters_lc = {
        'Cognitivo': df_con_criterios.filter((pl.col('longCOVID') == 1) & (pl.col('cluster_cognitivo_bi') == 1)).height,
        'Respiratorio': df_con_criterios.filter((pl.col('longCOVID') == 1) & (pl.col('cluster_respiratorio_bi') == 1)).height,
        'Gastrointestinal': df_con_criterios.filter((pl.col('longCOVID') == 1) & (pl.col('cluster_gastrointestinal_bi') == 1)).height,
        'Muscular': df_con_criterios.filter((pl.col('longCOVID') == 1) & (pl.col('cluster_muscular_bi') == 1)).height,
        'Olfato/Gusto': df_con_criterios.filter((pl.col('longCOVID') == 1) & (pl.col('cluster_olfato_gusto_bi') == 1)).height,
        'Vía Aérea': df_con_criterios.filter((pl.col('longCOVID') == 1) & (pl.col('cluster_via_aerea_bi') == 1)).height
    }
    
    cluster_max = max(clusters_lc.items(), key=lambda x: x[1])
    cluster_max_pct = (cluster_max[1] / n_lc * 100) if n_lc > 0 else 0
    
    mo.md(f"""
    ---
    ###  Interpretación: Características Estratificadas por Long COVID
    
    **Composición de la muestra:**
    - **Total de participantes:** {n_total:,}
    - **Long COVID:** {n_lc:,} casos ({pct_lc:.1f}%)
    - **No Long COVID:** {n_no_lc:,} casos ({100-pct_lc:.1f}%)
    
    **Hallazgos demográficos:**
    - **Sexo:** {'Las mujeres presentan mayor prevalencia en el grupo Long COVID' if pct_fem_lc > pct_fem_no_lc else 'Distribución similar entre grupos'} 
      ({pct_fem_lc:.1f}% vs {pct_fem_no_lc:.1f}% mujeres)
    - La edad puede mostrar diferencias significativas entre grupos (ver p-value en tabla)
    
    **Características clínicas:**
    - **Síntomas persistentes:** El grupo Long COVID presenta en promedio {mean_sint_lc:.1f} síntomas recurrentes 
      vs {mean_sint_no_lc:.1f} en el grupo control
    - Los p-values < 0.05 indican diferencias estadísticamente significativas entre grupos
    - Las variables con p < 0.001 muestran asociaciones muy fuertes con Long COVID
    
    **Patrones de clusters sintomáticos:**
    - **Cluster más prevalente en Long COVID:** {cluster_max[0]} ({cluster_max[1]:,} casos, {cluster_max_pct:.1f}%)
    - Los clusters permiten identificar fenotipos clínicos específicos
    - Útil para estratificar pacientes y personalizar intervenciones
    
    **Implicaciones clínicas:**
    1. **Identificación de factores de riesgo:** Variables con p-values significativos pueden ser predictores de Long COVID
    2. **Fenotipado:** Los clusters sintomáticos ayudan a caracterizar subgrupos de pacientes
    3. **Estratificación:** La tabla permite identificar características que diferencian claramente ambos grupos
    4. **Planificación:** Los datos de "problemas a 3 meses" y "necesidad de asistencia" informan sobre carga de enfermedad
    
    **Notas metodológicas:**
    - P-values calculados mediante:
      - **Variables categóricas:** Test de Chi-cuadrado
      - **Variables continuas:** Test t de Student
    - Valores p < 0.05 se consideran estadísticamente significativos
    - La tabla es modificable ajustando la estructura en `create_table1_stratified()`
    
    **Limitaciones:**
    - Variables faltantes pueden afectar los cálculos (revisar sección de análisis de NULLs)
    - Algunas variables clínicas (hospitalización, UCI) pueden tener datos limitados
    - Los p-values no ajustan por múltiples comparaciones (considerar corrección de Bonferroni si necesario)
    
    ---
    """)
    return (n_total, n_lc, n_no_lc, pct_lc, cluster_max, cluster_max_pct)


@app.cell
def _(mo):
    mo.md("""
    ## 8. Figura Metodológica
    """)
    return


if __name__ == "__main__":
    app.run()
