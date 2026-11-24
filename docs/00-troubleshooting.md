# Troubleshooting

Bitácora de incidencias resueltas (Windows 11 + WSL2 + Docker + RTX 5090).

## #1 — Docker no accede a la GPU: "failed to discover GPU vendor from CDI"
Causa: nvidia-smi funciona en WSL, pero Docker (engine nativo) no tiene puente a la GPU:
falta el NVIDIA Container Toolkit.
Solución: instalar nvidia-container-toolkit, luego:
  sudo nvidia-ctk runtime configure --runtime=docker && sudo service docker restart
Verificado: docker run --rm --gpus all nvidia/cuda:12.8.1-base-ubuntu24.04 nvidia-smi lista la 5090.

## #2 — Ficheros del contenedor como root: "Permission denied"
Causa: docker compose run corre como root → ficheros root:root en WSL.
Solución: sudo chown -R \$(id -u):\$(id -g) . tras los runs.

## Hardware
RTX 5090, 32 607 MiB GDDR7 · driver 610.57.01 · CUDA UMD 13.3 (sobrado del mínimo Blackwell 12.8).
