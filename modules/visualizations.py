"""
Visualizaciones específicas para análisis Long COVID
"""
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import polars as pl


def plot_dataset_overview(df: pl.DataFrame) -> go.Figure:
    """
    Resumen visual del dataset con múltiples métricas
    
    Args:
        df: DataFrame con datos de long COVID
    
    Returns:
        Figura con subplots de estadísticas generales
    """
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Distribución por Sexo',
            'Distribución de Edad',
            'Casos por Semana Epidemiológica',
            'Long COVID vs Control'
        ),
        specs=[[{"type": "bar"}, {"type": "histogram"}],
               [{"type": "scatter"}, {"type": "pie"}]]
    )
    
    # 1. Distribución por sexo
    sexo_counts = df.group_by('sexo').agg(pl.len().alias('n')).sort('sexo')
    fig.add_trace(
        go.Bar(x=sexo_counts['sexo'].to_list(), y=sexo_counts['n'].to_list(),
               marker_color='lightblue', name='Sexo'),
        row=1, col=1
    )
    
    # 2. Histograma de edad
    fig.add_trace(
        go.Histogram(x=df['edad_entrevistado'].to_list(), 
                     nbinsx=30, marker_color='coral', name='Edad'),
        row=1, col=2
    )
    
    # 3. Casos por semana epidemiológica
    casos_semana = df.group_by('epiweek').agg(pl.len().alias('n')).sort('epiweek')
    fig.add_trace(
        go.Scatter(x=casos_semana['epiweek'].to_list(), 
                   y=casos_semana['n'].to_list(),
                   mode='lines+markers', marker_color='green', name='Casos'),
        row=2, col=1
    )
    
    # 4. Long COVID vs Control
    lc_counts = df.group_by('longCOVID').agg(pl.len().alias('n'))
    labels = ['Control', 'Long COVID']
    fig.add_trace(
        go.Pie(labels=labels, values=lc_counts['n'].to_list(),
               marker_colors=['#3498db', '#e74c3c']),
        row=2, col=2
    )
    
    fig.update_layout(
        title_text="Resumen del Dataset Long COVID",
        showlegend=False,
        height=700
    )
    
    return fig


def plot_criterio_comparison(df: pl.DataFrame, colores_criterios: dict | None = None) -> go.Figure:
    """
    Comparación de todos los criterios en un solo gráfico
    
    Args:
        df: DataFrame con criterios calculados
        colores_criterios: Diccionario con colores por criterio {1: '#color1', 2: '#color2', ...}
    
    Returns:
        Figura de barras comparando criterios
    """
    # Colores por defecto si no se proporcionan
    if colores_criterios is None:
        colores_criterios = {
            1: '#3498db',
            2: '#e74c3c',
            3: '#f39c12',
            4: '#9b59b6'
        }
    
    criterios_data = []
    for i in range(1, 5):
        col = f'criterio_{i}'
        if col in df.columns:
            cumplen = df.filter(pl.col(col) == 1).height
            criterios_data.append({
                'criterio': f'Criterio {i}',
                'num_criterio': i,
                'cumplen': cumplen,
                'no_cumplen': df.filter(pl.col(col) == 0).height,
                'total': len(df)
            })
    
    df_plot = pl.DataFrame(criterios_data)
    
    fig = go.Figure()
    
    # Agregar barras de "Cumplen" con colores individuales por criterio
    for row in df_plot.iter_rows(named=True):
        fig.add_trace(go.Bar(
            name=row['criterio'],
            x=[row['criterio']],
            y=[row['cumplen']],
            marker_color=colores_criterios[row['num_criterio']],
            text=[row['cumplen']],
            textposition='auto',
            showlegend=True,
            legendgroup='cumplen'
        ))
    
    # Agregar barras de "No cumplen" en gris
    for row in df_plot.iter_rows(named=True):
        fig.add_trace(go.Bar(
            name=f"{row['criterio']} (No cumple)",
            x=[row['criterio']],
            y=[row['no_cumplen']],
            marker_color='#95a5a6',
            text=[row['no_cumplen']],
            textposition='auto',
            showlegend=False
        ))
    
    fig.update_layout(
        title='Comparación de Criterios Long COVID',
        xaxis_title='Criterio',
        yaxis_title='Número de Casos',
        barmode='stack',
        template='plotly_white',
        height=500
    )
    
    return fig


