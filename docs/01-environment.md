# Fase 0 — Entorno (Docker + WSL2)

- RTX 5090 = Blackwell, sm_120, 32 GB. Requiere CUDA 12.8+.
- Imagen base nvidia/cuda:12.8.1-devel (la devel trae nvrtc, que hashcat necesita).
- hashcat 8.0.0 (desde la 7.0 soporta ejecución containerizada).

## Prerrequisitos (Windows + WSL2)
- Driver NVIDIA en Windows (expone la GPU a WSL2; no se instala driver en Linux).
- Docker Engine en WSL + NVIDIA Container Toolkit (ver 00-troubleshooting).

## Arranque
  docker compose build
  docker compose run --rm lab hashcat -I     # debe ver la RTX 5090 con 32 GB
  docker compose run --rm lab hashcat -b -w 3
Nota: clGetPlatformIDs(): CL_PLATFORM_NOT_FOUND_KHR NO es error (es OpenCL; usamos CUDA).
