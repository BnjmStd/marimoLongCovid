#!/usr/bin/env python3
"""
Generador de PDFs individuales para cada gráfico del análisis Long COVID
Cada PDF contiene:
- Página 1: Interpretación del gráfico
- Página 2: El gráfico visualizado

Uso: python generate_pdf_reports.py
"""

import os
from pathlib import Path
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER
from reportlab.pdfgen import canvas
import polars as pl

# Imports de módulos del proyecto
from modules import (
    load_data,
    create_criterio_variables,
    plot_criterio_comparison,
    plot_criterio1_by_week,
    plot_criterio2_sintomas,
    plot_criterio2_promedio_sintomas,
    plot_criterio2_promedio_sintomas_by_week,
    plot_criterio2_recovery,
    plot_criterio3_clusters_comparison,
    plot_longcovid_by_week,
    plot_sintomas_recurrentes_by_week,
    plot_cluster_pertenencia_by_week,
    plot_clusters_individuales_by_week,
    plot_secuelas_by_week,
    plot_clusters_heatmap_by_diagnosis_week,
    plot_demographic_clinical_heatmap,
    plot_criterio_barplot,
    plot_cases_by_week_by_sex,
    plot_cases_by_week_by_age_group,
    plot_cases_by_week_by_secuelas,
    plot_cases_by_week_by_nueva_condicion,
    plot_cases_by_week_by_sintomas_recurrentes,
    plot_cases_by_week_by_criterio_3_sin_nulls,
    plot_linaje_barplot,
    plot_hospitalizacion_by_week,
    create_table1_stratified
)

# Crear directorio de salida
OUTPUT_DIR = Path("pdf_reports")
OUTPUT_DIR.mkdir(exist_ok=True)

# Configuración
IMG_DIR = OUTPUT_DIR / "temp_images"
IMG_DIR.mkdir(exist_ok=True)


def clean_filename(title: str) -> str:
    """Limpia el título para usarlo como nombre de archivo"""
    import re
    # Remover caracteres especiales y espacios
    cleaned = re.sub(r'[^\w\s-]', '', title)
    cleaned = re.sub(r'[-\s]+', '_', cleaned)
    return cleaned[:100]  # Limitar longitud


def save_plotly_figure_as_image(fig, filename: str) -> str:
    """Guarda una figura de plotly como imagen PNG"""
    img_path = IMG_DIR / f"{filename}.png"
    try:
        # Intentar con kaleido primero
        fig.write_image(str(img_path), width=1200, height=800)
    except Exception as e:
        print(f"   ⚠️  No se pudo usar kaleido, intentando con orca: {e}")
        try:
            import plotly.io as pio
            pio.write_image(fig, str(img_path), format='png', width=1200, height=800)
        except Exception as e2:
            print(f"   ❌ Error guardando imagen: {e2}")
            return None
    return str(img_path)