def plot_criterio1_by_week(df: pl.DataFrame) -> go.Figure:
    """
    Long COVID (criterio 1) por semana epidemiológica
    
    Args:
        df: DataFrame con criterio_1
    
    Returns:
        Figura de evolución temporal
    """
    weekly = df.group_by(['epiweek', 'criterio_1']).agg(
        pl.len().alias('n')
    ).sort('epiweek')
    
    fig = go.Figure()
    
    for criterio in [0, 1]:
        data = weekly.filter(pl.col('criterio_1') == criterio)
        fig.add_trace(go.Scatter(
            x=data['epiweek'].to_list(),
            y=data['n'].to_list(),
            mode='lines+markers',
            name='Long COVID' if criterio == 1 else 'Control',
            marker=dict(size=8),
            line=dict(width=2)
        ))
    
    fig.update_layout(
        title='Criterio 1: Evolución de Long COVID por Semana Epidemiológica',
        xaxis_title='Semana Epidemiológica',
        yaxis_title='Número de Casos',
        template='plotly_white',
        hovermode='x unified',
        height=500
    )
    
    return fig


def plot_criterio2_promedio_sintomas(df: pl.DataFrame, color_criterio: str = '#e74c3c') -> go.Figure:
    """
    Promedio de síntomas recurrentes: comparación entre casos que cumplen y no cumplen Criterio 2
    
    Args:
        df: DataFrame con sintoma_recurrente_count y criterio_2
        color_criterio: Color del criterio para visualización
    
    Returns:
        Figura con comparación de promedios
    """
    # Calcular promedios
    promedio_cumplen = df.filter(pl.col('criterio_2') == 1).select(
        pl.col('sintoma_recurrente_count').mean().alias('promedio')
    ).item(0, 0)
    
    promedio_no_cumplen = df.filter(pl.col('criterio_2') == 0).select(
        pl.col('sintoma_recurrente_count').mean().alias('promedio')
    ).item(0, 0)
    
    promedio_total = df.select(
        pl.col('sintoma_recurrente_count').mean().alias('promedio')
    ).item(0, 0)
    
    # Crear figura con subplots: indicadores y barplot
    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{"type": "indicator"}, {"type": "bar"}]],
        subplot_titles=('', '')  # Títulos vacíos, usamos los títulos dentro de cada gráfico
    )
    
    # Indicador de promedio general
    fig.add_trace(
        go.Indicator(
            mode="number+delta",
            value=promedio_total,
            title={"text": "Promedio de Síntomas<br>Recurrentes"},
            number={'valueformat': '.2f'},
            delta={'reference': 2, 'relative': False},
            domain={'x': [0, 1], 'y': [0, 1]}
        ),
        row=1, col=1
    )
    
    # Barplot comparativo
    fig.add_trace(
        go.Bar(
            name='Cumple Criterio 2',
            x=['Cumple Criterio 2'],
            y=[promedio_cumplen],
            marker_color=color_criterio,
            text=[f'{promedio_cumplen:.2f}'],
            textposition='outside'
        ),
        row=1, col=2
    )
    
    fig.add_trace(
        go.Bar(
            name='No Cumple',
            x=['No Cumple'],
            y=[promedio_no_cumplen],
            marker_color='#95a5a6',
            text=[f'{promedio_no_cumplen:.2f}'],
            textposition='outside'
        ),
        row=1, col=2
    )
    
    fig.update_layout(
        title='Criterio 2: Promedio de Síntomas Recurrentes',
        template='plotly_white',
        height=400,
        showlegend=False
    )
    
    fig.update_yaxes(title_text="Promedio de Síntomas", row=1, col=2)
    
    return fig


