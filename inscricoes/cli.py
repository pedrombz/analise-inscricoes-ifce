"""Interface de linha de comando.

Códigos de saída: 0 = sucesso, 1 = validação com erros, 2 = falha de execução.
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from . import __version__
from .amostra import gerar_pdf_exemplo
from .config import (
    ARQUIVO_PDF_EXEMPLO,
    ARQUIVO_PDF_PADRAO,
    CURSO_PADRAO,
    NOME_CSV_BASE,
    PASTA_RESULTADOS,
)
from .pipeline import (
    ExtracaoIncompletaError,
    ValidacaoFalhouError,
    executar_pipeline,
)
from .validacao import formatar_relatorio, validar_csv

log = logging.getLogger(__name__)


def construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="main.py",
        description="Pipeline de análise de inscrições (PDF → base validada → indicadores).",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="comando", required=True)

    executar = sub.add_parser("executar", help="extrai, analisa e gera gráficos (padrão)")
    executar.add_argument("--pdf", type=Path, default=ARQUIVO_PDF_PADRAO, help="PDF de entrada")
    executar.add_argument("--saida", type=Path, default=PASTA_RESULTADOS, help="pasta de saída")
    executar.add_argument("--curso", default=CURSO_PADRAO, help="curso esperado no PDF")
    executar.add_argument(
        "--estrito", action="store_true", help="falha se algum protocolo for descartado"
    )
    executar.add_argument(
        "--validar", action="store_true", help="valida a base após a extração"
    )

    validar = sub.add_parser("validar", help="valida uma base já extraída")
    validar.add_argument(
        "--csv", type=Path, default=PASTA_RESULTADOS / NOME_CSV_BASE, help="CSV a validar"
    )

    exemplo = sub.add_parser("exemplo", help="gera um PDF sintético para testar o pipeline")
    exemplo.add_argument("--saida", type=Path, default=ARQUIVO_PDF_EXEMPLO)
    exemplo.add_argument("--registros", type=int, default=120)
    exemplo.add_argument("--semente", type=int, default=42)
    return parser


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or (argv[0].startswith("-") and argv[0] not in ("-h", "--help", "--version")):
        argv.insert(0, "executar")  # `python main.py` sem subcomando roda o pipeline
    args = construir_parser().parse_args(argv)

    try:
        if args.comando == "executar":
            executar_pipeline(args.pdf, args.saida, args.curso, args.estrito, args.validar)
        elif args.comando == "validar":
            resultado = validar_csv(args.csv)
            print(formatar_relatorio(resultado))
            return 0 if resultado.ok else 1
        elif args.comando == "exemplo":
            caminho = gerar_pdf_exemplo(args.saida, args.registros, args.semente)
            log.info("PDF sintético gerado em: %s", caminho)
    except ValidacaoFalhouError:
        log.error("Pipeline interrompido: a validação encontrou erros críticos.")
        return 1
    except (FileNotFoundError, ExtracaoIncompletaError, ValueError) as erro:
        log.error("Erro: %s", erro)
        return 2
    return 0
