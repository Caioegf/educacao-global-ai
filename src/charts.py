"""
Bônus: geração automática de gráficos (PNG) a partir dos dados processados.
"""

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
REPORTS = os.path.join(DATA_DIR, "reports")


def line_by_country(df: pd.DataFrame, indicator: str, out: str):
    sub = df[df["indicator"] == indicator]
    if sub.empty:
        return
    fig, ax = plt.subplots(figsize=(10, 5.5))
    for country, g in sub.groupby("country"):
        g = g.sort_values("year")
        ax.plot(g["year"], g["value"], label=country, linewidth=1.8)
    ax.set_title(indicator.replace("_", " ").title())
    ax.set_xlabel("Ano")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8, ncol=2)
    fig.tight_layout()
    fig.savefig(out, dpi=120)
    plt.close(fig)


def bar_ranking(ranking: pd.DataFrame, indicator: str, out: str):
    sub = ranking[ranking["indicator"] == indicator].sort_values("last_value")
    if sub.empty:
        return
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.barh(sub["country"], sub["last_value"], color="#2b6cb0")
    ax.set_title(f"Ranking atual — {indicator.replace('_', ' ')}")
    ax.grid(axis="x", alpha=0.3)
    fig.tight_layout()
    fig.savefig(out, dpi=120)
    plt.close(fig)


def main():
    os.makedirs(REPORTS, exist_ok=True)
    df = pd.read_csv(os.path.join(DATA_DIR, "processed", "education_clean.csv"))
    ranking = pd.read_csv(os.path.join(DATA_DIR, "processed", "ranking.csv"))

    for ind in df["indicator"].unique():
        line_by_country(df, ind, os.path.join(REPORTS, f"serie_{ind}.png"))
    bar_ranking(ranking, "alfabetizacao_adultos_pct",
                os.path.join(REPORTS, "ranking_alfabetizacao.png"))
    bar_ranking(ranking, "gasto_publico_educacao_pct_pib",
                os.path.join(REPORTS, "ranking_gasto.png"))
    print(f"[charts] gráficos salvos em {REPORTS}")


if __name__ == "__main__":
    main()
