from pathlib import Path

from extracao import extrair_inscricoes
from analise import analisar_inscricoes
from graficos import gerar_graficos


# ============================================================
# CONFIGURAÇÕES
# ============================================================

PASTA_PROJETO = Path(__file__).parent
PASTA_DADOS = PASTA_PROJETO / "dados"
PASTA_RESULTADOS = PASTA_PROJETO / "resultados"

ARQUIVO_PDF = PASTA_DADOS / "Lista das inscrições deferidas.pdf"
ARQUIVO_CSV = PASTA_RESULTADOS / "inscricoes_deferidas.csv"


def executar_pipeline():
    """Executa o fluxo completo de processamento e análise."""

    PASTA_RESULTADOS.mkdir(parents=True, exist_ok=True)

    if not ARQUIVO_PDF.exists():
        raise FileNotFoundError(
            f"Arquivo PDF não encontrado: {ARQUIVO_PDF}"
        )

    print("=" * 60)
    print("ANÁLISE DE INSCRIÇÕES — IFCE")
    print("=" * 60)

    # 1. Extração estruturada
    print("\n[1/3] Extraindo inscrições do PDF...")

    df = extrair_inscricoes(ARQUIVO_PDF)

    if df.empty:
        raise ValueError(
            "A extração não retornou inscrições. Verifique o PDF."
        )

    df.to_csv(
        ARQUIVO_CSV,
        index=False,
        encoding="utf-8-sig"
    )

    print(f"Inscrições extraídas: {len(df)}")
    print(f"Base salva em: {ARQUIVO_CSV}")

    # 2. Análise estatística
    print("\n[2/3] Analisando os dados...")

    resumo, indicadores = analisar_inscricoes(df)

    # 3. Geração dos gráficos
    print("\n[3/3] Gerando gráficos...")

    gerar_graficos(resumo, PASTA_RESULTADOS)

    print("\n" + "=" * 60)
    print("PIPELINE CONCLUÍDO COM SUCESSO!")
    print(f"Resultados disponíveis em: {PASTA_RESULTADOS}")
    print("=" * 60)


if __name__ == "__main__":
    executar_pipeline()