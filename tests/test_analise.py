import pytest

from inscricoes.analise import analisar_inscricoes, eh_deferida

DEF = "Inscrição deferida"
INDEF = "Inscrição indeferida"


def _indicadores(df):
    return dict(zip(df["Indicador"], df["Valor"], strict=True))


def test_reproduz_numeros_da_execucao_de_referencia(montar_df):
    contagens = {
        "Fortaleza": 307,
        "Maracanaú": 132,
        "Itapipoca": 116,
        "Horizonte": 71,
        "Caucaia Novo Pabussu": 68,
        "Maranguape": 49,
    }
    linhas, n = [], 0
    for polo, qtd in contagens.items():
        for _ in range(qtd):
            linhas.append((f"{n:07d}", polo, DEF))
            n += 1

    resumo, ind = analisar_inscricoes(montar_df(linhas))
    valores = _indicadores(ind)

    assert resumo["Polo"].iloc[0] == "Fortaleza"
    assert resumo["Percentual"].iloc[0] == 41.32
    assert valores["Total de inscrições"] == 743
    assert valores["Quantidade de polos"] == 6
    assert valores["Média por polo"] == pytest.approx(123.83)
    assert valores["Mediana por polo"] == pytest.approx(93.5)
    assert valores["Diferença entre extremos"] == 258
    assert valores["Razão maior/menor polo"] == pytest.approx(6.27)
    assert valores["Inscrições nos 3 maiores polos"] == 555
    assert valores["Participação dos 3 maiores (%)"] == pytest.approx(74.70)


def test_ignora_indeferidas_e_normaliza_caixa(montar_df):
    df = montar_df(
        [
            ("0000001", "A", DEF),
            ("0000002", "A", "  INSCRIÇÃO DEFERIDA "),
            ("0000003", "B", INDEF),
        ]
    )
    resumo, _ = analisar_inscricoes(df)
    assert resumo["Polo"].tolist() == ["A"]
    assert resumo["Inscricoes"].tolist() == [2]


def test_desempate_e_deterministico(montar_df):
    df = montar_df([("0000001", "B", DEF), ("0000002", "B", DEF),
                    ("0000003", "A", DEF), ("0000004", "A", DEF)])
    resumo, _ = analisar_inscricoes(df)
    assert resumo["Polo"].tolist() == ["A", "B"]
    assert resumo["Posicao"].tolist() == [1, 2]


def test_percentuais_somam_cem(montar_df):
    df = montar_df([(f"{i:07d}", p, DEF) for i, p in enumerate("AAABBC")])
    resumo, _ = analisar_inscricoes(df)
    assert resumo["Percentual"].sum() == pytest.approx(100, abs=0.05)


def test_protocolo_duplicado_levanta_erro(montar_df):
    df = montar_df([("0000001", "A", DEF), ("0000001", "B", DEF)])
    with pytest.raises(ValueError, match="duplicados"):
        analisar_inscricoes(df)


def test_sem_deferidas_levanta_erro(montar_df):
    with pytest.raises(ValueError, match="Nenhuma inscrição deferida"):
        analisar_inscricoes(montar_df([("0000001", "A", INDEF)]))


def test_deferida_sem_polo_e_ignorada_do_ranking(montar_df):
    df = montar_df([("0000001", "A", DEF), ("0000002", "", DEF)])
    resumo, ind = analisar_inscricoes(df)
    assert resumo["Inscricoes"].sum() == 1
    assert _indicadores(ind)["Total de inscrições"] == 1


def test_eh_deferida_trata_valores_ausentes(montar_df):
    df = montar_df([("0000001", "A", DEF)])
    df.loc[0, "Situação"] = None
    assert not eh_deferida(df["Situação"]).iloc[0]
