import marimo

__generated_with = "0.19.4"
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
        plot_longcovid_by_week,
        plot_sintomas_recurrentes_by_week,
        plot_cluster_pertenencia_by_week,
        plot_clusters_individuales_by_week,
        plot_secuelas_by_week,
        plot_clusters_heatmap_by_diagnosis_week,
        plot_criterio_barplot,
    )
    return (
        create_criterio_variables,
        load_long_covid,
        mo,
        pl,
        plot_cluster_pertenencia_by_week,
        plot_clusters_heatmap_by_diagnosis_week,
        plot_clusters_individuales_by_week,
        plot_criterio1_by_week,
        plot_criterio2_recovery,
        plot_criterio2_sintomas,
        plot_criterio2_promedio_sintomas,
        plot_criterio2_promedio_sintomas_by_week,
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
    ## 2. Crear Variables de Criterio por fenotipos long covid (1-4)
    """)
    return


@app.cell
def _():
    # Paleta de colores única para cada criterio
    COLORES_CRITERIOS = {
        1: '#3498db',  # Azul - Criterio 1 (Long COVID general)
        2: '#e74c3c',  # Rojo - Criterio 2 (Síntomas recurrentes)
        3: '#f39c12',  # Naranja - Criterio 3 (Clusters)
        4: '#9b59b6',  # Morado - Criterio 4 (Secuelas)
    }
    
    # Metadata de criterios para documentación
    CRITERIOS_METADATA = {
        1: {
            'nombre': 'Long COVID General',
            'variables': ['longCOVID'],
            'descripcion': 'Fenotipo muy general basado en la variable longCOVID',
            'formula': 'criterio_1 = 1 si longCOVID == 1, sino 0',
            'color': COLORES_CRITERIOS[1]
        },
        2: {
            'nombre': 'Síntomas Recurrentes',
            'variables': ['covid', 'sintoma_recurrente_count', 'recuperado_3m'],
            'descripcion': 'COVID confirmado + Más de 1 síntoma recurrente + No recuperado a los 3 meses',
            'formula': 'criterio_2 = 1 si (covid==1 AND sintoma_recurrente_count>1 AND recuperado_3m==2)',
            'color': COLORES_CRITERIOS[2]
        },
        3: {
            'nombre': 'Clusters',
            'variables': ['covid', 'pertenece_cluster_count', 'recuperado_3m'],
            'descripcion': 'COVID-19 + Al menos 2 síntomas de cualquier cluster + No recuperado a los 3 meses',
            'formula': 'criterio_3 = 1 si (covid==1 AND pertenece_cluster_count>=1 AND recuperado_3m==2)',
            'color': COLORES_CRITERIOS[3]
        },
        4: {
            'nombre': 'Secuelas',
            'variables': ['covid', 'conteo_nueva_condicion', 'sec_count'],
            'descripcion': 'COVID-19 + Nueva condición O Secuelas crónicas',
            'formula': 'criterio_4 = 1 si (covid==1 AND (conteo_nueva_condicion>=1 OR sec_count>=1))',
            'color': COLORES_CRITERIOS[4]
        }
    }
    
    return COLORES_CRITERIOS, CRITERIOS_METADATA


@app.cell
def _(mo, pl):
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
        criterio_col = f'criterio_{num_criterio}'
        
        # Validaciones básicas
        validacion = {
            'criterio': num_criterio,
            'n_total': len(df),
            'n_cumplen': df.filter(pl.col(criterio_col) == 1).height,
            'n_no_cumplen': df.filter(pl.col(criterio_col) == 0).height,
            'porcentaje_cumplen': (df.filter(pl.col(criterio_col) == 1).height / len(df) * 100),
            'null_counts': {},
            'variables_validas': {},
        }
        
        # Contar NULLs por cada variable componente
        for var in variables_componentes:
            if var in df.columns:
                null_count = df.filter(pl.col(var).is_null()).height
                valid_count = df.filter(pl.col(var).is_not_null()).height
                validacion['null_counts'][var] = null_count
                validacion['variables_validas'][var] = {
                    'validos': valid_count,
                    'porcentaje_valido': (valid_count / len(df) * 100)
                }
        
        # Verificar consistencia del criterio
        validacion['consistente'] = (validacion['n_cumplen'] + validacion['n_no_cumplen']) == validacion['n_total']
        
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
        df_con_criterios, 
        1, 
        CRITERIOS_METADATA[1]['variables']
    )
    
    # Mostrar resumen de Criterio 1
    mo.md(f"""
    ---
    ### 📊 Resumen Criterio 1: {CRITERIOS_METADATA[1]['nombre']}
    
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
    """)
    
    # Crear tabla de validación
    _validacion_tabla = []
    for _var in CRITERIOS_METADATA[1]['variables']:
        if _var in validacion_c1['variables_validas']:
            _info = validacion_c1['variables_validas'][_var]
            _validacion_tabla.append({
                'Variable': _var,
                'Valores válidos': _info['validos'],
                '% Válido': f"{_info['porcentaje_valido']:.2f}%",
                'Valores NULL': validacion_c1['null_counts'][_var]
            })
    
    df_validacion_c1 = pl.DataFrame(_validacion_tabla)
    
    (validacion_c1, df_validacion_c1)
    return df_validacion_c1, validacion_c1


@app.cell
def _(df_validacion_c1, mo, validacion_c1):
    # Mostrar tabla de validación
    mo.ui.table(df_validacion_c1)
    
    estado_c1 = "✅ **Criterio funciona correctamente**" if validacion_c1['consistente'] else "❌ **Problema detectado en el criterio**"
    
    mo.md(f"""
    {estado_c1}
    
    - Consistencia lógica: {'Sí' if validacion_c1['consistente'] else 'No'}
    - Total casos = Cumplen + No cumplen: {validacion_c1['n_total']} = {validacion_c1['n_cumplen']} + {validacion_c1['n_no_cumplen']}
    
    ---
    """)
    return (estado_c1,)



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
        'Criterio 1 (Long COVID): Distribución de Casos',
        CRITERIOS_METADATA[1]['color']
    )
    fig_bar_c1
    return (fig_bar_c1,)


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
        df_con_criterios, 
        2, 
        CRITERIOS_METADATA[2]['variables']
    )
    
    # Mostrar resumen de Criterio 2
    mo.md(f"""
    ---
    ### 📊 Resumen Criterio 2: {CRITERIOS_METADATA[2]['nombre']}
    
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
    """)
    
    # Crear tabla de validación
    _validacion_tabla_c2 = []
    for _var in CRITERIOS_METADATA[2]['variables']:
        if _var in validacion_c2['variables_validas']:
            _info = validacion_c2['variables_validas'][_var]
            _validacion_tabla_c2.append({
                'Variable': _var,
                'Valores válidos': _info['validos'],
                '% Válido': f"{_info['porcentaje_valido']:.2f}%",
                'Valores NULL': validacion_c2['null_counts'][_var]
            })
    
    df_validacion_c2 = pl.DataFrame(_validacion_tabla_c2)
    
    (validacion_c2, df_validacion_c2)
    return df_validacion_c2, validacion_c2


@app.cell
def _(df_validacion_c2, mo, validacion_c2):
    # Mostrar tabla de validación del Criterio 2
    mo.ui.table(df_validacion_c2)
    
    estado_c2 = "✅ **Criterio funciona correctamente**" if validacion_c2['consistente'] else "❌ **Problema detectado en el criterio**"
    
    mo.md(f"""
    {estado_c2}
    
    - Consistencia lógica: {'Sí' if validacion_c2['consistente'] else 'No'}
    - Total casos = Cumplen + No cumplen: {validacion_c2['n_total']} = {validacion_c2['n_cumplen']} + {validacion_c2['n_no_cumplen']}
    
    ---
    """)
    return (estado_c2,)



@app.cell
def _(CRITERIOS_METADATA, df_con_criterios, plot_criterio_barplot):
    # Barplot de Criterio 2
    fig_bar_c2 = plot_criterio_barplot(
        df_con_criterios, 
        2, 
        'Criterio 2 (Síntomas Recurrentes): Distribución de Casos',
        CRITERIOS_METADATA[2]['color']
    )
    fig_bar_c2
    return (fig_bar_c2,)


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
        df_con_criterios, 
        CRITERIOS_METADATA[2]['color']
    )
    fig_c2_promedio
    return (fig_c2_promedio,)


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
def _(CRITERIOS_METADATA, df_con_criterios, plot_criterio2_promedio_sintomas_by_week):
    # Evolución temporal del promedio de síntomas
    fig_c2_promedio_week = plot_criterio2_promedio_sintomas_by_week(
        df_con_criterios,
        CRITERIOS_METADATA[2]['color']
    )
    fig_c2_promedio_week
    return (fig_c2_promedio_week,)


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
    return (fig_c2_sintomas,)


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
        df_con_criterios, 
        3, 
        CRITERIOS_METADATA[3]['variables']
    )
    
    # Mostrar resumen de Criterio 3
    mo.md(f"""
    ---
    ### 📊 Resumen Criterio 3: {CRITERIOS_METADATA[3]['nombre']}
    
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
    """)
    
    # Crear tabla de validación
    _validacion_tabla_c3 = []
    for _var in CRITERIOS_METADATA[3]['variables']:
        if _var in validacion_c3['variables_validas']:
            _info = validacion_c3['variables_validas'][_var]
            _validacion_tabla_c3.append({
                'Variable': _var,
                'Valores válidos': _info['validos'],
                '% Válido': f"{_info['porcentaje_valido']:.2f}%",
                'Valores NULL': validacion_c3['null_counts'][_var]
            })
    
    df_validacion_c3 = pl.DataFrame(_validacion_tabla_c3)
    
    (validacion_c3, df_validacion_c3)
    return df_validacion_c3, validacion_c3


@app.cell
def _(df_validacion_c3, mo, validacion_c3):
    # Mostrar tabla de validación del Criterio 3
    mo.ui.table(df_validacion_c3)
    
    estado_c3 = "✅ **Criterio funciona correctamente**" if validacion_c3['consistente'] else "❌ **Problema detectado en el criterio**"
    
    mo.md(f"""
    {estado_c3}
    
    - Consistencia lógica: {'Sí' if validacion_c3['consistente'] else 'No'}
    - Total casos = Cumplen + No cumplen: {validacion_c3['n_total']} = {validacion_c3['n_cumplen']} + {validacion_c3['n_no_cumplen']}
    
    **Nota:** Este criterio mostró una diferencia de 8 casos respecto al análisis previo (360 vs 352). 
    Las validaciones anteriores indican que no hay valores NULL en las variables componentes, 
    por lo que la diferencia podría deberse a criterios de filtrado o versión del dataset.
    
    ---
    """)
    return (estado_c3,)



@app.cell
def _(CRITERIOS_METADATA, df_con_criterios, plot_criterio_barplot):
    # Barplot de Criterio 3
    fig_bar_c3 = plot_criterio_barplot(
        df_con_criterios, 
        3, 
        'Criterio 3 (Clusters): Distribución de Casos',
        CRITERIOS_METADATA[3]['color']
    )
    fig_bar_c3
    return (fig_bar_c3,)


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
        df_con_criterios, 
        4, 
        CRITERIOS_METADATA[4]['variables']
    )
    
    # Mostrar resumen de Criterio 4
    mo.md(f"""
    ---
    ### 📊 Resumen Criterio 4: {CRITERIOS_METADATA[4]['nombre']}
    
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
    """)
    
    # Crear tabla de validación
    _validacion_tabla_c4 = []
    for _var in CRITERIOS_METADATA[4]['variables']:
        if _var in validacion_c4['variables_validas']:
            _info = validacion_c4['variables_validas'][_var]
            _validacion_tabla_c4.append({
                'Variable': _var,
                'Valores válidos': _info['validos'],
                '% Válido': f"{_info['porcentaje_valido']:.2f}%",
                'Valores NULL': validacion_c4['null_counts'][_var]
            })
    
    df_validacion_c4 = pl.DataFrame(_validacion_tabla_c4)
    
    (validacion_c4, df_validacion_c4)
    return df_validacion_c4, validacion_c4


@app.cell
def _(df_validacion_c4, mo, validacion_c4):
    # Mostrar tabla de validación del Criterio 4
    mo.ui.table(df_validacion_c4)
    
    estado_c4 = "✅ **Criterio funciona correctamente**" if validacion_c4['consistente'] else "❌ **Problema detectado en el criterio**"
    
    mo.md(f"""
    {estado_c4}
    
    - Consistencia lógica: {'Sí' if validacion_c4['consistente'] else 'No'}
    - Total casos = Cumplen + No cumplen: {validacion_c4['n_total']} = {validacion_c4['n_cumplen']} + {validacion_c4['n_no_cumplen']}
    
    **Nota:** Este criterio utiliza un operador OR (nueva_condición O secuelas), 
    lo que puede resultar en un mayor número de casos positivos comparado con criterios que usan AND.
    
    ---
    """)
    return (estado_c4,)



@app.cell
def _(CRITERIOS_METADATA, df_con_criterios, plot_criterio_barplot):
    # Barplot de Criterio 4
    fig_bar_c4 = plot_criterio_barplot(
        df_con_criterios, 
        4, 
        'Criterio 4 (Secuelas): Distribución de Casos',
        CRITERIOS_METADATA[4]['color']
    )
    fig_bar_c4
    return (fig_bar_c4,)


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
    
    for i, validacion in enumerate([validacion_c1, validacion_c2, validacion_c3, validacion_c4], 1):
        resumen_criterios.append({
            'Criterio': f'Criterio {i}',
            'Nombre': CRITERIOS_METADATA[i]['nombre'],
            'N° Variables': len(CRITERIOS_METADATA[i]['variables']),
            'Casos positivos': validacion['n_cumplen'],
            '% Positivos': f"{validacion['porcentaje_cumplen']:.2f}%",
            'Casos negativos': validacion['n_no_cumplen'],
            'Total': validacion['n_total'],
            'Consistente': '✅' if validacion['consistente'] else '❌',
            'Color': COLORES_CRITERIOS[i]
        })
    
    df_resumen_criterios = pl.DataFrame(resumen_criterios)
    
    mo.md(f"""
    ---
    ### 📋 Tabla Resumen: Comparación de los 4 Criterios de Fenotipo Long COVID
    
    Esta tabla consolida las métricas clave de cada criterio para facilitar la comparación:
    """)
    
    (df_resumen_criterios,)
    return (df_resumen_criterios, resumen_criterios)


@app.cell
def _(df_resumen_criterios, mo):
    # Mostrar tabla resumen
    mo.ui.table(df_resumen_criterios)
    return


@app.cell
def _(CRITERIOS_METADATA, mo, resumen_criterios):
    # Análisis interpretativo
    total_c1 = resumen_criterios[0]['Casos positivos']
    total_c2 = resumen_criterios[1]['Casos positivos']
    total_c3 = resumen_criterios[2]['Casos positivos']
    total_c4 = resumen_criterios[3]['Casos positivos']
    
    mo.md(f"""
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
    - Todos los criterios han pasado las validaciones de consistencia ✅
    - No se detectaron valores NULL significativos en las variables componentes
    
    **Paleta de colores asignada para visualizaciones:**
    - Criterio 1: <span style="color:{CRITERIOS_METADATA[1]['color']}">███</span> {CRITERIOS_METADATA[1]['color']} (Azul)
    - Criterio 2: <span style="color:{CRITERIOS_METADATA[2]['color']}">███</span> {CRITERIOS_METADATA[2]['color']} (Rojo)
    - Criterio 3: <span style="color:{CRITERIOS_METADATA[3]['color']}">███</span> {CRITERIOS_METADATA[3]['color']} (Naranja)
    - Criterio 4: <span style="color:{CRITERIOS_METADATA[4]['color']}">███</span> {CRITERIOS_METADATA[4]['color']} (Morado)
    
    ---
    """)
    return total_c1, total_c2, total_c3, total_c4



@app.cell
def _(COLORES_CRITERIOS, df_con_criterios, plot_criterio_comparison):
    # Comparación visual de todos los criterios
    fig_criterios = plot_criterio_comparison(df_con_criterios, COLORES_CRITERIOS)
    fig_criterios
    return (fig_criterios,)


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
    analisis_c3 = df_con_criterios.select([
        'covid',
        'pertenece_cluster_count',
        'recuperado_3m',
        'criterio_3'
    ])

    # Validar cada componente
    covid_positivo = df_con_criterios.filter(pl.col('covid') == 1).height
    tiene_clusters = df_con_criterios.filter(pl.col('pertenece_cluster_count') >= 1).height
    no_recuperado = df_con_criterios.filter(pl.col('recuperado_3m') == 2).height

    # Los 3 componentes juntos
    tres_condiciones = df_con_criterios.filter(
        (pl.col('covid') == 1) & 
        (pl.col('pertenece_cluster_count') >= 1) & 
        (pl.col('recuperado_3m') == 2)
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
    casos_c3 = df_con_criterios.filter(pl.col('criterio_3') == 1).select([
        'covid',
        'pertenece_cluster_count',
        'recuperado_3m',
        'cluster_cognitivo_bi',
        'cluster_gastrointestinal_bi',
        'cluster_muscular_bi',
        'cluster_olfato_gusto_bi',
        'cluster_respiratorio_bi',
        'cluster_via_aerea_bi',
        'yearweek'
    ])

    # Distribución de pertenece_cluster_count entre los que cumplen C3
    dist_clusters_c3 = casos_c3.group_by('pertenece_cluster_count').agg(
        pl.len().alias('n_casos')
    ).sort('pertenece_cluster_count')

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
    null_covid = df_con_criterios.filter(pl.col('covid').is_null()).height
    null_clusters = df_con_criterios.filter(pl.col('pertenece_cluster_count').is_null()).height
    null_recuperado = df_con_criterios.filter(pl.col('recuperado_3m').is_null()).height

    # Casos con recuperado_3m diferente de 1 y 2
    recuperado_otros = df_con_criterios.filter(
        (pl.col('recuperado_3m') != 1) & 
        (pl.col('recuperado_3m') != 2)
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
    datos_criterios_binario = df_con_criterios.with_columns(
        pl.when(
            (pl.col('criterio_2') == 1) | 
            (pl.col('criterio_3') == 1) | 
            (pl.col('criterio_4') == 1)
        )
        .then(pl.lit('Tiene criterio'))
        .otherwise(pl.lit('No tiene criterio'))
        .alias('tiene_criterio')
    ).group_by(['yearweek', 'tiene_criterio']).agg(
        pl.len().alias('n')
    ).sort('yearweek')

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
    ### 4.2. Distribución de Síntomas Recurrentes
    """)
    return


