# LOOKER STUDIO - SETUP RÁPIDO (5 MIN)

## Passo 1: Abrir Looker Studio
```
https://lookerstudio.google.com
```
- Login com: `joaopedroantuneslacerda7@gmail.com`

## Passo 2: Nova Report
```
Clique: Create → New report
```

## Passo 3: Conectar BigQuery
```
1. Clique: "Create new data source"
2. Selecione: "BigQuery"
3. Autorize sua conta
4. Escolha:
   - Project: my-olympic-etl
   - Dataset: olympics_dataset
   - Table: athletes
5. Clique: "Create"
```

## Passo 4: Dashboard (Copy-Paste pronto!)

### Card 1: Total Atletas
```
Insert → Scorecard
- Metric: COUNT(athlete_id)
- Title: "Total Athletes"
```

### Card 2: Total Países
```
Insert → Scorecard
- Metric: COUNT_DISTINCT(country)
- Title: "Countries"
```

### Card 3: Atletas por País
```
Insert → Bar Chart
- Dimension: country
- Metric: COUNT(athlete_id)
- Title: "Athletes by Country"
```

### Card 4: Esportes
```
Insert → Pie Chart
- Dimension: sport
- Metric: COUNT(athlete_id)
- Title: "Sports Distribution"
```

### Card 5: Tabela Completa
```
Insert → Table
- Columns: name, country, sport, medal, year
- Title: "All Athletes"
```

## Passo 5: Finalizar
```
File → Name: "Olympic Athletes Dashboard"
Share → Get shareable link
```

✅ **Pronto! Dashboard dinâmico no ar!**

Tempo: 5 min
Custo: $0
Live Data: ✅
