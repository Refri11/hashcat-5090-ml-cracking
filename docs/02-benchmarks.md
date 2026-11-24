# Fase 0 — Benchmarks RTX 5090

hashcat 8.0.0 · CUDA 12.8.1 · -w 3 · backend CUDA.

| Algoritmo | Modo | Velocidad |
|-----------|------|-----------|
| NTLM | 1000 | 363,1 GH/s |
| MD5 | 0 | 218,4 GH/s |
| SHA1 | 100 | 74,86 GH/s |
| SHA-256 | 1400 | 28,17 GH/s |
| WPA2 | 22000 | 3,64 MH/s |
| bcrypt (cost 5) | 3200 | 285,3 kH/s |

Titular: NTLM es ~1,27 millones de veces más rápido que bcrypt en la misma GPU.
Conclusión política (ISO 27001/ENS): funciones lentas con sal (bcrypt/Argon2); longitud > complejidad.
