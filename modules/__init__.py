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
    create_descriptive_table,
    analyze_criterios_null_impact
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
    plot_criterio_barplot,
    plot_criterios_null_impact,
    plot_cases_by_week_by_sex,
    plot_cases_by_week_by_age_group,
    plot_cases_by_week_by_secuelas,
    plot_cases_by_week_by_nueva_condicion,
    plot_cases_by_week_by_sintomas_recurrentes,
    plot_cases_by_week_by_criterio_3_sin_nulls,
    plot_linaje_barplot,
    plot_hospitalizacion_by_week,
    plot_demographic_clinical_heatmap,
    create_table1_stratified,
    plot_criterios_hospitalizacion_heatmap,
    plot_criterios_hospitalizacion_heatmap_opcionA,
    plot_criterios_hospitalizacion_heatmap_opcionB,
    plot_criterios_hospitalizacion_heatmap_agrupado_sexo
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
    'analyze_criterios_null_impact',
    
    # Visualizations
    'plot_variantes_stacked_bar',
    'plot_long_covid_by_variable',
    'plot_clusters_analysis',
    'create_table_1',
    'plot_dataset_overview',
    'plot_criterio_comparison',
    'plot_criterio1_by_week',
    'plot_criterio2_sintomas',
    'plot_criterio2_promedio_sintomas',
    'plot_criterio2_promedio_sintomas_by_week',
    'plot_criterio2_recovery',
    'plot_criterio3_clusters_comparison',
    'plot_longcovid_by_week',
    'plot_sintomas_recurrentes_by_week',
    'plot_cluster_pertenencia_by_week',
    'plot_clusters_individuales_by_week',
    'plot_secuelas_by_week',
    'plot_clusters_heatmap_by_diagnosis_week',
    'plot_criterio_barplot',
    'plot_criterios_null_impact',
    'plot_cases_by_week_by_sex',
    'plot_cases_by_week_by_age_group',
    'plot_cases_by_week_by_secuelas',
    'plot_cases_by_week_by_nueva_condicion',
    'plot_cases_by_week_by_sintomas_recurrentes',
    'plot_cases_by_week_by_criterio_3_sin_nulls',
    'plot_linaje_barplot',
    'plot_hospitalizacion_by_week',
    'plot_demographic_clinical_heatmap',
    'create_table1_stratified',
    'plot_criterios_hospitalizacion_heatmap',
    'plot_criterios_hospitalizacion_heatmap_opcionA',
    'plot_criterios_hospitalizacion_heatmap_opcionB',
    'plot_criterios_hospitalizacion_heatmap_agrupado_sexo'
]
