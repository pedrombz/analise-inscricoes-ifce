from inscricoes.validacao import formatar_relatorio, validar_dataframe

DEF = "Inscrição deferida"


def test_base_integra_e_aprovada(montar_df):
    res = validar_dataframe(montar_df([("0000001", "A", DEF), ("0000002", "B", DEF)]))
    assert res.ok
    assert not res.alertas
    assert res.contagens["Inscrições deferidas"] == 2
    assert res.deferidas_por_polo == {"A": 1, "B": 1}


def test_protocolo_fora_do_padrao_e_erro(montar_df):
    res = validar_dataframe(montar_df([("123", "A", DEF)]))
    assert not res.ok
    assert res.contagens["Protocolos fora do padrão de 7 dígitos"] == 1


def test_protocolo_duplicado_e_erro(montar_df):
    res = validar_dataframe(montar_df([("0000001", "A", DEF), ("0000001", "A", DEF)]))
    assert not res.ok
    assert res.contagens["Protocolos duplicados"] == 1


def test_campo_vazio_e_erro(montar_df):
    df = montar_df([("0000001", "A", DEF)])
    df.loc[0, "Nome"] = "   "
    res = validar_dataframe(df)
    assert not res.ok
    assert res.contagens["Campos vazios em 'Nome'"] == 1


def test_coluna_ausente_e_erro_sem_excecao(montar_df):
    df = montar_df([("0000001", "A", DEF)]).drop(columns=["Polo"])
    res = validar_dataframe(df)
    assert not res.ok
    assert "Polo" in res.erros[0]


def test_base_vazia_e_erro(montar_df):
    assert not validar_dataframe(montar_df([])).ok


def test_nao_deferida_gera_alerta_mas_nao_erro(montar_df):
    df = montar_df([("0000001", "A", DEF), ("0000002", "A", "Inscrição indeferida")])
    res = validar_dataframe(df)
    assert res.ok
    assert any("não estão classificados" in a for a in res.alertas)


def test_situacao_nao_identificada_gera_alerta(montar_df):
    res = validar_dataframe(montar_df([("0000001", "A", "Situação não identificada")]))
    assert res.ok
    assert any("não identificada" in a for a in res.alertas)


def test_polo_gigante_gera_alerta(montar_df):
    res = validar_dataframe(montar_df([("0000001", "X" * 80, DEF)]))
    assert any("caracteres" in a for a in res.alertas)


def test_relatorio_nao_expoe_dados_pessoais(montar_df):
    df = montar_df([("7654321", "A", DEF)])
    df.loc[0, "Nome"] = "NOME SECRETO DA SILVA"
    texto = formatar_relatorio(validar_dataframe(df))
    assert "NOME SECRETO" not in texto
    assert "7654321" not in texto
