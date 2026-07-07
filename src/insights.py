"""
Chamada à IA (OpenAI) para gerar o relatório executivo.

Pode ser executado direto (CLI) ou pelo n8n. Usa o mesmo prompt versionado
na Skill (skills/education-insights/references/prompt_openai.md).

Requer: variável de ambiente OPENAI_API_KEY.

Uso:
    python src/insights.py
"""

import json
import os
import sys
from datetime import date

import requests

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, "..", "data")

SYSTEM_PROMPT = (
    "Você é um analista sênior de política educacional de uma organização "
    "internacional. Você recebe dados processados do World Bank Education "
    "Statistics e produz relatórios executivos. Você NUNCA apenas resume "
    "números: toda métrica citada vem com interpretação, hipótese de causa e "
    "implicação prática. Distinga estagnação em nível alto (teto atingido) de "
    "estagnação problemática. Relacione investimento público (% PIB) com "
    "resultados, apontando eficiência e ineficiência. Declare limitações "
    "(dados interpolados, defasagem de coleta, correlação ≠ causalidade). "
    "Escreva em português, tom executivo, máximo 800 palavras, em Markdown, "
    "com as seções: Alertas críticos; Destaques de evolução; Estagnação e "
    "riscos; Investimento vs. resultado; Comparação entre países; "
    "Recomendações; Limitações da análise."
)


def main():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Defina OPENAI_API_KEY.", file=sys.stderr)
        sys.exit(1)

    payload_path = os.path.join(DATA_DIR, "processed", "ai_payload.json")
    with open(payload_path, encoding="utf-8") as f:
        data = f.read()

    resp = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "model": os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
            "temperature": 0.4,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Analise os dados e produza o relatório:\n\n{data}"},
            ],
        },
        timeout=120,
    )
    resp.raise_for_status()
    report = resp.json()["choices"][0]["message"]["content"]

    out_dir = os.path.join(DATA_DIR, "reports")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, f"relatorio_{date.today().isoformat()}.md")
    with open(out, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"[insights] relatório salvo em {out}")


if __name__ == "__main__":
    main()
