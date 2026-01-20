"""
Visualizaciones específicas para análisis Long COVID
"""
import plotly.express as px
import plotly.graph_objects as go
import polars as pl


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
        pl.count().alias('n_casos')
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
        pl.count().alias('n_casos')
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