def plot_criterio2_promedio_sintomas_by_week(df: pl.DataFrame, color_criterio: str = '#e74c3c') -> go.Figure:
    """
    Evolución del promedio de síntomas recurrentes por semana epidemiológica
    Compara casos que cumplen vs no cumplen Criterio 2
    
    Args:
        df: DataFrame con sintoma_recurrente_count, criterio_2 y yearweek
        color_criterio: Color del criterio para visualización
    
    Returns:
        Figura con líneas temporales de promedios
    """
    # Obtener todas las semanas únicas
    all_weeks = sorted(df.select('yearweek').unique().to_series().to_list())
    
    # Calcular promedio por semana para casos que cumplen criterio 2
    promedio_cumplen_week = df.filter(pl.col('criterio_2') == 1).group_by('yearweek').agg(
        pl.col('sintoma_recurrente_count').mean().alias('promedio'),
        pl.len().alias('n_casos')
    ).sort('yearweek')
    
    # Calcular promedio por semana para casos que NO cumplen criterio 2
    promedio_no_cumplen_week = df.filter(pl.col('criterio_2') == 0).group_by('yearweek').agg(
        pl.col('sintoma_recurrente_count').mean().alias('promedio'),
        pl.len().alias('n_casos')
    ).sort('yearweek')
    
    # Crear diccionarios para todas las semanas
    cumplen_dict = {week: None for week in all_weeks}
    no_cumplen_dict = {week: None for week in all_weeks}
    
    for row in promedio_cumplen_week.iter_rows(named=True):
        cumplen_dict[row['yearweek']] = row['promedio']
    
    for row in promedio_no_cumplen_week.iter_rows(named=True):
        no_cumplen_dict[row['yearweek']] = row['promedio']
    
    fig = go.Figure()
    
    # Línea de casos que cumplen Criterio 2
    fig.add_trace(go.Scatter(
        x=all_weeks,
        y=[cumplen_dict[w] for w in all_weeks],
        mode='lines+markers',
        name='Cumple Criterio 2',
        line=dict(color=color_criterio, width=3),
        marker=dict(size=8),
        hovertemplate='Semana: %{x}<br>Promedio: %{y:.2f}<extra></extra>'
    ))
    
    # Línea de casos que NO cumplen Criterio 2
    fig.add_trace(go.Scatter(
        x=all_weeks,
        y=[no_cumplen_dict[w] for w in all_weeks],
        mode='lines+markers',
        name='No Cumple Criterio 2',
        line=dict(color='#95a5a6', width=3),
        marker=dict(size=8),
        hovertemplate='Semana: %{x}<br>Promedio: %{y:.2f}<extra></extra>'
    ))
    
    # Línea de referencia en y=2 (umbral del criterio)
    fig.add_hline(
        y=2, 
        line_dash="dash", 
        line_color="rgba(0,0,0,0.3)",
        annotation_text="Umbral: >1 síntoma",
        annotation_position="right"
    )
    
    fig.update_layout(
        title='Evolución del Promedio de Síntomas Recurrentes por Semana Epidemiológica',
        xaxis_title='Semana Epidemiológica',
        yaxis_title='Promedio de Síntomas Recurrentes',
        template='plotly_white',
        height=500,
        hovermode='x unified',
        xaxis=dict(
            type='category',
            tickangle=-45
        ),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=-0.35,
            xanchor='center',
            x=0.5
        )
    )
    
    return fig


def plot_criterio2_sintomas(df: pl.DataFrame) -> go.Figure:
    """
    Análisis de síntomas recurrentes para criterio 2
    
    Args:
        df: DataFrame con sintoma_recurrente_count y criterio_2
    
    Returns:
        Figura de distribución de síntomas
    """
    sintomas_dist = df.group_by(['sintoma_recurrente_count', 'criterio_2']).agg(
        pl.len().alias('n')
    ).sort('sintoma_recurrente_count')
    
    fig = go.Figure()
    
    for criterio in [0, 1]:
        data = sintomas_dist.filter(pl.col('criterio_2') == criterio)
        fig.add_trace(go.Bar(
            name=f'Criterio 2: {"Cumple" if criterio == 1 else "No cumple"}',
            x=data['sintoma_recurrente_count'].to_list(),
            y=data['n'].to_list(),
            text=data['n'].to_list(),
            textposition='auto',
        ))
    
    fig.update_layout(
        title='Criterio 2: Distribución de Síntomas Recurrentes',
        xaxis_title='Número de Síntomas Recurrentes',
        yaxis_title='Frecuencia',
        barmode='group',
        template='plotly_white',
        height=500
    )
    
    return fig


