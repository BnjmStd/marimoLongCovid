import polars as pl
from modules import load_long_covid, create_criterio_variables

# Cargar datos
df_long_covid = load_long_covid('datasets/longcovid_2020W13-2021W22.csv')
df_con_criterios = create_criterio_variables(df_long_covid)

# Conteo criterio 3
criterio_3_count = df_con_criterios.filter(pl.col('criterio_3') == 1).height
print(f'Criterio 3 total: {criterio_3_count}')

# Desglose de componentes
covid_positivo = df_con_criterios.filter(pl.col('covid') == 1).height
tiene_clusters = df_con_criterios.filter(pl.col('pertenece_cluster_count') >= 1).height
no_recuperado = df_con_criterios.filter(pl.col('recuperado_3m') == 2).height

print(f'\nComponentes individuales:')
print(f'- COVID positivo: {covid_positivo}')
print(f'- Tiene clusters (>= 1): {tiene_clusters}')
print(f'- No recuperado (== 2): {no_recuperado}')

# Las 3 condiciones juntas
tres_condiciones = df_con_criterios.filter(
    (pl.col('covid') == 1) & 
    (pl.col('pertenece_cluster_count') >= 1) & 
    (pl.col('recuperado_3m') == 2)
).height
print(f'- Tres condiciones simultáneas: {tres_condiciones}')

# Valores NULL
null_covid = df_con_criterios.filter(pl.col('covid').is_null()).height
null_clusters = df_con_criterios.filter(pl.col('pertenece_cluster_count').is_null()).height
null_recuperado = df_con_criterios.filter(pl.col('recuperado_3m').is_null()).height

print(f'\nValores NULL:')
print(f'- NULL en covid: {null_covid}')
print(f'- NULL en pertenece_cluster_count: {null_clusters}')
print(f'- NULL en recuperado_3m: {null_recuperado}')

# Valores de recuperado_3m
valores_recuperado = df_con_criterios.group_by('recuperado_3m').agg(pl.len().alias('n')).sort('recuperado_3m')
print(f'\nDistribución de recuperado_3m:')
print(valores_recuperado)

# Distribución de pertenece_cluster_count para casos que cumplen C3
casos_c3 = df_con_criterios.filter(pl.col('criterio_3') == 1)
dist_clusters = casos_c3.group_by('pertenece_cluster_count').agg(pl.len().alias('n')).sort('pertenece_cluster_count')
print(f'\nDistribución de pertenece_cluster_count en casos C3:')
print(dist_clusters)

# Verificar si hay casos con pertenece_cluster_count == 0 que cumplan C3
casos_raros = df_con_criterios.filter(
    (pl.col('criterio_3') == 1) & 
    (pl.col('pertenece_cluster_count') == 0)
).height
print(f'\nCasos que cumplen C3 pero tienen pertenece_cluster_count == 0: {casos_raros}')

# Verificar definición de pertenece_cluster_count
print('\nVerificando cálculo de pertenece_cluster_count...')
casos_ejemplo = df_con_criterios.filter(pl.col('criterio_3') == 1).select([
    'pertenece_cluster_count',
    'cluster_cognitivo_bi',
    'cluster_gastrointestinal_bi', 
    'cluster_muscular_bi',
    'cluster_olfato_gusto_bi',
    'cluster_respiratorio_bi',
    'cluster_via_aerea_bi'
]).head(10)
print(casos_ejemplo)

# Verificar cómo se calcula pertenece_cluster_count en transformations.py
print('\n\nVerificando si hay NULLs en clusters binarios...')
for cluster in ['cluster_cognitivo_bi', 'cluster_gastrointestinal_bi', 'cluster_muscular_bi', 
                'cluster_olfato_gusto_bi', 'cluster_respiratorio_bi', 'cluster_via_aerea_bi']:
    nulls = df_con_criterios.filter(pl.col(cluster).is_null()).height
    print(f'{cluster}: {nulls} NULLs')
