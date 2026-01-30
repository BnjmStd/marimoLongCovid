"""
Transformaciones y análisis con Polars para Long COVID
"""
import polars as pl


def truncate_dataset(df: pl.DataFrame, fecha_inicio: str, fecha_fin: str) -> pl.DataFrame:
    """
    Trunca dataset por rango de fechas
    
    Args:
        df: DataFrame de entrada
        fecha_inicio: Fecha inicial
        fecha_fin: Fecha final
    
    Returns:
        DataFrame truncado
    """
    return df.filter(
        (pl.col("fecha") >= fecha_inicio) & (pl.col("fecha") <= fecha_fin)
    )


def create_criterio_variables(df: pl.DataFrame) -> pl.DataFrame:
    """
    Crea variables de criterio del 1 al 4
    
    Criterios:
    - Criterio 1: longCOVID (fenotipo general)
    - Criterio 2: Síntomas recurrentes (covid==1 & sintoma_recurrente_count>1 & recuperado_3m==2)
    - Criterio 3: Cluster (pertenece a algún cluster)
    - Criterio 4: Secuelas (tiene secuelas)
    
    Args:
        df: DataFrame de long COVID
    
    Returns:
        DataFrame con variables criterio_1, criterio_2, criterio_3, criterio_4
    """
    return df.with_columns([
        # Criterio 1: longCOVID general
        pl.when(pl.col("longCOVID") == 1)
        .then(1)
        .otherwise(0)
        .alias("criterio_1"),
        
        # Criterio 2: Síntomas recurrentes
        pl.when(
            (pl.col("covid") == 1) & 
            (pl.col("sintoma_recurrente_count") > 1) & 
            (pl.col("recuperado_3m") == 2)
        )
        .then(1)
        .otherwise(0)
        .alias("criterio_2"),
        
        # Criterio 3: COVID + pertenece_cluster_count >= 1 + No recuperado
        # DP4 (covid == 1) & P17 (pertenece_cluster_count >= 1) & P20 (recuperado_3m == 2)
        # IMPORTANTE: Si recuperado_3m es NULL, el caso se marca como 0 (no cumple criterio)
        pl.when(
            (pl.col("covid") == 1) & 
            (pl.col("pertenece_cluster_count") >= 1) & 
            (pl.col("recuperado_3m") == 2) &
            (~pl.col("recuperado_3m").is_null())
        )
        .then(1)
        .otherwise(0)
        .alias("criterio_3"),
        
        # Criterio 4: COVID + Nueva condición O Secuelas
        # DP4 (covid == 1) & (P21 (conteo_nueva_condicion >= 1) | P22 (sec_count >= 1))
        pl.when(
            (pl.col("covid") == 1) & 
            ((pl.col("conteo_nueva_condicion") >= 1) | (pl.col("sec_count") >= 1))
        )
        .then(1)
        .otherwise(0)
        .alias("criterio_4")
    ])


def count_by_criterio(df: pl.DataFrame) -> pl.DataFrame:
    """
    Cuenta cuántos casos hay por cada criterio
    
    Args:
        df: DataFrame con variables de criterio
    
    Returns:
        DataFrame con conteos por criterio
    """
    return pl.DataFrame({
        "criterio": ["criterio_1", "criterio_2", "criterio_3", "criterio_4"],
        "cumple_criterio": [
            df.filter(pl.col("criterio_1") == 1).height,
            df.filter(pl.col("criterio_2") == 1).height,
            df.filter(pl.col("criterio_3") == 1).height if "criterio_3" in df.columns else 0,
            df.filter(pl.col("criterio_4") == 1).height if "criterio_4" in df.columns else 0,
        ],
        "no_cumple": [
            df.filter(pl.col("criterio_1") == 0).height,
            df.filter(pl.col("criterio_2") == 0).height,
            df.filter(pl.col("criterio_3") == 0).height if "criterio_3" in df.columns else 0,
            df.filter(pl.col("criterio_4") == 0).height if "criterio_4" in df.columns else 0,
        ]
    })


