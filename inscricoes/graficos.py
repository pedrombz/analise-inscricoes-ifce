"""Visualizações em PNG a partir do resumo por polo."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from matplotlib.figure import Figure

COLUNAS_NECESSARIAS = {"Polo", "Inscricoes", "Percentual"}


def _grafico_barras(resumo: pd.DataFrame, destino: Path) -> Path:
    dados = resumo.sort_values("Inscricoes", ascending=True)

    fig = Figure(figsize=(11, 6))
    ax = fig.subplots()
    barras = ax.barh(dados["Polo"], dados["Inscricoes"])

    ax.set_title("Inscrições deferidas por polo", fontsize=16, pad=18)
    ax.set_xlabel("Quantidade de inscrições")
    ax.set_ylabel("Polo")
    ax.grid(axis="x", linestyle="--", alpha=0.3)
    ax.set_axisbelow(True)

    limite = dados["Inscricoes"].max() * 1.20
    ax.set_xlim(0, limite)
    for barra, (_, linha) in zip(barras, dados.iterrows(), strict=True):
        ax.text(
            barra.get_width() + limite * 0.01,
            barra.get_y() + barra.get_height() / 2,
            f"{int(linha['Inscricoes'])} ({linha['Percentual']:.2f}%)",
            va="center",
            fontsize=10,
        )

    fig.tight_layout()
    fig.savefig(destino, dpi=200, bbox_inches="tight")
    return destino


def _grafico_pizza(resumo: pd.DataFrame, destino: Path) -> Path:
    dados = resumo.sort_values("Inscricoes", ascending=False)

    fig = Figure(figsize=(9, 7))
    ax = fig.subplots()
    ax.pie(
        dados["Inscricoes"],
        labels=dados["Polo"],
        autopct="%1.1f%%",
        startangle=90,
        counterclock=False,
    )
    ax.set_title("Participação das inscrições por polo", fontsize=15, pad=18)

    fig.tight_layout()
    fig.savefig(destino, dpi=200, bbox_inches="tight")
    return destino


def gerar_graficos(resumo: pd.DataFrame, pasta_resultados: Path) -> list[Path]:
    """Gera os gráficos de quantidade e participação e retorna os caminhos criados.

    Usa a API orientada a objetos do Matplotlib (sem ``pyplot``), então funciona
    em servidores e CI sem tela e não deixa figuras abertas na memória.
    """
    faltantes = COLUNAS_NECESSARIAS - set(resumo.columns)
    if faltantes:
        raise ValueError(f"O resumo não possui as colunas: {sorted(faltantes)}")
    if resumo.empty:
        raise ValueError("O resumo está vazio; não há o que plotar.")

    pasta = Path(pasta_resultados)
    pasta.mkdir(parents=True, exist_ok=True)
    return [
        _grafico_barras(resumo, pasta / "01_inscricoes_por_polo.png"),
        _grafico_pizza(resumo, pasta / "02_participacao_por_polo.png"),
    ]
