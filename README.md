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

## Cómo funciona Marimo

Marimo es un notebook reactivo. A diferencia de Jupyter:

1. Las celdas son funciones Python decoradas con @app.cell
2. Cada celda retorna variables en una tupla
3. Si cambias una celda, todas las celdas que dependen de ella se ejecutan automáticamente
4. No hay estado oculto ni orden de ejecución confuso

### Anatomía de una celda

```python
@app.cell
def __():
    x = 10
    y = 20
    return x, y  # Variables disponibles para otras celdas
```

### Dependencias automáticas

```python
@app.cell
def __(x, y):  # Esta celda depende de x e y
    resultado = x + y
    return resultado,
```

Si modificas la celda que define `x`, esta segunda celda se re-ejecuta automáticamente.

### Cargar datos

```python
@app.cell
def __(pl):
    df = pl.read_csv("data/archivo.csv")
    return df,
```

El archivo analysis.py es un script Python normal. Puedes ejecutarlo con `python analysis.py` o en Marimo para la interfaz interactiva.
# marimoLongCovid
