# Soluciones Implementadas - Heatmap y Tablas en PDF

## 📋 Resumen de Problemas Solucionados

### ✅ Problema 1: Heatmap de Clusters
**ANTES:** El heatmap mostraba solo nombres de clusters por semana
**AHORA:** Muestra todos los síntomas individuales ordenados por cluster

### ✅ Problema 2: Tablas Cortadas en PDF
**ANTES:** Las tablas se exportaban como PNG y salían cortadas
**AHORA:** Las tablas usan ReportLab Table nativo con soporte multipágina

---

## 🔧 Cambios Implementados

### 1. Nueva Función de Heatmap (modules/visualizations.py)

**Archivo modificado:** `modules/visualizations.py`
**Función:** `plot_clusters_heatmap_by_diagnosis_week()`

#### Características:
- ✨ Muestra **25 síntomas individuales** agrupados por 6 clusters
- 📊 Organización clara con separadores visuales entre clusters
- 🎨 Colorscale Viridis para mostrar intensidad
- 📏 Dimensiones: 800px alto x 1400px ancho (para ver todos los síntomas)

#### Clusters y Síntomas Incluidos:

**AIRWAYS (Vías Aéreas):**
- Congestión nasal
- Tos
- Dolor de garganta

**COGNITIVE (Cognitivo):**
- Depresión/Ansiedad
- Problemas de memoria
- Dolor de cabeza
- Somnolencia

**GASTROINTESTINAL:**
- Dolor abdominal
- Náuseas
- Edema (piernas hinchadas)
- Diarrea
- Pérdida de peso
- Cambio en apetito

**MUSCULAR:**
- Dolor muscular
- Dolor articular
- Piernas pesadas

**RESPIRATORY (Respiratorio):**
- Falta de aliento
- Fatiga
- Dolor de pecho
- Dificultad para respirar

**SMELL/TASTE (Olfato/Gusto):**
- Anosmia
- Cambio en olfato
- Ageusia
- Cambio en gusto

#### Mapeo de Variables:
Los síntomas se mapean a las columnas del dataset:
- `congestion_3m`, `tos_3m`, `do_garganta_3m`
- `depresion_3m`, `memoria_3m`, `do_cabeza_3m`, `somnolencia_3m`
- `do_abdominal_3m`, `nausea_3m`, `hin_piernas_3m`, `diarrea_3m`, `pe_peso_3m`, `apetito_3m`
- `do_musculos_3m`, `do_articulacion_3m`, `pes_piernas_3m`
- `fa_aliento_3m`, `fatiga_3m`, `do_pecho_3m`, `di_respirar_3m`
- `pe_olfato_3m`, `ca_olfato_3m`, `pe_gusto_3m`, `ca_gusto_3m`

---

### 2. Nueva Función para Exportar Tablas (generate_pdf_reports.py)

**Archivo modificado:** `generate_pdf_reports.py`

#### Nuevas Funciones Agregadas:

##### `extract_table_data_from_plotly(fig)`
Extrae datos de una tabla de Plotly (go.Table) y los convierte a formato compatible con ReportLab.

##### `create_pdf_table_report(title, interpretation, table_fig, output_filename)`
Crea PDFs con tablas usando ReportLab Table nativo:
- ✅ **Sin cortes:** Las tablas se extienden a múltiples páginas
- 📄 **Formato profesional:** Headers fijos, zebra striping, colores
- 📏 **Anchos dinámicos:** Se ajustan al ancho de la página
- 🔁 **Repeat headers:** Headers se repiten en cada página

#### Características de las Tablas PDF:

**Estilo Visual:**
- Header: Fondo azul oscuro (#2c3e50), texto blanco
- Body: Filas alternas blancas y gris claro (#f0f0f0)
- Fuente: Helvetica, tamaños 8-10pt
- Bordes: Grid gris con línea gruesa bajo header

**Capacidad:**
- Máximo 100 filas por tabla (configurable)
- Si hay más filas, muestra mensaje indicando el total
- Soporte multipágina automático

**Limpieza de Datos:**
- Elimina tags HTML básicos (`<b>`, `<i>`, `<br>`)
- Convierte todos los valores a string
- Maneja celdas vacías correctamente

#### Detección Automática:
El script ahora detecta automáticamente si una figura es tabla o gráfico:
```python
if first_trace.type == 'table':
    # Usar create_pdf_table_report()
else:
    # Usar create_pdf_report() con PNG
```

---

## 🚀 Cómo Usar

### Generar PDFs con los Nuevos Cambios:

```bash
cd /home/fermin/marimoLongCovid
python generate_pdf_reports.py
```

### Ver el Nuevo Heatmap en Marimo:

```bash
marimo edit analysis_long_covid.py
```

Buscar la celda con `plot_clusters_heatmap_by_diagnosis_week()` para ver el heatmap actualizado.

---

## 🗂️ Archivos Modificados

| Archivo | Líneas Modificadas | Cambios Principales |
|---------|-------------------|---------------------|
| `modules/visualizations.py` | ~990-1070 | Nueva función heatmap con síntomas |
| `generate_pdf_reports.py` | ~75-200, ~806-850 | Funciones para tablas + detección automática |

---

## ✨ Beneficios

### Heatmap de Síntomas:
1. **Más detallado:** 25 síntomas vs 7 clusters
2. **Mejor organización:** Agrupado visualmente por cluster
3. **Más información:** Permite ver prevalencia de síntomas específicos
4. **Análisis temporal:** Evolución de cada síntoma por semana

### Tablas en PDF:
1. **Completas:** Ya no se cortan
2. **Multipágina:** Tablas largas se distribuyen correctamente
3. **Profesionales:** Formato similar a publicaciones científicas
4. **Mantenibles:** Más fácil modificar estilo que con PNG

---

## 📝 Notas Técnicas

### Dependencias Requeridas:
```bash
pip install reportlab plotly polars scipy
```

### Variables del Dataset Necesarias:
- Columnas de síntomas a 3 meses: `*_3m`
- Columna de semana: `yearweek`
- Columnas de clusters: `cluster_*_bi`

### Configuración Personalizable:

**En el heatmap:**
- `height=800` - Altura en pixeles
- `width=1400` - Ancho en pixeles
- `colorscale='Viridis'` - Paleta de colores

**En las tablas:**
- `max_rows = 100` - Límite de filas a mostrar
- `col_width` - Ancho de columnas
- Colores en `TableStyle()`

---

## 🐛 Solución de Problemas

### Si el heatmap sale vacío:
- Verificar que existan las columnas `*_3m` en el dataset
- Verificar que `yearweek` tenga valores

### Si las tablas no se generan:
- Verificar que el trace sea de tipo 'table'
- Revisar logs para ver errores de extracción

### Si las imágenes no se generan:
- Instalar kaleido: `pip install kaleido`
- O configurar orca como fallback

---

## 📧 Contacto

Para preguntas o problemas, consultar la documentación de:
- [Plotly](https://plotly.com/python/)
- [ReportLab](https://www.reportlab.com/docs/reportlab-userguide.pdf)
- [Polars](https://pola-rs.github.io/polars/py-polars/html/reference/)
