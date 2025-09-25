# Automatizador de CI/CD (Docker)

Sistema modular para build, unificação e publicação de imagens Docker a partir de uma estrutura de projeto padronizada.

Módulos:

- config.py: parsing/Config
- discovery.py: detecção de diretórios
- docker_ops.py: operações Docker
- file_ops.py: atualização de arquivos
- main.py: orquestração (pipeline)
- main.py: wrapper de compatibilidade (chama main)

## Estrutura esperada

```
{BASE_DIR}/
  {PROJETO}/
    Dockerfile             # unificador (gera {PROJETO}_unificado)
    {sub1}/Dockerfile      # 0..N subpastas com Dockerfile (imagens base)
    ...
  {PROJETO}_final/
    Dockerfile             # FROM {PROJETO}_unificado:{TAG}
    docker-compose.yml     # image: {PROJETO}_unificado:{TAG}
```

Detecção automática do par `{X}` e `{X}_final` quando `--project-dir` e `--final-dir` não são informados.

## Pré-requisitos

- Python 3.9+
- Docker CLI no PATH
- docker login no registry (ex.: `docker login vcp.ocir.io`)

## Uso (Windows PowerShell)

- Produção (tag por data, push padrão):

```
python main.py --base-dir . --tag-strategy date --registry vcp.ocir.io/ewnbfjunbic
```

- Homolog (tag latest):

```
python main.py --base-dir . --registry vcp.ocir.io/ewnbfjunbic
```

- Diretórios explícitos:

```
python main.py --base-dir . --project-dir ./app --final-dir ./app_final --registry vcp.ocir.io/ewnbfjunbic
```

- Dry-run (sem executar):

```
python main.py --base-dir . --dry-run
```

- Sem publicar:

```
python main.py --base-dir . --no-push
```

## O que o pipeline faz

1. Validações (Fail Fast): docker no PATH, arquivos obrigatórios.
2. Descoberta das bases: subpastas com Dockerfile em `{PROJETO}`.
3. Build das bases: `docker build -t {nome_pasta} .` (tag latest).
4. Build unificado: `{PROJETO}_unificado:{TAG}` via Dockerfile do `{PROJETO}`.
5. Atualizações no `{PROJETO}_final`: FROM e image para `{PROJETO}_unificado:{TAG}`.
6. Publicação: tag e push para `{REGISTRY}/{PROJETO}:{TAG}`.

## Opções

- `--base-dir PATH`
- `--project-dir PATH`, `--final-dir PATH`
- `--project-name NAME`
- `--registry URL`
- `--tag-strategy [date|latest]`, `--date-tag YY-MM-DD`
- `--dry-run`, `--skip-build`, `--skip-update-files`, `--no-push`

## Boas práticas aplicadas

- SOLID/SoC: responsabilidades divididas em módulos.
- DRY/KISS: utilidades compartilhadas; lógica simples e previsível.
- Encapsulamento: detalhes de regex/comandos isolados.
- Law of Demeter: baixo acoplamento entre módulos.
- Fail Fast: validações antecipadas com mensagens claras.
- 12-Factor: configuração via flags, fácil mapeamento a variáveis de ambiente.

## Observabilidade e CI/CD

- Logs claros de cada etapa.
- Sugestão de workflow GitHub Actions com login no registry e execução do script.

## Testabilidade e escalabilidade

- Esta versão modular facilita testes unitários por módulo (pytest).
- Possível evolução: adicionar validação `docker compose config`, logs estruturados (JSON), e camadas de retry exponencial nas operações de push.