def plot_criterio2_recovery(df: pl.DataFrame) -> go.Figure:
    """
    Estado de recuperación para criterio 2
    
    Args:
        df: DataFrame con recuperado_3m
    
    Returns:
        Figura de sankey o sunburst
    """
    recovery_data = df.group_by(['recuperado_3m', 'criterio_2']).agg(
        pl.len().alias('n')
    ).sort('recuperado_3m')
    
    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{"type": "pie"}, {"type": "bar"}]],
        subplot_titles=('Estado de Recuperación', 'Por Criterio 2')
    )
    
    # Pie chart general
    recovery_total = df.group_by('recuperado_3m').agg(pl.len().alias('n'))
    labels = []
    for val in recovery_total['recuperado_3m'].to_list():
        if val == 1:
            labels.append('Recuperado')
        elif val == 2:
            labels.append('No Recuperado')
        else:
            labels.append('Sin Datos')
    
    fig.add_trace(
        go.Pie(labels=labels, values=recovery_total['n'].to_list(),
               marker_colors=['#2ecc71', '#e74c3c', '#95a5a6']),
        row=1, col=1
    )
    
    # Bar chart por criterio 2
    for criterio in [0, 1]:
        data = recovery_data.filter(pl.col('criterio_2') == criterio)
        fig.add_trace(
            go.Bar(
                name=f'Criterio 2: {"Cumple" if criterio == 1 else "No cumple"}',
                x=['Recuperado' if x == 1 else 'No Recuperado' if x == 2 else 'Sin Datos' 
                   for x in data['recuperado_3m'].to_list()],
                y=data['n'].to_list(),
                text=data['n'].to_list(),
                textposition='auto',
            ),
            row=1, col=2
        )
    
    fig.update_layout(
        title_text='Criterio 2: Análisis de Recuperación',
        showlegend=True,
        height=500,
        template='plotly_white'
    )
    
    return fig


def plot_variantes_stacked_bar(
    df_variantes: pl.DataFrame,
    df_casos: pl.DataFrame | None = None
) -> go.Figure:
    """
    Barplot apilado de 11 linajes por semana epidemiológica
    + curva de casos positivos de Chile 2020-2021
    
    Args:
        df_variantes: DataFrame con columnas [semana_epi, linaje, n_casos]
        df_casos: DataFrame opcional con casos totales Chile [semana_epi, n_casos_chile]
    
    Returns:
        Figura de Plotly con barras apiladas y línea de casos
    """
    fig = go.Figure()
    
    # Barras apiladas por linaje
    df_pd = df_variantes.to_pandas()
    linajes = df_pd['linaje'].unique()
    
    for linaje in linajes:
        df_linaje = df_pd[df_pd['linaje'] == linaje]
        fig.add_trace(go.Bar(
            name=linaje,
            x=df_linaje['semana_epi'],
            y=df_linaje['n_casos'],
            hovertemplate=f'{linaje}<br>Semana: %{{x}}<br>Casos: %{{y}}<extra></extra>'
        ))
    
    # Agregar curva de casos totales de Chile si está disponible
    if df_casos is not None:
        df_casos_pd = df_casos.to_pandas()
        fig.add_trace(go.Scatter(
            name='Casos Totales Chile',
            x=df_casos_pd['semana_epi'],
            y=df_casos_pd['n_casos_chile'],
            mode='lines+markers',
            line=dict(color='black', width=3),
            yaxis='y2',
            hovertemplate='Semana: %{x}<br>Casos Chile: %{y}<extra></extra>'
        ))
    
    fig.update_layout(
        title='Distribución de Linajes por Semana Epidemiológica (2020-2021)',
        xaxis_title='Semana Epidemiológica',
        yaxis_title='Número de Casos por Linaje',
        barmode='stack',
        template='plotly_white',
        hovermode='x unified',
        legend=dict(orientation='v', x=1.02, y=1),
        yaxis2=dict(
            title='Casos Totales Chile',
            overlaying='y',
            side='right'
        ) if df_casos is not None else {}
    )
    
    return fig


def plot_long_covid_by_variable(
    df: pl.DataFrame,
    variable: str,
    title: str | None = None
) -> go.Figure:
    """
    Barplot de long COVID por semana epidemiológica coloreado por variable
    
    Variables soportadas:
    - longCOVID
    - sintomas_recurrentes_categoria
    - cluster
    - secuelas
    
    Args:
        df: DataFrame con datos de long COVID
        variable: Columna para colorear barras
        title: Título personalizado
    
    Returns:
        Figura de Plotly
    """
    if title is None:
        title = f'Long COVID por Semana Epidemiológica - {variable}'
    
    # Agregar por semana y variable
    df_agg = df.group_by(['semana_epi', variable]).agg(
        pl.len().alias('n_casos')
    ).sort('semana_epi')
    
    fig = px.bar(
        df_agg.to_pandas(),
        x='semana_epi',
        y='n_casos',
        color=variable,
        title=title,
        template='plotly_white',
        barmode='stack'
    )
    
    fig.update_layout(
        xaxis_title='Semana Epidemiológica',
        yaxis_title='Número de Casos',
        hovermode='x unified'
    )
    
    return fig


