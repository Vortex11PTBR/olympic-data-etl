#!/usr/bin/env python3
"""
Export Olympic Data to Multiple Formats (Local - No Cloud Storage Needed)
Exporta dados válidos em formatos prontos para análise e importação
"""

import json
import csv
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataExporter:
    """Exporta dados em múltiplos formatos"""
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def load_valid_records(self) -> list:
        """Carrega registros validados"""
        valid_file = self.output_dir / "valid_records.json"
        
        if not valid_file.exists():
            logger.error(f"Arquivo não encontrado: {valid_file}")
            return []
        
        with open(valid_file) as f:
            return json.load(f)
    
    def export_to_csv(self, records: list) -> str:
        """Exporta para CSV (BigQuery-compatible)"""
        csv_file = self.output_dir / "athletes.csv"
        
        if not records:
            logger.warning("Nenhum registro para exportar")
            return str(csv_file)
        
        # Headers
        headers = list(records[0].keys()) if records else []
        
        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(records)
        
        logger.info(f"✅ CSV exportado: {csv_file}")
        return str(csv_file)
    
    def export_to_ndjson(self, records: list) -> str:
        """Exporta para NDJSON (BigQuery-compatible)"""
        ndjson_file = self.output_dir / "athletes.ndjson"
        
        with open(ndjson_file, "w") as f:
            for record in records:
                f.write(json.dumps(record) + "\n")
        
        logger.info(f"✅ NDJSON exportado: {ndjson_file}")
        return str(ndjson_file)
    
    def export_to_json(self, records: list) -> str:
        """Exporta para JSON"""
        json_file = self.output_dir / "athletes_formatted.json"
        
        with open(json_file, "w") as f:
            json.dump(records, f, indent=2)
        
        logger.info(f"✅ JSON exportado: {json_file}")
        return str(json_file)
    
    def export_stats_report(self, records: list) -> str:
        """Cria relatório de estatísticas"""
        report_file = self.output_dir / "statistics_report.txt"
        
        # Análises
        total_records = len(records)
        countries = set(r.get("country", "Unknown") for r in records)
        sports = set(r.get("sport", "Unknown") for r in records)
        medals = {}
        
        for record in records:
            medal = record.get("medal", "None")
            medals[medal] = medals.get(medal, 0) + 1
        
        years = set(r.get("year") for r in records if r.get("year"))
        
        # Gerar relatório
        with open(report_file, "w", encoding="utf-8") as f:
            f.write("=" * 60 + "\n")
            f.write("OLYMPIC DATA - STATISTICAL REPORT\n")
            f.write("=" * 60 + "\n\n")
            
            f.write(f"Generated: {datetime.now().isoformat()}\n")
            f.write(f"Total Records: {total_records}\n\n")
            
            f.write("MEDALS DISTRIBUTION:\n")
            f.write("-" * 40 + "\n")
            for medal, count in sorted(medals.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / total_records * 100) if total_records > 0 else 0
                f.write(f"  {medal}: {count} ({percentage:.1f}%)\n")
            
            f.write(f"\nCOUNTRIES: {len(countries)}\n")
            f.write("-" * 40 + "\n")
            for country in sorted(countries):
                count = sum(1 for r in records if r.get("country") == country)
                f.write(f"  {country}: {count} athletes\n")
            
            f.write(f"\nSPORTS: {len(sports)}\n")
            f.write("-" * 40 + "\n")
            for sport in sorted(sports):
                count = sum(1 for r in records if r.get("sport") == sport)
                f.write(f"  {sport}: {count} athletes\n")
            
            f.write(f"\nYEARS: {len(years)}\n")
            f.write("-" * 40 + "\n")
            for year in sorted(years):
                count = sum(1 for r in records if r.get("year") == year)
                f.write(f"  {year}: {count} athletes\n")
            
            f.write("\n" + "=" * 60 + "\n")
            f.write("END OF REPORT\n")
            f.write("=" * 60 + "\n")
        
        logger.info(f"✅ Relatório criado: {report_file}")
        return str(report_file)
    
    def generate_bigquery_instructions(self, csv_file: str, ndjson_file: str) -> str:
        """Gera instruções para importar no BigQuery"""
        instructions_file = self.output_dir / "BIGQUERY_IMPORT_INSTRUCTIONS.md"
        
        with open(instructions_file, "w", encoding="utf-8") as f:
            f.write("# BigQuery Import Instructions\n\n")
            
            f.write("## Option 1: Import from CSV (Recommended)\n\n")
            f.write("1. Open BigQuery Console:\n")
            f.write("   https://console.cloud.google.com/bigquery\n\n")
            
            f.write("2. Create Dataset (if needed):\n")
            f.write("   - Click 'Create Dataset'\n")
            f.write("   - Name: `olympics_dataset`\n")
            f.write("   - Location: `US`\n\n")
            
            f.write("3. Upload CSV File:\n")
            f.write(f"   - File: `{csv_file}`\n")
            f.write("   - Destination Dataset: `olympics_dataset`\n")
            f.write("   - Destination Table: `athletes`\n")
            f.write("   - Table Type: `Native table`\n")
            f.write("           - Auto-detect schema: [X] Checked\n")
            f.write("   - Click 'Create table'\n\n")
            
            f.write("## Option 2: Import from NDJSON\n\n")
            f.write(f"   - Use same steps above with `{ndjson_file}`\n\n")
            
            f.write("## Command Line Option\n\n")
            f.write("```bash\n")
            f.write("# Load CSV\n")
            f.write("bq load --autodetect --source_format=CSV \\\n")
            f.write("  olympics_dataset.athletes \\\n")
            f.write(f"  {csv_file}\n\n")
            
            f.write("# Or load NDJSON\n")
            f.write("bq load --autodetect --source_format=NEWLINE_DELIMITED_JSON \\\n")
            f.write("  olympics_dataset.athletes \\\n")
            f.write(f"  {ndjson_file}\n")
            f.write("```\n\n")
            
            f.write("## Verify Data\n\n")
            f.write("```bash\n")
            f.write("# Check row count\n")
            f.write("bq query --use_legacy_sql=false \\\n")
            f.write("  'SELECT COUNT(*) as total FROM olympics_dataset.athletes'\n\n")
            
            f.write("# View first 10 rows\n")
            f.write("bq query --use_legacy_sql=false \\\n")
            f.write("  'SELECT * FROM olympics_dataset.athletes LIMIT 10'\n")
            f.write("```\n")
        
        logger.info(f"✅ Instruções de importação: {instructions_file}")
        return str(instructions_file)


