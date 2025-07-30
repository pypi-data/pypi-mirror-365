# Data Analysis Framework

## 📈 Purpose

Specialized framework for analyzing structured data files with AI-powered pattern detection and insights.

## 📦 Supported Formats

### Spreadsheets & Tables
- **Excel**: XLSX, XLS with multiple sheets
- **CSV/TSV**: Delimiter detection and parsing
- **Apache Parquet**: Columnar data analysis
- **JSON**: Nested and flat structure analysis
- **JSONL**: Line-delimited JSON streams

### Configuration Data
- **YAML**: Configuration files and data serialization
- **TOML**: Configuration file analysis
- **INI**: Legacy configuration parsing
- **Environment Files**: .env variable analysis

### Database Exports
- **SQL Dumps**: Schema and data analysis
- **SQLite**: Database file inspection
- **Database Connection**: Live data analysis

## 🤖 AI Integration Features

- **Schema Detection**: Automatic column type inference
- **Pattern Analysis**: Anomaly and trend detection
- **Data Quality Assessment**: Missing values, duplicates, outliers
- **Relationship Discovery**: Cross-table dependencies
- **Business Logic Extraction**: Rules and constraints
- **Predictive Insights**: Forecasting and recommendations

## 🚀 Quick Start

```python
from data_analysis_framework import DataAnalyzer

analyzer = DataAnalyzer()
result = analyzer.analyze("sales_data.xlsx")

print(f"Data Type: {result.document_type.type_name}")
print(f"Schema: {result.analysis.schema_info}")
print(f"Quality Score: {result.analysis.quality_metrics['overall_score']}")
print(f"AI Insights: {result.analysis.ai_insights}")
```

## 🏗️ Status

**🚧 Planned** - Architecture designed, implementation pending