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
    
    Args:
        df: DataFrame de long COVID
    
    Returns:
        DataFrame con variables criterio_1, criterio_2, criterio_3, criterio_4
    """
    # Aquí defines la lógica de cada criterio según tus reglas
    # Ejemplo genérico - ajustar según tus criterios reales
    return df.with_columns([
        pl.lit(None).alias("criterio_1"),  # Reemplazar con tu lógica
        pl.lit(None).alias("criterio_2"),
        pl.lit(None).alias("criterio_3"),
        pl.lit(None).alias("criterio_4")
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
        "n_casos": [
            df.filter(pl.col("criterio_1").is_not_null()).height,
            df.filter(pl.col("criterio_2").is_not_null()).height,
            df.filter(pl.col("criterio_3").is_not_null()).height,
            df.filter(pl.col("criterio_4").is_not_null()).height,
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
        pl.count().alias("n_casos")
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
            counts = df.group_by(var).agg(pl.count().alias("n"))
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
