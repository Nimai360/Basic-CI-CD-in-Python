"""
Módulo: main (orquestração)
Responsabilidade: coordenar o fluxo completo: parsing/configuração, validações, builds, atualização de arquivos e publicação.
"""
from __future__ import annotations

from pathlib import Path
import sys

from config import parse_cli_args, Config, CLIArgs
from discovery import detect_project_and_final
from docker_ops import (
    check_tool_available,
    validate_structure,
    build_base_images,
    build_unified_image,
    tag_and_push,
)
from file_ops import update_final_files


def build_config(args: CLIArgs) -> Config:
    base_dir = args.base_dir
    project_dir, final_dir = detect_project_and_final(base_dir, args.project_dir_opt, args.final_dir_opt)

    project_name = args.project_name_opt or project_dir.name

    return Config(
        base_dir=base_dir,
        project_dir=project_dir,
        final_dir=final_dir,
        project_name=project_name,
        registry=args.registry,
        tag_strategy=args.tag_strategy,
        date_tag=args.date_tag,
        dry_run=args.dry_run,
        skip_build=args.skip_build,
        skip_update_files=args.skip_update_files,
        do_push=args.do_push,
    )


def run_pipeline(cfg: Config) -> int:
    print(
        "Configuração:"\
        f"\n  base_dir     = {cfg.base_dir}"\
        f"\n  project_dir  = {cfg.project_dir}"\
        f"\n  final_dir    = {cfg.final_dir}"\
        f"\n  project_name = {cfg.project_name}"\
        f"\n  registry     = {cfg.registry}"\
        f"\n  tag_strategy = {cfg.tag_strategy} (tag={cfg.tag_value})"\
        f"\n  push         = {cfg.do_push}"
    )

    check_tool_available("docker")
    validate_structure(cfg)

    if not cfg.skip_build:
        print("==> Build das imagens base")
        build_base_images(cfg)
        print("==> Build da imagem unificada")
        build_unified_image(cfg)
    else:
        print("==> Pulando builds conforme solicitado")

    if not cfg.skip_update_files:
        print("==> Atualizando arquivos no diretório final")
        update_final_files(cfg)
    else:
        print("==> Pulando atualização de arquivos conforme solicitado")

    if cfg.do_push:
        print("==> Realizando tag e push para o registry")
        tag_and_push(cfg)
    else:
        print("==> Pulando push (use sem --no-push para habilitar)")

    print("Pipeline finalizado com sucesso.")
    print(f"Imagem unificada: {cfg.unified_ref}")
    print(f"Destino no registry: {cfg.target_ref}")
    return 0


def main(argv: list[str]) -> int:
    try:
        cli_args = parse_cli_args(argv)
        cfg = build_config(cli_args)
        return run_pipeline(cfg)
    except Exception as exc:
        print(f"ERRO: {exc}")
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
