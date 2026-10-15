
from pathlib import Path
import pandas as pd

from analise import analisar_inscricoes

pasta = Path(__file__).parent
arquivo = pasta / "resultados" / "inscricoes_deferidas.csv"

df = pd.read_csv(arquivo)

resumo, indicadores = analisar_inscricoes(df)

print("\nRANKING POR POLO")
print(resumo.to_string(index=False))

print("\nINDICADORES ESTATÍSTICOS")
print(indicadores.to_string(index=False))

# Exportar os resultados
saida = pasta / "resultados"
resumo.to_csv(
    saida / "ranking_por_polo.csv",
    index=False,
    encoding="utf-8-sig"
)

indicadores.to_csv(
    saida / "indicadores_estatisticos.csv",
    index=False,
    encoding="utf-8-sig"
)

print("\nAnálise concluída! Arquivos salvos em resultados/.")