def create_pdf_report(title: str, interpretation: str, image_path: str, output_filename: str):
    """
    Crea un PDF con interpretación en página 1 y gráfico en página 2
    
    Args:
        title: Título del gráfico
        interpretation: Texto de interpretación (puede incluir markdown básico)
        image_path: Path a la imagen del gráfico
        output_filename: Nombre del archivo PDF de salida
    """
    pdf_path = OUTPUT_DIR / output_filename
    
    # Crear documento
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=1*inch,
        bottomMargin=0.75*inch
    )
    
    # Estilos
    styles = getSampleStyleSheet()
    
    # Estilo personalizado para título
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor='#2c3e50',
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    # Estilo para texto normal
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        leading=16,
        alignment=TA_LEFT,
        spaceAfter=12,
        fontName='Helvetica'
    )
    
    # Estilo para subtítulos
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=13,
        textColor='#34495e',
        spaceAfter=10,
        spaceBefore=15,
        fontName='Helvetica-Bold'
    )
    
    # Construir contenido
    story = []
    
    # PÁGINA 1: INTERPRETACIÓN
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Procesar interpretación (convertir markdown básico a reportlab)
    lines = interpretation.strip().split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            story.append(Spacer(1, 0.1*inch))
            continue
        
        # Detectar subtítulos (líneas que empiezan con **)
        if line.startswith('**') and '**' in line[2:]:
            # Extraer texto entre **
            clean_line = line.replace('**', '').strip()
            if ':' in clean_line:
                clean_line = clean_line.split(':')[0]
            story.append(Paragraph(f"<b>{clean_line}</b>", subtitle_style))
        # Detectar listas
        elif line.startswith('- ') or line.startswith('• '):
            clean_line = line[2:].strip()
            # Remover todos los **
            clean_line = clean_line.replace('**', '')
            story.append(Paragraph(f"• {clean_line}", normal_style))
        # Texto normal
        else:
            # Remover todos los **
            clean_line = line.replace('**', '')
            if clean_line:
                story.append(Paragraph(clean_line, normal_style))
    
    # Page break antes del gráfico
    story.append(PageBreak())
    
    # PÁGINA 2: GRÁFICO
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 0.3*inch))
    
    if image_path and os.path.exists(image_path):
        # Calcular tamaño de imagen para que quepa en la página
        available_width = letter[0] - 1.5*inch
        available_height = letter[1] - 2*inch
        
        img = Image(image_path, width=available_width, height=available_height, kind='proportional')
        story.append(img)
    else:
        story.append(Paragraph("<i>Imagen no disponible</i>", normal_style))
    
    # Construir PDF
    doc.build(story)
    print(f"   ✅ PDF creado: {pdf_path.name}")


