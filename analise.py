
import pandas as pd


def analisar_inscricoes(df):
    """
    Calcula indicadores estatísticos e ranking
    a partir dos registros de inscrições deferidas.
    """

    # Considerar apenas inscrições deferidas
    df = df[
        df["Situação"].str.casefold().eq("inscrição deferida")
    ].copy()

    # Validar protocolos duplicados
    duplicados = df["Protocolo"].duplicated().sum()

    if duplicados:
        raise ValueError(
            f"Foram encontrados {duplicados} protocolos duplicados."
        )

    # Contagem por polo
    resumo = (
        df.groupby("Polo")
        .agg(Inscricoes=("Protocolo", "nunique"))
        .reset_index()
    )

    # Ordenar ranking
    resumo = resumo.sort_values(
        "Inscricoes",
        ascending=False
    ).reset_index(drop=True)

    resumo.insert(0, "Posicao", range(1, len(resumo) + 1))

    # Indicadores
    total = int(resumo["Inscricoes"].sum())
    resumo["Percentual"] = (
        resumo["Inscricoes"] / total * 100
    ).round(2)

    media = resumo["Inscricoes"].mean()
    mediana = resumo["Inscricoes"].median()

    maior = resumo.iloc[0]
    menor = resumo.iloc[-1]

    top3 = resumo.head(3)["Inscricoes"].sum()

    indicadores = pd.DataFrame([
        {"Indicador": "Total de inscrições", "Valor": total},
        {"Indicador": "Quantidade de polos", "Valor": len(resumo)},
        {"Indicador": "Média por polo", "Valor": round(media, 2)},
        {"Indicador": "Mediana por polo", "Valor": round(mediana, 2)},
        {"Indicador": "Maior polo", "Valor": maior["Polo"]},
        {"Indicador": "Inscrições no maior polo", "Valor": int(maior["Inscricoes"])},
        {"Indicador": "Menor polo", "Valor": menor["Polo"]},
        {"Indicador": "Inscrições no menor polo", "Valor": int(menor["Inscricoes"])},
        {"Indicador": "Diferença entre extremos", "Valor": int(maior["Inscricoes"] - menor["Inscricoes"])},
        {"Indicador": "Inscrições nos 3 maiores polos", "Valor": int(top3)},
        {"Indicador": "Participação dos 3 maiores (%)", "Valor": round(top3 / total * 100, 2)},
    ])

    return resumo, indicadores
