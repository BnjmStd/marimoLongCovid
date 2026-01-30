# Long COVID - Análisis de Datos

Stack: Python 3.13.2 + Polars + Plotly + Marimo

## Setup

```bash
pyenv virtualenv 3.13.2 long-covid
pyenv local long-covid
pip install -r requirements.txt
```

## Ejecutar

```bash
# Versión básica (todo en un archivo)
marimo edit analysis.py

# Versión modular (recomendado)
marimo edit analysis_modular.py
```

Se abre en el navegador en http://localhost:2718

## Estructura Modular

```
modules/
├── __init__.py
├── data_loader.py        # Funciones para cargar datos
├── transformations.py    # Análisis y transformaciones con Polars
└── visualizations.py     # Gráficos con Plotly
```

Ventajas:
- Código reutilizable
- Funciones testeables
- Notebook limpio y legible
- Separación de responsabilidades

# Cambios Realizados: Criterio 3 sin Nulls

## Objetivo

Modificar el Criterio 3 para que **automáticamente excluya casos con valores NULL** en la variable `recuperado_3m`, ya que esta variable es esencial para determinar si un paciente cumple el criterio.

## 📝 Cambios Implementados

### 1. **modules/transformations.py**

- Modificado `create_criterio_variables()` para filtrar nulls en `recuperado_3m`
- **Antes**: `(pl.col("recuperado_3m") == 2)`
- **Después**: `(pl.col("recuperado_3m") == 2) & (~pl.col("recuperado_3m").is_null())`
- **Resultado**: Los 8 casos con NULL en `recuperado_3m` ahora marcan `criterio_3 = 0` automáticamente

### 2. **modules/visualizations.py**

#### a) Corrección de errores de pvalue

- Corregidos todos los errores de tipo en comparaciones de pvalue
- **Antes**: `pvalue < 0.001` (causaba error de tipo tuple vs float)
- **Después**: `float(pvalue) < 0.001`
- **Afectadas**: 10+ líneas en `create_table1_stratified()`

#### b) Nueva función: `plot_cases_by_week_by_criterio_3_sin_nulls()`

- Agregada nueva función que filtra casos con nulls explícitamente
- Muestra distribución temporal del Criterio 3 (cumple vs no cumple)
- Colores: Naranja (#f39c12) para cumple, Gris (#95a5a6) para no cumple
- Filtra: `df.filter(~pl.col('recuperado_3m').is_null())`

#### c) Actualización: `plot_criterio3_clusters_comparison()`

- Ahora filtra casos con nulls antes de analizar clusters
- **Agregado**: `df_sin_nulls = df.filter(~pl.col('recuperado_3m').is_null())`
- Asegura consistencia en la comparación de clusters

### 3. **modules/**init**.py**

- Agregado export de `plot_cases_by_week_by_criterio_3_sin_nulls`
- Actualizado `__all__` con todas las nuevas funciones

### 4. **analysis_long_covid.py**

#### a) Imports actualizados

- Agregado `plot_cases_by_week_by_criterio_3_sin_nulls` a los imports
- Agregado a la lista de returns del módulo principal

#### b) Nueva sección en el notebook

Agregadas 3 nuevas celdas después de la comparación de clusters:

**Celda 1**: Título y explicación

```markdown
### Criterio 3: Evolución Temporal (sin casos con nulls)

**Nota importante:** El Criterio 3 ahora excluye automáticamente los casos
con valores NULL en `recuperado_3m`.
```

**Celda 2**: Gráfico

```python
fig_criterio3_week = plot_cases_by_week_by_criterio_3_sin_nulls(df_con_criterios)
fig_criterio3_week
```

**Celda 3**: Interpretación con estadísticas

- Total casos analizados (sin nulls): 1,497
- Cumplen Criterio 3: 360 (23.9%)
- No cumplen: 1,137 (76.1%)
- Casos excluidos con NULL: 8

## Resultados

### Estadísticas del Dataset

- **Total registros**: 1,505
- **Casos con NULL en `recuperado_3m`**: 8 (0.5%)
- **Casos válidos para análisis**: 1,497 (99.5%)

### Criterio 3

- **Casos que cumplen**: 360 (23.9% del total válido)
- **Casos que no cumplen**: 1,137 (76.1% del total válido)
- **Efecto del cambio**: Los 8 casos con NULL ahora se marcan explícitamente como `criterio_3 = 0`

## Verificaciones Realizadas

1.  **Compilación**: Todos los módulos compilan sin errores
2.  **Imports**: Todas las funciones se importan correctamente
3.  **Datos reales**: Probado con el dataset completo (1,505 registros)
4.  **Gráficos**: Los 3 gráficos se generan correctamente
5.  **Notebook**: `marimo check` pasa (solo warnings de indentación)
6.  **Type hints**: Sin errores de tipo en pvalue

## Cambios en Otros Gráficos

Todos los gráficos que usan `criterio_3` ahora trabajan con el criterio actualizado:

- `plot_criterio3_clusters_comparison()`: Filtra nulls explícitamente
- `plot_longcovid_by_week()`: Usa el criterio actualizado automáticamente
- `plot_criterio_barplot()`: Usa el criterio actualizado automáticamente

## Cómo Usar

```python
import polars as pl
from modules import (
    load_long_covid,
    create_criterio_variables,
    plot_cases_by_week_by_criterio_3_sin_nulls
)

# Cargar datos
df = load_long_covid('datasets/longcovid_2020W13-2021W22.csv')

# Crear criterios (criterio_3 ahora filtra nulls automáticamente)
df_con_criterios = create_criterio_variables(df)

# Generar gráfico
fig = plot_cases_by_week_by_criterio_3_sin_nulls(df_con_criterios)
fig.show()
```

## Notas Importantes

1. **Criterio 3 modificado a nivel de creación**: La función `create_criterio_variables()`
   ahora marca casos con NULL como `criterio_3 = 0` automáticamente.

2. **Consistencia**: Todos los gráficos y análisis que usan `criterio_3` ahora trabajan
   con datos consistentes (sin nulls).

3. **Documentación**: El notebook incluye explicación clara sobre la exclusión de nulls.

4. **Colores**: Se mantiene el color naranja (#f39c12) para Criterio 3, consistente
   con otros gráficos del sistema.

## 🎨 Colores por Criterio

- **Criterio 1**: Azul (#3498db)
- **Criterio 2**: Rojo (#e74c3c)
- **Criterio 3**: Naranja (#f39c12) ⭐
- **Criterio 4**: Violeta (#9b59b6)
- **No cumple**: Gris (#95a5a6)