def aggregate_by_semana_epi(df: pl.DataFrame, group_col: str) -> pl.DataFrame:
    """
    Agrega datos por semana epidemiológica
    
    Args:
        df: DataFrame de entrada
        group_col: Columna adicional para agrupar (linaje, cluster, etc.)
    
    Returns:
        DataFrame agregado por semana epidemiológica
    """
    return df.group_by(["semana_epi", group_col]).agg([
        pl.len().alias("n_casos")
    ]).sort("semana_epi")


def create_descriptive_table(df: pl.DataFrame, variables: list[str]) -> pl.DataFrame:
    """
    Crea tabla descriptiva (Tabla 1) con estadísticas de variables
    
    Args:
        df: DataFrame de entrada
        variables: Lista de variables a incluir
    
    Returns:
        DataFrame con estadísticas descriptivas
    """
    stats_list = []
    
    for var in variables:
        if df[var].dtype in [pl.Int64, pl.Float64]:
            # Variables numéricas
            stats_list.append({
                "variable": var,
                "n": df.select(pl.col(var).count()).item(),
                "media": df.select(pl.col(var).mean()).item(),
                "mediana": df.select(pl.col(var).median()).item(),
                "min": df.select(pl.col(var).min()).item(),
                "max": df.select(pl.col(var).max()).item(),
            })
        else:
            # Variables categóricas
            counts = df.group_by(var).agg(pl.len().alias("n"))
            stats_list.append({
                "variable": var,
                "n": df.select(pl.col(var).count()).item(),
                "categorias": counts.height,
                "media": None,
                "mediana": None,
                "min": None,
                "max": None,
            })
    
    return pl.DataFrame(stats_list)


def analyze_criterios_null_impact(df: pl.DataFrame) -> dict:
    """
    Analiza el impacto de los valores NULL en cada criterio.
    Compara los conteos originales vs conteos solo con datos completos.
    
    Args:
        df: DataFrame con los criterios calculados
    
    Returns:
        Dict con análisis de NULLs por criterio:
        {
            'criterio_1': {
                'total_casos': int,
                'casos_con_datos_completos': int,
                'casos_perdidos': int,
                'variables': list[str]
            },
            ...
        }
    """
    # Variables involucradas en cada criterio
    criterios_vars = {
        'criterio_1': ['longCOVID'],
        'criterio_2': ['covid', 'sintoma_recurrente_count', 'recuperado_3m'],
        'criterio_3': ['covid', 'pertenece_cluster_count', 'recuperado_3m'],
        'criterio_4': ['covid', 'conteo_nueva_condicion', 'sec_count']
    }
    
    resultado = {}
    
    for criterio_num in range(1, 5):
        criterio_col = f'criterio_{criterio_num}'
        variables = criterios_vars[criterio_col]
        
        # Conteo total de casos que cumplen el criterio (con o sin NULLs)
        total_casos = df.filter(pl.col(criterio_col) == 1).height
        
        # Filtrar solo los casos que cumplen el criterio Y tienen todos los datos completos
        df_sin_nulls = df
        for var in variables:
            df_sin_nulls = df_sin_nulls.filter(pl.col(var).is_not_null())
        
        casos_con_datos_completos = df_sin_nulls.filter(pl.col(criterio_col) == 1).height
        
        # Casos perdidos por tener NULLs
        casos_perdidos = total_casos - casos_con_datos_completos
        porcentaje_perdido = (casos_perdidos / total_casos * 100) if total_casos > 0 else 0
        
        # Total de registros con datos completos para este criterio
        total_con_datos_completos = df_sin_nulls.height
        
        resultado[criterio_col] = {
            'total_casos': total_casos,
            'casos_con_datos_completos': casos_con_datos_completos,
            'casos_perdidos': casos_perdidos,
            'porcentaje_perdido': porcentaje_perdido,
            'variables': variables,
            'total_registros_completos': total_con_datos_completos
        }
    
    return resultado
