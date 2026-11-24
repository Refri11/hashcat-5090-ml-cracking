# Fase 2 — Baselines (diccionario y reglas)

NTLM, test disjunto de 2 865 802 hashes. Wordlist = train.txt (disjunto del test).

| Método | Reglas | Candidatos | Craqueados | Recall | Tiempo |
|--------|--------|-----------|-----------|--------|--------|
| B0 diccionario | — | 11,46 M | 0 | 0,00 % | ~s |
| B1 best66 | 90 | 756,6 M | 930 512 | 32,47 % | 1m47s |
| B2 dive | ~99k | 1,13e12 | 2 232 333 | 77,90 % | 6m16s |

- B0 = 0 % valida el diseño disjunto: todo acierto es generalización.
- Con hash rápido, el generador es el cuello de botella (best66 13% GPU, dive 85%).
- Dive deja 633 469 (22,1 %) sin craquear → diana de los generadores.
- Nota: best64.rule ya no existe en hashcat 8.0.0 → best66.rule.
