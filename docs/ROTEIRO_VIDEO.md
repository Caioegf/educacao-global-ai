# Roteiro do vídeo (5–10 min)

## 0:00 – 0:45 | Abertura
- "Esse é o Agente de Inteligência Global em Educação, construído sobre o World Bank Education Statistics."
- Problema: organização internacional precisa monitorar indicadores de 200+ países continuamente — não dá pra fazer análise manual toda semana.
- Solução: pipeline automatizado — Python + n8n + OpenAI + Skill.

## 0:45 – 2:00 | Arquitetura (mostrar o diagrama do README)
- Gatilho no n8n → pipeline Python → payload estruturado → IA → relatório salvo.
- Destacar: são 8 atividades Python (coleta, limpeza, interpolação de ausentes, crescimento, ranking, comparação, CSV final).

## 2:00 – 3:30 | Demonstração do pipeline (terminal)
- Rodar: `python src/pipeline.py --offline`
- Mostrar as saídas: `education_final.csv`, `ranking.csv`, `alerts.json`, gráficos PNG.
- Comentar 1 alerta real (ex.: Nigéria com gasto abaixo de 3% do PIB).

## 3:30 – 5:30 | Demonstração do n8n
- Mostrar o workflow importado: gatilho manual + agendamento semanal (bônus).
- Executar. Mostrar o nó de IA e o relatório salvo em `data/reports/`.
- Abrir o relatório: destacar que a IA NÃO resume números — ela explica causas, distingue estagnação boa (Finlândia no teto) de ruim, e dá recomendações.

## 5:30 – 7:00 | Insights (a parte que vale nota)
Escolher 2–3 insights do relatório gerado, por exemplo:
- Quem mais evoluiu no período e hipótese de causa.
- Investimento vs. resultado: país que gasta muito e rende pouco (e vice-versa).
- Alerta crítico e recomendação da IA.

## 7:00 – 8:30 | Skill + Claude Code
- Mostrar `skills/education-insights/SKILL.md` no GitHub: regras de análise e formato versionados.
- Mostrar a seção "Como o Claude Code foi utilizado" do README (citar o bug do pandas 3.0 como exemplo concreto).

## 8:30 – 9:30 | Bônus e fechamento
- Dashboard Streamlit rápido (seleção de países, ranking).
- Fechar: "de análise exploratória a produto de dados automatizado."
