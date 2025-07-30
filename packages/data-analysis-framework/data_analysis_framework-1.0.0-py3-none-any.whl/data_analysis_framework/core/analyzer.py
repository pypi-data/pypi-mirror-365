"""
Core data analyzer for structured data files

Provides intelligent analysis of tabular data, databases, and configuration files
with focus on schema detection, data profiling, and AI-agent interaction preparation.
"""

import os
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Union, Tuple
from pathlib import Path
import pandas as pd
import numpy as np
import json
import yaml

logger = logging.getLogger(__name__)


@dataclass
class DataTypeInfo:
    """Information about detected data type and structure"""

    type_name: str  # "excel", "csv", "database", "json", etc.
    format_version: str = ""
    encoding: str = "utf-8"
    tables_count: int = 0
    total_rows: int = 0
    total_columns: int = 0
    file_size_mb: float = 0.0
    sheets_or_tables: List[str] = field(default_factory=list)

    # Data characteristics
    has_headers: bool = True
    has_index: bool = False
    has_missing_data: bool = False
    has_duplicates: bool = False

    # Schema complexity
    column_types: Dict[str, str] = field(default_factory=dict)
    relationship_complexity: str = "simple"  # simple, moderate, complex

    def __str__(self):
        return f"{self.type_name.title()} ({self.tables_count} tables, {self.total_rows:,} rows)"


@dataclass
class StructuredAnalysis:
    """Comprehensive analysis results for structured data"""

    # Schema information
    schema_info: Dict[str, Any] = field(default_factory=dict)
    column_profiles: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    # Data quality metrics
    quality_score: float = 0.0
    quality_issues: List[str] = field(default_factory=list)
    completeness_ratio: float = 0.0

    # Business intelligence
    detected_patterns: List[str] = field(default_factory=list)
    potential_keys: List[str] = field(default_factory=list)
    foreign_key_candidates: List[Dict[str, str]] = field(default_factory=list)

    # AI interaction readiness
    query_complexity: str = "simple"  # simple, moderate, complex
    recommended_operations: List[str] = field(default_factory=list)
    safety_constraints: List[str] = field(default_factory=list)

    # Business insights
    business_metrics: Dict[str, Any] = field(default_factory=dict)
    anomaly_indicators: List[str] = field(default_factory=list)
    trend_analysis: Dict[str, Any] = field(default_factory=dict)


