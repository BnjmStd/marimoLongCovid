# 📄 Generador de Reportes PDF

Script automatizado para generar reportes PDF individuales de todos los gráficos del análisis Long COVID.

## 🎯 Características

- ✅ Genera **11 PDFs individuales** (uno por gráfico)
- ✅ Cada PDF tiene **2 páginas**:
  - **Página 1:** Interpretación clínica y epidemiológica
  - **Página 2:** Gráfico en alta resolución (1200x800 px)
- ✅ Nombres de archivo basados en títulos de gráficos
- ✅ Exportación automática usando Plotly + Kaleido
- ✅ Formato profesional con ReportLab

## 🚀 Uso

### Generar todos los PDFs

```bash
python generate_pdf_reports.py
```

**Salida:**
- PDFs en directorio `pdf_reports/`
- Imágenes temporales en `pdf_reports/temp_images/`

### Limpiar archivos temporales

```bash
python cleanup_temp_files.py
```

O directamente:

```bash
rm -rf pdf_reports/temp_images
```

## 📊 Reportes Generados

| # | Reporte | Tamaño | Descripción |
|---|---------|--------|-------------|
| 1 | Criterio_1_COVID_19_Confirmado_por_Semana.pdf | 99K | Casos COVID confirmados |
| 2 | Criterio_2_Distribución_de_Síntomas_Persistentes.pdf | 34K | Síntomas recurrentes ≥3 meses |
| 3 | Criterio_3_Comparación_de_Clusters_Sintomáticos.pdf | 55K | Clusters + No recuperado |
| 4 | Criterio_3_sin_Nulls_Evolución_Temporal.pdf | 54K | Criterio 3 sin datos incompletos |
| 5 | Long_COVID_General_por_Semana_Epidemiológica.pdf | 48K | Vista general temporal |
| 6 | Heatmap_de_Clusters_por_Semana_de_Diagnóstico.pdf | 68K | Intensidad temporal por fenotipo |
| 7 | Heatmap_Demográfico_Clínico.pdf | 75K | Características por edad/sexo |
| 8 | Distribución_de_Ancestrías_Genéticas.pdf | 30K | EUR, AFR, EAS, AYM, MAP |
| 9 | Hospitalización_por_Semana_Epidemiológica.pdf | 28K | Hospitalizados vs no hospitalizados |
| 10 | Distribución_de_Casos_por_Sexo.pdf | 51K | Análisis de género |
| 11 | Distribución_de_Casos_por_Grupos_Etarios.pdf | 44K | Estratificación por edad |

**Total:** ~585 KB

## 🛠️ Dependencias

```bash
pip install reportlab kaleido polars plotly
```

### Versiones probadas:
- Python 3.13.2
- reportlab 4.2.5
- kaleido 0.2.1
- polars 1.20.0
- plotly 5.24.1

## 📁 Estructura de Archivos

```
long-covid/
├── generate_pdf_reports.py       # Script principal
├── cleanup_temp_files.py          # Limpieza de temporales
├── pdf_reports/                   # Directorio de salida
│   ├── README.md                  # Documentación de PDFs
│   ├── *.pdf                      # 11 PDFs generados
│   └── temp_images/               # Imágenes temporales (PNG)
│       └── *.png
└── modules/                       # Módulos de análisis
    ├── visualizations.py
    └── ...
```

## 🎨 Personalización

### Modificar reportes

Edita el diccionario `reports` en `generate_pdf_reports.py`:

```python
reports.append({
    'function': tu_funcion_de_grafico,
    'args': (df_con_criterios, otros_args),
    'title': 'Título del Gráfico',
    'interpretation': """
    Tu interpretación aquí...
    Puede incluir:
    - Listas con viñetas
    - Múltiples párrafos
    - Estadísticas clave
    """
})
```

### Cambiar formato de página

En `create_pdf_report()`, modifica:

```python
from reportlab.lib.pagesizes import A4, letter

doc = SimpleDocTemplate(
    str(pdf_path),
    pagesize=A4,  # O letter, legal, etc.
    ...
)
```

### Ajustar resolución de imágenes

En `save_plotly_figure_as_image()`:

```python
fig.write_image(
    str(img_path), 
    width=1200,   # Ancho en pixels
    height=800    # Alto en pixels
)
```

## 🔍 Ejemplo de Salida

### Página 1: Interpretación
```
┌────────────────────────────────────────┐
│  Heatmap Demográfico-Clínico          │
│                                        │
│  Variables: EUR, AFR, EAS, AYM, MAP   │
│                                        │
│  Hallazgos clave:                     │
│  • EUR (Europea): 54.41%              │
│  • MAP (Mapuche): 32.40%              │
│  • ...                                 │
│                                        │
│  Implicaciones:                        │
│  • Diversidad genética de Chile       │
│  • ...                                 │
└────────────────────────────────────────┘
```

### Página 2: Gráfico
```
┌────────────────────────────────────────┐
│  Heatmap Demográfico-Clínico          │
│                                        │
│  [GRÁFICO EN ALTA RESOLUCIÓN]         │
│  [1200x800 pixels]                    │
│                                        │
└────────────────────────────────────────┘
```

## 🐛 Solución de Problemas

### Error: "kaleido no encontrado"

```bash
pip install kaleido
```

### Error: "reportlab no encontrado"

```bash
pip install reportlab
```

### Los PDFs están en blanco

Verifica que los gráficos se generen correctamente:

```python
from modules import plot_linaje_barplot, load_data, create_criterio_variables

df = load_data('datasets/longcovid_2020W13-2021W22.csv')
df_c = create_criterio_variables(df)
fig = plot_linaje_barplot(df_c)
fig.show()  # Debe mostrar el gráfico
```

### Imágenes temporales muy grandes

Ajusta la resolución en `save_plotly_figure_as_image()` o limpia regularmente con:

```bash
python cleanup_temp_files.py
```

## 📝 Notas

- El script carga ~1.5K registros, toma 15-20 segundos generar todos los PDFs
- Las imágenes temporales pueden ser eliminadas después de generar PDFs
- Los PDFs son independientes, puedes compartirlos individualmente
- Formato optimizado para impresión (Letter 8.5"x11")

## 🎓 Uso Académico

Estos PDFs son ideales para:
- Presentaciones en conferencias
- Suplementos de artículos científicos
- Reportes a organismos de salud
- Documentación de proyectos
- Material didáctico

## 📧 Soporte

Si encuentras problemas, verifica:
1. Todas las dependencias instaladas
2. Dataset presente en `datasets/longcovid_2020W13-2021W22.csv`
3. Permisos de escritura en directorio `pdf_reports/`

---

**Autor:** Generador automático Long COVID  
**Última actualización:** Enero 2026  
**Licencia:** Proyecto académico
