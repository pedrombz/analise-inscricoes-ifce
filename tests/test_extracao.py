import pandas as pd
import pytest

from inscricoes.amostra import gerar_pdf_exemplo, gerar_registros_exemplo
from inscricoes.extracao import extrair_inscricoes, extrair_texto, parse_registros

TEXTO_BASE = """Nome Curso Situação da inscrição
1234567
Maria Silva
Tecnologia em Inteligência Artificial - UAB - Fortaleza
Inscrição deferida
Página 1
Nome Curso Situação da inscrição
0000123
João Souza
Tecnologia em Inteligência Artificial - UAB - Caucaia - Novo Pabussu
Inscrição deferida
"""


def test_extrai_registros_basicos():
    res = parse_registros(TEXTO_BASE)
    assert res.protocolos_encontrados == 2
    assert res.completo
    assert res.registros["Protocolo"].tolist() == ["1234567", "0000123"]  # zero à esquerda
    assert res.registros["Nome"].tolist() == ["Maria Silva", "João Souza"]
    assert res.registros["Polo"].tolist() == ["Fortaleza", "Caucaia - Novo Pabussu"]
    assert set(res.registros["Situação"]) == {"Inscrição deferida"}


def test_cabecalho_e_rodape_nao_vazam_para_os_campos():
    res = parse_registros(TEXTO_BASE)
    for coluna in ("Nome", "Polo", "Situação"):
        for valor in res.registros[coluna]:
            assert "Página" not in valor
            assert "Situação da inscrição" not in valor


def test_remove_rotulos_de_cabecalho_do_nome():
    texto = (
        "7654321\nNome Maria Silva Curso\n"
        "Tecnologia em Inteligência Artificial - UAB - Itapipoca\nInscrição deferida\n"
    )
    assert parse_registros(texto).registros["Nome"].iloc[0] == "Maria Silva"


def test_protocolo_de_outro_curso_e_contado_como_descartado():
    texto = TEXTO_BASE + "9999999\nAna Costa\nPedagogia - UAB - Maracanaú\nInscrição deferida\n"
    res = parse_registros(texto)
    assert res.protocolos_encontrados == 3
    assert len(res.registros) == 2
    assert res.descartados == ["9999999"]
    assert not res.completo


def test_curso_configuravel():
    texto = "9999999\nAna Costa\nPedagogia - UAB - Maracanaú\nInscrição indeferida\n"
    res = parse_registros(texto, curso="Pedagogia - UAB")
    assert res.registros["Polo"].iloc[0] == "Maracanaú"
    assert res.registros["Situação"].iloc[0] == "Inscrição indeferida"
    assert res.registros["Curso"].iloc[0] == "Pedagogia - UAB"


def test_situacao_ausente_vira_nao_identificada():
    texto = "1111111\nAna Costa\nTecnologia em Inteligência Artificial - UAB - Fortaleza\n"
    res = parse_registros(texto)
    assert res.registros["Situação"].iloc[0] == "Situação não identificada"
    assert res.registros["Polo"].iloc[0] == "Fortaleza"


def test_ruido_de_paginacao_nao_contamina_polo_quando_falta_situacao():
    texto = (
        "1111111\nAna Costa\nTecnologia em Inteligência Artificial - UAB - Fortaleza\n"
        "Página 3 de 20\n2222222\nBia Lima\n"
        "Tecnologia em Inteligência Artificial - UAB - Itapipoca\nInscrição deferida\n"
    )
    res = parse_registros(texto)
    assert res.registros["Polo"].tolist() == ["Fortaleza", "Itapipoca"]


def test_texto_sem_protocolos_retorna_base_vazia_com_colunas():
    res = parse_registros("nada relevante aqui")
    assert res.protocolos_encontrados == 0
    assert res.registros.empty
    assert list(res.registros.columns) == ["Protocolo", "Nome", "Curso", "Polo", "Situação"]


def test_roundtrip_com_pdf_sintetico(tmp_path):
    pdf = gerar_pdf_exemplo(tmp_path / "exemplo.pdf", quantidade=60, semente=7, indeferidas=0.2)
    res = extrair_inscricoes(pdf)
    esperado = pd.DataFrame(gerar_registros_exemplo(60, 7, 0.2))
    assert res.completo
    assert res.protocolos_encontrados == 60
    pd.testing.assert_frame_equal(
        res.registros[["Protocolo", "Nome", "Polo", "Situação"]].reset_index(drop=True),
        esperado,
        check_dtype=False,
    )


def test_pdf_inexistente(tmp_path):
    with pytest.raises(FileNotFoundError):
        extrair_texto(tmp_path / "nao_existe.pdf")


def test_arquivo_que_nao_e_pdf(tmp_path):
    falso = tmp_path / "falso.pdf"
    falso.write_text("isto não é um PDF")
    with pytest.raises(ValueError, match="PDF válido"):
        extrair_texto(falso)
