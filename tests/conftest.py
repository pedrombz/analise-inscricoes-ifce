import pandas as pd
import pytest

from inscricoes.config import COLUNAS, CURSO_PADRAO


@pytest.fixture
def montar_df():
    """Fábrica de DataFrames: recebe tuplas (protocolo, polo, situação)."""

    def _montar(linhas):
        return pd.DataFrame(
            [
                {
                    "Protocolo": protocolo,
                    "Nome": f"Pessoa Ficticia {i}",
                    "Curso": CURSO_PADRAO,
                    "Polo": polo,
                    "Situação": situacao,
                }
                for i, (protocolo, polo, situacao) in enumerate(linhas)
            ],
            columns=COLUNAS,
        )

    return _montar
