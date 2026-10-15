from pathlib import Path

import pandas as pd


# ============================================================
# CONFIGURAÇÕES
# ============================================================

PASTA_PROJETO = Path(__file__).parent
ARQUIVO_CSV = (
    PASTA_PROJETO
    / "resultados"
    / "inscricoes_deferidas.csv"
)

COLUNAS_OBRIGATORIAS = [
    "Protocolo",
    "Nome",
    "Curso",
    "Polo",
    "Situação",
]


def validar_dados():
    """Verifica a integridade da base extraída sem exibir dados pessoais."""

    if not ARQUIVO_CSV.exists():
        raise FileNotFoundError(
            f"Base não encontrada: {ARQUIVO_CSV}"
        )

    df = pd.read_csv(
        ARQUIVO_CSV,
        dtype={"Protocolo": "string"},
        encoding="utf-8-sig",
    )

    print("=" * 55)
    print("VALIDAÇÃO DA BASE DE INSCRIÇÕES")
    print("=" * 55)

    erros = []
    alertas = []

    # 1. Estrutura
    colunas_ausentes = [
        coluna
        for coluna in COLUNAS_OBRIGATORIAS
        if coluna not in df.columns
    ]

    if colunas_ausentes:
        raise ValueError(
            f"Colunas obrigatórias ausentes: {colunas_ausentes}"
        )

    print(f"\nTotal de registros: {len(df)}")
    print(f"Total de colunas: {len(df.columns)}")

    if df.empty:
        raise ValueError("A base está vazia.")

    # 2. Campos ausentes ou vazios
    campos_textuais = [
        "Protocolo",
        "Nome",
        "Curso",
        "Polo",
        "Situação",
    ]

    for coluna in campos_textuais:
        valores = df[coluna].astype("string").str.strip()
        ausentes = (
            df[coluna].isna()
            | valores.eq("").fillna(False)
        )
        quantidade = int(ausentes.sum())

        print(f"Campos vazios em '{coluna}': {quantidade}")

        if quantidade:
            erros.append(
                f"{coluna}: {quantidade} valores ausentes ou vazios"
            )

    # 3. Formato dos protocolos
    protocolos = df["Protocolo"].astype("string").str.strip()
    protocolos_validos = protocolos.str.fullmatch(r"\d{7}", na=False)
    protocolos_invalidos = int((~protocolos_validos).sum())

    print(f"Protocolos fora do padrão de 7 dígitos: {protocolos_invalidos}")

    if protocolos_invalidos:
        alertas.append(
            f"{protocolos_invalidos} protocolos fora do padrão esperado"
        )

    # 4. Duplicidades
    duplicados = int(
        protocolos[protocolos_validos].duplicated().sum()
    )

    print(f"Protocolos duplicados: {duplicados}")

    if duplicados:
        erros.append(
            f"Foram encontrados {duplicados} protocolos duplicados"
        )

    # 5. Situação das inscrições
    situacoes = (
        df["Situação"]
        .astype("string")
        .str.strip()
        .str.casefold()
    )

    print("\nDistribuição das situações:")
    print(
        situacoes.value_counts(dropna=False).to_string()
    )

    deferidas = int(
        situacoes.eq("inscrição deferida").sum()
    )

    print(f"\nInscrições deferidas: {deferidas}")

    nao_deferidas = len(df) - deferidas

    if nao_deferidas:
        alertas.append(
            f"{nao_deferidas} registros não estão classificados "
            "como 'Inscrição deferida'"
        )

    # 6. Distribuição por polo
    polos = df["Polo"].astype("string").str.strip()
    polos_validos = polos.notna() & polos.ne("")

    print(f"Polos distintos não vazios: {polos[polos_validos].nunique()}")

    resumo = (
        df.loc[
            situacoes.eq("inscrição deferida") & polos_validos
        ]
        .assign(Polo=polos[ situacoes.eq("inscrição deferida") & polos_validos ])
        .groupby("Polo")["Protocolo"]
        .nunique()
        .sort_values(ascending=False)
    )

    print("\nInscrições deferidas por polo:")
    print(resumo.to_string())

    # 7. Resultado
    print("\n" + "=" * 55)

    if erros:
        print("VALIDAÇÃO COM ERROS")
        for erro in erros:
            print(f"- {erro}")
    else:
        print("Nenhum erro crítico identificado.")

    if alertas:
        print("\nPontos para revisar:")
        for alerta in alertas:
            print(f"- {alerta}")

    if not erros and not alertas:
        print("Base aprovada nas verificações implementadas.")

    print("=" * 55)

    return not erros


if __name__ == "__main__":
    validar_dados()