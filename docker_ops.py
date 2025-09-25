"""
Módulo: docker_ops
Responsabilidade: operações relacionadas ao Docker (validação de ferramenta, build, tag e push).
"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Iterable, Optional, List, Tuple

from config import Config
from discovery import discover_base_build_dirs


class StepError(RuntimeError):
    """Erro controlado para falhas de etapa (fail fast)."""


def run(cmd: Iterable[str], *, cwd: Optional[Path] = None, dry_run: bool = False) -> None:
    cmd_list = list(cmd)
    printable = " ".join(cmd_list)
    print(f"$ {printable}")
    if dry_run:
        return
    try:
        subprocess.run(cmd_list, cwd=str(cwd) if cwd else None, check=True)
    except subprocess.CalledProcessError as exc:
        raise StepError(f"Comando falhou (exit={exc.returncode}): {printable}") from exc


def check_tool_available(tool: str) -> None:
    if shutil.which(tool) is None:
        raise StepError(f"Ferramenta obrigatória não encontrada no PATH: {tool}")


def validate_structure(cfg: Config) -> None:
    project_dir = cfg.project_dir
    final_dir = cfg.final_dir

    required = [
        project_dir / "Dockerfile",        # unificado (no diretório raiz do projeto)
        final_dir / "Dockerfile",
        final_dir / "docker-compose.yml",
    ]

    missing = [str(p) for p in required if not p.is_file()]
    if missing:
        raise StepError("Arquivos obrigatórios ausentes:\n- " + "\n- ".join(missing))


def build_base_images(cfg: Config) -> None:
    bases = discover_base_build_dirs(cfg.project_dir)
    if not bases:
        print("[Aviso] Nenhuma subpasta com Dockerfile encontrada para build base.")
    for ctx, image in bases:
        run(["docker", "build", "-t", image, "."], cwd=ctx, dry_run=cfg.dry_run)


def build_unified_image(cfg: Config) -> None:
    ctx = cfg.project_dir
    run(["docker", "build", "-t", cfg.unified_ref, "."], cwd=ctx, dry_run=cfg.dry_run)


def tag_and_push(cfg: Config) -> None:
    run(["docker", "tag", cfg.unified_ref, cfg.target_ref], dry_run=cfg.dry_run)
    run(["docker", "push", cfg.target_ref], dry_run=cfg.dry_run)
