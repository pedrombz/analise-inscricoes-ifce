import pandas as pd
import pytest

from inscricoes import pipeline
from inscricoes.amostra import gerar_pdf_exemplo
from inscricoes.armazenamento import ler_base, salvar_csv
from inscricoes.cli import main
from inscricoes.extracao import ResultadoExtracao
from inscricoes.pipeline import ExtracaoIncompletaError, executar_pipeline


@pytest.fixture
def pdf(tmp_path):
    return gerar_pdf_exemplo(tmp_path / "exemplo.pdf", quantidade=80, semente=1)


def test_pipeline_completo_gera_todos_os_arquivos(pdf, tmp_path):
    saida = tmp_path / "res"
    res = executar_pipeline(pdf, saida, validar=True)
    nomes = {a.name for a in res.arquivos}
    assert nomes == {
        "inscricoes_deferidas.csv",
        "ranking_por_polo.csv",
        "indicadores_estatisticos.csv",
        "01_inscricoes_por_polo.png",
        "02_participacao_por_polo.png",
    }
    assert all(a.exists() for a in res.arquivos)
    assert res.validacao.ok
    assert res.resumo["Inscricoes"].sum() == 80


def test_csv_preserva_zeros_a_esquerda(pdf, tmp_path):
    executar_pipeline(pdf, tmp_path / "res")
    base = ler_base(tmp_path / "res" / "inscricoes_deferidas.csv")
    assert (base["Protocolo"].str.len() == 7).all()


def test_modo_estrito_falha_quando_ha_descartes(pdf, tmp_path, monkeypatch):
    incompleto = ResultadoExtracao(
        pd.DataFrame(), protocolos_encontrados=2, descartados=["1234567"]
    )
    monkeypatch.setattr(pipeline, "extrair_inscricoes", lambda *_: incompleto)
    with pytest.raises(ExtracaoIncompletaError):
        executar_pipeline(pdf, tmp_path / "res", estrito=True)


def test_curso_errado_nao_extrai_nada(pdf, tmp_path):
    with pytest.raises(ValueError, match="não retornou"):
        executar_pipeline(pdf, tmp_path / "res", curso="Pedagogia - UAB")


# --- CLI ---------------------------------------------------------------------


def test_cli_executar_e_validar(pdf, tmp_path):
    saida = tmp_path / "res"
    assert main(["executar", "--pdf", str(pdf), "--saida", str(saida), "--validar"]) == 0
    assert main(["validar", "--csv", str(saida / "inscricoes_deferidas.csv")]) == 0


def test_cli_sem_subcomando_executa_pipeline(pdf, tmp_path):
    assert main(["--pdf", str(pdf), "--saida", str(tmp_path / "res")]) == 0


def test_cli_pdf_inexistente_retorna_2(tmp_path):
    assert main(["executar", "--pdf", str(tmp_path / "x.pdf"), "--saida", str(tmp_path)]) == 2


def test_cli_validar_base_com_erro_retorna_1(pdf, tmp_path):
    saida = tmp_path / "res"
    executar_pipeline(pdf, saida)
    caminho = saida / "inscricoes_deferidas.csv"
    base = ler_base(caminho)
    salvar_csv(pd.concat([base, base.iloc[[0]]]), caminho)  # duplica um protocolo
    assert main(["validar", "--csv", str(caminho)]) == 1


def test_cli_validar_sem_arquivo_retorna_2(tmp_path):
    assert main(["validar", "--csv", str(tmp_path / "nada.csv")]) == 2


def test_cli_exemplo_gera_pdf(tmp_path):
    destino = tmp_path / "amostra.pdf"
    assert main(["exemplo", "--saida", str(destino), "--registros", "30"]) == 0
    assert destino.exists()
