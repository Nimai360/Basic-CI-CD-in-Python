"""
Módulo: file_ops
Responsabilidade: alterações de conteúdo nos arquivos Dockerfile e docker-compose.yml
para referenciar a imagem unificada com a tag desejada.
"""
from __future__ import annotations

import re
from pathlib import Path

from config import Config


class StepError(RuntimeError):
    pass


def _replace_first_from_line(dockerfile_text: str, new_from_line: str) -> str:
    lines = dockerfile_text.splitlines(keepends=True)
    for i, line in enumerate(lines):
        if line.strip().startswith("FROM "):
            line_ending = "\n"
            if line.endswith("\r\n"):
                line_ending = "\r\n"
            lines[i] = f"{new_from_line}{line_ending}"
            return "".join(lines)
    raise StepError("Nenhuma linha 'FROM' encontrada no Dockerfile para substituição.")


def _replace_first_image_line(yml_text: str, new_image: str) -> str:
    pattern = re.compile(r"^(\s*)image:\s*.*$", re.MULTILINE)

    def repl(match):
        indent = match.group(1) or ""
        return f"{indent}image: {new_image}"

    new_text, count = pattern.subn(repl, yml_text, count=1)
    if count == 0:
        raise StepError("Nenhuma linha 'image:' encontrada no docker-compose.yml para substituição.")
    return new_text


def update_final_files(cfg: Config) -> None:
    dockerfile_path = cfg.final_dir / "Dockerfile"
    compose_path = cfg.final_dir / "docker-compose.yml"

    dockerfile_text = dockerfile_path.read_text(encoding="utf-8")
    new_from = f"FROM {cfg.unified_image}:{cfg.tag_value}"
    updated_dockerfile = _replace_first_from_line(dockerfile_text, new_from)

    compose_text = compose_path.read_text(encoding="utf-8")
    new_image = f"{cfg.unified_image}:{cfg.tag_value}"
    updated_compose = _replace_first_image_line(compose_text, new_image)

    if cfg.dry_run:
        print(f"Atualizaria {dockerfile_path} -> {new_from}")
        print(f"Atualizaria {compose_path} -> image: {new_image}")
        return

    dockerfile_path.write_text(updated_dockerfile, encoding="utf-8")
    compose_path.write_text(updated_compose, encoding="utf-8")
    print(f"Atualizados: {dockerfile_path} e {compose_path}")
