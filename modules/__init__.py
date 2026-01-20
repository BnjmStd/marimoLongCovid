"""
Módulos para análisis de datos Long COVID
"""

from .data_loader import (
    load_data,
    load_long_covid
)

from .transformations import (
    truncate_dataset,
    create_criterio_variables,
    count_by_criterio,
    aggregate_by_semana_epi,
    create_descriptive_table
)

from .visualizations import (
    plot_variantes_stacked_bar,
    plot_long_covid_by_variable,
    plot_clusters_analysis,
    create_table_1,
    plot_dataset_overview,
    plot_criterio_comparison,
    plot_criterio1_by_week,
    plot_criterio2_sintomas,
    plot_criterio2_recovery,
    plot_longcovid_by_week,
    plot_sintomas_recurrentes_by_week,
    plot_cluster_pertenencia_by_week,
    plot_clusters_individuales_by_week,
    plot_secuelas_by_week,
    plot_clusters_heatmap_by_diagnosis_week,
    plot_criterio_barplot
)

__all__ = [
    # Data loading
    'load_data',
    'load_long_covid',
    
    # Transformations
    'truncate_dataset',
    'create_criterio_variables',
    'count_by_criterio',
    'aggregate_by_semana_epi',
    'create_descriptive_table',
    
    # Visualizations
    'plot_variantes_stacked_bar',
    'plot_long_covid_by_variable',
    'plot_clusters_analysis',
    'create_table_1',
    'plot_dataset_overview',
    'plot_criterio_comparison',
    'plot_criterio1_by_week',
    'plot_criterio2_sintomas',
    'plot_criterio2_recovery',
    'plot_longcovid_by_week',
    'plot_sintomas_recurrentes_by_week',
    'plot_cluster_pertenencia_by_week',
    'plot_clusters_individuales_by_week',
    'plot_secuelas_by_week',
    'plot_clusters_heatmap_by_diagnosis_week',
    'plot_criterio_barplot'
]
