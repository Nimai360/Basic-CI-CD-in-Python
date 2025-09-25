"""
Módulo: config
Responsabilidade: parsing de argumentos de CLI e estrutura de configuração (Config) para o pipeline.
"""
from __future__ import annotations

import argparse
import datetime as _dt
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class CLIArgs:
    """Representa os argumentos crus obtidos da CLI.

    Observação: diretórios de projeto/final podem ser detectados posteriormente.
    """
    base_dir: Path
    project_dir_opt: Optional[Path]
    final_dir_opt: Optional[Path]
    project_name_opt: Optional[str]
    registry: str
    tag_strategy: str  # 'date' ou 'latest'
    date_tag: str
    dry_run: bool
    skip_build: bool
    skip_update_files: bool
    do_push: bool


@dataclass(frozen=True)
class Config:
    """Configuração final do pipeline, pronta para uso pelas etapas.

    - project_name: nome lógico do projeto (usado para nome da imagem e no registry)
    - unified_image: {project_name}_unificado
    - tag_value: depende de tag_strategy (date -> date_tag; latest -> 'latest')
    """
    base_dir: Path
    project_dir: Path
    final_dir: Path
    project_name: str
    registry: str
    tag_strategy: str
    date_tag: str
    dry_run: bool
    skip_build: bool
    skip_update_files: bool
    do_push: bool

    @property
    def unified_image(self) -> str:
        return f"{self.project_name}_unificado"

    @property
    def tag_value(self) -> str:
        return self.date_tag if self.tag_strategy == "date" else "latest"

    @property
    def unified_ref(self) -> str:
        return f"{self.unified_image}:{self.tag_value}"

    @property
    def target_ref(self) -> str:
        return f"{self.registry}/{self.project_name}:{self.tag_value}"


def parse_cli_args(argv: list[str]) -> CLIArgs:
    """Realiza o parsing dos argumentos de linha de comando.

    Mantém a responsabilidade de apenas coletar dados da CLI. A resolução dos
    diretórios e composição da Config ocorre na camada de orquestração (main).
    """
    parser = argparse.ArgumentParser(description="Automatiza CI/CD de imagens Docker de um projeto padronizado.")
    parser.add_argument("--base-dir", default=".", help="Diretório base que contém {PROJETO} e {PROJETO}_final")
    parser.add_argument("--project-dir", help="Caminho do diretório do projeto (contendo Dockerfile unificado)")
    parser.add_argument("--final-dir", help="Caminho do diretório do projeto final (com Dockerfile e docker-compose.yml)")
    parser.add_argument("--project-name", help="Nome lógico do projeto; se omitido, usa o nome do diretório do projeto")

    parser.add_argument("--registry", default="vcp.ocir.io/ewnbfjunbic", help="Caminho base do registry")
    parser.add_argument("--tag-strategy", choices=["date", "latest"], default="latest", help="Estratégia de tag")
    parser.add_argument("--date-tag", default=_dt.datetime.now().strftime("%y-%m-%d"), help="YY-MM-DD quando tag-strategy=date")

    parser.add_argument("--dry-run", action="store_true", help="Exibe ações sem executar (validação)")
    parser.add_argument("--skip-build", action="store_true", help="Não executa os builds (base e unificado)")
    parser.add_argument("--skip-update-files", action="store_true", help="Não altera os arquivos do diretório final")

    push_group = parser.add_mutually_exclusive_group()
    push_group.add_argument("--no-push", dest="do_push", action="store_false", help="Não realiza tag/push")
    push_group.set_defaults(do_push=True)

    args = parser.parse_args(argv)

    return CLIArgs(
        base_dir=Path(args.base_dir).resolve(),
        project_dir_opt=Path(args.project_dir).resolve() if args.project_dir else None,
        final_dir_opt=Path(args.final_dir).resolve() if args.final_dir else None,
        project_name_opt=args.project_name,
        registry=args.registry.rstrip("/"),
        tag_strategy=args.tag_strategy,
        date_tag=args.date_tag,
        dry_run=bool(args.dry_run),
        skip_build=bool(args.skip_build),
        skip_update_files=bool(args.skip_update_files),
        do_push=bool(args.do_push),
    )