def plot_clusters_analysis(df: pl.DataFrame) -> go.Figure:
    """
    Análisis de clusters: pertenencia y secuelas por cluster
    
    Args:
        df: DataFrame con columnas [cluster, secuelas]
    
    Returns:
        Figura de Plotly con análisis de clusters
    """
    # Contar casos por cluster y secuelas
    df_agg = df.group_by(['cluster', 'secuelas']).agg(
        pl.len().alias('n_casos')
    )
    
    fig = px.bar(
        df_agg.to_pandas(),
        x='cluster',
        y='n_casos',
        color='secuelas',
        title='Análisis de Clusters: Secuelas por Cluster',
        template='plotly_white',
        barmode='group',
        color_discrete_map={'si': '#e74c3c', 'no': '#2ecc71'}
    )
    
    fig.update_layout(
        xaxis_title='Cluster',
        yaxis_title='Número de Casos',
        legend_title='Tiene Secuelas'
    )
    
    return fig


def create_table_1(df_stats: pl.DataFrame) -> go.Figure:
    """
    Crea Tabla 1 descriptiva como figura de Plotly
    
    Args:
        df_stats: DataFrame con estadísticas descriptivas
    
    Returns:
        Figura de Plotly con tabla
    """
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=list(df_stats.columns),
            fill_color='paleturquoise',
            align='left',
            font=dict(size=12, color='black')
        ),
        cells=dict(
            values=[df_stats[col].to_list() for col in df_stats.columns],
            fill_color='lavender',
            align='left',
            font=dict(size=11)
        )
    )])
    
    fig.update_layout(
        title='Tabla 1: Características Descriptivas del Dataset',
        template='plotly_white'
    )
    
    return fig


def plot_longcovid_by_week(df: pl.DataFrame) -> go.Figure:
    """
    Barplot de casos por semana: Tiene vs No tiene criterio diagnóstico
    Un caso tiene criterio si cumple alguno de los criterios 2, 3 o 4
    
    Args:
        df: DataFrame con columnas yearweek, criterio_2, criterio_3, criterio_4
    
    Returns:
        Figura con barplot apilado binario
    """
    # Obtener todas las semanas únicas ordenadas
    all_weeks = sorted(df.select('yearweek').unique().to_series().to_list())
    
    # Crear variable binaria: tiene criterio si cumple ALGUNO de los 3
    df_cat = df.with_columns(
        pl.when(
            (pl.col('criterio_2') == 1) | 
            (pl.col('criterio_3') == 1) | 
            (pl.col('criterio_4') == 1)
        )
        .then(pl.lit('Tiene criterio'))
        .otherwise(pl.lit('No tiene criterio'))
        .alias('tiene_criterio')
    )
    
    # Agrupar por semana
    df_week = df_cat.group_by(['yearweek', 'tiene_criterio']).agg(
        pl.len().alias('n')
    ).sort('yearweek')
    
    # Crear diccionarios para cada categoría
    tiene_dict = {week: 0 for week in all_weeks}
    no_tiene_dict = {week: 0 for week in all_weeks}
    
    for row in df_week.iter_rows(named=True):
        if row['tiene_criterio'] == 'Tiene criterio':
            tiene_dict[row['yearweek']] = row['n']
        else:
            no_tiene_dict[row['yearweek']] = row['n']
    
    fig = go.Figure()
    
    # Agregar barras apiladas
    fig.add_trace(go.Bar(
        x=all_weeks,
        y=[tiene_dict[w] for w in all_weeks],
        name='Tiene criterio',
        marker_color='#e74c3c'  # Rojo
    ))
    
    fig.add_trace(go.Bar(
        x=all_weeks,
        y=[no_tiene_dict[w] for w in all_weeks],
        name='No tiene criterio',
        marker_color='#3498db'  # Azul
    ))
    
    fig.update_layout(
        title='Casos por Semana Epidemiológica - Criterios Diagnósticos',
        xaxis_title='Semana Epidemiológica',
        yaxis_title='Número de Casos',
        barmode='stack',
        template='plotly_white',
        height=500,
        xaxis=dict(
            type='category',
            tickangle=-45
        ),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=-0.35,
            xanchor='center',
            x=0.5
        )
    )
    
    return fig


