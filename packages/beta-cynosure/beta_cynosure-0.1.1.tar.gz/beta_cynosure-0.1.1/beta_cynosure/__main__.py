import argparse
from beta_cynosure.engine import run

def cli():
    parser = argparse.ArgumentParser(description="Extrai dados financeiros da CVM e gera CSVs (DFP + ITR)")
    parser.add_argument("period", help="Intervalo de anos no formato INICIO-FIM (ex: 2020-2024)")

    args = parser.parse_args()
    try:
        start_year, end_year = map(int, args.period.split("-"))
        if start_year > end_year:
            raise ValueError
        anos = list(range(start_year, end_year + 1))
    except Exception:
        print("Formato inválido. Exemplo: use: b-cynosure 2023-2025")
        return

    run(anos)

if __name__ == "__main__":
    cli()
