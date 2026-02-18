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
    Heatmap de SÍNTOMAS ordenados por cluster, por semana de diagnóstico COVID
    Muestra la prevalencia de cada síntoma individual agrupado por cluster
    
    Args:
        df: DataFrame con columnas de síntomas a 3 meses y yearweek
    
    Returns:
        Figura con heatmap de síntomas (ordenados por cluster) x semanas
    """
    # Definición de clusters con sus síntomas individuales
    # Cada tupla: (variable_sintoma, nombre_mostrar, cluster_grupo)
    sintomas_por_cluster = [
        # AIRWAYS cluster
        ('congestion_3m', 'Nasal congestion', 'AIRWAYS'),
        ('tos_3m', 'Cough', 'AIRWAYS'),
        ('', 'Phlegm', 'AIRWAYS'),  # No disponible en dataset
        ('do_garganta_3m', 'Sore throat', 'AIRWAYS'),
        
        # COGNITIVE cluster
        ('depresion_3m', 'Depression/Anxiety', 'COGNITIVE'),
        ('memoria_3m', 'Memory impairment', 'COGNITIVE'),
        ('do_cabeza_3m', 'Headache', 'COGNITIVE'),
        ('somnolencia_3m', 'Drowsiness', 'COGNITIVE'),
        
        # GASTROINTESTINAL cluster
        ('do_abdominal_3m', 'Abdominal pain', 'GASTROINTESTINAL'),
        ('nausea_3m', 'Nausea', 'GASTROINTESTINAL'),
        ('hin_piernas_3m', 'Edema (swollen legs)', 'GASTROINTESTINAL'),
        ('diarrea_3m', 'Diarrhea', 'GASTROINTESTINAL'),
        ('pe_peso_3m', 'Weight loss', 'GASTROINTESTINAL'),
        ('apetito_3m', 'Change in appetite', 'GASTROINTESTINAL'),
        
        # MUSCULAR cluster
        ('do_musculos_3m', 'Muscle pain', 'MUSCULAR'),
        ('do_articulacion_3m', 'Joint pain', 'MUSCULAR'),
        ('pes_piernas_3m', 'Legs feel heavy', 'MUSCULAR'),
        
        # RESPIRATORY cluster
        ('fa_aliento_3m', 'Shortness of breath', 'RESPIRATORY'),
        ('fatiga_3m', 'Fatigue', 'RESPIRATORY'),
        ('do_pecho_3m', 'Chest pain', 'RESPIRATORY'),
        ('di_respirar_3m', 'Breathing difficulty', 'RESPIRATORY'),
        
        # SMELL/TASTE cluster
        ('pe_olfato_3m', 'Anosmia', 'SMELL/TASTE'),
        ('ca_olfato_3m', 'Change in smell', 'SMELL/TASTE'),
        ('pe_gusto_3m', 'Ageusia', 'SMELL/TASTE'),
        ('ca_gusto_3m', 'Change in taste', 'SMELL/TASTE'),
    ]
    
    # Obtener semanas únicas ordenadas
    all_weeks = sorted(df.select('yearweek').unique().to_series().to_list())
    
    # Crear matriz de datos y etiquetas
    heatmap_data = []
    symptom_labels = []
    cluster_boundaries = []  # Para marcar separación entre clusters
    
    current_cluster = None
    row_idx = 0
    
    for var_col, label, cluster in sintomas_por_cluster:
        # Detectar cambio de cluster para agregar separador visual
        if cluster != current_cluster:
            if current_cluster is not None:
                # Agregar línea separadora (fila vacía)
                cluster_boundaries.append(row_idx)
            current_cluster = cluster
        
        symptom_labels.append(f"{label}")
        
        # Si la columna no existe o está vacía, agregar fila con ceros
        if not var_col or var_col not in df.columns:
            heatmap_data.append([0] * len(all_weeks))
            row_idx += 1
            continue
        
        # Contar casos por semana para este síntoma (valor == 1)
        row_data = []
        for week in all_weeks:
            # Filtrar por semana y síntoma presente (==1)
            count = df.filter(
                (pl.col('yearweek') == week) & 
                (pl.col(var_col) == 1)
            ).height
            row_data.append(count)
        
        heatmap_data.append(row_data)
        row_idx += 1
    
    # Crear anotaciones para nombres de clusters (a la izquierda)
    annotations = []
    cluster_ranges = {
        'AIRWAYS': (0, 4),
        'COGNITIVE': (4, 8),
        'GASTROINTESTINAL': (8, 14),
        'MUSCULAR': (14, 17),
        'RESPIRATORY': (17, 21),
        'SMELL/TASTE': (21, 25)
    }
    
    # Crear heatmap
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data,
        x=all_weeks,
        y=symptom_labels,
        colorscale='Viridis',
        colorbar=dict(title='N° individuals'),
        hoverongaps=False,
        hovertemplate='Week: %{x}<br>Symptom: %{y}<br>Cases: %{z}<extra></extra>'
    ))
    
    # Agregar líneas divisorias entre clusters
    shapes = []
    for boundary_idx in cluster_boundaries:
        shapes.append(dict(
            type='line',
            x0=-0.5,
            x1=len(all_weeks) - 0.5,
            y0=boundary_idx - 0.5,
            y1=boundary_idx - 0.5,
            line=dict(color='white', width=2)
        ))
    
    fig.update_layout(
        title='Symptoms at ≥3 months (ordered by cluster) by Week of Diagnosis',
        xaxis_title='Epidemiological Week',
        yaxis_title='Symptoms (grouped by cluster)',
        template='plotly_white',
        height=800,  # Más alto para mostrar todos los síntomas
        width=1400,
        xaxis=dict(
            type='category',
            tickangle=-45,
            side='bottom'
        ),
        yaxis=dict(
            side='left',
            autorange='reversed',
            tickfont=dict(size=10)
        ),
        shapes=shapes
    )
    
    return fig


def plot_criterio3_clusters_comparison(df: pl.DataFrame, color_criterio: str = '#f39c12') -> go.Figure:
    """
    Comparación de clusters individuales entre casos que cumplen vs no cumplen Criterio 3
    Barplot horizontal mostrando cada cluster con separación por sexo
    
    Args:
        df: DataFrame con columnas de clusters, criterio_3 y sexo
        color_criterio: Color del criterio para casos que cumplen
    
    Returns:
        Figura con barplot horizontal comparativo
    """
    # Definición de clusters con sus nombres
    clusters_info = [
        ('cluster_via_aerea_bi', 'AIRWAYS', ['Nasal congestion', 'Cough', 'Phlegm', 'Sore throat']),
        ('cluster_cognitivo_bi', 'COGNITIVE', ['Depression or anxiety', 'Memory impairment', 'Headache', 'Drowsiness']),
        ('cluster_gastrointestinal_bi', 'GASTRO-INTESTINAL', ['Abdominal pain', 'Nausea', 'Chiken legs (edema)', 'Diarrhea', 'Weight loss', 'Change in appetite']),
        ('cluster_muscular_bi', 'MUSCULAR', ['Muscle pain', 'Joint pain', 'Legs feel heavy']),
        ('cluster_respiratorio_bi', 'RESPIRATORY', ['Shortness of breath', 'Fatigue', 'Chest pain', 'Breathing difficulty']),
        ('cluster_olfato_gusto_bi', 'SMELL/TASTE', ['Anosmia', 'Change in smell', 'Ageusia', 'Change in taste']),
    ]
    
    # Filtrar casos con datos completos en criterio_3 (sin nulls en recuperado_3m)
    df_sin_nulls = df.filter(~pl.col('recuperado_3m').is_null())
    
    # Crear datos para el gráfico
    plot_data = []
    
    for col, nombre, sintomas in clusters_info:
        # Casos que cumplen Criterio 3
        casos_cumple = df_sin_nulls.filter(pl.col('criterio_3') == 1)
        
        # Casos femeninos que cumplen y tienen el cluster
        casos_f = casos_cumple.filter(
            (pl.col(col) == 1) & (pl.col('sexo') == 2)
        ).height
        
        # Casos masculinos que cumplen y tienen el cluster
        casos_m = casos_cumple.filter(
            (pl.col(col) == 1) & (pl.col('sexo') == 1)
        ).height
        
        # Controles (no cumplen Criterio 3)
        controles = df_sin_nulls.filter(pl.col('criterio_3') == 0)
        
        # Controles femeninos con el cluster
        controles_f = controles.filter(
            (pl.col(col) == 1) & (pl.col('sexo') == 2)
        ).height
        
        # Controles masculinos con el cluster
        controles_m = controles.filter(
            (pl.col(col) == 1) & (pl.col('sexo') == 1)
        ).height
        
        plot_data.append({
            'cluster': nombre,
            'sintomas': '<br>'.join(sintomas),
            'casos_f': casos_f,
            'casos_m': casos_m,
            'controles_f': controles_f,
            'controles_m': controles_m
        })
    
    # Crear figura
    fig = go.Figure()
    
    # Orden inverso para que aparezcan de arriba hacia abajo como en la imagen
    clusters_names = [d['cluster'] for d in plot_data]
    
    # Barras para casos femeninos (morado)
    fig.add_trace(go.Bar(
        name='Cases Female',
        y=clusters_names,
        x=[d['casos_f'] for d in plot_data],
        orientation='h',
        marker=dict(color='#8B7AB8'),
        text=[d['casos_f'] for d in plot_data],
        textposition='inside',
        hovertemplate='%{y}<br>Cases Female: %{x}<extra></extra>'
    ))
    
    # Barras para casos masculinos (verde claro)
    fig.add_trace(go.Bar(
        name='Cases Male',
        y=clusters_names,
        x=[d['casos_m'] for d in plot_data],
        orientation='h',
        marker=dict(color='#90C695'),
        text=[d['casos_m'] for d in plot_data],
        textposition='inside',
        hovertemplate='%{y}<br>Cases Male: %{x}<extra></extra>'
    ))
    
    # Barras para controles femeninos (azul/morado más claro)
    fig.add_trace(go.Bar(
        name='Controls Female',
        y=clusters_names,
        x=[d['controles_f'] for d in plot_data],
        orientation='h',
        marker=dict(color='#B8B0D4'),
        text=[d['controles_f'] for d in plot_data],
        textposition='inside',
        hovertemplate='%{y}<br>Controls Female: %{x}<extra></extra>'
    ))
    
    # Barras para controles masculinos (verde más claro)
    fig.add_trace(go.Bar(
        name='Controls Male',
        y=clusters_names,
        x=[d['controles_m'] for d in plot_data],
        orientation='h',
        marker=dict(color='#C8D9CA'),
        text=[d['controles_m'] for d in plot_data],
        textposition='inside',
        hovertemplate='%{y}<br>Controls Male: %{x}<extra></extra>'
    ))
    
    fig.update_layout(
        title='Criterio 3: Clusters por Casos vs Controles (separado por Sexo)',
        xaxis_title='Número de Personas',
        yaxis_title='Cluster/Phenotype',
        barmode='stack',
        template='plotly_white',
        height=600,
        legend=dict(
            orientation='v',
            yanchor='top',
            y=1.0,
            xanchor='right',
            x=1.15
        ),
        yaxis=dict(
            categoryorder='array',
            categoryarray=clusters_names[::-1]  # Invertir orden
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


def plot_criterios_null_impact(null_analysis: dict, colores_criterios: dict) -> go.Figure:
    """
    Visualiza el impacto de los valores NULL en cada criterio.
    Compara casos totales vs casos con datos completos.
    
    Args:
        null_analysis: Dict con análisis de NULLs por criterio (resultado de analyze_criterios_null_impact)
        colores_criterios: Dict con los colores para cada criterio
    
    Returns:
        Figura de Plotly con comparación de NULLs
    """
    criterios = ['criterio_1', 'criterio_2', 'criterio_3', 'criterio_4']
    criterios_labels = ['Criterio 1', 'Criterio 2', 'Criterio 3', 'Criterio 4']
    
    total_casos = [null_analysis[c]['total_casos'] for c in criterios]
    casos_completos = [null_analysis[c]['casos_con_datos_completos'] for c in criterios]
    casos_perdidos = [null_analysis[c]['casos_perdidos'] for c in criterios]
    
    fig = go.Figure()
    
    # Barras de casos con datos completos
    fig.add_trace(go.Bar(
        name='Casos con datos completos',
        x=criterios_labels,
        y=casos_completos,
        marker=dict(
            color=[colores_criterios[c] for c in criterios],
            line=dict(width=2, color='white')
        ),
        text=casos_completos,
        textposition='inside',
        textfont=dict(color='white', size=14),
        hovertemplate='%{x}<br>Casos con datos completos: %{y}<extra></extra>'
    ))
    
    # Barras de casos perdidos por NULLs
    fig.add_trace(go.Bar(
        name='Casos perdidos (con NULLs)',
        x=criterios_labels,
        y=casos_perdidos,
        marker=dict(
            color='#e74c3c',
            opacity=0.6,
            line=dict(width=2, color='white')
        ),
        text=[f'{cp} ({null_analysis[criterios[i]]["porcentaje_perdido"]:.1f}%)' if cp > 0 else ''
              for i, cp in enumerate(casos_perdidos)],
        textposition='inside',
        textfont=dict(color='white', size=12),
        hovertemplate='%{x}<br>Casos perdidos: %{y} (%{text})<extra></extra>'
    ))
    
    fig.update_layout(
        title='Impacto de Valores NULL en los Criterios de Long COVID',
        xaxis_title='Criterio',
        yaxis_title='Número de Casos',
        template='plotly_white',
        height=600,
        barmode='stack',
        legend=dict(
            orientation='h',
            yanchor='top',
            y=-0.15,
            xanchor='center',
            x=0.5
        ),
        # Añadir anotación con total
        annotations=[
            dict(
                x=i,
                y=total_casos[i] + 20,
                text=f'<b>Total: {total_casos[i]}</b>',
                showarrow=False,
                font=dict(size=12, color='#2c3e50')
            )
            for i in range(len(criterios_labels))
        ]
    )
    
    return fig


def plot_cases_by_week_by_sex(df: pl.DataFrame) -> go.Figure:
    """
    Barplot de casos por semana epidemiológica coloreado por sexo
    
    Args:
        df: DataFrame con columnas yearweek y sexo
    
    Returns:
        Figura con barplot apilado por sexo
    """
    # Obtener todas las semanas únicas
    all_weeks = sorted(df.select('yearweek').unique().to_series().to_list())
    
    # Agrupar por semana y sexo
    df_week = df.group_by(['yearweek', 'sexo']).agg(
        pl.len().alias('n')
    ).sort('yearweek')
    
    # Crear diccionarios para cada sexo
    femenino_dict = {week: 0 for week in all_weeks}
    masculino_dict = {week: 0 for week in all_weeks}
    
    for row in df_week.iter_rows(named=True):
        sexo_val = row['sexo']
        if sexo_val == 1:  # Femenino
            femenino_dict[row['yearweek']] = row['n']
        elif sexo_val == 2:  # Masculino
            masculino_dict[row['yearweek']] = row['n']
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=all_weeks,
        y=[femenino_dict[w] for w in all_weeks],
        name='Femenino',
        marker_color='#e74c3c'  # Rojo
    ))
    
    fig.add_trace(go.Bar(
        x=all_weeks,
        y=[masculino_dict[w] for w in all_weeks],
        name='Masculino',
        marker_color='#3498db'  # Azul
    ))
    
    fig.update_layout(
        title='Casos por Semana Epidemiológica - Distribución por Sexo',
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


def plot_cases_by_week_by_age_group(df: pl.DataFrame) -> go.Figure:
    """
    Barplot de casos por semana epidemiológica coloreado por grupo etario
    
    Args:
        df: DataFrame con columnas yearweek y edad_entrevistado
    
    Returns:
        Figura con barplot apilado por grupos de edad
    """
    # Obtener todas las semanas únicas
    all_weeks = sorted(df.select('yearweek').unique().to_series().to_list())
    
    # Crear grupos etarios
    df_cat = df.with_columns(
        pl.when(pl.col('edad_entrevistado') < 30)
        .then(pl.lit('<30'))
        .when((pl.col('edad_entrevistado') >= 30) & (pl.col('edad_entrevistado') < 45))
        .then(pl.lit('30-44'))
        .when((pl.col('edad_entrevistado') >= 45) & (pl.col('edad_entrevistado') < 60))
        .then(pl.lit('45-59'))
        .otherwise(pl.lit('≥60'))
        .alias('grupo_edad')
    )
    
    # Agrupar por semana y grupo
    df_week = df_cat.group_by(['yearweek', 'grupo_edad']).agg(
        pl.len().alias('n')
    ).sort('yearweek')
    
    # Colores por grupo
    grupos = ['<30', '30-44', '45-59', '≥60']
    colores = ['#3498db', '#2ecc71', '#f39c12', '#e74c3c']
    
    # Crear diccionarios para cada grupo
    grupos_dict = {grupo: {week: 0 for week in all_weeks} for grupo in grupos}
    
    for row in df_week.iter_rows(named=True):
        grupo = row['grupo_edad']
        if grupo in grupos_dict:
            grupos_dict[grupo][row['yearweek']] = row['n']
    
    fig = go.Figure()
    
    for grupo, color in zip(grupos, colores):
        fig.add_trace(go.Bar(
            x=all_weeks,
            y=[grupos_dict[grupo][w] for w in all_weeks],
            name=grupo,
            marker_color=color
        ))
    
    fig.update_layout(
        title='Casos por Semana Epidemiológica - Distribución por Grupo Etario',
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


def plot_cases_by_week_by_secuelas(df: pl.DataFrame) -> go.Figure:
    """
    Barplot de casos por semana epidemiológica coloreado por presencia de secuelas
    
    Args:
        df: DataFrame con columnas yearweek y sec_count
    
    Returns:
        Figura con barplot apilado por secuelas
    """
    # Obtener todas las semanas únicas
    all_weeks = sorted(df.select('yearweek').unique().to_series().to_list())
    
    # Crear categoría binaria
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
    
    # Crear diccionarios
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
        marker_color='#e74c3c'  # Rojo
    ))
    
    fig.add_trace(go.Bar(
        x=all_weeks,
        y=[sin_dict[w] for w in all_weeks],
        name='Sin secuelas',
        marker_color='#2ecc71'  # Verde
    ))
    
    fig.update_layout(
        title='Casos por Semana Epidemiológica - Presencia de Secuelas',
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


def plot_cases_by_week_by_nueva_condicion(df: pl.DataFrame) -> go.Figure:
    """
    Barplot de casos por semana epidemiológica coloreado por nueva condición
    
    Args:
        df: DataFrame con columnas yearweek y conteo_nueva_condicion
    
    Returns:
        Figura con barplot apilado por nueva condición
    """
    # Obtener todas las semanas únicas
    all_weeks = sorted(df.select('yearweek').unique().to_series().to_list())
    
    # Crear categoría binaria
    df_cat = df.with_columns(
        pl.when(pl.col('conteo_nueva_condicion') >= 1)
        .then(pl.lit('Con nueva condición'))
        .otherwise(pl.lit('Sin nueva condición'))
        .alias('tiene_nueva_condicion')
    )
    
    # Agrupar
    df_week = df_cat.group_by(['yearweek', 'tiene_nueva_condicion']).agg(
        pl.len().alias('n')
    ).sort('yearweek')
    
    # Crear diccionarios
    con_dict = {week: 0 for week in all_weeks}
    sin_dict = {week: 0 for week in all_weeks}
    
    for row in df_week.iter_rows(named=True):
        if row['tiene_nueva_condicion'] == 'Con nueva condición':
            con_dict[row['yearweek']] = row['n']
        else:
            sin_dict[row['yearweek']] = row['n']
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=all_weeks,
        y=[con_dict[w] for w in all_weeks],
        name='Con nueva condición',
        marker_color='#9b59b6'  # Morado
    ))
    
    fig.add_trace(go.Bar(
        x=all_weeks,
        y=[sin_dict[w] for w in all_weeks],
        name='Sin nueva condición',
        marker_color='#95a5a6'  # Gris
    ))
    
    fig.update_layout(
        title='Casos por Semana Epidemiológica - Nueva Condición Médica',
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


def plot_cases_by_week_by_sintomas_recurrentes(df: pl.DataFrame) -> go.Figure:
    """
    Barplot de casos por semana epidemiológica coloreado por síntomas recurrentes
    
    Args:
        df: DataFrame con columnas yearweek y sintoma_recurrente_count
    
    Returns:
        Figura con barplot apilado por nivel de síntomas
    """
    # Obtener todas las semanas únicas
    all_weeks = sorted(df.select('yearweek').unique().to_series().to_list())
    
    # Crear categorías de síntomas
    df_cat = df.with_columns(
        pl.when(pl.col('sintoma_recurrente_count') == 0)
        .then(pl.lit('0 síntomas'))
        .when(pl.col('sintoma_recurrente_count') == 1)
        .then(pl.lit('1 síntoma'))
        .when(pl.col('sintoma_recurrente_count') == 2)
        .then(pl.lit('2 síntomas'))
        .when(pl.col('sintoma_recurrente_count') == 3)
        .then(pl.lit('3 síntomas'))
        .otherwise(pl.lit('4+ síntomas'))
        .alias('categoria_sintomas')
    )
    
    # Agrupar
    df_week = df_cat.group_by(['yearweek', 'categoria_sintomas']).agg(
        pl.len().alias('n')
    ).sort('yearweek')
    
    # Categorías y colores
    categorias = ['0 síntomas', '1 síntoma', '2 síntomas', '3 síntomas', '4+ síntomas']
    colores = ['#95a5a6', '#3498db', '#f39c12', '#e67e22', '#e74c3c']
    
    # Crear diccionarios
    cat_dict = {cat: {week: 0 for week in all_weeks} for cat in categorias}
    
    for row in df_week.iter_rows(named=True):
        cat = row['categoria_sintomas']
        if cat in cat_dict:
            cat_dict[cat][row['yearweek']] = row['n']
    
    fig = go.Figure()
    
    for cat, color in zip(categorias, colores):
        fig.add_trace(go.Bar(
            x=all_weeks,
            y=[cat_dict[cat][w] for w in all_weeks],
            name=cat,
            marker_color=color
        ))
    
    fig.update_layout(
        title='Casos por Semana Epidemiológica - Síntomas Recurrentes',
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


def plot_cases_by_week_by_criterio_3_sin_nulls(df: pl.DataFrame) -> go.Figure:
    """
    Barplot de casos por semana epidemiológica para Criterio 3, omitiendo nulls en recuperado_3m
    
    Args:
        df: DataFrame con columnas yearweek, criterio_3 y recuperado_3m
    
    Returns:
        Figura con barplot apilado por criterio 3 (sin casos con nulls)
    """
    # Filtrar nulls en recuperado_3m (variable crítica para criterio_3)
    df_sin_nulls = df.filter(~pl.col('recuperado_3m').is_null())
    
    # Obtener todas las semanas únicas
    all_weeks = sorted(df_sin_nulls.select('yearweek').unique().to_series().to_list())
    
    # Agrupar por semana y criterio_3
    df_week = df_sin_nulls.group_by(['yearweek', 'criterio_3']).agg(
        pl.len().alias('n')
    ).sort('yearweek')
    
    # Diccionarios para cada categoría
    cumple_dict = {week: 0 for week in all_weeks}
    no_cumple_dict = {week: 0 for week in all_weeks}
    
    for row in df_week.iter_rows(named=True):
        if row['criterio_3'] == 1:
            cumple_dict[row['yearweek']] = row['n']
        elif row['criterio_3'] == 0:
            no_cumple_dict[row['yearweek']] = row['n']
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=all_weeks,
        y=[cumple_dict[w] for w in all_weeks],
        name='Cumple Criterio 3',
        marker_color='#f39c12'  # Naranja (color criterio 3)
    ))
    
    fig.add_trace(go.Bar(
        x=all_weeks,
        y=[no_cumple_dict[w] for w in all_weeks],
        name='No cumple',
        marker_color='#95a5a6'  # Gris
    ))
    
    fig.update_layout(
        title='Casos por Semana Epidemiológica - Criterio 3 (sin casos con nulls)',
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


def create_table1_stratified(df: pl.DataFrame, stratify_by: str = 'longCOVID') -> go.Figure:
    """
    Crea Tabla 1 descriptiva estratificada por variable (ej. Long COVID)
    Similar al formato de tablas clínicas con estadísticas por grupo.
    
    Args:
        df: DataFrame con todas las variables
        stratify_by: Variable de estratificación (default: 'longCOVID')
    
    Returns:
        Figura de Plotly con tabla
    """
    from scipy import stats
    
    # Definir la estructura de la tabla
    table_structure = {
        'Demographic characteristics': [
            {'var': 'sexo', 'type': 'categorical', 'label': 'Sex', 
             'categories': {1: 'Female', 2: 'Male'}},
            {'var': 'edad_entrevistado', 'type': 'age_groups', 'label': 'Age group',
             'groups': [(0, 30, '< 30'), (30, 45, '30-44'), (45, 60, '45-59'), (60, 100, '≥ 60')]},
            {'var': 'Nacionalidad', 'type': 'categorical_str', 'label': 'Nationality'},
            {'var': 'Región', 'type': 'categorical_str', 'label': 'Region'}
        ],
        'Clinical characteristics (acute COVID)': [
            {'var': 'Hospitalización', 'type': 'binary', 'label': 'Hospitalization', 
             'yes_value': 1},
            {'var': 'Total_Sintomas', 'type': 'continuous', 'label': 'Number of acute symptoms'},
            {'var': 'Total_Cond_pre', 'type': 'continuous', 'label': 'Pre-existing conditions'}
        ],
        'Lifestyle': [
            {'var': 'Tipo_Salud', 'type': 'categorical', 'label': 'Health insurance type',
             'categories': {1: 'Type 1', 2: 'Type 2'}},
            {'var': 'Más.de.100.Cigarros', 'type': 'binary', 'label': '>100 cigarettes lifetime',
             'yes_value': 1}
        ],
        'Biological markers': [
            {'var': 'Grupo.Sanguíneo', 'type': 'categorical_str', 'label': 'Blood group'},
            {'var': 'Grupo.Rh', 'type': 'categorical_str', 'label': 'Rh group'}
        ],
        'Ancestry proportions': [
            {'var': 'EUR', 'type': 'continuous', 'label': 'European ancestry'},
            {'var': 'AFR', 'type': 'continuous', 'label': 'African ancestry'},
            {'var': 'EAS', 'type': 'continuous', 'label': 'East Asian ancestry'},
            {'var': 'AYM', 'type': 'continuous', 'label': 'Aymara ancestry'},
            {'var': 'MAP', 'type': 'continuous', 'label': 'Mapuche ancestry'}
        ],
        'Long COVID characteristics': [
            {'var': 'problemas_3m', 'type': 'binary', 'label': 'Problems at 3 months', 
             'yes_value': 1},
            {'var': 'ayuda_3m', 'type': 'binary', 'label': 'Need for assistance', 
             'yes_value': 1}
        ]
    }
    
    # Filtrar datos por estratificación
    df_no_lc = df.filter(pl.col(stratify_by) == 0)
    df_lc = df.filter(pl.col(stratify_by) == 1)
    
    n_no_lc = df_no_lc.height
    n_lc = df_lc.height
    
    # Construir datos para la tabla
    variables = []
    no_lc_vals = []
    lc_vals = []
    pvalues = []
    
    for section, var_list in table_structure.items():
        # Fila de encabezado de sección
        variables.append(f'<b>{section}</b>')
        no_lc_vals.append('')
        lc_vals.append('')
        pvalues.append('')
        
        for var_info in var_list:
            var_name = var_info['var']
            
            # Verificar si la variable existe
            if var_name not in df.columns:
                continue
                
            var_type = var_info['type']
            label = var_info['label']
            
            if var_type == 'categorical':
                categories = var_info['categories']
                for cat_val, cat_label in categories.items():
                    n_no_lc_cat = df_no_lc.filter(pl.col(var_name) == cat_val).height
                    n_lc_cat = df_lc.filter(pl.col(var_name) == cat_val).height
                    
                    pct_no_lc = (n_no_lc_cat / n_no_lc * 100) if n_no_lc > 0 else 0
                    pct_lc = (n_lc_cat / n_lc * 100) if n_lc > 0 else 0
                    
                    contingency = [[n_no_lc_cat, n_lc_cat], 
                                   [n_no_lc - n_no_lc_cat, n_lc - n_lc_cat]]
                    try:
                        chi2, pvalue, dof, expected = stats.chi2_contingency(contingency)
                        p_str = f'<0.001' if float(pvalue) < 0.001 else f'{float(pvalue):.3f}'
                    except:
                        p_str = '-'
                    
                    variables.append(f'  {label}: {cat_label}')
                    no_lc_vals.append(f'{n_no_lc_cat} ({pct_no_lc:.1f}%)')
                    lc_vals.append(f'{n_lc_cat} ({pct_lc:.1f}%)')
                    pvalues.append(p_str)
            
            elif var_type == 'categorical_str':
                # Para categorías de strings, obtener los valores únicos
                unique_values = sorted(df.select(var_name).unique().to_series().drop_nulls().to_list())
                
                # Si hay muchas categorías (>10), mostrar solo las más comunes
                if len(unique_values) > 10:
                    # Contar frecuencias y obtener top 5
                    freq_no_lc = df_no_lc.group_by(var_name).count().sort('count', descending=True).head(5)
                    freq_lc = df_lc.group_by(var_name).count().sort('count', descending=True).head(5)
                    unique_values = sorted(list(set(freq_no_lc.select(var_name).to_series().to_list() + 
                                                     freq_lc.select(var_name).to_series().to_list())))
                    unique_values = unique_values[:10]  # Limitar a 10
                
                for cat_val in unique_values:
                    n_no_lc_cat = df_no_lc.filter(pl.col(var_name) == cat_val).height
                    n_lc_cat = df_lc.filter(pl.col(var_name) == cat_val).height
                    
                    pct_no_lc = (n_no_lc_cat / n_no_lc * 100) if n_no_lc > 0 else 0
                    pct_lc = (n_lc_cat / n_lc * 100) if n_lc > 0 else 0
                    
                    contingency = [[n_no_lc_cat, n_lc_cat], 
                                   [n_no_lc - n_no_lc_cat, n_lc - n_lc_cat]]
                    try:
                        chi2, pvalue, dof, expected = stats.chi2_contingency(contingency)
                        p_str = f'<0.001' if float(pvalue) < 0.001 else f'{float(pvalue):.3f}'
                    except:
                        p_str = '-'
                    
                    variables.append(f'  {label}: {cat_val}')
                    no_lc_vals.append(f'{n_no_lc_cat} ({pct_no_lc:.1f}%)')
                    lc_vals.append(f'{n_lc_cat} ({pct_lc:.1f}%)')
                    pvalues.append(p_str)
            
            elif var_type == 'age_groups':
                groups = var_info['groups']
                for min_age, max_age, group_label in groups:
                    n_no_lc_cat = df_no_lc.filter(
                        (pl.col(var_name) >= min_age) & (pl.col(var_name) < max_age)
                    ).height
                    n_lc_cat = df_lc.filter(
                        (pl.col(var_name) >= min_age) & (pl.col(var_name) < max_age)
                    ).height
                    
                    pct_no_lc = (n_no_lc_cat / n_no_lc * 100) if n_no_lc > 0 else 0
                    pct_lc = (n_lc_cat / n_lc * 100) if n_lc > 0 else 0
                    
                    contingency = [[n_no_lc_cat, n_lc_cat], 
                                   [n_no_lc - n_no_lc_cat, n_lc - n_lc_cat]]
                    try:
                        chi2, pvalue, dof, expected = stats.chi2_contingency(contingency)
                        p_str = f'<0.001' if float(pvalue) < 0.001 else f'{float(pvalue):.3f}'
                    except:
                        p_str = '-'
                    
                    variables.append(f'  {label}: {group_label}')
                    no_lc_vals.append(f'{n_no_lc_cat} ({pct_no_lc:.1f}%)')
                    lc_vals.append(f'{n_lc_cat} ({pct_lc:.1f}%)')
                    pvalues.append(p_str)
            
            elif var_type == 'binary':
                yes_val = var_info['yes_value']
                n_no_lc_yes = df_no_lc.filter(pl.col(var_name) == yes_val).height
                n_lc_yes = df_lc.filter(pl.col(var_name) == yes_val).height
                
                pct_no_lc = (n_no_lc_yes / n_no_lc * 100) if n_no_lc > 0 else 0
                pct_lc = (n_lc_yes / n_lc * 100) if n_lc > 0 else 0
                
                contingency = [[n_no_lc_yes, n_lc_yes], 
                               [n_no_lc - n_no_lc_yes, n_lc - n_lc_yes]]
                try:
                    chi2, pvalue, dof, expected = stats.chi2_contingency(contingency)
                    p_str = f'<0.001' if float(pvalue) < 0.001 else f'{float(pvalue):.3f}'
                except:
                    p_str = '-'
                
                variables.append(f'  {label}: Yes')
                no_lc_vals.append(f'{n_no_lc_yes} ({pct_no_lc:.1f}%)')
                lc_vals.append(f'{n_lc_yes} ({pct_lc:.1f}%)')
                pvalues.append(p_str)
            
            elif var_type == 'continuous':
                mean_no_lc = df_no_lc.select(pl.col(var_name).mean()).item()
                std_no_lc = df_no_lc.select(pl.col(var_name).std()).item()
                mean_lc = df_lc.select(pl.col(var_name).mean()).item()
                std_lc = df_lc.select(pl.col(var_name).std()).item()
                
                try:
                    vals_no_lc = df_no_lc.select(var_name).to_series().drop_nulls().to_list()
                    vals_lc = df_lc.select(var_name).to_series().drop_nulls().to_list()
                    tstat, pvalue = stats.ttest_ind(vals_no_lc, vals_lc)
                    p_str = f'<0.001' if float(pvalue) < 0.001 else f'{float(pvalue):.3f}'
                except:
                    p_str = '-'
                
                variables.append(f'  {label}')
                no_lc_vals.append(f'{mean_no_lc:.2f} ± {std_no_lc:.2f}')
                lc_vals.append(f'{mean_lc:.2f} ± {std_lc:.2f}')
                pvalues.append(p_str)
    
    # Crear tabla con Plotly
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=[
                '<b>Variable</b>',
                f'<b>No Long COVID<br>(n={n_no_lc})</b>',
                f'<b>Long COVID<br>(n={n_lc})</b>',
                '<b>P-value</b>'
            ],
            fill_color='#2c3e50',
            align='left',
            font=dict(color='white', size=13),
            height=40
        ),
        cells=dict(
            values=[variables, no_lc_vals, lc_vals, pvalues],
            fill_color=[['#ecf0f1' if '<b>' in v else '#ffffff' for v in variables]],
            align=['left', 'center', 'center', 'center'],
            font=dict(size=12),
            height=30
        )
    )])
    
    fig.update_layout(
        title='Table 1. Characteristics Stratified by Long COVID Status',
        template='plotly_white',
        height=2000,
        width=1200,
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    return fig


    """
    Crea Tabla 1 descriptiva estratificada por variable (ej. Long COVID)
    Similar al formato de tablas clínicas con estadísticas por grupo.
    
    Args:
        df: DataFrame con todas las variables
        stratify_by: Variable de estratificación (default: 'longCOVID')
    
    Returns:
        Figura de Plotly con tabla HTML estilizada
    """
    from scipy import stats
    
    # Definir la estructura de la tabla
    table_structure = {
        'Demographic characteristics': [
            {'var': 'sexo', 'type': 'categorical', 'label': 'Sex', 
             'categories': {1: 'Female', 2: 'Male'}},
            {'var': 'edad_entrevistado', 'type': 'age_groups', 'label': 'Age group',
             'groups': [(0, 45, '< 45'), (45, 100, '≥ 45')]}
        ],
        'Clinical characteristics (acute COVID)': [
            {'var': 'Hospitalización', 'type': 'binary', 'label': 'Hospitalization', 
             'yes_value': 1},
            {'var': 'Total_Sintomas', 'type': 'continuous', 'label': 'Number of acute symptoms'}
        ],
        'Vaccination status': [
            {'var': 'inmune_3m', 'type': 'binary', 'label': 'Vaccinated', 
             'yes_value': 1}
        ],
        'Long COVID characteristics': [
            {'var': 'sintoma_recurrente_count', 'type': 'categorical_num', 'label': 'Number of persistent symptoms',
             'categories': {0: '0', 1: '1', 2: '2', 3: '≥3'}},
            {'var': 'problemas_3m', 'type': 'binary', 'label': 'Problems at 3 months', 
             'yes_value': 1},
            {'var': 'ayuda_3m', 'type': 'binary', 'label': 'Need for assistance', 
             'yes_value': 1}
        ],
        'Symptom clusters': [
            {'var': 'cluster_cognitivo_bi', 'type': 'binary', 'label': 'Cognitive', 
             'yes_value': 1},
            {'var': 'cluster_respiratorio_bi', 'type': 'binary', 'label': 'Respiratory', 
             'yes_value': 1},
            {'var': 'cluster_gastrointestinal_bi', 'type': 'binary', 'label': 'Gastrointestinal', 
             'yes_value': 1},
            {'var': 'cluster_muscular_bi', 'type': 'binary', 'label': 'Muscular', 
             'yes_value': 1},
            {'var': 'cluster_olfato_gusto_bi', 'type': 'binary', 'label': 'Olfactory/gustatory', 
             'yes_value': 1},
            {'var': 'cluster_via_aerea_bi', 'type': 'binary', 'label': 'Upper airway', 
             'yes_value': 1}
        ]
    }
    
    # Filtrar datos por estratificación
    df_no_lc = df.filter(pl.col(stratify_by) == 0)
    df_lc = df.filter(pl.col(stratify_by) == 1)
    
    n_no_lc = df_no_lc.height
    n_lc = df_lc.height
    
    # Construir filas de la tabla
    rows = []
    
    for section, variables in table_structure.items():
        # Fila de encabezado de sección
        rows.append({
            'variable': f'<b>{section}</b>',
            'no_lc': '',
            'lc': '',
            'pvalue': '',
            'is_header': True
        })
        
        for var_info in variables:
            var_name = var_info['var']
            
            # Verificar si la variable existe
            if var_name not in df.columns:
                continue
                
            var_type = var_info['type']
            label = var_info['label']
            
            if var_type == 'categorical':
                categories = var_info['categories']
                for cat_val, cat_label in categories.items():
                    # Contar en cada grupo
                    n_no_lc_cat = df_no_lc.filter(pl.col(var_name) == cat_val).height
                    n_lc_cat = df_lc.filter(pl.col(var_name) == cat_val).height
                    
                    pct_no_lc = (n_no_lc_cat / n_no_lc * 100) if n_no_lc > 0 else 0
                    pct_lc = (n_lc_cat / n_lc * 100) if n_lc > 0 else 0
                    
                    # Chi-square test
                    contingency = [[n_no_lc_cat, n_lc_cat], 
                                   [n_no_lc - n_no_lc_cat, n_lc - n_lc_cat]]
                    try:
                        chi2, pvalue, dof, expected = stats.chi2_contingency(contingency)
                        p_str = f'<0.001' if float(pvalue) < 0.001 else f'{float(pvalue):.3f}'
                    except:
                        p_str = '-'
                    
                    rows.append({
                        'variable': f'{label}: {cat_label}',
                        'no_lc': f'{n_no_lc_cat} ({pct_no_lc:.1f}%)',
                        'lc': f'{n_lc_cat} ({pct_lc:.1f}%)',
                        'pvalue': p_str,
                        'is_header': False
                    })
            
            elif var_type == 'age_groups':
                groups = var_info['groups']
                for min_age, max_age, group_label in groups:
                    n_no_lc_cat = df_no_lc.filter(
                        (pl.col(var_name) >= min_age) & (pl.col(var_name) < max_age)
                    ).height
                    n_lc_cat = df_lc.filter(
                        (pl.col(var_name) >= min_age) & (pl.col(var_name) < max_age)
                    ).height
                    
                    pct_no_lc = (n_no_lc_cat / n_no_lc * 100) if n_no_lc > 0 else 0
                    pct_lc = (n_lc_cat / n_lc * 100) if n_lc > 0 else 0
                    
                    # Chi-square test
                    contingency = [[n_no_lc_cat, n_lc_cat], 
                                   [n_no_lc - n_no_lc_cat, n_lc - n_lc_cat]]
                    try:
                        chi2, pvalue, dof, expected = stats.chi2_contingency(contingency)
                        p_str = f'<0.001' if float(pvalue) < 0.001 else f'{float(pvalue):.3f}'
                    except:
                        p_str = '-'
                    
                    rows.append({
                        'variable': f'{label}: {group_label}',
                        'no_lc': f'{n_no_lc_cat} ({pct_no_lc:.1f}%)',
                        'lc': f'{n_lc_cat} ({pct_lc:.1f}%)',
                        'pvalue': p_str,
                        'is_header': False
                    })
            
            elif var_type == 'binary':
                yes_val = var_info['yes_value']
                n_no_lc_yes = df_no_lc.filter(pl.col(var_name) == yes_val).height
                n_lc_yes = df_lc.filter(pl.col(var_name) == yes_val).height
                
                pct_no_lc = (n_no_lc_yes / n_no_lc * 100) if n_no_lc > 0 else 0
                pct_lc = (n_lc_yes / n_lc * 100) if n_lc > 0 else 0
                
                # Chi-square test
                contingency = [[n_no_lc_yes, n_lc_yes], 
                               [n_no_lc - n_no_lc_yes, n_lc - n_lc_yes]]
                try:
                    chi2, pvalue, dof, expected = stats.chi2_contingency(contingency)
                    p_str = f'<0.001' if float(pvalue) < 0.001 else f'{float(pvalue):.3f}'
                except:
                    p_str = '-'
                
                rows.append({
                    'variable': f'{label}: Yes',
                    'no_lc': f'{n_no_lc_yes} ({pct_no_lc:.1f}%)',
                    'lc': f'{n_lc_yes} ({pct_lc:.1f}%)',
                    'pvalue': p_str,
                    'is_header': False
                })
            
            elif var_type == 'continuous':
                # Media ± DE
                mean_no_lc = df_no_lc.select(pl.col(var_name).mean()).item()
                std_no_lc = df_no_lc.select(pl.col(var_name).std()).item()
                mean_lc = df_lc.select(pl.col(var_name).mean()).item()
                std_lc = df_lc.select(pl.col(var_name).std()).item()
                
                # T-test
                try:
                    vals_no_lc = df_no_lc.select(var_name).to_series().drop_nulls().to_list()
                    vals_lc = df_lc.select(var_name).to_series().drop_nulls().to_list()
                    tstat, pvalue = stats.ttest_ind(vals_no_lc, vals_lc)
                    p_str = f'<0.001' if float(pvalue) < 0.001 else f'{float(pvalue):.3f}'
                except:
                    p_str = '-'
                
                rows.append({
                    'variable': label,
                    'no_lc': f'{mean_no_lc:.2f} ± {std_no_lc:.2f}',
                    'lc': f'{mean_lc:.2f} ± {std_lc:.2f}',
                    'pvalue': p_str,
                    'is_header': False
                })
            
            elif var_type == 'categorical_num':
                categories = var_info['categories']
                for cat_val, cat_label in categories.items():
                    if cat_val == 3:  # ≥3
                        n_no_lc_cat = df_no_lc.filter(pl.col(var_name) >= cat_val).height
                        n_lc_cat = df_lc.filter(pl.col(var_name) >= cat_val).height
                    else:
                        n_no_lc_cat = df_no_lc.filter(pl.col(var_name) == cat_val).height
                        n_lc_cat = df_lc.filter(pl.col(var_name) == cat_val).height
                    
                    pct_no_lc = (n_no_lc_cat / n_no_lc * 100) if n_no_lc > 0 else 0
                    pct_lc = (n_lc_cat / n_lc * 100) if n_lc > 0 else 0
                    
                    contingency = [[n_no_lc_cat, n_lc_cat], 
                                   [n_no_lc - n_no_lc_cat, n_lc - n_lc_cat]]
                    try:
                        chi2, pvalue, dof, expected = stats.chi2_contingency(contingency)
                        p_str = f'<0.001' if float(pvalue) < 0.001 else f'{float(pvalue):.3f}'
                    except:
                        p_str = '-'
                    
                    rows.append({
                        'variable': f'{label}: {cat_label}',
                        'no_lc': f'{n_no_lc_cat} ({pct_no_lc:.1f}%)',
                        'lc': f'{n_lc_cat} ({pct_lc:.1f}%)',
                        'pvalue': p_str,
                        'is_header': False
                    })
    
    # Crear HTML de la tabla
    html_rows = []
    html_rows.append(f'''
    <tr style="background-color: #2c3e50; color: white;">
        <th style="padding: 12px; text-align: left; border: 1px solid #ddd;"><b>Variable</b></th>
        <th style="padding: 12px; text-align: center; border: 1px solid #ddd;"><b>No Long COVID (n={n_no_lc})</b></th>
        <th style="padding: 12px; text-align: center; border: 1px solid #ddd;"><b>Long COVID (n={n_lc})</b></th>
        <th style="padding: 12px; text-align: center; border: 1px solid #ddd;"><b>P-value</b></th>
    </tr>
    ''')
    
    for i, row in enumerate(rows):
        bg_color = '#ecf0f1' if row.get('is_header') else ('#ffffff' if i % 2 == 0 else '#f8f9fa')
        html_rows.append(f'''
        <tr style="background-color: {bg_color};">
            <td style="padding: 8px; border: 1px solid #ddd;">{row['variable']}</td>
            <td style="padding: 8px; text-align: center; border: 1px solid #ddd;">{row['no_lc']}</td>
            <td style="padding: 8px; text-align: center; border: 1px solid #ddd;">{row['lc']}</td>
            <td style="padding: 8px; text-align: center; border: 1px solid #ddd;">{row['pvalue']}</td>
        </tr>
        ''')
    
    html_table = f'''
    <div style="overflow-x: auto; font-family: Arial, sans-serif;">
        <table style="width: 100%; border-collapse: collapse; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            {''.join(html_rows)}
        </table>
    </div>
    '''
    
    # Crear figura con HTML
    fig = go.Figure()
    
    fig.add_annotation(
        text=html_table,
        xref='paper',
        yref='paper',
        x=0.5,
        y=0.5,
        showarrow=False,
        font=dict(size=12),
        align='left',
        xanchor='center',
        yanchor='middle'
    )
    
    fig.update_layout(
        title='Table 1. Characteristics Stratified by Long COVID Status',
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        template='plotly_white',
        height=800,
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    return fig


def plot_linaje_barplot(df: pl.DataFrame) -> go.Figure:
    """
    Barplot de proporción promedio de ancestrías genéticas
    
    Args:
        df: DataFrame con columnas EUR, AFR, EAS, AYM, MAP
        
    Returns:
        Figura de plotly con barplot de ancestrías promedio
    """
    # Calcular promedios de ancestría
    ancestrias = ['EUR', 'AFR', 'EAS', 'AYM', 'MAP']
    promedios = []
    
    for anc in ancestrias:
        promedio = df[anc].mean()
        promedios.append(promedio)
    
    # Crear DataFrame para gráfico
    df_ancestrias = pl.DataFrame({
        'Ancestría': ancestrias,
        'Proporción_Promedio': promedios
    })
    
    df_pd = df_ancestrias.to_pandas()
    
    # Colores por ancestría
    colores = {
        'EUR': '#3498db',  # Azul - Europea
        'AFR': '#e67e22',  # Naranja - Africana
        'EAS': '#2ecc71',  # Verde - Este Asiática
        'AYM': '#9b59b6',  # Púrpura - Aymara
        'MAP': '#e74c3c'   # Rojo - Mapuche
    }
    
    colors_list = [colores[anc] for anc in ancestrias]
    
    # Crear barplot
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df_pd['Ancestría'],
        y=df_pd['Proporción_Promedio'],
        marker=dict(
            color=colors_list,
            line=dict(color='#34495e', width=1.5)
        ),
        hovertemplate='Ancestría: %{x}<br>Proporción Promedio: %{y:.4f}<extra></extra>'
    ))
    
    fig.update_layout(
        title='Distribución Promedio de Ancestrías Genéticas',
        xaxis_title='Ancestría Genética',
        yaxis_title='Proporción Promedio',
        template='plotly_white',
        height=500,
        font=dict(size=12),
        margin=dict(l=60, r=40, t=80, b=60)
    )
    
    return fig


def plot_hospitalizacion_by_week(df: pl.DataFrame) -> go.Figure:
    """
    Gráfico de hospitalización por semana epidemiológica
    
    Args:
        df: DataFrame con columnas 'yearweek' y 'Hospitalización'
        
    Returns:
        Figura de plotly con barplot apilado por semana
    """
    # Obtener todas las semanas únicas y ordenarlas
    all_weeks = sorted(df.select('yearweek').unique().to_series().to_list())
    
    # Inicializar diccionarios para cada categoría
    no_hosp_counts = {week: 0 for week in all_weeks}
    hosp_counts = {week: 0 for week in all_weeks}
    
    # Contar casos por semana y hospitalización
    for week in all_weeks:
        week_data = df.filter(pl.col('yearweek') == week)
        no_hosp_counts[week] = week_data.filter(pl.col('Hospitalización') == 0).height
        hosp_counts[week] = week_data.filter(pl.col('Hospitalización') == 1).height
    
    # Calcular totales
    total_no_hosp = sum(no_hosp_counts.values())
    total_hosp = sum(hosp_counts.values())
    
    # Crear gráfico
    fig = go.Figure()
    
    # Hospitalización = 0 (No hospitalizado)
    fig.add_trace(go.Bar(
        name='No Hospitalizado',
        x=all_weeks,
        y=[no_hosp_counts[w] for w in all_weeks],
        marker=dict(color='#95a5a6'),  # Gris
        hovertemplate='<b>Semana %{x}</b><br>No Hospitalizado: %{y}<extra></extra>'
    ))
    
    # Hospitalización = 1 (Hospitalizado)
    fig.add_trace(go.Bar(
        name='Hospitalizado',
        x=all_weeks,
        y=[hosp_counts[w] for w in all_weeks],
        marker=dict(color='#e74c3c'),  # Rojo
        hovertemplate='<b>Semana %{x}</b><br>Hospitalizado: %{y}<extra></extra>'
    ))
    
    fig.update_layout(
        title=f'Casos de Hospitalización por Semana Epidemiológica<br><sub>No Hospitalizado: {total_no_hosp} | Hospitalizado: {total_hosp}</sub>',
        xaxis_title='Semana Epidemiológica',
        yaxis_title='Número de Casos',
        barmode='stack',
        template='plotly_white',
        height=500,
        font=dict(size=12),
        margin=dict(l=60, r=40, t=100, b=60),
        xaxis=dict(
            type='category',
            tickangle=-45
        ),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        )
    )
    
    return fig


def plot_demographic_clinical_heatmap(df: pl.DataFrame) -> go.Figure:
    """
    Heatmap demográfico-clínico mostrando características por grupos etarios y sexo
    
    Eje Y: Hospitalizados, No hospitalizados, Severos, No severos, Total síntomas preexistentes promedio
    Eje X: Grupos etarios (< 30, 30-44, 45-59, >60) y Sexo
    
    Args:
        df: DataFrame con columnas Hospitalización, Severo, sexo, edad_entrevistado, Total_Cond_pre
        
    Returns:
        Figura de plotly con heatmap
    """
    import numpy as np
    
    # Crear grupos etarios
    df_with_age_group = df.with_columns([
        pl.when(pl.col('edad_entrevistado') < 30).then(pl.lit('< 30'))
        .when((pl.col('edad_entrevistado') >= 30) & (pl.col('edad_entrevistado') < 45)).then(pl.lit('30-44'))
        .when((pl.col('edad_entrevistado') >= 45) & (pl.col('edad_entrevistado') < 60)).then(pl.lit('45-59'))
        .when(pl.col('edad_entrevistado') >= 60).then(pl.lit('>60'))
        .otherwise(pl.lit('Desconocido'))
        .alias('grupo_etario')
    ])
    
    # Filtrar casos válidos
    df_valid = df_with_age_group.filter(
        ~pl.col('Hospitalización').is_null() &
        ~pl.col('Severo').is_null() &
        ~pl.col('sexo').is_null() &
        (pl.col('grupo_etario') != 'Desconocido')
    )
    
    # Definir columnas X (grupos etarios + sexo)
    age_groups = ['< 30', '30-44', '45-59', '>60']
    sex_labels = ['Femenino', 'Masculino']
    
    # Matriz de datos
    heatmap_data = []
    y_labels = []
    
    # 1. Hospitalizados por grupo etario
    row_hosp = []
    for age in age_groups:
        df_age = df_valid.filter(pl.col('grupo_etario') == age)
        total_age = df_age.height
        hosp = df_age.filter(pl.col('Hospitalización') == 1).height
        pct = (hosp / total_age * 100) if total_age > 0 else 0
        row_hosp.append(pct)
    # Agregar por sexo
    for sex_val, sex_label in [(1, 'Femenino'), (2, 'Masculino')]:
        df_sex = df_valid.filter(pl.col('sexo') == sex_val)
        total_sex = df_sex.height
        hosp_sex = df_sex.filter(pl.col('Hospitalización') == 1).height
        pct_sex = (hosp_sex / total_sex * 100) if total_sex > 0 else 0
        row_hosp.append(pct_sex)
    
    heatmap_data.append(row_hosp)
    y_labels.append('Hospitalizados (%)')
    
    # 2. No hospitalizados por grupo etario
    row_no_hosp = []
    for age in age_groups:
        df_age = df_valid.filter(pl.col('grupo_etario') == age)
        total_age = df_age.height
        no_hosp = df_age.filter(pl.col('Hospitalización') == 0).height
        pct = (no_hosp / total_age * 100) if total_age > 0 else 0
        row_no_hosp.append(pct)
    # Agregar por sexo
    for sex_val, sex_label in [(1, 'Femenino'), (2, 'Masculino')]:
        df_sex = df_valid.filter(pl.col('sexo') == sex_val)
        total_sex = df_sex.height
        no_hosp_sex = df_sex.filter(pl.col('Hospitalización') == 0).height
        pct_sex = (no_hosp_sex / total_sex * 100) if total_sex > 0 else 0
        row_no_hosp.append(pct_sex)
    
    heatmap_data.append(row_no_hosp)
    y_labels.append('No hospitalizados (%)')
    
    # 3. Severos por grupo etario
    row_sev = []
    for age in age_groups:
        df_age = df_valid.filter(pl.col('grupo_etario') == age)
        total_age = df_age.height
        sev = df_age.filter(pl.col('Severo') == 1).height
        pct = (sev / total_age * 100) if total_age > 0 else 0
        row_sev.append(pct)
    # Agregar por sexo
    for sex_val, sex_label in [(1, 'Femenino'), (2, 'Masculino')]:
        df_sex = df_valid.filter(pl.col('sexo') == sex_val)
        total_sex = df_sex.height
        sev_sex = df_sex.filter(pl.col('Severo') == 1).height
        pct_sex = (sev_sex / total_sex * 100) if total_sex > 0 else 0
        row_sev.append(pct_sex)
    
    heatmap_data.append(row_sev)
    y_labels.append('Severos (%)')
    
    # 4. No severos por grupo etario
    row_no_sev = []
    for age in age_groups:
        df_age = df_valid.filter(pl.col('grupo_etario') == age)
        total_age = df_age.height
        no_sev = df_age.filter(pl.col('Severo') == 0).height
        pct = (no_sev / total_age * 100) if total_age > 0 else 0
        row_no_sev.append(pct)
    # Agregar por sexo
    for sex_val, sex_label in [(1, 'Femenino'), (2, 'Masculino')]:
        df_sex = df_valid.filter(pl.col('sexo') == sex_val)
        total_sex = df_sex.height
        no_sev_sex = df_sex.filter(pl.col('Severo') == 0).height
        pct_sex = (no_sev_sex / total_sex * 100) if total_sex > 0 else 0
        row_no_sev.append(pct_sex)
    
    heatmap_data.append(row_no_sev)
    y_labels.append('No severos (%)')
    
    # 5. Total síntomas preexistentes promedio
    row_cond = []
    for age in age_groups:
        df_age = df_valid.filter(pl.col('grupo_etario') == age)
        if df_age.height > 0:
            avg_cond = df_age['Total_Cond_pre'].mean()
        else:
            avg_cond = 0
        row_cond.append(avg_cond if avg_cond is not None else 0)
    # Agregar por sexo
    for sex_val, sex_label in [(1, 'Femenino'), (2, 'Masculino')]:
        df_sex = df_valid.filter(pl.col('sexo') == sex_val)
        if df_sex.height > 0:
            avg_cond_sex = df_sex['Total_Cond_pre'].mean()
        else:
            avg_cond_sex = 0
        row_cond.append(avg_cond_sex if avg_cond_sex is not None else 0)
    
    heatmap_data.append(row_cond)
    y_labels.append('Condiciones preexistentes<br>(promedio)')
    
    # Columnas X
    x_labels = age_groups + sex_labels
    
    # Crear heatmap
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data,
        x=x_labels,
        y=y_labels,
        colorscale='RdYlBu_r',  # Rojo (alto) a Azul (bajo)
        colorbar=dict(title='Valor'),
        hoverongaps=False,
        text=[[f'{val:.1f}' for val in row] for row in heatmap_data],
        texttemplate='%{text}',
        textfont=dict(size=11),
        hovertemplate='Grupo: %{x}<br>Variable: %{y}<br>Valor: %{z:.2f}<extra></extra>'
    ))
    
    fig.update_layout(
        title='Heatmap Demográfico-Clínico: Características por Edad y Sexo',
        xaxis_title='Grupo Etario / Sexo',
        yaxis_title='Característica Clínica',
        template='plotly_white',
        height=600,
        font=dict(size=12),
        xaxis=dict(
            side='top',
            tickangle=0
        ),
        yaxis=dict(
            side='left'
        ),
        margin=dict(l=150, r=40, t=120, b=40)
    )
    
    return fig

