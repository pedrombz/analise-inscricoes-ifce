"""Ranking por polo e indicadores estatísticos das inscrições deferidas."""

from __future__ import annotations

import logging

import pandas as pd

from .config import SITUACAO_DEFERIDA

log = logging.getLogger(__name__)


def eh_deferida(situacao: pd.Series) -> pd.Series:
    """Máscara booleana das inscrições deferidas (ignora caixa e espaços)."""
    normalizada = situacao.astype("string").str.strip().str.casefold()
    return normalizada.eq(SITUACAO_DEFERIDA.casefold()).fillna(False).astype(bool)


def analisar_inscricoes(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Calcula o ranking por polo e os indicadores das inscrições deferidas.

    Retorna ``(resumo, indicadores)``. O ranking desempata por nome do polo,
    então o resultado é determinístico.
    """
    deferidas = df[eh_deferida(df["Situação"])].copy()
    if deferidas.empty:
        raise ValueError("Nenhuma inscrição deferida encontrada na base.")

    duplicados = int(deferidas["Protocolo"].duplicated().sum())
    if duplicados:
        raise ValueError(f"Foram encontrados {duplicados} protocolos duplicados.")

    deferidas["Polo"] = deferidas["Polo"].astype("string").str.strip().fillna("")
    sem_polo = int((deferidas["Polo"] == "").sum())
    if sem_polo:
        log.warning("%d inscrição(ões) deferida(s) sem polo foram ignoradas no ranking.", sem_polo)
        deferidas = deferidas[deferidas["Polo"] != ""]
    if deferidas.empty:
        raise ValueError("Nenhuma inscrição deferida com polo informado.")
    deferidas["Polo"] = deferidas["Polo"].astype(str)

    resumo = (
        deferidas.groupby("Polo", as_index=False)
        .agg(Inscricoes=("Protocolo", "nunique"))
        .sort_values(["Inscricoes", "Polo"], ascending=[False, True])
        .reset_index(drop=True)
    )
    resumo.insert(0, "Posicao", range(1, len(resumo) + 1))

    total = int(resumo["Inscricoes"].sum())
    resumo["Percentual"] = (resumo["Inscricoes"] / total * 100).round(2)

    maior = resumo.iloc[0]
    menor = resumo.iloc[-1]
    top3 = int(resumo.head(3)["Inscricoes"].sum())

    indicadores = pd.DataFrame(
        [
            {"Indicador": "Total de inscrições", "Valor": total},
            {"Indicador": "Quantidade de polos", "Valor": len(resumo)},
            {"Indicador": "Média por polo", "Valor": round(float(resumo["Inscricoes"].mean()), 2)},
            {
                "Indicador": "Mediana por polo",
                "Valor": round(float(resumo["Inscricoes"].median()), 2),
            },
            {"Indicador": "Maior polo", "Valor": maior["Polo"]},
            {"Indicador": "Inscrições no maior polo", "Valor": int(maior["Inscricoes"])},
            {"Indicador": "Menor polo", "Valor": menor["Polo"]},
            {"Indicador": "Inscrições no menor polo", "Valor": int(menor["Inscricoes"])},
            {
                "Indicador": "Diferença entre extremos",
                "Valor": int(maior["Inscricoes"] - menor["Inscricoes"]),
            },
            {
                "Indicador": "Razão maior/menor polo",
                "Valor": round(float(maior["Inscricoes"] / menor["Inscricoes"]), 2),
            },
            {"Indicador": "Inscrições nos 3 maiores polos", "Valor": top3},
            {"Indicador": "Participação dos 3 maiores (%)", "Valor": round(top3 / total * 100, 2)},
        ]
    )
    return resumo, indicadores
