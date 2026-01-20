---
title: Analysis Long Covid
marimo-version: 0.19.4
width: medium
---

```python {.marimo}
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
    plot_criterio2_recovery,
    plot_longcovid_by_week,
    plot_sintomas_recurrentes_by_week,
    plot_cluster_pertenencia_by_week,
    plot_clusters_individuales_by_week,
    plot_secuelas_by_week,
    plot_clusters_heatmap_by_diagnosis_week,
    plot_criterio_barplot,
)
```

# Análisis Long COVID - Chile 2020-2021

## Tareas del análisis:
1. Dataset truncado (variantes y long COVID) - generar estadísticas
2. Variables de criterio (1-4)
3. Variantes: barplot apilado por semana epidemiológica (11 linajes) + curva casos Chile
4. Long COVID por semana epidemiológica por diferentes variables
5. Análisis de clusters y secuelas
6. Tabla 1 descriptiva
7. Figura metodológica
<!---->
## 1. Cargar Dataset y Generar Estadísticas

```python {.marimo}
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
```

### Resumen Visual del Dataset

```python {.marimo}
# Gráfico de resumen del dataset
fig_overview = plot_dataset_overview(df_long_covid)
fig_overview
```

## 2. Crear Variables de Criterio por fenotipos long covid (1-4)
<!---->
### 2.1. Criterio 1 (longCOVID, fenotipo muy general)

```python {.marimo}
mo.md(f"""
**Criterio 1:** Long COVID (fenotipo general)
- Variable: `longCOVID == 1`
- **Fórmula:** `criterio_1 = 1` si longCOVID == 1, sino 0

**Casos en dataset:**
- Cumplen longCOVID: {df_long_covid.filter(pl.col('longCOVID') == 1).height:,}
- No cumplen: {df_long_covid.filter(pl.col('longCOVID') == 0).height:,}
""")
```

```python {.marimo}
# Crear todas las variables de criterio
df_con_criterios = create_criterio_variables(df_long_covid)
df_con_criterios
```

```python {.marimo}
# Barplot de Criterio 1
fig_bar_c1 = plot_criterio_barplot(df_con_criterios, 1, 'Criterio 1 (Long COVID): Distribución de Casos')
fig_bar_c1
```

### Criterio 1: Evolución Temporal

```python {.marimo}
# Long COVID por semana epidemiológica
fig_c1_week = plot_criterio1_by_week(df_con_criterios)
fig_c1_week
```

## 2.2. Criterio 2 (Síntomas recurrentes)

**Definición:** COVID confirmado + Más de 1 síntoma recurrente + No recuperado a los 3 meses

**Fórmula:** `criterio_2 = 1` si cumple:
- DP4: COVID confirmado (`covid == 1`)
- P17: Más de 1 síntoma recurrente (`sintoma_recurrente_count > 1`)
- P20: No recuperado a los 3 meses (`recuperado_3m == 2`)

```python {.marimo}
# Validar Criterio 2
conteo_c2 = df_con_criterios.filter(pl.col("criterio_2") == 1).height
no_cumple_c2 = df_con_criterios.filter(pl.col("criterio_2") == 0).height

(conteo_c2, no_cumple_c2)
```

```python {.marimo}
mo.md(f"""
**Casos en dataset:**
- Cumplen criterio 2: {conteo_c2:,}
- No cumplen: {no_cumple_c2:,}
""")
```

```python {.marimo}
# Barplot de Criterio 2
fig_bar_c2 = plot_criterio_barplot(df_con_criterios, 2, 'Criterio 2 (Síntomas Recurrentes): Distribución de Casos')
fig_bar_c2
```

### Criterio 2: Análisis de Síntomas

```python {.marimo}
# Distribución de síntomas recurrentes
fig_c2_sintomas = plot_criterio2_sintomas(df_con_criterios)
fig_c2_sintomas
```

### Criterio 2: Estado de Recuperación

```python {.marimo}
# Análisis de recuperación
fig_c2_recovery = plot_criterio2_recovery(df_con_criterios)
fig_c2_recovery
```

## 2.3. Criterio 3 (Cluster)

**Definición:** COVID-19 + Al menos 2 síntomas de cualquier cluster + No recuperado a los 3 meses

**Fórmula:** `criterio_3 = 1` si cumple:
- `covid == 1` (DP4: Diagnóstico de COVID)
- `pertenece_cluster_count >= 1` (P17: Al menos 2 síntomas de cualquier cluster)
- `recuperado_3m == 2` (P20: No recuperado)

```python {.marimo}
# Validar Criterio 3
conteo_c3 = df_con_criterios.filter(pl.col("criterio_3") == 1).height
no_cumple_c3 = df_con_criterios.filter(pl.col("criterio_3") == 0).height

(conteo_c3, no_cumple_c3)
```

```python {.marimo}
mo.md(f"""
**Casos en dataset:**
- Cumplen criterio 3: {conteo_c3:,}
- No cumplen: {no_cumple_c3:,}
""")
```

```python {.marimo}
# Barplot de Criterio 3
fig_bar_c3 = plot_criterio_barplot(df_con_criterios, 3, 'Criterio 3 (Clusters): Distribución de Casos')
fig_bar_c3
```

## 2.4. Criterio 4 (Secuelas)

