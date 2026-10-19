"""Leitura e escrita da base tabular em CSV."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .config import ENCODING_CSV


def salvar_csv(df: pd.DataFrame, caminho: Path) -> Path:
    """Salva um DataFrame em CSV (UTF-8 com BOM, compatível com Excel)."""
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(caminho, index=False, encoding=ENCODING_CSV)
    return caminho


def ler_base(caminho: Path) -> pd.DataFrame:
    """Lê a base preservando o protocolo como texto (não perde zeros à esquerda)."""
    caminho = Path(caminho)
    if not caminho.exists():
        raise FileNotFoundError(f"Base não encontrada: {caminho}")
    return pd.read_csv(caminho, dtype={"Protocolo": "string"}, encoding=ENCODING_CSV)
