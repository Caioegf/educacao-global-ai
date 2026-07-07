"""
Gera uma amostra local (data/raw/sample_worldbank_education.csv) com valores
plausíveis baseados nas séries reais do World Bank, permitindo rodar o
pipeline offline (útil para testes e correção do professor).
"""

import os

import numpy as np
import pandas as pd

RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")

# (país, nome, alfabetização~2020, gasto %PIB~2020, matr. prim., sec., terc.)
BASE = {
    "BRA": ("Brazil", 93.2, 6.0, 113.0, 105.0, 55.0),
    "ARG": ("Argentina", 99.0, 4.8, 109.0, 108.0, 95.0),
    "CHL": ("Chile", 96.4, 5.6, 100.0, 100.0, 91.0),
    "MEX": ("Mexico", 95.2, 4.3, 104.0, 87.0, 43.0),
    "USA": ("United States", 99.0, 5.4, 101.0, 99.0, 88.0),
    "KOR": ("Korea, Rep.", 98.8, 4.7, 98.0, 98.0, 98.0),
    "FIN": ("Finland", 100.0, 6.4, 100.0, 118.0, 90.0),
    "PRT": ("Portugal", 96.8, 4.9, 104.0, 118.0, 68.0),
    "IND": ("India", 74.4, 4.5, 100.0, 74.0, 29.0),
    "NGA": ("Nigeria", 62.0, 1.8, 85.0, 44.0, 10.0),
}

INDICATORS = {
    "SE.ADT.LITR.ZS": ("alfabetizacao_adultos_pct", 2),
    "SE.XPD.TOTL.GD.ZS": ("gasto_publico_educacao_pct_pib", 3),
    "SE.PRM.ENRR": ("matricula_primaria_bruta_pct", 4),
    "SE.SEC.ENRR": ("matricula_secundaria_bruta_pct", 5),
    "SE.TER.ENRR": ("matricula_terciaria_bruta_pct", 6),
}

# tendência anual aproximada por país (países em desenvolvimento melhoram mais rápido)
TREND = {"BRA": 0.45, "ARG": 0.1, "CHL": 0.3, "MEX": 0.35, "USA": 0.05,
         "KOR": 0.15, "FIN": 0.02, "PRT": 0.25, "IND": 0.9, "NGA": 0.5}


def main():
    rng = np.random.default_rng(42)
    rows = []
    years = range(2000, 2024)
    for code, vals in BASE.items():
        name = vals[0]
        for ind_code, (ind_name, idx) in INDICATORS.items():
            v2020 = vals[idx - 1]
            for year in years:
                # valor retrocede a partir de 2020 conforme a tendência do país
                drift = TREND[code] * (year - 2020) * (0.5 if idx == 2 else 1.0)
                value = v2020 + drift + rng.normal(0, 0.4)
                value = float(np.clip(value, 0, 100 if idx in (1,) else 130))
                # simula valores ausentes (~12%), como no dataset real
                if rng.random() < 0.12:
                    value = None
                rows.append({
                    "country_code": code,
                    "country": name,
                    "year": year,
                    "indicator_code": ind_code,
                    "indicator": ind_name,
                    "value": round(value, 2) if value is not None else None,
                })
    df = pd.DataFrame(rows)
    os.makedirs(RAW_DIR, exist_ok=True)
    out = os.path.join(RAW_DIR, "sample_worldbank_education.csv")
    df.to_csv(out, index=False)
    print(f"[sample] {len(df)} linhas salvas em {out}")


if __name__ == "__main__":
    main()
