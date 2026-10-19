"""Ponto de entrada: ``python main.py`` roda o pipeline completo.

Subcomandos: ``executar`` (padrão), ``validar`` e ``exemplo``. Veja ``python main.py -h``.
"""

from inscricoes.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
