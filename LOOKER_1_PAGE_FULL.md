# 📊 LOOKER STUDIO - 1 PÁGINA COMPLETA

## 📝 NOME DO RELATÓRIO

**Use este nome exato:**

```
Olympic Games Analytics 2026
```

Clica no título "Relatório sem título" no topo e digita isso!

---

## 📄 PÁGINA ÚNICA: OLYMPIC GAMES ANALYTICS

Todos os dados em 1 página épica!

---

### ROW 1: KPI Cards (4 cards em linha)

#### Card 1: Total Athletes
```
Insert → Scorecard
- Metric: COUNT(athlete_id)
- Title: "Total Athletes"
- Big number: ON
```

#### Card 2: Gold Medals
```
Insert → Scorecard
- Metric: COUNTIF(medal="Gold")
- Title: "Gold Medals"
- Big number: ON
- Color: Gold (#FFD700)
```

#### Card 3: Nations
```
Insert → Scorecard
- Metric: COUNT_DISTINCT(country)
- Title: "Nations"
- Big number: ON
- Color: Green
```

#### Card 4: Sports
```
Insert → Scorecard
- Metric: COUNT_DISTINCT(sport)
- Title: "Sports"
- Big number: ON
- Color: Purple
```

---

### ROW 2: Visualizações Principais (3 gráficos)

#### Viz 1: Medal Count by Country
```
Insert → Bar chart
- Dimension: country
- Metric: COUNT(athlete_id)
- Sort: Descending
- Title: "Medal Count by Country"
- Width: ~33%
```

#### Viz 2: Sports Distribution
```
Insert → Pie chart
- Dimension: sport
- Metric: COUNT(athlete_id)
- Title: "Sports Distribution"
- Show legend: ON
- Width: ~33%
```

#### Viz 3: Athletes Timeline
```
Insert → Line chart
- Dimension: year
- Metric: COUNT(athlete_id)
- Title: "Athletes Over Time"
- Width: ~33%
```

---

### ROW 3: Table with All Data

#### Athletes Full Table
```
Insert → Table
- Dimensions: name, country, sport, medal, year
- Sort: year DESC
- Pagination: ON
- Title: "Complete Athletes Directory"
- Full width (100%)
```

---

## ✅ RESUMO FINAL

**1 PÁGINA | 8 VISUALIZAÇÕES:**
- ✅ 4 KPI Cards (Total, Gold, Nations, Sports)
- ✅ Bar Chart (Countries)
- ✅ Pie Chart (Sports)
- ✅ Line Chart (Timeline)
- ✅ Full Data Table

---

## 🎯 LAYOUT

```
┌────────┬────────┬────────┬────────┐
│ 5      │ 5 Gold │ 3      │ 4      │
│Athletes│        │Nations │ Sports │
├────────┴────────┴────────┴────────┤
│ Countries (33%) │ Sports (33%) │ Timeline (33%)
├─────────────────────────────────────┤
│ Complete Athletes Directory (100%)  │
│                                     │
│ name│country│sport│medal│year      │
└─────────────────────────────────────┘
```

---

## ⏱️ TEMPO TOTAL: 7 MINUTOS

1. Renomear relatório: 1 min
2. Adicionar 4 KPI Cards: 2 min
3. Adicionar 3 gráficos: 2 min
4. Adicionar tabela final: 1 min
5. Organizar layout: 1 min

---

## 🚀 PRÓXIMOS PASSOS

Quando terminar:
1. ✅ Share o dashboard
2. ✅ Ir para **GitHub Actions** (próxima task FREE!)

---

**VAMOS LÁ! 💪**
