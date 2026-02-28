# GITHUB ACTIONS - SETUP RÁPIDO (10 MIN)

## Passo 1: Push código para GitHub
```powershell
# Na pasta do projeto:
git init
git add .
git commit -m "Initial commit - Olympic ETL"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/olympic-data-etl.git
git push -u origin main
```

## Passo 2: Criar Secrets (GCP)
```
1. GitHub → Settings → Secrets and variables → Actions
2. Crie 2 secrets:

SECRET 1: GCP_SA_KEY
- Valor: Arquivo JSON da service account
- Obter em: GCP Console → Service Accounts

SECRET 2: GCP_PROJECT_ID  
- Valor: my-olympic-etl
```

### Como gerar Service Account Key:
```powershell
# 1. No GCP Console:
# IAM & Admin → Service Accounts → Create Service Account
# Nome: github-actions
# Role: Editor

# 2. Gerar chave JSON:
# Keys → Add Key → Create new key → JSON

# 3. Copiar conteúdo do arquivo JSON para SECRET GCP_SA_KEY
```

## Passo 3: Verificar Workflow
```
GitHub → Actions → Olympic ETL Pipeline
```

Ver os arquivos do workflow:
```
.github/workflows/olympic-etl-pipeline.yml
```

## Passo 4: Executar Manual
```
Actions → Olympic ETL Pipeline → Run workflow
```

## Resultado
- ✅ Pipeline executa automaticamente
- ✅ Dados exportados
- ✅ BigQuery atualizado
- ✅ Relatórios gerados
- ✅ Nenhum custo!

## Próximas Execuções
```
Automático:
- Daily: 2AM UTC
- Ao fazer push em main/develop
```

Tempo: 10 min
Custo: $0
Automação: ✅
