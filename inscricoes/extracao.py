"""Extração dos registros de inscrição a partir do PDF."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd
import pymupdf

from .config import COLUNAS, CURSO_PADRAO, SITUACAO_NAO_IDENTIFICADA

log = logging.getLogger(__name__)

# Protocolo: sete dígitos sozinhos em uma linha.
_RE_PROTOCOLO = re.compile(r"(?m)^[ \t]*(\d{7})[ \t]*$")

# Ruído de paginação ("Página 3", "Página 3 de 20", "3/20") que cai no meio dos blocos.
_RE_RUIDO = re.compile(
    r"(?mi)^[ \t]*(?:p[áa]gina[ \t]+\d+(?:[ \t]*(?:de|/)[ \t]*\d+)?"
    r"|\d+[ \t]*/[ \t]*\d+)[ \t]*(?:\n|$)"
)

_RE_SITUACAO = re.compile(r"Inscrição\s+(deferida|indeferida)", re.IGNORECASE)

# Rótulos de cabeçalho de tabela que podem vazar para o início/fim do nome.
_ROTULOS = r"(?:Protocolo|Nome|Curso|Situação\s+da\s+inscrição)"
_RE_ROTULO_INICIO = re.compile(rf"^(?:{_ROTULOS}\s+)+")
_RE_ROTULO_FIM = re.compile(rf"(?:\s+{_ROTULOS})+$")


@dataclass
class ResultadoExtracao:
    """Resultado da extração, com contagem de controle.

    ``protocolos_encontrados`` conta todos os protocolos vistos no texto;
    ``descartados`` lista os que não puderam ser interpretados. Se os dois
    números não fecham com o esperado, a extração perdeu registros.
    """

    registros: pd.DataFrame
    protocolos_encontrados: int
    descartados: list[str] = field(default_factory=list)

    @property
    def completo(self) -> bool:
        return not self.descartados


def extrair_texto(caminho_pdf: str | Path) -> str:
    """Lê o texto bruto de todas as páginas do PDF."""
    caminho = Path(caminho_pdf)
    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo PDF não encontrado: {caminho}")
    try:
        with pymupdf.open(str(caminho)) as documento:
            return "\n".join(pagina.get_text("text") for pagina in documento)
    except pymupdf.FileDataError as erro:
        raise ValueError(f"O arquivo não é um PDF válido: {caminho}") from erro


def _padrao_curso(curso: str) -> re.Pattern[str]:
    """Constrói o regex 'Curso - Polo' tolerante a espaços e traços."""
    partes = [
        r"\s+".join(re.escape(palavra) for palavra in parte.split())
        for parte in re.split(r"\s*[-–]\s*", curso.strip())
        if parte.strip()
    ]
    prefixo = r"\s*[-–]\s*".join(partes)
    return re.compile(
        prefixo + r"\s*[-–]\s*(.*?)(?=\s+Inscrição\s+(?:deferida|indeferida)\b|$)",
        re.IGNORECASE,
    )


def _limpar_nome(trecho: str) -> str:
    nome = trecho.strip()
    nome = _RE_ROTULO_INICIO.sub("", nome)
    nome = _RE_ROTULO_FIM.sub("", nome)
    return nome.strip()


def parse_registros(texto: str, curso: str = CURSO_PADRAO) -> ResultadoExtracao:
    """Converte o texto bruto do PDF em registros estruturados."""
    texto = _RE_RUIDO.sub("", texto)
    padrao_curso = _padrao_curso(curso)
    protocolos = list(_RE_PROTOCOLO.finditer(texto))

    registros: list[dict[str, str]] = []
    descartados: list[str] = []

    for i, protocolo in enumerate(protocolos):
        inicio = protocolo.end()
        fim = protocolos[i + 1].start() if i + 1 < len(protocolos) else len(texto)
        bloco = re.sub(r"\s+", " ", texto[inicio:fim]).strip()

        casamento = padrao_curso.search(bloco)
        if not casamento:
            descartados.append(protocolo.group(1))
            continue

        situacao_match = _RE_SITUACAO.search(bloco, casamento.start())
        situacao = (
            f"Inscrição {situacao_match.group(1).lower()}"
            if situacao_match
            else SITUACAO_NAO_IDENTIFICADA
        )

        registros.append(
            {
                "Protocolo": protocolo.group(1),
                "Nome": _limpar_nome(bloco[: casamento.start()]),
                "Curso": curso,
                "Polo": casamento.group(1).strip(" -–"),
                "Situação": situacao,
            }
        )

    return ResultadoExtracao(
        registros=pd.DataFrame(registros, columns=COLUNAS),
        protocolos_encontrados=len(protocolos),
        descartados=descartados,
    )


def extrair_inscricoes(caminho_pdf: str | Path, curso: str = CURSO_PADRAO) -> ResultadoExtracao:
    """Extrai as inscrições do PDF e avisa quando algum protocolo foi descartado."""
    resultado = parse_registros(extrair_texto(caminho_pdf), curso)
    log.info(
        "Protocolos encontrados: %d | registros extraídos: %d",
        resultado.protocolos_encontrados,
        len(resultado.registros),
    )
    if resultado.descartados:
        log.warning(
            "ATENÇÃO: %d protocolo(s) foram descartados por não casarem com o curso '%s'. "
            "Confira o layout do PDF ou use --curso.",
            len(resultado.descartados),
            curso,
        )
    return resultado
