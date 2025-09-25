"""
Módulo: discovery
Responsabilidade: detecção de diretórios de projeto e final, e descoberta de subpastas com Dockerfile
para build de imagens base.
"""
from __future__ import annotations

from pathlib import Path
from typing import List, Tuple, Optional

from config import Config, CLIArgs


def detect_project_and_final(base_dir: Path, project_dir_opt: Optional[Path], final_dir_opt: Optional[Path]) -> Tuple[Path, Path]:
    """
    Detecta os diretórios de projeto e projeto_final a partir do base_dir, caso não sejam
    informados explicitamente. Heurística:
      - Se ambos informados, apenas valida e retorna.
      - Se um informado, tenta deduzir o outro por convenção (nome + "_final").
      - Se nenhum informado, procura por um par {X} e {X}_final.
    """
    dirs = [d for d in base_dir.iterdir() if d.is_dir() and not d.name.startswith('.')]

    if project_dir_opt and final_dir_opt:
        return project_dir_opt, final_dir_opt

    if project_dir_opt and not final_dir_opt:
        cand = base_dir / f"{project_dir_opt.name}_final"
        if cand.is_dir():
            return project_dir_opt, cand
        raise RuntimeError("Não foi possível deduzir o diretório final (esperado {project}_final).")

    if final_dir_opt and not project_dir_opt:
        name = final_dir_opt.name
        if name.endswith("_final"):
            base_name = name[:-6]
            cand = base_dir / base_name
            if cand.is_dir():
                return cand, final_dir_opt
        raise RuntimeError("Não foi possível deduzir o diretório de projeto a partir do final.")

    finals = [d for d in dirs if d.name.endswith("_final")]
    bases = [d for d in dirs if not d.name.endswith("_final")]

    if len(finals) == 1 and len(bases) >= 1:
        base_name = finals[0].name[:-6]
        for b in bases:
            if b.name == base_name:
                return b, finals[0]
        if len(bases) == 1:
            return bases[0], finals[0]

    raise RuntimeError(
        "Detecção ambígua de diretórios. Informe --project-dir e --final-dir ou mantenha o padrão {X} e {X}_final."
    )


def discover_base_build_dirs(project_dir: Path) -> List[Tuple[Path, str]]:
    """
    Descobre subdiretórios imediatos do diretório de projeto que contêm um Dockerfile.
    Retorna lista de tuplas (caminho_do_contexto, nome_da_imagem), usando o nome da pasta.
    """
    results: List[Tuple[Path, str]] = []
    for child in sorted(project_dir.iterdir()):
        if child.is_dir() and not child.name.startswith('.'):
            dockerfile = child / "Dockerfile"
            if dockerfile.is_file():
                results.append((child, child.name))
    return results
