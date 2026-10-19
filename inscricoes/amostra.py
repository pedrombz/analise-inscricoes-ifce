"""Geração de um PDF sintético no mesmo formato esperado pelo extrator.

Permite rodar, demonstrar e testar o pipeline sem usar dados pessoais reais.
Todos os nomes e protocolos são fictícios e gerados aleatoriamente.
"""

from __future__ import annotations

import random
from pathlib import Path

import pymupdf

from .config import CURSO_PADRAO, SITUACAO_DEFERIDA, SITUACAO_INDEFERIDA

POLOS_EXEMPLO = {
    "Fortaleza": 0.40,
    "Maracanaú": 0.18,
    "Itapipoca": 0.16,
    "Horizonte": 0.10,
    "Caucaia Novo Pabussu": 0.09,
    "Maranguape": 0.07,
}

_PRIMEIROS_NOMES = [
    "Ana", "Bruno", "Carla", "Daniel", "Elisa", "Felipe", "Gabriela", "Hugo", "Isabela",
    "João", "Karina", "Lucas", "Marina", "Nicolas", "Olívia", "Paulo", "Rafaela", "Sérgio",
    "Tânia", "Vinícius",
]
_SOBRENOMES = [
    "Almeida", "Barbosa", "Cardoso", "Dias", "Esteves", "Ferreira", "Gomes", "Holanda",
    "Lima", "Macedo", "Nogueira", "Oliveira", "Pereira", "Queiroz", "Rocha", "Sales",
    "Teixeira", "Uchôa", "Viana", "Xavier",
]

_ALTURA_REGISTRO = 4 * 13 + 8
_LIMITE_PAGINA = 790


def gerar_registros_exemplo(
    quantidade: int = 120,
    semente: int = 42,
    indeferidas: float = 0.0,
) -> list[dict[str, str]]:
    """Gera registros fictícios (protocolo, nome, polo, situação) de forma reprodutível."""
    rng = random.Random(semente)
    numeros = rng.sample(range(10_000_000), quantidade)  # inclui protocolos com zero à esquerda
    polos = list(POLOS_EXEMPLO)
    pesos = list(POLOS_EXEMPLO.values())

    registros = []
    for numero in numeros:
        nome = (
            f"{rng.choice(_PRIMEIROS_NOMES)} {rng.choice(_SOBRENOMES)} {rng.choice(_SOBRENOMES)}"
        )
        situacao = SITUACAO_INDEFERIDA if rng.random() < indeferidas else SITUACAO_DEFERIDA
        registros.append(
            {
                "Protocolo": f"{numero:07d}",
                "Nome": nome,
                "Polo": rng.choices(polos, weights=pesos)[0],
                "Situação": situacao,
            }
        )
    return registros


def gerar_pdf_exemplo(
    caminho: str | Path,
    quantidade: int = 120,
    semente: int = 42,
    indeferidas: float = 0.0,
    curso: str = CURSO_PADRAO,
) -> Path:
    """Escreve um PDF sintético com cabeçalho e rodapé repetidos em cada página."""
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    registros = gerar_registros_exemplo(quantidade, semente, indeferidas)

    documento = pymupdf.open()
    pagina = None
    y = 0.0
    for registro in registros:
        if pagina is None or y + _ALTURA_REGISTRO > _LIMITE_PAGINA:
            pagina = documento.new_page(width=595, height=842)
            pagina.insert_text((50, 40), "Nome Curso Situação da inscrição", fontsize=9)
            y = 70.0
        for linha in (
            registro["Protocolo"],
            registro["Nome"],
            f"{curso} - {registro['Polo']}",
            registro["Situação"],
        ):
            pagina.insert_text((50, y), linha, fontsize=9)
            y += 13
        y += 8

    for numero, pagina in enumerate(documento, start=1):
        pagina.insert_text((50, 820), f"Página {numero}", fontsize=9)

    documento.save(str(caminho))
    documento.close()
    return caminho
