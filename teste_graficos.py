
from pathlib import Path
import pandas as pd

from graficos import gerar_graficos

pasta = Path(__file__).parent
arquivo = pasta / "resultados" / "ranking_por_polo.csv"

resumo = pd.read_csv(arquivo)

gerar_graficos(
    resumo,
    pasta / "resultados"
)

print("Confira os PNGs na pasta resultados.")
