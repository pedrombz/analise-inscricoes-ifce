"""Orquestração: extração, validação opcional, análise e gráficos."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

from .analise import analisar_inscricoes
from .armazenamento import salvar_csv
from .config import (
    CURSO_PADRAO,
    NOME_CSV_BASE,
    NOME_CSV_INDICADORES,
    NOME_CSV_RANKING,
)
from .extracao import extrair_inscricoes
from .graficos import gerar_graficos
from .validacao import ResultadoValidacao, formatar_relatorio, validar_dataframe

log = logging.getLogger(__name__)
LARGURA = 60


class ExtracaoIncompletaError(ValueError):
    """Alguns protocolos foram descartados e o modo estrito está ativo."""


class ValidacaoFalhouError(Exception):
    """A validação encontrou erros críticos na base extraída."""

    def __init__(self, resultado: ResultadoValidacao):
        super().__init__("A validação da base encontrou erros críticos.")
        self.resultado = resultado


@dataclass
class ResultadoPipeline:
    base: pd.DataFrame
    resumo: pd.DataFrame
    indicadores: pd.DataFrame
    validacao: ResultadoValidacao | None = None
    arquivos: list[Path] = field(default_factory=list)


def executar_pipeline(
    pdf: Path,
    pasta_resultados: Path,
    curso: str = CURSO_PADRAO,
    estrito: bool = False,
    validar: bool = False,
) -> ResultadoPipeline:
    """Executa o fluxo completo e grava os resultados em ``pasta_resultados``.

    - ``estrito``: falha se algum protocolo não puder ser interpretado.
    - ``validar``: valida a base logo após a extração e interrompe se houver erros.
    """
    pdf = Path(pdf)
    pasta_resultados = Path(pasta_resultados)
    if not pdf.exists():
        raise FileNotFoundError(f"Arquivo PDF não encontrado: {pdf}")

    log.info("=" * LARGURA)
    log.info("ANÁLISE DE INSCRIÇÕES — IFCE")
    log.info("=" * LARGURA)

    log.info("\n[1/3] Extraindo inscrições do PDF...")
    extracao = extrair_inscricoes(pdf, curso)
    if estrito and not extracao.completo:
        raise ExtracaoIncompletaError(
            f"{len(extracao.descartados)} protocolo(s) descartados; "
            "execução interrompida pelo modo estrito."
        )
    base = extracao.registros
    if base.empty:
        raise ValueError("A extração não retornou inscrições. Verifique o PDF e o curso.")

    arquivos = [salvar_csv(base, pasta_resultados / NOME_CSV_BASE)]
    log.info("Base salva em: %s", arquivos[0])

    validacao = None
    if validar:
        validacao = validar_dataframe(base)
        log.info("\n%s", formatar_relatorio(validacao))
        if not validacao.ok:
            raise ValidacaoFalhouError(validacao)

    log.info("\n[2/3] Analisando os dados...")
    resumo, indicadores = analisar_inscricoes(base)
    arquivos.append(salvar_csv(resumo, pasta_resultados / NOME_CSV_RANKING))
    arquivos.append(salvar_csv(indicadores, pasta_resultados / NOME_CSV_INDICADORES))

    log.info("\n[3/3] Gerando gráficos...")
    arquivos += gerar_graficos(resumo, pasta_resultados)

    log.info("\n%s", "=" * LARGURA)
    log.info("PIPELINE CONCLUÍDO COM SUCESSO!")
    log.info("Resultados disponíveis em: %s", pasta_resultados)
    log.info("=" * LARGURA)
    return ResultadoPipeline(base, resumo, indicadores, validacao, arquivos)
