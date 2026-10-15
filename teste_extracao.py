
from pathlib import Path
from extracao import extrair_inscricoes

pasta = Path(__file__).parent

pdf = (
    pasta
    / "dados"
    / "Lista das inscrições deferidas.pdf"
)

df = extrair_inscricoes(pdf)

print("Total de registros extraídos:", len(df))
print("\nPrimeiros registros:")
print(df.head(10).to_string(index=False))

print("\nSituação das inscrições:")
print(df["Situação"].value_counts(dropna=False))

print("\nPolos identificados:")
print(df["Polo"].value_counts(dropna=False))
pasta = Path(__file__).parent
saida = pasta / "resultados"
saida.mkdir(exist_ok=True)

df.to_csv(
    saida / "inscricoes_deferidas.csv",
    index=False,
    encoding="utf-8-sig"
)

print("\nBase salva em:")
print(saida / "inscricoes_deferidas.csv")