def plot_sintomas_recurrentes_by_week(df: pl.DataFrame) -> go.Figure:
    """
    Histograma de distribución de síntomas recurrentes
    Muestra cuántas personas tienen 0, 1, 2, 3, 4+ síntomas
    
    Args:
        df: DataFrame con columna sintoma_recurrente_count
    
    Returns:
        Figura con histograma de barras
    """
    # Crear categorías de síntomas recurrentes
    df_cat = df.with_columns(
        pl.when(pl.col('sintoma_recurrente_count') == 0)
        .then(pl.lit('0'))
        .when(pl.col('sintoma_recurrente_count') == 1)
        .then(pl.lit('1'))
        .when(pl.col('sintoma_recurrente_count') == 2)
        .then(pl.lit('2'))
        .when(pl.col('sintoma_recurrente_count') == 3)
        .then(pl.lit('3'))
        .otherwise(pl.lit('4+'))
        .alias('categoria_sintomas')
    )
    
    # Contar personas por categoría
    df_hist = df_cat.group_by('categoria_sintomas').agg(
        pl.len().alias('n')
    )
    
    # Ordenar categorías
    categorias_orden = ['0', '1', '2', '3', '4+']
    cat_dict = {row['categoria_sintomas']: row['n'] for row in df_hist.iter_rows(named=True)}
    
    x_vals = []
    y_vals = []
    for cat in categorias_orden:
        x_vals.append(cat)
        y_vals.append(cat_dict.get(cat, 0))
    
    # Colores según cantidad de síntomas
    colores = ['#54C6C4', '#81C784', '#FFB74D', '#E57373', '#BA68C8']
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=x_vals,
        y=y_vals,
        marker_color=colores,
        text=y_vals,
        textposition='outside',
        showlegend=False
    ))
    
    fig.update_layout(
        title='Distribución de Síntomas Recurrentes',
        xaxis_title='Número de Síntomas Recurrentes',
        yaxis_title='Número de Personas',
        template='plotly_white',
        height=500,
        xaxis=dict(type='category')
    )
    
    return fig


def plot_cluster_pertenencia_by_week(df: pl.DataFrame) -> go.Figure:
    """
    Barplot por semana coloreado por pertenencia a clusters
    
    Args:
        df: DataFrame con columnas yearweek y pertenece_cluster_count
    
    Returns:
        Figura con barplot apilado
    """
    # Obtener todas las semanas únicas
    all_weeks = sorted(df.select('yearweek').unique().to_series().to_list())
    
    # Crear variable binaria de pertenencia
    df_cat = df.with_columns(
        pl.when(pl.col('pertenece_cluster_count') >= 1)
        .then(pl.lit('Pertenece a cluster'))
        .otherwise(pl.lit('No pertenece'))
        .alias('pertenece_cluster')
    )
    
    # Agrupar
    df_week = df_cat.group_by(['yearweek', 'pertenece_cluster']).agg(
        pl.len().alias('n')
    ).sort('yearweek')
    
    # Crear diccionarios para cada categoría
    pertenece_dict = {week: 0 for week in all_weeks}
    no_pertenece_dict = {week: 0 for week in all_weeks}
    
    for row in df_week.iter_rows(named=True):
        if row['pertenece_cluster'] == 'Pertenece a cluster':
            pertenece_dict[row['yearweek']] = row['n']
        else:
            no_pertenece_dict[row['yearweek']] = row['n']
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=all_weeks,
        y=[pertenece_dict[w] for w in all_weeks],
        name='Pertenece a cluster',
        marker_color='#e74c3c'
    ))
    
    fig.add_trace(go.Bar(
        x=all_weeks,
        y=[no_pertenece_dict[w] for w in all_weeks],
        name='No pertenece',
        marker_color='#95a5a6'
    ))
    
    fig.update_layout(
        title='Casos por Semana Epidemiológica - Pertenencia a Clusters',
        xaxis_title='Semana Epidemiológica',
        yaxis_title='Número de Casos',
        barmode='stack',
        template='plotly_white',
        height=500,
        xaxis=dict(
            type='category',
            tickangle=-45
        )
    )
    
    return fig


