"""
Funciones para cargar datos de variantes y long COVID
"""
import polars as pl
from pathlib import Path


def load_data(filepath: str, file_type: str = "csv") -> pl.DataFrame:
    """
    Carga datos desde diferentes formatos
    
    Args:
        filepath: Ruta al archivo
        file_type: Tipo de archivo (csv, parquet, excel)
    
    Returns:
        DataFrame de Polars
    """
    file_path = Path(filepath)
    
    if not file_path.exists():
        raise FileNotFoundError(f"Archivo no encontrado: {file_path}")
    
    if file_type == "csv":
        return pl.read_csv(
            file_path,
            null_values=["NA", "N/A", ""],
            infer_schema_length=10000
        )
    elif file_type == "parquet":
        return pl.read_parquet(file_path)
    elif file_type == "excel":
        return pl.read_excel(file_path)
    else:
        raise ValueError(f"Tipo de archivo no soportado: {file_type}")


def load_long_covid(filepath: str = "data/long_covid.csv") -> pl.DataFrame:
    """
    Carga dataset de long COVID
    
    Args:
        filepath: Ruta al archivo de long COVID
    
    Returns:
        DataFrame con datos de long COVID
    """
    return load_data(filepath, file_type="csv")
