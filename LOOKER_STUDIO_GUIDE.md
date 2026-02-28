# Dashboard Looker Studio - Quick Setup

## 1. Conectar BigQuery ao Looker Studio

```
1. Abra: https://lookerstudio.google.com
2. Clique em "Create" → "New report"
3. Clique em "Create new data source"
4. Selecione "BigQuery"
5. Autorize sua conta Google
6. Selecione:
   - Project: my-olympic-etl
   - Dataset: olympics_dataset
   - Table: athletes
7. Clique "Create"
```

## 2. Criar Visualizações

**Scorecard - Total Atletas:**
- Métrica: COUNT(athlete_id)
- Título: "Total Athletes"

**Scorecard - Países:**
- Métrica: COUNT(DISTINCT country)
- Título: "Countries"

**Bar Chart - Medalhas por País:**
- Dimensão: country
- Métrica: COUNT(athlete_id)
- Título: "Athletes by Country"

**Pie Chart - Esportes:**
- Dimensão: sport
- Métrica: COUNT(athlete_id)
- Título: "Athletes by Sport"

**Table - Todos os Atletas:**
- Colunas: name, country, sport, medal, year
- Título: "All Athletes"

## 3. Treinos

- Clique em "Share" para compartilhar o dashboard
- Salve como: "Olympic Athletes Dashboard"
- Personalize cores e formato

## 4. Resultado
Dashboard interativo com dados em tempo real do BigQuery!

Tempo: ~5 minutos
Custo: $0
