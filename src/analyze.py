"""
Atividades Python #4 a #7:
- Agregações por país/indicador
- Cálculo de crescimento (variação absoluta e % no período)
- Ranking de países por indicador
- Comparação entre países (tabela pivô do último ano disponível)

Também gera alertas quando indicadores ultrapassam limites (bônus).
"""

import json
import os

import numpy as np
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

# Bônus: limites de alerta (indicador -> (limite, direção))
ALERT_THRESHOLDS = {
    "alfabetizacao_adultos_pct": (80.0, "below"),
    "gasto_publico_educacao_pct_pib": (3.0, "below"),
    "matricula_secundaria_bruta_pct": (60.0, "below"),
}


def compute_growth(df: pd.DataFrame) -> pd.DataFrame:
    """Crescimento por (país, indicador): primeiro vs. último ano da série."""
    def _g(group: pd.DataFrame) -> pd.Series:
        group = group.sort_values("year")
        first, last = group.iloc[0], group.iloc[-1]
        span = int(last["year"] - first["year"]) or 1
        abs_change = last["value"] - first["value"]
        pct_change = (abs_change / first["value"] * 100) if first["value"] else np.nan
        return pd.Series({
            "first_year": int(first["year"]),
            "last_year": int(last["year"]),
            "first_value": round(float(first["value"]), 2),
            "last_value": round(float(last["value"]), 2),
            "abs_change": round(float(abs_change), 2),
            "pct_change": round(float(pct_change), 2),
            "avg_annual_change": round(float(abs_change) / span, 3),
        })

    return (
        df.groupby(["country_code", "country", "indicator"])
        .apply(_g)
        .reset_index()
    )


def build_ranking(growth: pd.DataFrame) -> pd.DataFrame:
    """Ranking por indicador: valor atual e evolução no período."""
    ranking = growth.copy()
    ranking["rank_valor_atual"] = (
        ranking.groupby("indicator")["last_value"].rank(ascending=False, method="min").astype(int)
    )
    ranking["rank_evolucao"] = (
        ranking.groupby("indicator")["abs_change"].rank(ascending=False, method="min").astype(int)
    )
    return ranking.sort_values(["indicator", "rank_valor_atual"]).reset_index(drop=True)


def build_comparison(df: pd.DataFrame) -> pd.DataFrame:
    """Comparação entre países: pivô com o último valor de cada indicador."""
    last = (
        df.sort_values("year")
        .groupby(["country_code", "country", "indicator"])
        .tail(1)
    )
    pivot = last.pivot_table(
        index=["country_code", "country"],
        columns="indicator",
        values="value",
        aggfunc="first",
    ).round(2).reset_index()
    pivot.columns.name = None
    return pivot


def build_alerts(df: pd.DataFrame) -> list[dict]:
    """Bônus: alerta quando o último valor viola o limite configurado."""
    alerts = []
    last = df.sort_values("year").groupby(["country_code", "indicator"]).tail(1)
    for _, row in last.iterrows():
        rule = ALERT_THRESHOLDS.get(row["indicator"])
        if not rule:
            continue
        limit, direction = rule
        breached = row["value"] < limit if direction == "below" else row["value"] > limit
        if breached:
            alerts.append({
                "country": row["country"],
                "indicator": row["indicator"],
                "year": int(row["year"]),
                "value": round(float(row["value"]), 2),
                "threshold": limit,
                "rule": f"valor {'abaixo' if direction == 'below' else 'acima'} de {limit}",
            })
    return alerts


def main():
    df = pd.read_csv(os.path.join(DATA_DIR, "processed", "education_clean.csv"))

    growth = compute_growth(df)
    ranking = build_ranking(growth)
    comparison = build_comparison(df)
    alerts = build_alerts(df)

    processed = os.path.join(DATA_DIR, "processed")
    growth.to_csv(os.path.join(processed, "growth.csv"), index=False)
    ranking.to_csv(os.path.join(processed, "ranking.csv"), index=False)
    comparison.to_csv(os.path.join(processed, "comparison.csv"), index=False)
    with open(os.path.join(processed, "alerts.json"), "w", encoding="utf-8") as f:
        json.dump(alerts, f, ensure_ascii=False, indent=2)

    print(f"[analyze] growth={len(growth)} ranking={len(ranking)} "
          f"comparison={len(comparison)} alerts={len(alerts)}")


if __name__ == "__main__":
    main()
