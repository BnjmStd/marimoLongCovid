# Decisiones — Tablas 1 y 2

n=1505 (346 controles, 1159 casos), 555 hombres, 950 mujeres.

---

## Tabla 1 — Sociodemográfico + Clínico (por sexo y por Long COVID)

### Socio-Demographic

**peso** — Filtrado con `peso > 30 kg` por entradas inválidas (0.0 y 1.0). Rango válido: 45–160 kg.

**Consumo.alcohol** — `"Dos o tres veces a la semana"` y `"Cuatro o más veces a la semana"` se agrupan en una sola categoría `"2 or more times a week"` (n=85 en total).

**Sistema de salud** — Public=842, Private=567, no-null=1409.

**Situación ocupacional** — Employed=1018, Unemployed=68, Idle=256. no-null=1342.

### COVID-19

**No. Symptoms** → `Total_Sintomas`. Continua. Media=10.5, SD=6.71. Sin nulos.

**No. Pre-existing diseases** → `Total_Cond_pre`. Continua. Media=0.88, SD=1.21. Sin nulos.

**More than 5 Symptoms** → `Mas_de_5`. Yes=1102, No=403. Sin nulos.

**Severe Infection** → `Severo`. Yes=158, No=1347. Sin nulos.

**Recovered** → `recuperado_3m`. Yes=1077, No=420. 8 nulos.

**Health problems that limit daily activities** → `problemas_3m`. Yes=25, No=1465, NS/NR=10. 5 nulos. El valor NS/NR se cuenta en el Total pero no en Yes ni No.

**Need someone to help regularly** → `ayuda_3m`. Yes=41, No=1450, NS/NR=9. 5 nulos. Mismo criterio NS/NR.

**Health problems that require to stay at home** → `casa_3m`. Yes=43, No=1448, NS/NR=10. 4 nulos. Mismo criterio NS/NR.

---

## Tabla 2 — Comparación Long COVID (Controles vs Casos)

Mismas variables que la Tabla 1. Solo columnas Controls y Cases. Se añaden Grupo Sanguíneo y Rh en Clinical-Lifestyle.

### Clinical - Lifestyle (adiciones)

**Grupo sanguíneo** → `Grupo.Sanguíneo`. O=505, A=239, B=95, AB=25. no-null=864 (~57% del total).

**Grupo Rh** → `Grupo.Rh`. Rh+=800, Rh-=70. no-null=870 (~58% del total).