class DataAnalyzer:
    """
    Main analyzer for structured data files

    Focuses on understanding data schema, relationships, and preparing
    data for AI agent interaction rather than document chunking.
    """

    def __init__(self, max_file_size_mb: float = 500.0):
        """
        Initialize the data analyzer

        Args:
            max_file_size_mb: Maximum file size to process (default 500MB)
        """
        self.max_file_size_mb = max_file_size_mb
        self.supported_formats = {
            # Spreadsheet formats
            ".xlsx": self._analyze_excel,
            ".xls": self._analyze_excel,
            ".csv": self._analyze_csv,
            ".tsv": self._analyze_csv,
            ".parquet": self._analyze_parquet,
            # Structured data formats
            ".json": self._analyze_json,
            ".jsonl": self._analyze_jsonl,
            ".yaml": self._analyze_yaml,
            ".yml": self._analyze_yaml,
            ".toml": self._analyze_toml,
            # Database formats
            ".sqlite": self._analyze_sqlite,
            ".db": self._analyze_sqlite,
            ".sql": self._analyze_sql_dump,
            # Configuration formats
            ".ini": self._analyze_ini,
            ".env": self._analyze_env,
            ".conf": self._analyze_config,
            ".cfg": self._analyze_config,
        }

    def analyze_file(self, file_path: str, **kwargs) -> Dict[str, Any]:
        """
        Analyze a structured data file

        Args:
            file_path: Path to the data file
            **kwargs: Additional options

        Returns:
            dict: Complete analysis results
        """
        file_path = Path(file_path)

        try:
            # Validate file
            if not file_path.exists():
                return {"error": f"File not found: {file_path}"}

            # Check file size
            file_size_mb = file_path.stat().st_size / (1024 * 1024)
            if file_size_mb > self.max_file_size_mb:
                return {
                    "error": f"File too large: {file_size_mb:.1f}MB "
                    f"(max: {self.max_file_size_mb}MB)"
                }

            # Detect format and analyze
            file_ext = file_path.suffix.lower()
            if file_ext not in self.supported_formats:
                return {"error": f"Unsupported format: {file_ext}"}

            logger.info(f"Analyzing {file_ext} file: {file_path}")

            # Run format-specific analysis
            analyzer_func = self.supported_formats[file_ext]
            data_type_info, structured_analysis = analyzer_func(file_path, **kwargs)

            return {
                "file_path": str(file_path),
                "data_type": data_type_info,
                "analysis": structured_analysis,
                "ai_readiness": self._assess_ai_readiness(data_type_info, structured_analysis),
                "agent_capabilities": self._determine_agent_capabilities(
                    data_type_info, structured_analysis
                ),
            }

        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {e}")
            return {"error": f"Analysis failed: {str(e)}"}

    def _analyze_excel(self, file_path: Path, **kwargs) -> Tuple[DataTypeInfo, StructuredAnalysis]:
        """Analyze Excel files (.xlsx, .xls)"""
        # Read Excel file with multiple sheets
        excel_file = pd.ExcelFile(file_path)
        sheets = excel_file.sheet_names

        total_rows = 0
        total_columns = 0
        all_column_types = {}

        # Analyze each sheet
        for sheet_name in sheets:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            total_rows += len(df)
            total_columns = max(total_columns, len(df.columns))

            # Column type analysis
            for col in df.columns:
                dtype = str(df[col].dtype)
                if col not in all_column_types:
                    all_column_types[col] = dtype

        # Create data type info
        data_type_info = DataTypeInfo(
            type_name="excel",
            format_version="xlsx" if file_path.suffix == ".xlsx" else "xls",
            tables_count=len(sheets),
            total_rows=total_rows,
            total_columns=total_columns,
            file_size_mb=file_path.stat().st_size / (1024 * 1024),
            sheets_or_tables=sheets,
            column_types=all_column_types,
            has_headers=True,  # Excel usually has headers
            relationship_complexity="moderate" if len(sheets) > 1 else "simple",
        )

        # Perform structured analysis
        structured_analysis = self._perform_structured_analysis(file_path, data_type_info)

        return data_type_info, structured_analysis

    def _analyze_csv(self, file_path: Path, **kwargs) -> Tuple[DataTypeInfo, StructuredAnalysis]:
        """Analyze CSV/TSV files"""
        # Detect delimiter
        delimiter = "\t" if file_path.suffix.lower() == ".tsv" else ","

        # Read CSV
        try:
            df = pd.read_csv(file_path, delimiter=delimiter, nrows=1000)  # Sample for analysis

            # Column type analysis
            column_types = {col: str(df[col].dtype) for col in df.columns}

            # Get full row count efficiently
            with open(file_path, "r") as f:
                total_rows = sum(1 for _ in f) - 1  # Subtract header

            data_type_info = DataTypeInfo(
                type_name="csv" if delimiter == "," else "tsv",
                encoding="utf-8",
                tables_count=1,
                total_rows=total_rows,
                total_columns=len(df.columns),
                file_size_mb=file_path.stat().st_size / (1024 * 1024),
                sheets_or_tables=["main"],
                column_types=column_types,
                has_headers=True,
                relationship_complexity="simple",
            )

            structured_analysis = self._perform_structured_analysis(file_path, data_type_info, df)

        except Exception as e:
            # Fallback for problematic files
            data_type_info = DataTypeInfo(
                type_name="csv_problematic", file_size_mb=file_path.stat().st_size / (1024 * 1024)
            )
            structured_analysis = StructuredAnalysis(
                quality_issues=[f"Failed to parse: {str(e)}"],
                safety_constraints=["manual_review_required"],
            )

        return data_type_info, structured_analysis

    def _analyze_json(self, file_path: Path, **kwargs) -> Tuple[DataTypeInfo, StructuredAnalysis]:
        """Analyze JSON files"""
        with open(file_path, "r") as f:
            data = json.load(f)

        # Analyze JSON structure
        if isinstance(data, list):
            # Array of objects - table-like
            if data and isinstance(data[0], dict):
                columns = list(data[0].keys())
                data_type_info = DataTypeInfo(
                    type_name="json_table",
                    tables_count=1,
                    total_rows=len(data),
                    total_columns=len(columns),
                    sheets_or_tables=["main"],
                    column_types={col: "mixed" for col in columns},
                    relationship_complexity="simple",
                )
            else:
                # Simple array
                data_type_info = DataTypeInfo(
                    type_name="json_array", total_rows=len(data), relationship_complexity="simple"
                )
        elif isinstance(data, dict):
            # Object structure
            data_type_info = DataTypeInfo(
                type_name="json_object",
                relationship_complexity="moderate" if self._is_nested_dict(data) else "simple",
            )
        else:
            data_type_info = DataTypeInfo(type_name="json_simple")

        data_type_info.file_size_mb = file_path.stat().st_size / (1024 * 1024)
        structured_analysis = self._perform_structured_analysis(file_path, data_type_info, data)

        return data_type_info, structured_analysis

    def _analyze_yaml(self, file_path: Path, **kwargs) -> Tuple[DataTypeInfo, StructuredAnalysis]:
        """Analyze YAML files"""
        with open(file_path, "r") as f:
            data = yaml.safe_load(f)

        data_type_info = DataTypeInfo(
            type_name="yaml",
            file_size_mb=file_path.stat().st_size / (1024 * 1024),
            relationship_complexity=(
                "moderate" if isinstance(data, dict) and self._is_nested_dict(data) else "simple"
            ),
        )

        structured_analysis = self._perform_structured_analysis(file_path, data_type_info, data)
        return data_type_info, structured_analysis

    def _analyze_parquet(
        self, file_path: Path, **kwargs
    ) -> Tuple[DataTypeInfo, StructuredAnalysis]:
        """Analyze Parquet files"""
        df = pd.read_parquet(file_path)

        data_type_info = DataTypeInfo(
            type_name="parquet",
            tables_count=1,
            total_rows=len(df),
            total_columns=len(df.columns),
            file_size_mb=file_path.stat().st_size / (1024 * 1024),
            sheets_or_tables=["main"],
            column_types={col: str(df[col].dtype) for col in df.columns},
            has_headers=True,
            relationship_complexity="simple",
        )

        structured_analysis = self._perform_structured_analysis(file_path, data_type_info, df)
        return data_type_info, structured_analysis

    # Placeholder methods for other formats
    def _analyze_jsonl(self, file_path: Path, **kwargs) -> Tuple[DataTypeInfo, StructuredAnalysis]:
        """Analyze JSONL files"""
        return DataTypeInfo(type_name="jsonl"), StructuredAnalysis()

    def _analyze_toml(self, file_path: Path, **kwargs) -> Tuple[DataTypeInfo, StructuredAnalysis]:
        """Analyze TOML files"""
        return DataTypeInfo(type_name="toml"), StructuredAnalysis()

    def _analyze_sqlite(self, file_path: Path, **kwargs) -> Tuple[DataTypeInfo, StructuredAnalysis]:
        """Analyze SQLite databases"""
        return DataTypeInfo(type_name="sqlite"), StructuredAnalysis()

    def _analyze_sql_dump(
        self, file_path: Path, **kwargs
    ) -> Tuple[DataTypeInfo, StructuredAnalysis]:
        """Analyze SQL dump files"""
        return DataTypeInfo(type_name="sql_dump"), StructuredAnalysis()

    def _analyze_ini(self, file_path: Path, **kwargs) -> Tuple[DataTypeInfo, StructuredAnalysis]:
        """Analyze INI configuration files"""
        return DataTypeInfo(type_name="ini"), StructuredAnalysis()

    def _analyze_env(self, file_path: Path, **kwargs) -> Tuple[DataTypeInfo, StructuredAnalysis]:
        """Analyze .env files"""
        return DataTypeInfo(type_name="env"), StructuredAnalysis()

    def _analyze_config(self, file_path: Path, **kwargs) -> Tuple[DataTypeInfo, StructuredAnalysis]:
        """Analyze configuration files"""
        return DataTypeInfo(type_name="config"), StructuredAnalysis()

    def _perform_structured_analysis(
        self, file_path: Path, data_type_info: DataTypeInfo, data: Any = None
    ) -> StructuredAnalysis:
        """
        Perform comprehensive structured analysis

        This is where the real AI-readiness assessment happens
        """
        analysis = StructuredAnalysis()

        # Schema analysis
        if hasattr(data, "columns") and hasattr(data, "dtypes"):  # DataFrame
            analysis.schema_info = self._analyze_dataframe_schema(data)
            analysis.column_profiles = self._profile_dataframe_columns(data)
        elif isinstance(data, (dict, list)):
            analysis.schema_info = self._analyze_json_schema(data)

        # Quality assessment
        analysis.quality_score = self._calculate_quality_score(data_type_info, data)
        analysis.quality_issues = self._identify_quality_issues(data_type_info, data)

        # Business intelligence
        analysis.detected_patterns = self._detect_business_patterns(data_type_info, data)
        analysis.potential_keys = self._identify_potential_keys(data)

        # AI interaction preparation
        analysis.query_complexity = self._assess_query_complexity(data_type_info)
        analysis.recommended_operations = self._recommend_operations(data_type_info)
        analysis.safety_constraints = self._determine_safety_constraints(data_type_info)

        return analysis

    def _analyze_dataframe_schema(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze pandas DataFrame schema"""
        return {
            "columns": list(df.columns),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "shape": df.shape,
            "memory_usage": df.memory_usage(deep=True).sum(),
            "null_counts": df.isnull().sum().to_dict(),
        }

    def _profile_dataframe_columns(self, df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """Generate detailed column profiles"""
        profiles = {}

        for col in df.columns:
            series = df[col]
            profile = {
                "dtype": str(series.dtype),
                "null_count": series.isnull().sum(),
                "null_percentage": (series.isnull().sum() / len(series)) * 100,
                "unique_count": series.nunique(),
                "unique_percentage": (series.nunique() / len(series)) * 100,
            }

            # Add type-specific statistics
            if pd.api.types.is_numeric_dtype(series):
                profile.update(
                    {
                        "min": series.min(),
                        "max": series.max(),
                        "mean": series.mean(),
                        "std": series.std(),
                        "median": series.median(),
                    }
                )
            elif pd.api.types.is_datetime64_any_dtype(series):
                profile.update(
                    {
                        "min_date": series.min(),
                        "max_date": series.max(),
                        "date_range_days": (
                            (series.max() - series.min()).days
                            if pd.notna(series.max()) and pd.notna(series.min())
                            else None
                        ),
                    }
                )

            profiles[col] = profile

        return profiles

    def _analyze_json_schema(self, data: Any) -> Dict[str, Any]:
        """Analyze JSON/YAML data schema"""
        if isinstance(data, list) and data:
            return {
                "type": "array",
                "length": len(data),
                "item_type": type(data[0]).__name__ if data else "empty",
                "sample_keys": list(data[0].keys()) if isinstance(data[0], dict) else None,
            }
        elif isinstance(data, dict):
            return {
                "type": "object",
                "keys": list(data.keys()),
                "nested_levels": self._count_nested_levels(data),
            }
        else:
            return {"type": type(data).__name__}

    def _calculate_quality_score(self, data_type_info: DataTypeInfo, data: Any) -> float:
        """Calculate overall data quality score (0-1)"""
        score = 1.0

        # Penalize for missing data
        if data_type_info.has_missing_data:
            score -= 0.2

        # Penalize for duplicates
        if data_type_info.has_duplicates:
            score -= 0.1

        # Reward for good structure
        if data_type_info.has_headers:
            score += 0.1

        return max(0.0, min(1.0, score))

    def _identify_quality_issues(self, data_type_info: DataTypeInfo, data: Any) -> List[str]:
        """Identify specific data quality issues"""
        issues = []

        if data_type_info.has_missing_data:
            issues.append("missing_values_detected")

        if data_type_info.has_duplicates:
            issues.append("duplicate_rows_found")

        if not data_type_info.has_headers:
            issues.append("no_column_headers")

        return issues

    def _detect_business_patterns(self, data_type_info: DataTypeInfo, data: Any) -> List[str]:
        """Detect business logic patterns in the data"""
        patterns = []

        # Look for common business patterns based on column names
        if hasattr(data, "columns"):
            columns_lower = [col.lower() for col in data.columns]

            if any(
                term in col
                for col in columns_lower
                for term in ["price", "cost", "amount", "value"]
            ):
                patterns.append("financial_data")

            if any(
                term in col
                for col in columns_lower
                for term in ["date", "time", "created", "updated"]
            ):
                patterns.append("temporal_data")

            if any(term in col for col in columns_lower for term in ["id", "key", "identifier"]):
                patterns.append("keyed_data")

            if any(
                term in col for col in columns_lower for term in ["name", "title", "description"]
            ):
                patterns.append("descriptive_data")

        return patterns

    def _identify_potential_keys(self, data: Any) -> List[str]:
        """Identify columns that could serve as primary keys"""
        if not hasattr(data, "columns"):
            return []

        potential_keys = []
        for col in data.columns:
            # Check if column has unique values
            if data[col].nunique() == len(data) and data[col].notna().all():
                potential_keys.append(col)

        return potential_keys

    def _assess_query_complexity(self, data_type_info: DataTypeInfo) -> str:
        """Assess how complex AI queries can be on this data"""
        if data_type_info.relationship_complexity == "complex" or data_type_info.tables_count > 5:
            return "complex"
        elif (
            data_type_info.relationship_complexity == "moderate" or data_type_info.tables_count > 1
        ):
            return "moderate"
        else:
            return "simple"

    def _recommend_operations(self, data_type_info: DataTypeInfo) -> List[str]:
        """Recommend operations that AI agents can safely perform"""
        operations = ["filter", "sort", "aggregate"]

        if data_type_info.type_name in ["excel", "csv", "parquet"]:
            operations.extend(["pivot", "group_by", "statistical_analysis"])

        if data_type_info.tables_count > 1:
            operations.append("join_tables")

        return operations

    def _determine_safety_constraints(self, data_type_info: DataTypeInfo) -> List[str]:
        """Determine safety constraints for AI agent interaction"""
        constraints = ["read_only_access", "result_size_limit"]

        if data_type_info.file_size_mb > 100:
            constraints.append("streaming_required")

        if "financial_data" in getattr(data_type_info, "detected_patterns", []):
            constraints.append("sensitive_data_handling")

        return constraints

    def _assess_ai_readiness(
        self, data_type_info: DataTypeInfo, analysis: StructuredAnalysis
    ) -> Dict[str, Any]:
        """Assess how ready the data is for AI agent interaction"""
        return {
            "readiness_score": analysis.quality_score,
            "complexity_level": analysis.query_complexity,
            "recommended_approach": (
                "direct_query" if analysis.quality_score > 0.7 else "preprocessing_required"
            ),
            "preprocessing_suggestions": analysis.quality_issues,
        }

    def _determine_agent_capabilities(
        self, data_type_info: DataTypeInfo, analysis: StructuredAnalysis
    ) -> Dict[str, Any]:
        """Determine what capabilities AI agents should have with this data"""
        return {
            "query_operations": analysis.recommended_operations,
            "safety_level": (
                "high" if "sensitive_data_handling" in analysis.safety_constraints else "standard"
            ),
            "result_formats": ["table", "summary", "visualization"],
            "interaction_patterns": [
                "natural_language_query",
                "structured_filter",
                "guided_exploration",
            ],
        }

    # Helper methods
    def _is_nested_dict(self, data: dict, max_depth: int = 3) -> bool:
        """Check if dictionary has nested structure"""

        def check_depth(obj, current_depth=0):
            if current_depth >= max_depth:
                return True
            if isinstance(obj, dict):
                return any(check_depth(v, current_depth + 1) for v in obj.values())
            return False

        return check_depth(data)

    def _count_nested_levels(self, data: dict) -> int:
        """Count maximum nesting levels in dictionary"""

        def max_depth(obj):
            if isinstance(obj, dict) and obj:
                return 1 + max(max_depth(v) for v in obj.values())
            elif isinstance(obj, list) and obj:
                return max(max_depth(item) for item in obj if isinstance(item, (dict, list)))
            return 0

        return max_depth(data)
