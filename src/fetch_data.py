"""
Atividade Python #1: Coleta de dados educacionais do World Bank.

Busca indicadores da API pública do World Bank (mesma fonte do dataset
EdStats do Kaggle). Se estiver offline, usa a amostra local em data/raw/.

Uso:
    python src/fetch_data.py --countries BRA,USA,KOR --start 2000 --end 2023
"""

import argparse
import json
import os
import sys
import time

import pandas as pd

try:
    import requests
except ImportError:
    requests = None

# Indicadores selecionados (Atividade Python: seleção de indicadores)
INDICATORS = {
    "SE.ADT.LITR.ZS": "alfabetizacao_adultos_pct",
    "SE.XPD.TOTL.GD.ZS": "gasto_publico_educacao_pct_pib",
    "SE.PRM.ENRR": "matricula_primaria_bruta_pct",
    "SE.SEC.ENRR": "matricula_secundaria_bruta_pct",
    "SE.TER.ENRR": "matricula_terciaria_bruta_pct",
}

DEFAULT_COUNTRIES = ["BRA", "ARG", "CHL", "MEX", "USA", "KOR", "FIN", "PRT", "IND", "NGA"]

API_URL = "https://api.worldbank.org/v2/country/{countries}/indicator/{indicator}"

RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")


def fetch_indicator(indicator: str, countries: list[str], start: int, end: int) -> pd.DataFrame:
    """Busca um indicador na API do World Bank e retorna DataFrame tidy."""
    url = API_URL.format(countries=";".join(countries), indicator=indicator)
    params = {"format": "json", "date": f"{start}:{end}", "per_page": 2000}
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    payload = resp.json()
    if len(payload) < 2 or payload[1] is None:
        return pd.DataFrame()
    rows = [
        {
            "country_code": item["countryiso3code"],
            "country": item["country"]["value"],
            "year": int(item["date"]),
            "indicator_code": indicator,
            "value": item["value"],
        }
        for item in payload[1]
    ]
    return pd.DataFrame(rows)


def fetch_all(countries: list[str], start: int, end: int) -> pd.DataFrame:
    frames = []
    for code in INDICATORS:
        print(f"[fetch] {code} ...")
        frames.append(fetch_indicator(code, countries, start, end))
        time.sleep(0.3)  # respeitar rate limit
    df = pd.concat(frames, ignore_index=True)
    df["indicator"] = df["indicator_code"].map(INDICATORS)
    return df


def load_offline_sample() -> pd.DataFrame:
    path = os.path.join(RAW_DIR, "sample_worldbank_education.csv")
    if not os.path.exists(path):
        raise FileNotFoundError(
            "Sem internet e sem amostra local. Rode gen_sample_data.py ou conecte-se à rede."
        )
    print("[fetch] Modo offline: usando amostra local.")
    return pd.read_csv(path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--countries", default=",".join(DEFAULT_COUNTRIES))
    parser.add_argument("--start", type=int, default=2000)
    parser.add_argument("--end", type=int, default=2023)
    parser.add_argument("--offline", action="store_true", help="Força uso da amostra local")
    args = parser.parse_args()

    countries = [c.strip().upper() for c in args.countries.split(",")]

    if args.offline or requests is None:
        df = load_offline_sample()
        df = df[df["country_code"].isin(countries)]
    else:
        try:
            df = fetch_all(countries, args.start, args.end)
        except Exception as e:
            print(f"[fetch] Falha na API ({e}). Tentando amostra local...", file=sys.stderr)
            df = load_offline_sample()
            df = df[df["country_code"].isin(countries)]

    os.makedirs(RAW_DIR, exist_ok=True)
    out = os.path.join(RAW_DIR, "worldbank_education_raw.csv")
    df.to_csv(out, index=False)
    print(f"[fetch] {len(df)} linhas salvas em {out}")
    print(json.dumps({"rows": len(df), "countries": countries}, ensure_ascii=False))


if __name__ == "__main__":
    main()