def main():
    """Main entry point"""
    logger.info("=" * 60)
    logger.info("Olympic Data Export Tool")
    logger.info("=" * 60)
    
    try:
        exporter = DataExporter()
        
        # 1. Carregar dados
        logger.info("\n📖 Carregando dados validados...")
        records = exporter.load_valid_records()
        
        if not records:
            logger.error("Nenhum dado encontrado!")
            return 1
        
        logger.info(f"✅ {len(records)} registros carregados")
        
        # 2. Exportar para múltiplos formatos
        logger.info("\n📤 Exportando para múltiplos formatos...")
        csv_file = exporter.export_to_csv(records)
        ndjson_file = exporter.export_to_ndjson(records)
        json_file = exporter.export_to_json(records)
        
        # 3. Gerar relatório
        logger.info("\n📊 Gerando relatório estatístico...")
        report_file = exporter.export_stats_report(records)
        
        # 4. Gerar instruções
        logger.info("\n📝 Gerando instruções de importação...")
        instructions_file = exporter.generate_bigquery_instructions(csv_file, ndjson_file)
        
        # 5. Exibir resumo
        logger.info("\n" + "=" * 60)
        logger.info("✅ EXPORTAÇÃO CONCLUÍDA COM SUCESSO!")
        logger.info("=" * 60)
        
        logger.info("\n📁 Arquivos gerados:")
        logger.info(f"  • CSV: {csv_file}")
        logger.info(f"  • NDJSON: {ndjson_file}")
        logger.info(f"  • JSON: {json_file}")
        logger.info(f"  • Relatório: {report_file}")
        logger.info(f"  • Instruções: {instructions_file}")
        
        logger.info("\n💡 Próximos passos:")
        logger.info("  1. Abra: output/BIGQUERY_IMPORT_INSTRUCTIONS.md")
        logger.info("  2. Siga as instruções para importar no BigQuery")
        logger.info("  3. Ou use o comando bq load (command line)")
        
        # Exibir relatório
        logger.info("\n" + "=" * 60)
        logger.info("RESUMO DE DADOS")
        logger.info("=" * 60)
        with open(report_file, encoding="utf-8") as f:
            logger.info("\n" + f.read())
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Erro: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
