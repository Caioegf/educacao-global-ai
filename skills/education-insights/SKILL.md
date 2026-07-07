---
name: education-insights
description: Gera análises executivas de indicadores educacionais do World Bank (EdStats). Use esta skill sempre que o usuário pedir insights, relatórios, comparações entre países, rankings, explicações de tendências ou recomendações de política educacional a partir dos dados processados deste projeto (arquivo data/processed/ai_payload.json), mesmo que ele não use a palavra "relatório" — por exemplo "quais países evoluíram mais?", "o Brasil está bem em educação?", "resuma os dados".
---

# Education Insights

Skill para transformar os dados processados do pipeline (World Bank EdStats)
em **inteligência executiva** — não apenas resumo de números.

## Entrada

Ler `data/processed/ai_payload.json`, que contém:
- `comparacao_ultimo_ano`: valores mais recentes por país/indicador
- `maiores_evolucoes`: top 3 países por evolução em cada indicador
- `series_estagnadas`: séries com variação < 1 ponto no período
- `ranking_valor_atual`: posição de cada país (valor atual e evolução)
- `alertas`: indicadores que violaram limites críticos

## Regras de análise (obrigatórias)

1. **Nunca apenas resumir números.** Toda métrica citada deve vir acompanhada
   de interpretação: o que significa, por que provavelmente aconteceu, o que fazer.
2. Identificar explicitamente:
   - países que **mais evoluíram** (e hipóteses de causa: investimento, demografia,
     políticas conhecidas — ex.: FUNDEB no Brasil, reformas na Coreia)
   - países **estagnados** (distinguir estagnação em nível alto — ex.: Finlândia
     com alfabetização ~100% — de estagnação problemática em nível baixo)
   - relação entre **gasto público (% PIB)** e resultados: apontar países com
     alto gasto e baixo retorno, e vice-versa
3. Tratar **alertas** como prioridade: abrir o relatório por eles se existirem.
4. Fornecer **recomendações acionáveis** por país em situação crítica
   (2–3 recomendações, específicas, não genéricas).
5. Declarar limitações: dados imputados por interpolação, defasagem de coleta
   do World Bank, correlação ≠ causalidade.

## Formato de saída

Markdown com esta estrutura exata:

```
# Relatório de Inteligência Educacional — {período}
## 🚨 Alertas críticos
## 📈 Destaques de evolução
## 🧊 Estagnação e riscos
## 💰 Investimento vs. resultado
## 🌎 Comparação entre países selecionados
## ✅ Recomendações
## ⚠️ Limitações da análise
```

Tom: executivo, direto, para tomadores de decisão de uma organização
internacional. Máximo ~800 palavras.

## Recursos

- `references/prompt_openai.md`: prompt pronto para uso via API da OpenAI
  (é o mesmo prompt usado pelo nó de IA no workflow do n8n).
