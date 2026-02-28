# 📊 LOOKER STUDIO - 4 PÁGINAS EXTRAS (QUICK MODE - 3 MIN)

## PÁGINA 1: Análise por País 🌍 (1 min)

**Nova página:** File → New page → Rename para "By Country"

### Viz 1: Top Countries (Card)
```
Insert → Scorecard
- Metric: COUNT_DISTINCT(country)
- Title: "Total Countries"
- Number format: 0
```

### Viz 2: Medalhas por País
```
Insert → Bar chart
- Dimension: country
- Metric: COUNT(athlete_id)
- Sort: Descending
- Title: "Medal Count by Country"
```

### Viz 3: Distribuição USA
```
Insert → Pie chart
- Dimension: sport
- Metric: COUNT(athlete_id)
- Filter: country = "USA"
- Title: "USA Athletes by Sport"
```

---

## PÁGINA 2: Timeline 📈 (1 min)

**Nova página:** File → New page → Rename para "Timeline"

### Viz 1: Atletas por Ano
```
Insert → Line chart
- Dimension: year
- Metric: COUNT(athlete_id)
- Title: "Athletes Over Time"
- X-axis: year (ascending)
- Y-axis: count
```

### Viz 2: Card - Anos Cobertos
```
Insert → Scorecard
- Metric: COUNT_DISTINCT(year)
- Title: "Years in Dataset"
```

### Viz 3: Histórico de Medalhas
```
Insert → Table
- Dimensions: year, country, name, medal
- Sort by: year DESC
- Title: "Medal History"
- Pagination: ON
```

---

## PÁGINA 3: Análise por Esporte ⚽ (1 min)

**Nova página:** File → New page → Rename para "By Sport"

### Viz 1: Total Esportes
```
Insert → Scorecard
- Metric: COUNT_DISTINCT(sport)
- Title: "Total Sports"
```

### Viz 2: Atletas por Esporte
```
Insert → Bar chart
- Dimension: sport
- Metric: COUNT(athlete_id)
- Sort: Descending
- Title: "Athletes by Sport"
```

### Viz 3: Distribuição Detalhada
```
Insert → Table
- Dimensions: sport, country, name, medal
- Filter: sort by sport
- Title: "Sport Details"
- Pagination: ON
```

---

## PÁGINA 4: Dashboard Executivo 👔 (1 min)

**Nova página:** File → New page → Rename para "Executive Summary"

### Viz 1: KPI - Total Athletes
```
Insert → Scorecard
- Metric: COUNT(athlete_id)
- Title: "Total Athletes"
- Big: ON
```

### Viz 2: KPI - Gold Medals
```
Insert → Scorecard
- Metric: COUNTIF(medal="Gold")
- Title: "Gold Medals"
- Color: Gold
```

### Viz 3: KPI - Countries
```
Insert → Scorecard
- Metric: COUNT_DISTINCT(country)
- Title: "Nations"
```

### Viz 4: KPI - Sports
```
Insert → Scorecard
- Metric: COUNT_DISTINCT(sport)
- Title: "Sports"
```

### Viz 5: Top Country Card
```
Insert → Tile
- Dimension: country
- Metric: COUNT(athlete_id)
- Limit: 1
- Title: "Top Country"
```

### Viz 6: Summary Table
```
Insert → Table
- Dimensions: country, sport, COUNT(athlete_id) as athletes
- Group by: country, sport
- Title: "Country-Sport Matrix"
```

---

## ✅ RESULTADO FINAL

5 Páginas no Dashboard:
1. ✅ Overview (original)
2. ✅ By Country (análises por país)
3. ✅ Timeline (histórico temporal)
4. ✅ By Sport (análises por esporte)
5. ✅ Executive Summary (KPIs)

**BONUS:**
- Cada página tem 3-6 visualizações
- Todos os dados conectados ao BigQuery
- Totalmente interativo
- Atualizações em tempo real
- 100% Grátis

---

## 🎨 DICAS FINAIS

### Adicionar filtros globais:
```
Insert → Date/Time or Dropdown filter
- Dimension: country (ou year ou sport)
- Apply to all pages
- Title: "Filter by..."
```

### Personalizar cores:
```
Selecione qualquer gráfico
→ Style tab
→ Theme: escolha cores
```

### Compartilhar:
```
Share (canto superior direito)
→ Get link
→ Set "Anyone with the link"
```

---

## ⏱️ TIMING TOTAL

- Página 1 (By Country): 1 min
- Página 2 (Timeline): 1 min
- Página 3 (By Sport): 1 min
- Página 4 (Executive): 1 min
- **TOTAL: 4 minutos**

---

## 🎉 RESULTADO

Dashboard ÉPICO com 5 páginas, 20+ visualizações, dados em tempo real, 100% FREE!

Let's go! 🚀
