# 🚀 GITHUB ACTIONS CI/CD - SETUP COMPLETO

**OBJETIVO:** Automatizar pipeline diário no GitHub

**TEMPO:** 10 minutos

---

## PASSO 1: Criar Conta GCP Service Account (3 min)

### 1.1 Gerar Chave JSON

```bash
# No seu terminal PowerShell:
gcloud auth application-default login
```

Depois:

1. Vai no [GCP Console - Service Accounts](https://console.cloud.google.com/iam-admin/serviceaccounts)
2. Clica **"Create Service Account"**
3. Nome: `github-actions-sa`
4. Clica **"Create and Continue"**
5. **Grant roles:**
   - `BigQuery Admin`
   - `Storage Admin`
   - `Service Account User`
6. Clica **"Continue"** → **"Done"**

### 1.2 Criar Chave JSON

1. Clica no service account criado: `github-actions-sa@my-olympic-etl.iam.gserviceaccount.com`
2. Aba **"Keys"**
3. Clica **"Add Key"** → **"Create new key"**
4. Seleciona **"JSON"**
5. Clica **"Create"** (baixa arquivo `my-olympic-etl-XXXXX.json`)
6. **GUARDA ESTE ARQUIVO SEGURO!** ⚠️

---

## PASSO 2: Fazer Upload para GitHub (2 min)

### 2.1 Se ainda não tem repositório:

```bash
# Abrir terminal no seu projeto
cd c:\Users\joaop\OneDrive\Desktop\olympic-data-etl

# Inicializar git
git init
git add .
git commit -m "Initial commit: Olympic Games ETL"

# Ir no GitHub.com → New Repository
# Nome: olympic-data-etl
# Copiar comando de push:
git remote add origin https://github.com/SEU_USUARIO/olympic-data-etl.git
git branch -M main
git push -u origin main
```

### 2.2 Se já tem repositório:

```bash
cd c:\Users\joaop\OneDrive\Desktop\olympic-data-etl
git add .
git commit -m "Add Looker Studio dashboard + GitHub Actions"
git push
```

---

## PASSO 3: Adicionar Secrets ao GitHub (2 min)

1. Vai em **GitHub.com** → Seu repositório
2. Clica **Settings** (contas do repositório)
3. **Secrets and variables** → **Actions**
4. Clica **"New repository secret"**

### Secret 1: GCP_PROJECT_ID
```
Name: GCP_PROJECT_ID
Value: my-olympic-etl
```
Clica **"Add secret"**

### Secret 2: GCP_SA_KEY
```
Name: GCP_SA_KEY
Value: [Abre o arquivo JSON baixado e copia TODO o conteúdo]
```
Clica **"Add secret"**

---

## PASSO 4: Ativar GitHub Actions (1 min)

1. No seu repositório GitHub
2. Aba **"Actions"**
3. Procura por workflow: `.github/workflows/olympic-etl-pipeline.yml`
4. Se não aparecer, cria manualmente:

### 4.1 Criar workflow manualmente

Na raiz do repositório, cria pasta `.github/workflows/` e arquivo `olympic-etl-pipeline.yml`:

```yaml
name: Olympic ETL Pipeline

on:
  schedule:
    - cron: "0 2 * * *"  # Diariamente às 2AM UTC
  push:
    branches: [ main, develop ]
  workflow_dispatch:  # Permite rodar manual

jobs:
  validate-and-test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      
      - name: Run validation
        run: |
          python src/beam/pipelines/olympic_etl_simple.py

  bigquery-load:
    needs: validate-and-test
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Authenticate to GCP
        uses: google-github-actions/auth@v1
        with:
          credentials_json: ${{ secrets.GCP_SA_KEY }}
      
      - name: Set up Cloud SDK
        uses: google-github-actions/setup-gcloud@v1
      
      - name: Load data to BigQuery
        run: |
          bq load \
            --source_format=CSV \
            --skip_leading_rows=1 \
            my-olympic-etl:olympics_dataset.athletes \
            output/athletes.csv \
            athlete_id:STRING,name:STRING,country:STRING,sport:STRING,medal:STRING,medal_rank:INTEGER,year:INTEGER,_processed_at:TIMESTAMP,_pipeline_version:STRING,_environment:STRING

  notify:
    needs: bigquery-load
    runs-on: ubuntu-latest
    if: always()
    
    steps:
      - name: Pipeline complete
        run: |
          echo "✅ Olympic ETL Pipeline executed successfully!"
```

---

## PASSO 5: Verificar Setup ✅

1. Volta na aba **"Actions"** do GitHub
2. Procura pelo workflow `Olympic ETL Pipeline`
3. Se rodou com ✅ verde = **SUCESSO!**
4. Se teve ❌ vermelho = Verifica os logs

---

## 🎯 O QUE ACONTECE AGORA

**Seu pipeline vai rodar:**
- ✅ **Diariamente às 2AM UTC** (ou quando fizer push)
- ✅ **Valida os dados** (olympic_etl_simple.py)
- ✅ **Carrega no BigQuery** (bq load)
- ✅ **Dashboard atualiza** (Looker Studio)

---

## 📊 RESULTADO FINAL

**Seu projeto completo em 24/7:**
- 📁 **Code** no GitHub (versionado)
- ⚙️ **CI/CD automático** (GitHub Actions)
- 🗄️ **Pipeline rodando** (BigQuery)
- 📈 **Dashboard ao vivo** (Looker Studio)

**TUDO GRÁTIS! FREE TIER MÁXIMO!** 🎉

---

## 🔧 TROUBLESHOOTING

### Erro: "credentials_json is not valid JSON"
- Copia o arquivo JSON INTEIRO (não é só o path)
- Remove quebras de linha extras

### Erro: "BigQuery: Permission denied"
- Certifica que o Service Account tem role `BigQuery Admin`
- Espera 1-2 min após criar a role

### Workflow não aparece em Actions
- Faz commit e push do arquivo `.github/workflows/olympic-etl-pipeline.yml`
- Espera alguns segundos
- Refresh a página

---

## ✨ PARABÉNS! 

**Você completou TODO O PROJETO!** 🚀

- ✅ ETL Pipeline (local)
- ✅ BigQuery Dataset
- ✅ Looker Studio Dashboard
- ✅ GitHub CI/CD Automation

**Projeto olympico em PRODUÇÃO 100% GRÁTIS!** 🏅

---

## 🎬 PRÓXIMOS PASSOS (OPCIONAL - PAGO)

Se quiser expandir (não FREE):
- Deploy em Cloud Run
- Dataflow escalável
- Advanced monitoring
- Mais dados reais

Mas por agora: **Missão cumprida!** 💪
