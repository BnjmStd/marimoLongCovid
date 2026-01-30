#!/usr/bin/env python3
"""
GENERADOR DE PDFs - GUÍA RÁPIDA
================================

Este script genera PDFs individuales para cada gráfico del análisis Long COVID.
Cada PDF contiene 2 páginas: interpretación + gráfico.

COMANDOS PRINCIPALES:
---------------------

1. Generar todos los PDFs:
   $ python generate_pdf_reports.py

2. Limpiar archivos temporales:
   $ python cleanup_temp_files.py

3. Ver este menú:
   $ python quick_start.py

CARACTERÍSTICAS:
----------------
✓ 11 PDFs generados automáticamente
✓ Nombres basados en títulos de gráficos  
✓ Formato profesional (Letter 8.5"x11")
✓ Alta resolución (1200x800 px)
✓ ~580 KB total

SALIDA:
-------
📁 pdf_reports/
   ├── Criterio_1_COVID_19_Confirmado_por_Semana.pdf (99K)
   ├── Criterio_2_Distribución_de_Síntomas_Persistentes.pdf (34K)
   ├── Criterio_3_Comparación_de_Clusters_Sintomáticos.pdf (54K)
   ├── Criterio_3_sin_Nulls_Evolución_Temporal.pdf (53K)
   ├── Distribución_de_Ancestrías_Genéticas.pdf (30K)
   ├── Distribución_de_Casos_por_Grupos_Etarios.pdf (44K)
   ├── Distribución_de_Casos_por_Sexo.pdf (50K)
   ├── Heatmap_Demográfico_Clínico.pdf (74K)
   ├── Heatmap_de_Clusters_por_Semana_de_Diagnóstico.pdf (68K)
   ├── Hospitalización_por_Semana_Epidemiológica.pdf (27K)
   └── Long_COVID_General_por_Semana_Epidemiológica.pdf (47K)

TIEMPO DE EJECUCIÓN:
--------------------
• Carga de datos: ~1 segundo
• Generación de cada PDF: ~1-2 segundos  
• Total: ~15-20 segundos

DEPENDENCIAS:
-------------
pip install reportlab kaleido polars plotly

DOCUMENTACIÓN COMPLETA:
-----------------------
Ver: GENERADOR_PDF_README.md

¿NECESITAS AYUDA?
-----------------
1. Verifica que el dataset exista: datasets/longcovid_2020W13-2021W22.csv
2. Verifica dependencias: python -c "import reportlab, kaleido; print('OK')"
3. Revisa los logs de ejecución para errores específicos

"""

def main():
    import sys
    from pathlib import Path
    
    print(__doc__)
    
    # Verificar estado
    pdf_dir = Path("pdf_reports")
    
    if pdf_dir.exists():
        pdfs = list(pdf_dir.glob("*.pdf"))
        print(f"\n📊 ESTADO ACTUAL:")
        print(f"   PDFs existentes: {len(pdfs)}")
        
        if pdfs:
            total_size = sum(p.stat().st_size for p in pdfs) / 1024
            print(f"   Tamaño total: {total_size:.1f} KB")
            print(f"\n   Usa 'ls pdf_reports/' para ver la lista completa")
    else:
        print(f"\n⚠️  Directorio 'pdf_reports/' no existe aún.")
        print(f"   Ejecuta 'python generate_pdf_reports.py' para crear los PDFs")
    
    print("\n" + "="*70)
    
    # Menú interactivo
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        print("\n🎯 MENÚ INTERACTIVO")
        print("-"*70)
        print("1. Generar todos los PDFs")
        print("2. Limpiar archivos temporales")
        print("3. Ver lista de PDFs")
        print("4. Salir")
        
        choice = input("\nSelecciona una opción (1-4): ")
        
        if choice == "1":
            import subprocess
            subprocess.run(["python", "generate_pdf_reports.py"])
        elif choice == "2":
            import subprocess
            subprocess.run(["python", "cleanup_temp_files.py"])
        elif choice == "3":
            import subprocess
            subprocess.run(["ls", "-lh", "pdf_reports/*.pdf"])
        else:
            print("Saliendo...")

if __name__ == "__main__":
    main()
