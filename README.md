# Cracking de contraseñas asistido por ML en RTX 5090

Laboratorio de investigación sobre **fortaleza de contraseñas**: benchmarking de hashcat en una
NVIDIA RTX 5090 (Blackwell, 32 GB) y estudio comparativo de cinco estrategias de generación de
candidatos — diccionario, reglas, PCFG (estadístico) y PassGPT (neuronal) — orquestadas por un
**LLM local** con un diseño que le impide inventar comandos o métricas.

> **Alcance ético.** Todo el trabajo se hace sobre hashes *propios*, generados a partir de un
> corpus público de research (rockyou) partido en train/test. Nunca se atacan credenciales de
> terceros. Cualquier auditoría real requiere autorización y alcance por escrito.

## Resultados (NTLM, test disjunto de 2 865 802 hashes)

| Método | Tipo | Recall | Nota |
|--------|------|--------|------|
| Diccionario (train) | control | 0,00 % | Sets disjuntos → todo recall es generalización |
| best66 (90 reglas) | reglas | 32,47 % | Mejor relación recall/tiempo |
| dive (~99k reglas) | reglas | 77,90 % | Techo de las reglas |
| PCFG | estadístico | 28,97 % | ~13× más eficiente por candidato que best66 |
| PassGPT | neuronal | 3,39 % | Bajo en bruto, pero +8 649 contraseñas que PCFG no pilla |

**Hallazgos clave (honestos):**
1. El algoritmo de hash importa tanto como la contraseña: NTLM es ~1,27 millones de veces más
   rápido de atacar que bcrypt en la misma GPU.
2. Un generador estadístico (PCFG) es mucho más eficiente por intento que las reglas.
3. Neuronal y estadístico son complementarios, no redundantes: cada familia cubre un rincón
   distinto. No existe "el mejor generador"; apilarlos cubre más.
4. El núcleo duro no cae con ninguna técnica → lo que resiste es longitud + aleatoriedad real.

## Arquitectura

El LLM local (Ollama / qwen3-coder:30b, ~22 GB VRAM en la 5090) DECIDE la estrategia; el script
`crack_agent.py` ejecuta y MIDE. Diseño anti-alucinación: el LLM solo elige pasos de un catálogo
fijo y su orden; NO escribe comandos ni inventa métricas. El recall siempre se mide de la salida
de hashcat.

## Estructura
- `estado.md` — política + estado del agente (la "memoria" del proyecto)
- `docs/00..05` — troubleshooting, entorno, benchmarks, baselines, PCFG, PassGPT
- `scripts/` — split_dataset, make_hashes, crack_agent, passgpt_train, passgpt_gen
- `Dockerfile` (hashcat 8.0.0 + CUDA 12.8) · `Dockerfile.passgpt` (PyTorch cu128) · `docker-compose.yml`

## Entorno
RTX 5090 (sm_120) · Windows 11 + WSL2 + Docker + NVIDIA Container Toolkit · hashcat 8.0.0 ·
CUDA 12.8.1 · PyTorch 2.11+cu128 · Ollama + qwen3-coder:30b
