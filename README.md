# Análise de Inscrições — IFCE

Projeto de análise de dados desenvolvido em Python para automatizar a extração, a validação, a análise estatística e a visualização de inscrições a partir de um documento PDF.

## Objetivo

Transformar informações de um documento PDF em dados estruturados, facilitando a análise da distribuição de inscrições por polo.

## Funcionalidades

- Extração de registros de PDF com PyMuPDF.
- Estruturação e manipulação dos dados com Pandas.
- Validação de campos obrigatórios e protocolos duplicados.
- Cálculo de indicadores estatísticos.
- Ranking e participação percentual por polo.
- Geração de gráficos com Matplotlib.
- Execução do pipeline completo por meio de um único arquivo.

## Tecnologias

- Python
- Pandas
- PyMuPDF
- Matplotlib
- Git e GitHub

## Estrutura do projeto

```text
analise_inscricoes_ifce/
├── analise.py
├── extracao.py
├── graficos.py
├── main.py
├── validar_dados.py
├── teste_analise.py
├── teste_extracao.py
├── teste_graficos.py
├── requirements.txt
├── .gitignore
├── README.md
├── dados/       # Arquivos locais, não versionados
└── resultados/  # Resultados locais, não versionados
```

## Como executar

### 1. Criar o ambiente virtual

```bash
python -m venv .venv
```

### 2. Instalar as dependências

```bash
python -m pip install -r requirements.txt
```

### 3. Adicionar o PDF de entrada

Coloque o arquivo de entrada esperado pelo projeto na pasta `dados/`.

### 4. Executar o pipeline

```bash
python main.py
```

### 5. Validar os dados

```bash
python validar_dados.py
```

Os resultados são salvos localmente na pasta `resultados/`.

## Resultados da validação

Na execução utilizada durante o desenvolvimento, foram identificados:

- 743 registros de inscrição.
- 6 polos distintos.
- Nenhum campo obrigatório vazio.
- Nenhum protocolo duplicado.
- Nenhum protocolo fora do padrão de sete dígitos.

Esses resultados descrevem a execução de validação realizada durante o desenvolvimento e podem variar conforme a base utilizada.


## Aprendizados

O projeto reúne conceitos de extração de dados, ETL, validação, análise exploratória, estatística descritiva e visualização de dados.
