import os
from typing import List
from beta_cynosure.utils.loaders import load_dfp_year, load_itr_year
from beta_cynosure.utils.cleaner import clean_financial_data
from beta_cynosure.utils.processor import prepare_quarterly_data
from beta_cynosure.config.config import DFP_FILE, ITR_FILE
import pandas as pd

def ensure_output_dir():
    os.makedirs(os.path.dirname(DFP_FILE), exist_ok=True)

def run(years: List[int]):
    ensure_output_dir()

    dfp_dfs = []
    for year in years:
        try:
            dfp = load_dfp_year(year)
            dfp_dfs.append(dfp)
        except Exception as exc:
            print(f"Erro ao carregar DFP {year}: {exc}")
    dfp_all = clean_financial_data(pd.concat(dfp_dfs, ignore_index=True))
    for col in ['DENOM_CIA', 'DS_CONTA', 'GRUPO_DFP']:
        if col not in dfp_all.columns:
            dfp_all[col] = pd.NA
    dfp_all[['CNPJ_CIA', 'DENOM_CIA', 'CD_CONTA', 'DS_CONTA', 'GRUPO_DFP', 'VL_CONTA', 'YEAR']].to_csv(DFP_FILE, index=False)

    itr_dfs = []
    for year in years:
        try:
            itr = load_itr_year(year)
            itr_dfs.append(itr)
        except Exception as exc:
            print(f"Erro ao carregar ITR {year}: {exc}")
    quarter_data = prepare_quarterly_data(itr_dfs)
    quarter_data.to_csv(ITR_FILE, index=False)