def generate_all_reports():
    """Genera todos los reportes PDF"""
    print("="*70)
    print("GENERADOR DE REPORTES PDF - ANÁLISIS LONG COVID")
    print("="*70)
    
    # 1. Cargar datos
    print("\n📊 Cargando datos...")
    df = load_data('datasets/longcovid_2020W13-2021W22.csv')
    df_con_criterios = create_criterio_variables(df)
    print(f"   ✅ {df_con_criterios.height:,} registros cargados")
    
    # Lista de gráficos a generar: (nombre_funcion, args, título, interpretación)
    reports = []
    
    # CRITERIO 1
    reports.append({
        'function': plot_criterio1_by_week,
        'args': (df_con_criterios,),
        'title': 'Criterio 1 - COVID-19 Confirmado por Semana',
        'interpretation': """
**Definición del Criterio 1:**
COVID-19 confirmado por diagnóstico médico (variable covid == 1 en DP4)

**Hallazgos clave:**
- Representa la base mínima para Long COVID
- Muestra la evolución temporal de casos confirmados
- Color naranja indica casos que cumplen el criterio

**Implicaciones clínicas:**
- Todos los análisis posteriores parten de casos COVID confirmados
- La confirmación diagnóstica es esencial para Long COVID
- Patrón temporal refleja las olas de la pandemia en el período estudiado
        """
    })
    
    # CRITERIO 2
    reports.append({
        'function': plot_criterio2_sintomas,
        'args': (df_con_criterios,),
        'title': 'Criterio 2 - Distribución de Síntomas Persistentes',
        'interpretation': """
**Definición del Criterio 2:**
COVID-19 + Síntomas recurrentes (≥3 meses)

**Hallazgos clave:**
- Muestra la distribución de síntomas que persisten a los 3 meses
- Color verde indica casos que cumplen el criterio
- Identifica la carga sintomática post-COVID

**Implicaciones clínicas:**
- Los síntomas recurrentes son un marcador clave de Long COVID
- Permite identificar la frecuencia de presentaciones sintomáticas prolongadas
- Útil para planificación de seguimiento clínico
        """
    })
    
    # CRITERIO 3
    reports.append({
        'function': plot_criterio3_clusters_comparison,
        'args': (df_con_criterios,),
        'title': 'Criterio 3 - Comparación de Clusters Sintomáticos',
        'interpretation': """
**Definición del Criterio 3:**
COVID-19 + Clusters sintomáticos + No recuperado a 3 meses

**Hallazgos clave:**
- Compara la presencia de clusters entre casos que cumplen vs no cumplen el criterio
- Identifica fenotipos sintomáticos asociados a persistencia
- Color naranja para casos con Long COVID por clusters

**Implicaciones clínicas:**
- Los clusters permiten identificar subgrupos de Long COVID
- Útil para estratificar intervenciones según fenotipo
- Facilita el seguimiento de patrones sintomáticos específicos
        """
    })
    
    # CRITERIO 3 SIN NULLS
    reports.append({
        'function': plot_cases_by_week_by_criterio_3_sin_nulls,
        'args': (df_con_criterios,),
        'title': 'Criterio 3 sin Nulls - Evolución Temporal',
        'interpretation': """
**Definición:**
Criterio 3 excluyendo casos con valores NULL en recuperado_3m (8 casos omitidos)

**Hallazgos clave:**
- Excluye 8 casos sin información de recuperación a 3 meses
- Muestra evolución temporal de casos con datos completos
- Permite análisis más preciso al filtrar datos incompletos

**Implicaciones:**
- Análisis con mayor calidad de datos
- 360 casos cumplen el criterio 3 (23.9%)
- Útil para estudios longitudinales con seguimiento completo
        """
    })
    
    # LONG COVID GENERAL
    reports.append({
        'function': plot_longcovid_by_week,
        'args': (df_con_criterios,),
        'title': 'Long COVID General por Semana Epidemiológica',
        'interpretation': """
**Definición:**
Variable longCOVID calculada a partir de múltiples criterios

**Hallazgos clave:**
- Vista general de la carga de Long COVID en el tiempo
- Identifica períodos de mayor prevalencia
- Color morado para casos con Long COVID

**Implicaciones:**
- Herramienta de vigilancia epidemiológica
- Permite identificar tendencias temporales
- Útil para planificación de recursos de salud
        """
    })
    
    # HEATMAP CLUSTERS
    reports.append({
        'function': plot_clusters_heatmap_by_diagnosis_week,
        'args': (df_con_criterios,),
        'title': 'Heatmap de Clusters por Semana de Diagnóstico',
        'interpretation': """
**Estructura:**
Eje X: Semana epidemiológica | Eje Y: Clusters sintomáticos

**Hallazgos clave:**
- Visualiza la intensidad temporal de cada fenotipo
- Colores cálidos (amarillo) = mayor número de casos
- Colores fríos (azul) = menor número de casos

**Implicaciones:**
- Identifica patrones temporales específicos por cluster
- Permite detectar semanas con mayor carga sintomática
- Útil para análisis de fenotipos predominantes en diferentes períodos
        """
    })
    
    # HEATMAP DEMOGRÁFICO
    reports.append({
        'function': plot_demographic_clinical_heatmap,
        'args': (df_con_criterios,),
        'title': 'Heatmap Demográfico-Clínico',
        'interpretation': """
**Estructura:**
Eje X: Grupos etarios (< 30, 30-44, 45-59, >60) + Sexo
Eje Y: Hospitalización, Severidad, Condiciones preexistentes

**Hallazgos clave:**
- Gradiente etario claro: mayor edad = mayor riesgo
- Adultos mayores (>60): 38.6% hospitalizados vs 4.3% en jóvenes (<30)
- Comorbilidades aumentan 4.7x de jóvenes a adultos mayores
- Diferencias por sexo: Femenino 20.3% hosp vs Masculino 11.7%

**Implicaciones:**
- Identificación de poblaciones prioritarias
- Estratificación de riesgo basada en demografía
- Diseño de políticas focalizadas por grupo vulnerable
        """
    })
    
    # ANCESTRÍAS GENÉTICAS
    reports.append({
        'function': plot_linaje_barplot,
        'args': (df_con_criterios,),
        'title': 'Distribución de Ancestrías Genéticas',
        'interpretation': """
**Variables:** EUR, AFR, EAS, AYM, MAP

**Hallazgos clave:**
- EUR (Europea): 54.41% - Ancestría predominante
- MAP (Mapuche): 32.40% - Componente indígena significativo
- AYM (Aymara): 10.45% - Población indígena del norte
- EAS (Este Asiática): 1.76%
- AFR (Africana): 0.98%

**Implicaciones:**
- Refleja la diversidad genética de Chile
- Permite estudios de asociación entre ancestría y Long COVID
- Visibiliza poblaciones indígenas en investigación
- Contexto para medicina de precisión y equidad en salud
        """
    })
    
    # HOSPITALIZACIÓN POR SEMANA
    reports.append({
        'function': plot_hospitalizacion_by_week,
        'args': (df_con_criterios,),
        'title': 'Hospitalización por Semana Epidemiológica',
        'interpretation': """
**Variables:** yearweek, Hospitalización

**Hallazgos clave:**
- 223 casos hospitalizados (14.8% del total)
- 1,273 casos no hospitalizados (85.2%)
- Color rojo = hospitalizados (severidad aguda)
- Color gris = no hospitalizados

**Implicaciones:**
- La hospitalización en fase aguda puede predecir Long COVID
- Útil para planificación de recursos hospitalarios
- Permite analizar si severidad aguda se asocia con síntomas persistentes
- Identificación de períodos de mayor demanda asistencial
        """
    })
    
    # SEXO
    reports.append({
        'function': plot_cases_by_week_by_sex,
        'args': (df_con_criterios,),
        'title': 'Distribución de Casos por Sexo',
        'interpretation': """
**Variables:** sexo (1=Femenino, 2=Masculino)

**Hallazgos clave:**
- Permite identificar diferencias de género en Long COVID
- Distribución temporal por sexo
- Identifica períodos con mayor afectación por género

**Implicaciones:**
- Algunos estudios sugieren mayor prevalencia de Long COVID en mujeres
- Útil para análisis de equidad de género en salud
- Planificación de intervenciones específicas por sexo
        """
    })
    
    # EDAD
    reports.append({
        'function': plot_cases_by_week_by_age_group,
        'args': (df_con_criterios,),
        'title': 'Distribución de Casos por Grupos Etarios',
        'interpretation': """
**Grupos:** <30, 30-44, 45-59, ≥60 años

**Hallazgos clave:**
- Visualiza la distribución etaria de casos en el tiempo
- Identifica grupos de edad más afectados
- Permite detectar cambios demográficos temporales

**Implicaciones:**
- Estratificación de riesgo por edad
- Planificación de campañas preventivas focalizadas
- Identificación de poblaciones vulnerables
        """
    })
    
    # TABLA 1 - CARACTERÍSTICAS ESTRATIFICADAS
    reports.append({
        'function': create_table1_stratified,
        'args': (df_con_criterios,),
        'title': 'Tabla 1 - Características Demográficas y Clínicas',
        'interpretation': """
**Tabla descriptiva estratificada por presencia de Long COVID**

**Secciones incluidas:**

1. **Características demográficas:**
   - Sexo (Femenino/Masculino)
   - Grupos etarios (<30, 30-44, 45-59, ≥60 años)
   - Nacionalidad
   - Región de residencia

2. **Características clínicas (COVID agudo):**
   - Hospitalización durante fase aguda
   - Número de síntomas agudos (media ± DE)
   - Condiciones médicas pre-existentes (media ± DE)

3. **Estilo de vida:**
   - Tipo de previsión de salud
   - Consumo de >100 cigarrillos en la vida

4. **Marcadores biológicos:**
   - Grupo sanguíneo (A, B, AB, O)
   - Grupo Rh (Rh+, Rh-)

5. **Proporciones de ancestría genética:**
   - Europea (EUR)
   - Africana (AFR)
   - Asia Oriental (EAS)
   - Aymara (AYM)
   - Mapuche (MAP)

6. **Características de Long COVID:**
   - Problemas a los 3 meses
   - Necesidad de asistencia

**Interpretación estadística:**
- P-valores calculados mediante Chi-cuadrado (categóricas) y t-test (continuas)
- P < 0.05 indica diferencias estadísticamente significativas
- Permite identificar factores de riesgo asociados a Long COVID
        """
    })
    
    # CRITERIO COMPARISON
    reports.append({
        'function': plot_criterio_comparison,
        'args': (df_con_criterios,),
        'title': 'Comparación de los 4 Criterios de Long COVID',
        'interpretation': """
**Comparación de criterios diagnósticos:**

**Criterios evaluados:**
1. COVID-19 confirmado (criterio base)
2. COVID + síntomas recurrentes + no recuperado
3. COVID + clusters sintomáticos + no recuperado  
4. COVID + nuevas condiciones O secuelas

**Hallazgos clave:**
- Visualiza el solapamiento entre diferentes definiciones
- Identifica qué criterio es más restrictivo/inclusivo
- Muestra la heterogeneidad del Long COVID

**Implicaciones:**
- Diferentes criterios capturan distintos fenotipos
- La elección del criterio afecta prevalencia estimada
- Útil para comparar con literatura internacional
        """
    })
    
    # CRITERIO 2 - PROMEDIO SINTOMAS
    reports.append({
        'function': plot_criterio2_promedio_sintomas,
        'args': (df_con_criterios,),
        'title': 'Criterio 2 - Promedio de Síntomas por Grupo',
        'interpretation': """
**Análisis de carga sintomática en Criterio 2**

**Hallazgos clave:**
- Compara el número promedio de síntomas entre grupos
- Identifica la intensidad sintomática en casos que cumplen criterio
- Permite cuantificar la carga de síntomas persistentes

**Implicaciones clínicas:**
- Mayor número de síntomas asociado a mayor impacto en calidad de vida
- Útil para estratificar severidad de Long COVID
- Guía la intensidad del seguimiento clínico necesario
        """
    })
    
    # CRITERIO 2 - RECOVERY
    reports.append({
        'function': plot_criterio2_recovery,
        'args': (df_con_criterios,),
        'title': 'Criterio 2 - Patrón de Recuperación a 3 Meses',
        'interpretation': """
**Análisis de recuperación post-COVID**

**Hallazgos clave:**
- Muestra proporción de recuperados vs no recuperados a los 3 meses
- Identifica la persistencia de síntomas en el tiempo
- Permite estimar tasa de recuperación

**Implicaciones clínicas:**
- Fundamental para pronóstico de Long COVID
- Identifica población que requiere seguimiento prolongado
- Útil para planificación de recursos de salud
        """
    })
    
    # SINTOMAS RECURRENTES BY WEEK
    reports.append({
        'function': plot_sintomas_recurrentes_by_week,
        'args': (df_con_criterios,),
        'title': 'Síntomas Recurrentes por Semana Epidemiológica',
        'interpretation': """
**Evolución temporal de síntomas recurrentes**

**Hallazgos clave:**
- Muestra la distribución temporal de casos con síntomas recurrentes
- Identifica períodos con mayor persistencia sintomática
- Permite detectar cambios en patrones de Long COVID

**Implicaciones:**
- Variaciones temporales pueden relacionarse con variantes virales
- Útil para monitoreo epidemiológico de Long COVID
- Informa políticas de seguimiento post-COVID
        """
    })
    
    # SECUELAS BY WEEK
    reports.append({
        'function': plot_secuelas_by_week,
        'args': (df_con_criterios,),
        'title': 'Secuelas por Semana Epidemiológica',
        'interpretation': """
**Evolución temporal de secuelas post-COVID**

**Hallazgos clave:**
- Distribución temporal de casos con secuelas
- Identifica períodos con mayor incidencia de secuelas
- Muestra la carga de complicaciones a largo plazo

**Implicaciones clínicas:**
- Las secuelas representan impacto severo de COVID
- Requieren seguimiento médico especializado
- Importantes para estimación de carga de enfermedad
        """
    })
    
    # CASES BY SECUELAS
    reports.append({
        'function': plot_cases_by_week_by_secuelas,
        'args': (df_con_criterios,),
        'title': 'Casos por Semana según Presencia de Secuelas',
        'interpretation': """
**Estratificación temporal por secuelas**

**Hallazgos clave:**
- Compara casos con y sin secuelas en el tiempo
- Identifica la proporción de casos que desarrollan secuelas
- Permite análisis de factores temporales

**Implicaciones:**
- Secuelas como marcador de severidad de Long COVID
- Útil para identificación temprana de casos graves
- Guía necesidad de intervenciones preventivas
        """
    })
    
    # CASES BY NUEVA CONDICION
    reports.append({
        'function': plot_cases_by_week_by_nueva_condicion,
        'args': (df_con_criterios,),
        'title': 'Casos por Semana según Nueva Condición',
        'interpretation': """
**Nuevas condiciones médicas post-COVID**

**Hallazgos clave:**
- Muestra casos que desarrollaron nuevas condiciones médicas
- Identifica la incidencia temporal de nuevas patologías
- Permite detectar complicaciones a largo plazo

**Implicaciones clínicas:**
- Nuevas condiciones indican daño persistente
- Requieren abordaje multidisciplinario
- Importantes para seguimiento integral del paciente
        """
    })
    
    # CASES BY SINTOMAS RECURRENTES
    reports.append({
        'function': plot_cases_by_week_by_sintomas_recurrentes,
        'args': (df_con_criterios,),
        'title': 'Casos por Semana según Síntomas Recurrentes',
        'interpretation': """
**Patrón temporal de síntomas recurrentes**

**Hallazgos clave:**
- Estratifica casos por presencia de síntomas recurrentes
- Muestra evolución de la persistencia sintomática
- Identifica períodos con mayor recurrencia

**Implicaciones:**
- Síntomas recurrentes como marcador de Long COVID
- Útil para monitoreo epidemiológico
- Guía estrategias de seguimiento clínico
        """
    })


    
    print(f"\n📝 Generando {len(reports)} reportes PDF...")
    print("-"*70)
    
    # Generar cada reporte
    for i, report in enumerate(reports, 1):
        print(f"\n{i}/{len(reports)} - {report['title']}")
        
        try:
            # Generar figura
            print("   🎨 Generando gráfico...")
            fig = report['function'](*report['args'])
            
            # Guardar como imagen
            print("   💾 Guardando imagen temporal...")
            img_filename = clean_filename(report['title'])
            img_path = save_plotly_figure_as_image(fig, img_filename)
            
            if img_path is None:
                print("   ⚠️  Saltando (no se pudo generar imagen)")
                continue
            
            # Crear PDF
            print("   📄 Creando PDF...")
            pdf_filename = f"{img_filename}.pdf"
            create_pdf_report(
                report['title'],
                report['interpretation'],
                img_path,
                pdf_filename
            )
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    print("\n" + "="*70)
    print(f"✅ PROCESO COMPLETADO")
    print("="*70)
    print(f"\n📁 PDFs generados en: {OUTPUT_DIR.absolute()}")
    print(f"🗑️  Imágenes temporales en: {IMG_DIR.absolute()}")
    print("\nPara eliminar imágenes temporales:")
    print(f"   rm -rf {IMG_DIR}")
    print("="*70)


if __name__ == "__main__":
    generate_all_reports()
