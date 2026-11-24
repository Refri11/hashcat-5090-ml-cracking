# Fase 3 — Generador estadístico (PCFG)

pcfg_cracker (lakiw) entrenado sobre train.txt. Aprende estructura, no reglas fijas.

| Método | Candidatos | Craqueados | Recall |
|--------|-----------|-----------|--------|
| B1 best66 | 7,57e8 | 930 512 | 32,47 % |
| PCFG | 5,0e7 | 830 210 | 28,97 % |

- PCFG ~13x más eficiente por candidato que best66 (casi el mismo recall con 15x menos candidatos).
- Novedad vs dive: 148 contraseñas que ~99k reglas no alcanzaron → prueba de concepto del 22 % duro.
