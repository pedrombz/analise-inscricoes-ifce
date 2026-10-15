
import re
import fitz
import pandas as pd


def extrair_inscricoes(caminho_pdf):
    """
    Extrai os registros de inscrição de um PDF.

    Retorna um DataFrame com:
    Protocolo, Nome, Curso, Polo e Situação.
    """

    paginas = []

    with fitz.open(caminho_pdf) as documento:
        for pagina in documento:
            paginas.append(pagina.get_text("text"))

    texto = "\n".join(paginas)

    # Localiza os protocolos de 7 dígitos.
    protocolos = list(
        re.finditer(r"(?m)^\s*(\d{7})\s*$", texto)
    )

    registros = []

    for i, protocolo in enumerate(protocolos):
        inicio = protocolo.end()

        fim = (
            protocolos[i + 1].start()
            if i + 1 < len(protocolos)
            else len(texto)
        )

        bloco = re.sub(
            r"\s+", " ", texto[inicio:fim]
        ).strip()

        curso = re.search(
            r"Tecnologia em Inteligência Artificial\s*-\s*UAB\s*-\s*(.*?)(?=\s+Inscrição\s+(?:deferida|indeferida)\b|$)",
            bloco,
            flags=re.IGNORECASE
        )

        if not curso:
            continue

        nome = bloco[:curso.start()].strip()
        nome = re.sub(
            r"^(?:Nome|Curso|Situação da inscrição)\s+",
            "",
            nome,
            flags=re.IGNORECASE
        ).strip()

        polo = curso.group(1).strip(" -–")

        situacao_match = re.search(
            r"Inscrição\s+(deferida|indeferida)",
            bloco,
            flags=re.IGNORECASE
        )

        situacao = (
            situacao_match.group(0).title()
            if situacao_match
            else "Situação não identificada"
        )

        registros.append({
            "Protocolo": protocolo.group(1),
            "Nome": nome,
            "Curso": "Tecnologia em Inteligência Artificial - UAB",
            "Polo": polo,
            "Situação": situacao
        })

    return pd.DataFrame(registros)
