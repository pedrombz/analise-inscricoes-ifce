"""Configurações e constantes compartilhadas por todos os módulos."""

from pathlib import Path

RAIZ_PROJETO = Path(__file__).resolve().parent.parent
PASTA_DADOS = RAIZ_PROJETO / "dados"
PASTA_RESULTADOS = RAIZ_PROJETO / "resultados"

ARQUIVO_PDF_PADRAO = PASTA_DADOS / "Lista das inscrições deferidas.pdf"
ARQUIVO_PDF_EXEMPLO = PASTA_DADOS / "exemplo_sintetico.pdf"

NOME_CSV_BASE = "inscricoes_deferidas.csv"
NOME_CSV_RANKING = "ranking_por_polo.csv"
NOME_CSV_INDICADORES = "indicadores_estatisticos.csv"
ENCODING_CSV = "utf-8-sig"

COLUNAS = ["Protocolo", "Nome", "Curso", "Polo", "Situação"]

CURSO_PADRAO = "Tecnologia em Inteligência Artificial - UAB"

SITUACAO_DEFERIDA = "Inscrição deferida"
SITUACAO_INDEFERIDA = "Inscrição indeferida"
SITUACAO_NAO_IDENTIFICADA = "Situação não identificada"

REGEX_PROTOCOLO = r"\d{7}"
TAMANHO_MAXIMO_POLO = 60  # acima disso, o polo provavelmente "engoliu" texto vizinho
