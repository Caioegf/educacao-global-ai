"""
Pipeline completo (chamado pelo n8n via Execute Command).

Etapas: coleta -> limpeza -> análise -> gráficos -> payload para IA.

Gera:
- data/processed/education_final.csv  (CSV final consolidado)
- data/processed/ai_payload.json      (resumo estruturado p/ prompt da IA)

Uso:
    python src/pipeline.py --countries BRA,USA,KOR --offline
"""

import argparse
import json
import os
import subprocess
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, "..", "data")


def run_step(script: str, extra: list[str] | None = None):
    cmd = [sys.executable, os.path.join(HERE, script)] + (extra or [])
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        raise RuntimeError(f"Falha em {script}")


def build_final_csv() -> pd.DataFrame:
    """Atividade Python #8: geração do CSV final consolidado."""
    clean = pd.read_csv(os.path.join(DATA_DIR, "processed", "education_clean.csv"))
    growth = pd.read_csv(os.path.join(DATA_DIR, "processed", "growth.csv"))
    final = clean.merge(
        growth[["country_code", "indicator", "abs_change", "pct_change", "avg_annual_change"]],
        on=["country_code", "indicator"], how="left",
    )
    out = os.path.join(DATA_DIR, "processed", "education_final.csv")
    final.to_csv(out, index=False)
    print(f"[pipeline] CSV final: {out} ({len(final)} linhas)")
    return final


def build_ai_payload():
    """Monta um resumo compacto e estruturado para alimentar o prompt da IA."""
    processed = os.path.join(DATA_DIR, "processed")
    growth = pd.read_csv(os.path.join(processed, "growth.csv"))
    ranking = pd.read_csv(os.path.join(processed, "ranking.csv"))
    comparison = pd.read_csv(os.path.join(processed, "comparison.csv"))
    with open(os.path.join(processed, "alerts.json"), encoding="utf-8") as f:
        alerts = json.load(f)

    top_evolucao = (
        growth.sort_values("abs_change", ascending=False)
        .groupby("indicator").head(3)
        [["indicator", "country", "first_year", "last_year", "first_value",
          "last_value", "abs_change", "pct_change"]]
        .to_dict(orient="records")
    )
    estagnados = (
        growth[growth["abs_change"].abs() < 1.0]
        [["indicator", "country", "abs_change"]]
        .to_dict(orient="records")
    )

    payload = {
        "periodo": f"{int(growth['first_year'].min())}-{int(growth['last_year'].max())}",
        "paises": sorted(comparison["country"].tolist()),
        "comparacao_ultimo_ano": comparison.to_dict(orient="records"),
        "maiores_evolucoes": top_evolucao,
        "series_estagnadas": estagnados,
        "ranking_valor_atual": ranking[
            ["indicator", "country", "last_value", "rank_valor_atual", "rank_evolucao"]
        ].to_dict(orient="records"),
        "alertas": alerts,
    }
    out = os.path.join(processed, "ai_payload.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"[pipeline] payload da IA: {out}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--countries", default=None)
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args()

    fetch_args = []
    if args.countries:
        fetch_args += ["--countries", args.countries]
    if args.offline:
        fetch_args += ["--offline"]

    run_step("fetch_data.py", fetch_args)
    run_step("clean_data.py")
    run_step("analyze.py")
    run_step("charts.py")
    build_final_csv()
    build_ai_payload()
    print("[pipeline] concluído com sucesso ✔")


if __name__ == "__main__":
    main()
