# estado.md — Política y estado del agente de cracking

Documento de estado que un agente (o un humano) consulta para decidir cómo atacar un hash.
Se actualiza con cada experimento: es la "memoria" del proyecto.

> Alcance ético: solo hashes propios (corpus de research, auditorías autorizadas con scope).
> Principio: un hash NO revela su contraseña. Se decide por el TIPO de hash, no por el hash.

## Escalera de ataque NTLM (modo 1000) — medido en RTX 5090
| # | Ataque | Recall | Nota |
|---|--------|--------|------|
| 1 | Diccionario rockyou (train) | 0,00 % | control; sets disjuntos |
| 2 | + best66 (90 reglas) | 32,47 % | mejor relación recall/tiempo |
| 3 | + dive (~99k reglas) | 77,90 % | techo de reglas |
| 4 | PCFG (5·10⁷ cand.) | 28,97 % | ~13× más eficiente/intento |
| 5 | PassGPT (10⁷ cand.) | 3,39 % | +8 649 que PCFG no pilla (complementario) |

## bcrypt (modo 3200) — hash lento
Fuerza bruta inviable. Solo diccionario + reglas ligeras sobre candidatos de alta probabilidad.

## Telemetría 5090 (benchmark)
NTLM 363,1 GH/s · MD5 218,4 GH/s · SHA1 74,9 GH/s · SHA-256 28,2 GH/s · WPA2 3,64 MH/s · bcrypt(c5) 285,3 kH/s.
Con hash rápido, el generador es el cuello de botella (best66 13% GPU vs dive 85%).

## Aprendizajes
- best64.rule ya no existe en hashcat 8.0.0 → usar best66.rule.
- Diccionario plano sobre test disjunto = 0 % → todo recall es generalización.
- Dive deja 633 469 (22,1 %) sin craquear: diana de los generadores.
- PCFG ~13× más eficiente por candidato que best66.
- PassGPT (neuronal) y PCFG (estadístico) son COMPLEMENTARIOS: no hay "mejor generador".
- Orquestador LLM (qwen3-coder:30b, ~22 GB VRAM): solo ELIGE estrategia; el script mide. No inventa.
- Docker corre como root → sudo chown -R \$(id -u):\$(id -g) . tras cada run.

## Estado
- [x] Fase 0 — entorno + benchmark (RTX 5090, hashcat 8.0.0, Docker)
- [x] Fase 1 — dataset train/test + hashes (ground truth)
- [x] Fase 2 — baselines: 0 / 32,47 / 77,90 %
- [x] Fase 3 — PCFG: 28,97 %; 148 que dive no pilló
- [x] Fase 4 — PassGPT: 3,39 %; 8 649 que PCFG no pilló
- [x] Orquestador LLM local + crack_agent.py (anti-alucinación), 5 generadores
- [ ] Fase 5 — apilado (Venn) + conclusiones de política
