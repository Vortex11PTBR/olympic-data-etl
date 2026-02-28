# 🎨 LOOKER STUDIO DASHBOARD - STEP BY STEP

## LOGIN
Email: `joaopedroantuneslacerda7@gmail.com`

---

## PASSO 1: Criar Report (1 minuto)
```
1. Clique em "Create" (canto superior esquerdo)
2. Selecione "Report"
3. Escolha "Blank"
```

---

## PASSO 2: Conectar BigQuery (2 minutos)
```
1. Clique em "Create new data source" (ou + icon)
2. Escolha "BigQuery"
3. Autorize sua conta Google (vai pedir permissão)
4. Depois de autorizar:
   - Project: my-olympic-etl
   - Dataset: olympics_dataset
   - Table: athletes
5. Clique "Create"
```

---

## PASSO 3: Criar Visualizações (2 minutos cada)

### VIZ 1: Scorecard - Total Athletes ⭐
```
Menu: Insert → Scorecard

Na aba direita:
- Data Source: athletes (BigQuery)
- Metric: COUNT → athlete_id

Na aba Style:
- Title: "Total Athletes"
- Number format: #,###
- Big number: ON
```

### VIZ 2: Scorecard - Countries 🌍
```
Menu: Insert → Scorecard

Na aba direita:
- Data Source: athletes
- Metric: COUNT_DISTINCT → country

Na aba Style:
- Title: "Countries"
```

### VIZ 3: Bar Chart - Athletes by Country 📊
```
Menu: Insert → Bar chart

Na aba direita:
- Data Source: athletes
- Dimension: country
- Metric: COUNT(athlete_id)

Na aba Style:
- Title: "Athletes by Country"
- Sort: Descending (by count)
```

### VIZ 4: Pie Chart - Sports 🥧
```
Menu: Insert → Pie chart

Na aba direita:
- Data Source: athletes
- Dimension: sport
- Metric: COUNT(athlete_id)

Na aba Style:
- Title: "Sports Distribution"
- Show legend: ON
```

### VIZ 5: Table - All Athletes 📋
```
Menu: Insert → Table

Na aba direita:
- Data Source: athletes
- Dimensions: name, country, sport, medal, year

Na aba Style:
- Title: "All Athletes"
- Enable pagination: ON
```

---

## PASSO 4: Finalizar (1 minuto)

### Dar nome ao relatório:
```
File → Rename
Nome: "Olympic Athletes Dashboard"
```

### Compartilhar:
```
Share (canto superior direito)
→ Change to "Anyone with the link"
→ Copy link e salve
```

---

## ✅ RESULTADO ESPERADO

Dashboard com:
- ✅ 2 números grandes (5 atletas, 3 países)
- ✅ 1 gráfico de barras dinamicamente sortido
- ✅ 1 pizza colorida com 4 esportes
- ✅ 1 tabela filtrable com 5 atletas
- ✅ Todos os dados conectados ao BigQuery
- ✅ Atualizações em tempo real

---

## 💡 DICAS

**Se der erro "Table not found":**
- Volte para Passo 2
- Verifique: my-olympic-etl.olympics_dataset.athletes
- Tente fazer refresh no BigQuery

**Se os dados não aparecerem:**
- Clique em "Refresh data" (circular icon)
- Aguarde 5 segundos
- Se ainda não aparecer, volte para Passo 2

**Para personalizar cores:**
- Selecione cada gráfico
- Aba direita → Setup → Theme
- Escolha cores

---

## 🎯 TEMPO TOTAL: 5-7 MINUTOS

✅ Dashboard ao vivo
✅ Com dados reais do BigQuery
✅ Atualizações automáticas
✅ 100% Grátis

Let's go! 🚀