def plot_clusters_individuales_by_week(df: pl.DataFrame) -> go.Figure:
    """
    Barplot apilado por semana mostrando cada cluster individual con su color
    
    Args:
        df: DataFrame con columnas de clusters binarios
    
    Returns:
        Figura con barplot apilado multicolor
    """
    # Obtener todas las semanas únicas
    all_weeks = sorted(df.select('yearweek').unique().to_series().to_list())
    
    # Clusters disponibles con sus colores
    clusters = [
        ('cluster_cognitivo_bi', 'Cognitivo', '#9b59b6'),
        ('cluster_gastrointestinal_bi', 'Gastrointestinal', '#e67e22'),
        ('cluster_muscular_bi', 'Muscular', '#e74c3c'),
        ('cluster_olfato_gusto_bi', 'Olfato/Gusto', '#f39c12'),
        ('cluster_respiratorio_bi', 'Respiratorio', '#3498db'),
        ('cluster_via_aerea_bi', 'Vía Aérea', '#1abc9c')
    ]
    
    fig = go.Figure()
    
    # Agregar cada cluster como una traza apilada
    for col, name, color in clusters:
        # Agrupar por semana para este cluster
        df_cluster = df.filter(pl.col(col) == 1).group_by('yearweek').agg(
            pl.len().alias('n')
        ).sort('yearweek')
        
        # Crear diccionario con todas las semanas
        cluster_dict = {week: 0 for week in all_weeks}
        for row in df_cluster.iter_rows(named=True):
            cluster_dict[row['yearweek']] = row['n']
        
        # Agregar traza
        fig.add_trace(go.Bar(
            x=all_weeks,
            y=[cluster_dict[w] for w in all_weeks],
            name=name,
            marker_color=color
        ))
    
    fig.update_layout(
        title='Casos por Semana Epidemiológica - Clusters Individuales',
        xaxis_title='Semana Epidemiológica',
        yaxis_title='Número de Casos',
        barmode='stack',
        template='plotly_white',
        height=500,
        xaxis=dict(
            type='category',
            tickangle=-45
        ),
        legend=dict(
            orientation='v',
            yanchor='top',
            y=1,
            xanchor='right',
            x=1.15
        )
    )
    
    return fig


def plot_secuelas_by_week(df: pl.DataFrame) -> go.Figure:
    """
    Barplot por semana coloreado por tiene o no secuelas
    
    Args:
        df: DataFrame con columnas yearweek y sec_count
    
    Returns:
        Figura con barplot apilado
    """
    # Obtener todas las semanas únicas
    all_weeks = sorted(df.select('yearweek').unique().to_series().to_list())
    
    # Crear variable binaria de secuelas
    df_cat = df.with_columns(
        pl.when(pl.col('sec_count') >= 1)
        .then(pl.lit('Con secuelas'))
        .otherwise(pl.lit('Sin secuelas'))
        .alias('tiene_secuelas')
    )
    
    # Agrupar
    df_week = df_cat.group_by(['yearweek', 'tiene_secuelas']).agg(
        pl.len().alias('n')
    ).sort('yearweek')
    
    # Crear diccionarios para cada categoría
    con_dict = {week: 0 for week in all_weeks}
    sin_dict = {week: 0 for week in all_weeks}
    
    for row in df_week.iter_rows(named=True):
        if row['tiene_secuelas'] == 'Con secuelas':
            con_dict[row['yearweek']] = row['n']
        else:
            sin_dict[row['yearweek']] = row['n']
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=all_weeks,
        y=[con_dict[w] for w in all_weeks],
        name='Con secuelas',
        marker_color='#e74c3c'
    ))
    
    fig.add_trace(go.Bar(
        x=all_weeks,
        y=[sin_dict[w] for w in all_weeks],
        name='Sin secuelas',
        marker_color='#3498db'
    ))
    
    fig.update_layout(
        title='Casos por Semana Epidemiológica - Secuelas',
        xaxis_title='Semana Epidemiológica',
        yaxis_title='Número de Casos',
        barmode='stack',
        template='plotly_white',
        height=500,
        xaxis=dict(
            type='category',
            tickangle=-45
        )
    )
    
    return fig