**Definición:** COVID-19 + Nueva condición O Secuelas crónicas

**Fórmula:** `criterio_4 = 1` si cumple:
- `covid == 1` (DP4: Diagnóstico de COVID)
- `conteo_nueva_condicion >= 1` (P21: Ha desarrollado una nueva condición) **O**
- `sec_count >= 1` (P22: Condición crónica no reportada en etapa aguda)

```python {.marimo}
# Validar Criterio 4
conteo_c4 = df_con_criterios.filter(pl.col("criterio_4") == 1).height
no_cumple_c4 = df_con_criterios.filter(pl.col("criterio_4") == 0).height

(conteo_c4, no_cumple_c4)
```

```python {.marimo}
mo.md(f"""
**Casos en dataset:**
- Cumplen criterio 4: {conteo_c4:,}
- No cumplen: {no_cumple_c4:,}
""")
```

```python {.marimo}
# Barplot de Criterio 4
fig_bar_c4 = plot_criterio_barplot(df_con_criterios, 4, 'Criterio 4 (Secuelas): Distribución de Casos')
fig_bar_c4
```

## 2.5. Comparación de Criterios

```python {.marimo}
# Comparación visual de todos los criterios
fig_criterios = plot_criterio_comparison(df_con_criterios)
fig_criterios
```

## 2.6. Comparación de Resultados - Criterio 3

**Objetivo:** Investigar diferencia entre resultados
- Resultado actual: 360 casos
- Resultado Josefa: 352 casos
- Diferencia: 8 casos

**Análisis de componentes del Criterio 3:**

```python {.marimo}
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
```

```python {.marimo}
mo.md(f"""
**Conteos por componente:**
- COVID positivo (`covid == 1`): {covid_positivo:,}
- Pertenece a algún cluster (`pertenece_cluster_count >= 1`): {tiene_clusters:,}
- No recuperado a los 3 meses (`recuperado_3m == 2`): {no_recuperado:,}
- **Cumplen las 3 condiciones simultáneamente: {tres_condiciones:,}**

**Verificación:** El criterio_3 debería coincidir con el conteo de las 3 condiciones.
""")
```

```python {.marimo}
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
```

```python {.marimo}
mo.md(f"""
**Distribución de clusters entre casos que cumplen Criterio 3:**

{dist_clusters_c3}

**Posibles causas de discrepancia (360 vs 352):**
1. Manejo diferente de valores NULL en alguna variable
2. Definición diferente de `pertenece_cluster_count`
3. Filtrado diferente de `recuperado_3m`
4. Versión diferente del dataset
""")
```

```python {.marimo}
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
```

```python {.marimo}
mo.md(f"""
**Análisis de valores NULL y edge cases:**
- NULL en `covid`: {null_covid}
- NULL en `pertenece_cluster_count`: {null_clusters}
- NULL en `recuperado_3m`: {null_recuperado}
- Valores de `recuperado_3m` diferentes de 1 y 2: {recuperado_otros}
""")
```

## 3. Variantes: Barplot Apilado por Semana Epidemiológica
<!---->
## 4. Long COVID por Semana Epidemiológica

Análisis temporal de casos con diferentes categorizaciones
<!---->
### 4.1. Long COVID por Criterios Diagnósticos
<!---->
### 4.1. Criterios Diagnósticos por Semana

```python {.marimo}
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
```

```python {.marimo}
fig_longcovid_week = plot_longcovid_by_week(df_con_criterios)
fig_longcovid_week
```

### 4.2. Distribución de Síntomas Recurrentes

```python {.marimo}
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
```

```python {.marimo}
fig_sintomas_hist = plot_sintomas_recurrentes_by_week(df_con_criterios)
fig_sintomas_hist
```

### 4.3. Pertenencia a Clusters por Semana

```python {.marimo}
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
```

```python {.marimo}
fig_cluster_week = plot_cluster_pertenencia_by_week(df_con_criterios)
fig_cluster_week
```

### 4.4. Clusters Individuales por Semana

```python {.marimo}
# Validar datos: un ejemplo con cluster cognitivo
datos_cognitivo_semana = df_con_criterios.group_by(['yearweek', 'cluster_cognitivo_bi']).agg(
    pl.len().alias('n')
).sort('yearweek')

datos_cognitivo_semana.head(15)
```

```python {.marimo}
fig_clusters_ind = plot_clusters_individuales_by_week(df_con_criterios)
fig_clusters_ind
```

### 4.5. Secuelas por Semana

```python {.marimo}
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
```

```python {.marimo}
fig_secuelas_week = plot_secuelas_by_week(df_con_criterios)
fig_secuelas_week
```

### 4.6. Heatmap de Clusters por Semana de Diagnóstico

```python {.marimo}
fig_heatmap_clusters = plot_clusters_heatmap_by_diagnosis_week(df_con_criterios)
fig_heatmap_clusters
```

### 4.1. Por variable longCOVID
<!---->
### 4.2. Por síntomas recurrentes
<!---->
### 4.3. Por pertenencia a cluster
<!---->
### 4.4. Por secuelas
<!---->
## 5. Análisis de Clusters y Secuelas
<!---->
## 6. Tabla 1: Descriptiva
<!---->
## 7. Figura Metodológica
