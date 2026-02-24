# Heatmap Criterios Long COVID — Preguntas frecuentes

## ¿Por qué hay espacios blancos (gaps)?

Cada columna = un paciente. El heatmap tiene **8 filas**: 4 criterios × 2 sexos (H / M).

Para un paciente **hombre** sólo aplican las filas `C1·H`, `C2·H`, `C3·H`, `C4·H`.  
Las filas `C1·M … C4·M` son irrelevantes → se marcan `None` → **Plotly las dibuja blancas**.

Hay exactamente **6.020 celdas blancas** (4 filas × 1.505 pacientes).  
Eso es intencional: indica separación por sexo, **no un error de datos**.

---

## ¿Por qué aparecen hospitalizados a la derecha en Criterio 1 y 4?

La **línea vertical negra** separa hospitalizados (izq.) de no hospitalizados (der.).  
El **color de celda** indica si el paciente cumple el criterio, no su hospitalización.

→ Celda azul a la **derecha** = paciente no hospitalizado que **sí cumple** el criterio.  
→ Esto es correcto: Long COVID no implica hospitalización previa.

Si esperabas que "todo lo azul quede a la izquierda", el clustering jerárquico
ya ordena por similitud de patrones **dentro de cada grupo**, pero no puede mover
un no-hospitalizado al grupo de hospitalizados.

---

## Variantes disponibles

| Versión | Filas | Gaps | Separación sexo |
|---|---|---|---|
| **Original** | 8 (H + M por criterio) | Blanco (`None`) | Por fila |
| **Opción A** | 8 (H + M por criterio) | Gris muy claro | Por fila |
| **Opción B** | 4 (un criterio por fila) | Sin gaps | Tira de color encima |

### Opción A — "Gaps gris claro"
- Mantiene la estructura de 8 filas con separación H / M.
- Cambia `None` → valor neutral con color `#F0F0F0` (gris muy suave).
- **Ventaja:** la estructura visual es continua, no hay "roturas" en columnas.
- **Desventaja:** sexo en filas sigue generando mitad de celdas no informativas.

### Opción B — "4 filas + tira de sexo" *(recomendada para presentación)*
- Una sola fila por criterio (C1, C2, C3, C4), sin split por sexo.
- **Tira de color adicional** encima del heatmap: azul oscuro = Hombre, rosa = Mujer.
- **Sin gaps**: cada celda tiene valor 0 ó 1.
- **Ventaja:** bloques azules y rosas más limpios y legibles para tu jefa.
- La tira de sexo preserva la información sin fragmentar en filas.

---

## Interpretación rápida de colores

| Color | Significado |
|---|---|
| Azul oscuro `#2C3E7A` | El paciente **cumple** el criterio Long COVID |
| Rosa claro `#F4C2C2` | El paciente **no cumple** el criterio |
| Blanco / Gris claro | Sexo no aplica para esa fila (solo Opción A/Original) |
| Azul tira `#2980b9` | Sexo Hombre (solo Opción B) |
| Rosa tira `#e74c3c` | Sexo Mujer (solo Opción B) |
