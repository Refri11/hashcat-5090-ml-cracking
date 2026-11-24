# Fase 4 — Generador neuronal (PassGPT)

GPT char-level propio (~3,2M params) entrenado en la RTX 5090 (PyTorch 2.11+cu128, sm_120).

| Método | Craqueados | Recall |
|--------|-----------|--------|
| PCFG (5e7) | 830 210 | 28,97 % |
| PassGPT (1e7) | 97 213 | 3,39 % |

Novedad: vs dive = 29 · vs PCFG = 8 649.

- Débil como cracker en solitario (modelo pequeño). No se vende como "la IA gana".
- Hallazgo real: neuronal y estadístico son COMPLEMENTARIOS. PassGPT pilla 8 649 que PCFG no.
- Política: ni reglas, ni PCFG, ni neuronal revientan el núcleo duro → longitud + aleatoriedad.
