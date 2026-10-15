
import matplotlib.pyplot as plt


def gerar_graficos(resumo, pasta_resultados):
    """
    Gera gráficos de quantidade e participação
    das inscrições por polo.
    """

    pasta_resultados.mkdir(parents=True, exist_ok=True)

    # -----------------------------------------
    # 1. Gráfico de barras horizontais
    # -----------------------------------------

    dados = resumo.sort_values(
        "Inscricoes",
        ascending=True
    )

    fig, ax = plt.subplots(figsize=(11, 6))

    barras = ax.barh(
        dados["Polo"],
        dados["Inscricoes"]
    )

    ax.set_title(
        "Inscrições deferidas por polo",
        fontsize=16,
        pad=18
    )
    ax.set_xlabel("Quantidade de inscrições")
    ax.set_ylabel("Polo")
    ax.grid(axis="x", linestyle="--", alpha=0.3)
    ax.set_axisbelow(True)

    limite = dados["Inscricoes"].max() * 1.20
    ax.set_xlim(0, limite)

    for barra, (_, linha) in zip(
        barras,
        dados.iterrows()
    ):
        ax.text(
            barra.get_width() + limite * 0.01,
            barra.get_y() + barra.get_height() / 2,
            f'{int(linha["Inscricoes"])} '
            f'({linha["Percentual"]:.2f}%)',
            va="center",
            fontsize=10
        )

    fig.tight_layout()
    fig.savefig(
        pasta_resultados / "01_inscricoes_por_polo.png",
        dpi=200,
        bbox_inches="tight"
    )
    plt.close(fig)

    # -----------------------------------------
    # 2. Gráfico de participação percentual
    # -----------------------------------------

    dados = resumo.sort_values(
        "Inscricoes",
        ascending=False
    )

    fig, ax = plt.subplots(figsize=(9, 7))

    ax.pie(
        dados["Inscricoes"],
        labels=dados["Polo"],
        autopct="%1.1f%%",
        startangle=90,
        counterclock=False
    )

    ax.set_title(
        "Participação das inscrições por polo",
        fontsize=15,
        pad=18
    )

    fig.tight_layout()
    fig.savefig(
        pasta_resultados / "02_participacao_por_polo.png",
        dpi=200,
        bbox_inches="tight"
    )
    plt.close(fig)

    print("\nGráficos gerados com sucesso!")
