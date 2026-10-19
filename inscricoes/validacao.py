"""Verificações de integridade da base extraída (sem expor dados pessoais)."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

from .analise import eh_deferida
from .armazenamento import ler_base
from .config import COLUNAS, REGEX_PROTOCOLO, TAMANHO_MAXIMO_POLO

LARGURA = 55


@dataclass
class ResultadoValidacao:
    """Resumo da validação. Contém apenas contagens, nunca nomes ou protocolos."""

    erros: list[str] = field(default_factory=list)
    alertas: list[str] = field(default_factory=list)
    contagens: dict[str, int] = field(default_factory=dict)
    situacoes: dict[str, int] = field(default_factory=dict)
    deferidas_por_polo: dict[str, int] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return not self.erros


def _vazios(serie: pd.Series) -> int:
    valores = serie.astype("string").str.strip()
    return int((valores.isna() | valores.fillna("").eq("")).sum())


def validar_dataframe(df: pd.DataFrame) -> ResultadoValidacao:
    """Valida estrutura, campos obrigatórios, protocolos, situações e polos."""
    res = ResultadoValidacao()

    ausentes = [c for c in COLUNAS if c not in df.columns]
    if ausentes:
        res.erros.append(f"Colunas obrigatórias ausentes: {ausentes}")
        return res
    if df.empty:
        res.erros.append("A base está vazia.")
        return res

    res.contagens["Total de registros"] = len(df)
    res.contagens["Total de colunas"] = len(df.columns)

    # 1. Campos vazios
    for coluna in COLUNAS:
        quantidade = _vazios(df[coluna])
        res.contagens[f"Campos vazios em '{coluna}'"] = quantidade
        if quantidade:
            res.erros.append(f"{coluna}: {quantidade} valores ausentes ou vazios")

    # 2. Formato dos protocolos
    protocolos = df["Protocolo"].astype("string").str.strip()
    validos = protocolos.str.fullmatch(REGEX_PROTOCOLO, na=False)
    invalidos = int((~validos).sum())
    res.contagens["Protocolos fora do padrão de 7 dígitos"] = invalidos
    if invalidos:
        res.erros.append(f"{invalidos} protocolos fora do padrão esperado")

    # 3. Duplicidades
    preenchidos = protocolos[protocolos.notna() & protocolos.fillna("").ne("")]
    duplicados = int(preenchidos.duplicated().sum())
    res.contagens["Protocolos duplicados"] = duplicados
    if duplicados:
        res.erros.append(f"Foram encontrados {duplicados} protocolos duplicados")

    # 4. Situações
    situacoes = df["Situação"].astype("string").str.strip().fillna("<ausente>")
    res.situacoes = {
        str(situacao): int(qtd)
        for situacao, qtd in situacoes.str.casefold().value_counts().items()
    }
    deferida = eh_deferida(df["Situação"])
    res.contagens["Inscrições deferidas"] = int(deferida.sum())

    nao_identificadas = int(situacoes.str.casefold().eq("situação não identificada").sum())
    if nao_identificadas:
        res.alertas.append(f"{nao_identificadas} registros com situação não identificada")
    nao_deferidas = int((~deferida).sum()) - nao_identificadas
    if nao_deferidas > 0:
        res.alertas.append(f"{nao_deferidas} registros não estão classificados como deferidos")

    # 5. Polos
    polos = df["Polo"].astype("string").str.strip()
    polos_validos = polos.notna() & polos.fillna("").ne("")
    res.contagens["Polos distintos não vazios"] = int(polos[polos_validos].nunique())

    suspeitos = int((polos.fillna("").str.len() > TAMANHO_MAXIMO_POLO).sum())
    if suspeitos:
        res.alertas.append(
            f"{suspeitos} polos com mais de {TAMANHO_MAXIMO_POLO} caracteres "
            "(possível texto extra capturado na extração)"
        )

    por_polo = (
        df.loc[deferida & polos_validos]
        .assign(Polo=polos[deferida & polos_validos])
        .groupby("Polo")["Protocolo"]
        .nunique()
        .sort_values(ascending=False)
    )
    res.deferidas_por_polo = {str(polo): int(qtd) for polo, qtd in por_polo.items()}
    return res


def validar_csv(caminho: Path) -> ResultadoValidacao:
    """Lê a base do disco e a valida."""
    return validar_dataframe(ler_base(caminho))


def formatar_relatorio(res: ResultadoValidacao) -> str:
    """Monta o relatório de texto (somente contagens agregadas)."""
    linhas = ["=" * LARGURA, "VALIDAÇÃO DA BASE DE INSCRIÇÕES", "=" * LARGURA, ""]
    for nome, valor in res.contagens.items():
        linhas.append(f"{nome}: {valor}")
    if res.situacoes:
        linhas += ["", "Distribuição das situações:"]
        linhas += [f"  {situacao}: {qtd}" for situacao, qtd in res.situacoes.items()]
    if res.deferidas_por_polo:
        linhas += ["", "Inscrições deferidas por polo:"]
        linhas += [f"  {polo}: {qtd}" for polo, qtd in res.deferidas_por_polo.items()]

    linhas += ["", "=" * LARGURA]
    if res.erros:
        linhas.append("VALIDAÇÃO COM ERROS")
        linhas += [f"- {erro}" for erro in res.erros]
    else:
        linhas.append("Nenhum erro crítico identificado.")
    if res.alertas:
        linhas += ["", "Pontos para revisar:"]
        linhas += [f"- {alerta}" for alerta in res.alertas]
    if not res.erros and not res.alertas:
        linhas.append("Base aprovada nas verificações implementadas.")
    linhas.append("=" * LARGURA)
    return "\n".join(linhas)