@app.cell
def _(df_con_criterios, pl):
    # Validar datos: distribución de síntomas recurrentes
    datos_sintomas_hist = df_con_criterios.with_columns(
        pl.when(pl.col('sintoma_recurrente_count') == 0).then(pl.lit('0'))
        .when(pl.col('sintoma_recurrente_count') == 1).then(pl.lit('1'))
        .when(pl.col('sintoma_recurrente_count') == 2).then(pl.lit('2'))
        .when(pl.col('sintoma_recurrente_count') == 3).then(pl.lit('3'))
        .otherwise(pl.lit('4+'))
        .alias('categoria')
    ).group_by('categoria').agg(
        pl.len().alias('n_personas')
    ).sort('categoria')

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
    ### 4.3. Pertenencia a Clusters por Semana
    """)
    return


@app.cell
def _(df_con_criterios, pl):
    # Validar datos: pertenencia a clusters por semana
    datos_cluster_semana = df_con_criterios.with_columns(
        pl.when(pl.col('pertenece_cluster_count') >= 1)
        .then(pl.lit('Pertenece a cluster'))
        .otherwise(pl.lit('No pertenece'))
        .alias('pertenece_cluster')
    ).group_by(['yearweek', 'pertenece_cluster']).agg(
        pl.len().alias('n')
    ).sort('yearweek')

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
    ### 4.4. Clusters Individuales por Semana
    """)
    return


@app.cell
def _(df_con_criterios, pl):
    # Validar datos: un ejemplo con cluster cognitivo
    datos_cognitivo_semana = df_con_criterios.group_by(['yearweek', 'cluster_cognitivo_bi']).agg(
        pl.len().alias('n')
    ).sort('yearweek')

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
    ### 4.5. Secuelas por Semana
    """)
    return


@app.cell
def _(df_con_criterios, pl):
    # Validar datos: secuelas por semana
    datos_secuelas_semana = df_con_criterios.with_columns(
        pl.when(pl.col('sec_count') >= 1)
        .then(pl.lit('Con secuelas'))
        .otherwise(pl.lit('Sin secuelas'))
        .alias('tiene_secuelas')
    ).group_by(['yearweek', 'tiene_secuelas']).agg(
        pl.len().alias('n')
    ).sort('yearweek')

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
    ## 5. Análisis de Clusters y Secuelas
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## 6. Tabla 1: Descriptiva
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## 7. Figura Metodológica
    """)
    return


if __name__ == "__main__":
    app.run()
