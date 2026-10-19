import pytest

from inscricoes.analise import analisar_inscricoes
from inscricoes.graficos import gerar_graficos

DEF = "Inscrição deferida"


def test_gera_os_dois_png(tmp_path, montar_df):
    df = montar_df([(f"{i:07d}", p, DEF) for i, p in enumerate("AAABBC")])
    resumo, _ = analisar_inscricoes(df)
    arquivos = gerar_graficos(resumo, tmp_path / "saida")
    assert [a.name for a in arquivos] == [
        "01_inscricoes_por_polo.png",
        "02_participacao_por_polo.png",
    ]
    for arquivo in arquivos:
        assert arquivo.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"


def test_resumo_sem_colunas_levanta_erro(tmp_path, montar_df):
    with pytest.raises(ValueError, match="colunas"):
        gerar_graficos(montar_df([]), tmp_path)
