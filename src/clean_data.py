"""
Atividades Python #2 e #3: Limpeza de dados e tratamento de valores ausentes.

- Remove duplicatas e linhas inválidas
- Padroniza tipos
- Trata valores ausentes com interpolação linear por país/indicador
  (comum em séries temporais do World Bank, que têm lacunas de coleta)
"""

import os

import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Limpeza básica: tipos, duplicatas, linhas sem identificação."""
    df = df.copy()
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna(subset=["country_code", "indicator", "year"])
    df = df.drop_duplicates(subset=["country_code", "indicator", "year"], keep="last")
    return df.sort_values(["country_code", "indicator", "year"]).reset_index(drop=True)


def treat_missing(df: pd.DataFrame) -> pd.DataFrame:
    """
    Interpolação linear por (país, indicador) + preenchimento nas bordas.
    Marca a coluna `imputed` para transparência analítica.
    """
    df = df.copy()
    df["imputed"] = df["value"].isna()
    df = df.sort_values(["country_code", "indicator", "year"])
    df["value"] = (
        df.groupby(["country_code", "indicator"])["value"]
        .transform(lambda s: s.interpolate(method="linear", limit_direction="both"))
    )
    df = df.reset_index(drop=True)
    # se um país nunca reportou o indicador, descarta a série
    df = df.dropna(subset=["value"]).reset_index(drop=True)
    return df


def main():
    raw_path = os.path.join(DATA_DIR, "raw", "worldbank_education_raw.csv")
    df = pd.read_csv(raw_path)
    before = len(df)
    df = clean(df)
    missing_before = int(df["value"].isna().sum())
    df = treat_missing(df)

    out = os.path.join(DATA_DIR, "processed", "education_clean.csv")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    df.to_csv(out, index=False)
    print(f"[clean] {before} -> {len(df)} linhas | {missing_before} ausentes tratados")
    print(f"[clean] salvo em {out}")


if __name__ == "__main__":
    main()