def plot_clusters_heatmap_by_diagnosis_week(df: pl.DataFrame) -> go.Figure:
    """
    Heatmap de clusters por semana de diagnóstico COVID
    Muestra el número de personas diagnosticadas cada semana que tienen cada cluster
    
    Args:
        df: DataFrame con columnas de clusters y covid_dg_fecha
    
    Returns:
        Figura con heatmap de clusters x semanas
    """
    # Clusters disponibles
    clusters_info = [
        ('cluster_via_aerea_bi', 'AIRWAYS'),
        ('cluster_cognitivo_bi', 'COGNITIVE'),
        ('cluster_gastrointestinal_bi', 'GASTROINTESTINAL'),
        ('cluster_muscular_bi', 'MUSCULAR'),
        ('cluster_respiratorio_bi', 'RESPIRATORY'),
        ('cluster_olfato_gusto_bi', 'SMELL/TASTE'),
        ('longCOVID', 'Long-COVID')
    ]
    
    # Convertir fecha de diagnóstico a yearweek si no existe
    # Usar yearweek existente como aproximación
    df_heat = df.select(['yearweek'] + [col for col, _ in clusters_info])
    
    # Obtener semanas únicas ordenadas
    all_weeks = sorted(df_heat.select('yearweek').unique().to_series().to_list())
    
    # Crear matriz de datos
    heatmap_data = []
    cluster_labels = []
    
    for col, label in clusters_info:
        cluster_labels.append(label)
        row_data = []
        
        # Contar casos por semana para este cluster
        df_cluster = df_heat.filter(pl.col(col) == 1).group_by('yearweek').agg(
            pl.len().alias('n')
        )
        
        # Crear diccionario
        week_dict = {week: 0 for week in all_weeks}
        for row in df_cluster.iter_rows(named=True):
            week_dict[row['yearweek']] = row['n']
        
        # Agregar datos en orden
        row_data = [week_dict[w] for w in all_weeks]
        heatmap_data.append(row_data)
    
    # Crear heatmap
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data,
        x=all_weeks,
        y=cluster_labels,
        colorscale='Viridis',
        colorbar=dict(title='Number of individuals'),
        hoverongaps=False,
        hovertemplate='Semana: %{x}<br>Cluster: %{y}<br>Casos: %{z}<extra></extra>'
    ))
    
    fig.update_layout(
        title='Clusters/Phenotype - Síntomas ≥ 3 meses por Semana de Diagnóstico',
        xaxis_title='Semana Epidemiológica',
        yaxis_title='Cluster/Phenotype',
        template='plotly_white',
        height=500,
        xaxis=dict(
            type='category',
            tickangle=-45,
            side='bottom'
        ),
        yaxis=dict(
            side='left',
            autorange='reversed'
        )
    )
    
    return fig


def plot_criterio_barplot(df: pl.DataFrame, criterio_num: int, titulo: str | None = None, color_criterio: str | None = None) -> go.Figure:
    """
    Barplot por semana epidemiológica mostrando cumple vs no cumple para un criterio
    
    Args:
        df: DataFrame con columna de criterio y yearweek
        criterio_num: Número del criterio (1, 2, 3, 4)
        titulo: Título personalizado (opcional)
        color_criterio: Color específico del criterio (opcional, por defecto verde)
    
    Returns:
        Figura con barplot apilado por semana
    """
    col_name = f'criterio_{criterio_num}' if criterio_num > 1 else 'longCOVID'
    
    # Color por defecto si no se proporciona
    if color_criterio is None:
        color_criterio = '#27ae60'
    
    # Obtener todas las semanas únicas
    all_weeks = sorted(df.select('yearweek').unique().to_series().to_list())
    
    # Crear variable de cumple/no cumple
    df_cat = df.with_columns(
        pl.when(pl.col(col_name) == 1)
        .then(pl.lit('Cumple criterio'))
        .otherwise(pl.lit('No cumple'))
        .alias('cumple_criterio')
    )
    
    # Agrupar por semana
    df_week = df_cat.group_by(['yearweek', 'cumple_criterio']).agg(
        pl.len().alias('n')
    ).sort('yearweek')
    
    # Crear diccionarios
    cumple_dict = {week: 0 for week in all_weeks}
    no_cumple_dict = {week: 0 for week in all_weeks}
    
    for row in df_week.iter_rows(named=True):
        if row['cumple_criterio'] == 'Cumple criterio':
            cumple_dict[row['yearweek']] = row['n']
        else:
            no_cumple_dict[row['yearweek']] = row['n']
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=all_weeks,
        y=[cumple_dict[w] for w in all_weeks],
        name='Cumple criterio',
        marker_color=color_criterio
    ))
    
    fig.add_trace(go.Bar(
        x=all_weeks,
        y=[no_cumple_dict[w] for w in all_weeks],
        name='No cumple',
        marker_color='#95a5a6'
    ))
    
    if titulo is None:
        titulo = f'Criterio {criterio_num}: Casos por Semana Epidemiológica'
    
    fig.update_layout(
        title=titulo,
        xaxis_title='Semana Epidemiológica',
        yaxis_title='Número de Casos',
        template='plotly_white',
        height=500,
        barmode='stack',
        xaxis=dict(
            type='category',
            tickangle=-45
        )
    )
    
    return fig
