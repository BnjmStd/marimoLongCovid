#!/usr/bin/env python3
"""
Script de limpieza para archivos temporales del generador de PDFs
"""

import shutil
from pathlib import Path

print("="*70)
print("LIMPIEZA DE ARCHIVOS TEMPORALES")
print("="*70)

# Directorio de imágenes temporales
TEMP_DIR = Path("pdf_reports/temp_images")

if TEMP_DIR.exists():
    # Contar archivos
    temp_files = list(TEMP_DIR.glob("*.png"))
    total_files = len(temp_files)
    
    # Calcular tamaño total
    total_size = sum(f.stat().st_size for f in temp_files)
    total_size_mb = total_size / (1024 * 1024)
    
    print(f"\n📁 Directorio encontrado: {TEMP_DIR}")
    print(f"📊 Archivos temporales: {total_files}")
    print(f"💾 Espacio ocupado: {total_size_mb:.2f} MB")
    
    # Confirmar eliminación
    response = input("\n¿Deseas eliminar estos archivos? (s/n): ")
    
    if response.lower() in ['s', 'si', 'y', 'yes']:
        try:
            shutil.rmtree(TEMP_DIR)
            print(f"\n✅ Directorio {TEMP_DIR} eliminado exitosamente")
            print(f"💾 Espacio liberado: {total_size_mb:.2f} MB")
        except Exception as e:
            print(f"\n❌ Error al eliminar: {e}")
    else:
        print("\n❌ Operación cancelada")
else:
    print(f"\n✅ No hay archivos temporales para limpiar")
    print(f"   (Directorio {TEMP_DIR} no existe)")

print("="*70)
