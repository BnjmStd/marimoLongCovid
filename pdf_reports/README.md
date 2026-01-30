# 📊 Reportes PDF - Análisis Long COVID

Este directorio contiene reportes PDF individuales generados automáticamente del análisis Long COVID.

## 📁 Estructura

Cada PDF contiene:
- **Página 1:** Interpretación clínica y epidemiológica del gráfico
- **Página 2:** Visualización del gráfico en alta resolución

## 📋 Lista de Reportes

### Criterios de Long COVID
1. **Criterio_1_COVID_19_Confirmado_por_Semana.pdf** (99K)
   - Casos COVID confirmados por semana epidemiológica
   
2. **Criterio_2_Distribución_de_Síntomas_Persistentes.pdf** (34K)
   - Síntomas recurrentes ≥3 meses
   
3. **Criterio_3_Comparación_de_Clusters_Sintomáticos.pdf** (55K)
   - Clusters sintomáticos + No recuperado a 3 meses
   
4. **Criterio_3_sin_Nulls_Evolución_Temporal.pdf** (54K)
   - Criterio 3 excluyendo casos con datos incompletos

### Análisis Temporal
5. **Long_COVID_General_por_Semana_Epidemiológica.pdf** (48K)
   - Vista general de Long COVID en el tiempo

### Heatmaps
6. **Heatmap_de_Clusters_por_Semana_de_Diagnóstico.pdf** (68K)
   - Intensidad temporal por cluster/fenotipo
   
7. **Heatmap_Demográfico_Clínico.pdf** (75K)
   - Características clínicas por edad y sexo

### Análisis Demográficos y Genéticos
8. **Distribución_de_Ancestrías_Genéticas.pdf** (30K)
   - Proporciones de EUR, AFR, EAS, AYM, MAP
   
9. **Hospitalización_por_Semana_Epidemiológica.pdf** (28K)
   - Casos hospitalizados vs no hospitalizados
   
10. **Distribución_de_Casos_por_Sexo.pdf** (51K)
    - Análisis de género
    
11. **Distribución_de_Casos_por_Grupos_Etarios.pdf** (44K)
    - Estratificación por edad

## 🎨 Características Técnicas

- **Formato:** PDF (Portable Document Format)
- **Tamaño de página:** Letter (8.5" x 11")
- **Resolución de imágenes:** 1200x800 pixels
- **Generado con:** 
  - Python 3.13
  - ReportLab (generación de PDFs)
  - Plotly + Kaleido (exportación de gráficos)
  - Polars (análisis de datos)

## 🔄 Regenerar Reportes

Para regenerar todos los PDFs:

```bash
python generate_pdf_reports.py
```

Esto creará/actualizará todos los archivos PDF en este directorio.

## 🗑️ Limpiar Archivos Temporales

Las imágenes temporales se guardan en `temp_images/`. Para eliminarlas:

```bash
rm -rf pdf_reports/temp_images
```

O usa el script de limpieza:

```bash
python cleanup_temp_files.py
```

## 📊 Estadísticas

- **Total de reportes:** 11 PDFs
- **Tamaño total:** ~585 KB
- **Promedio por reporte:** ~53 KB
- **Tiempo de generación:** ~15-20 segundos

## 🚀 Uso

Estos PDFs están diseñados para:
- Presentaciones científicas
- Documentación de resultados
- Compartir con colaboradores
- Publicaciones y reportes
- Archivo de análisis

## ⚠️ Notas

- Los PDFs se regeneran cada vez que ejecutas el script
- Las imágenes temporales pueden ser eliminadas después de la generación
- Los nombres de archivo se basan en los títulos de los gráficos

---

Generado automáticamente por `generate_pdf_reports.py`  
Proyecto: Análisis Long COVID  
Fecha: $(date +"%Y-%m-%d")
