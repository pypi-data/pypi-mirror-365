"""
Data profiler for comprehensive quality assessment and statistical analysis

Provides detailed data profiling capabilities including statistical summaries,
data quality metrics, anomaly detection, and business intelligence insights.
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple, Set
from pathlib import Path
import pandas as pd
import numpy as np
from collections import Counter
import re

logger = logging.getLogger(__name__)


@dataclass
class SchemaInfo:
    """Detailed schema information for structured data"""

    # Basic structure
    total_columns: int = 0
    column_names: List[str] = field(default_factory=list)
    column_types: Dict[str, str] = field(default_factory=dict)
    inferred_types: Dict[str, str] = field(default_factory=dict)

    # Data characteristics
    primary_key_candidates: List[str] = field(default_factory=list)
    foreign_key_candidates: Dict[str, str] = field(default_factory=dict)
    unique_columns: List[str] = field(default_factory=list)

    # Constraints and patterns
    nullable_columns: List[str] = field(default_factory=list)
    constant_columns: List[str] = field(default_factory=list)
    enum_like_columns: Dict[str, List[Any]] = field(default_factory=dict)

    # Business logic patterns
    date_columns: List[str] = field(default_factory=list)
    monetary_columns: List[str] = field(default_factory=list)
    identifier_columns: List[str] = field(default_factory=list)
    measurement_columns: List[str] = field(default_factory=list)


@dataclass
class QualityMetrics:
    """Comprehensive data quality assessment metrics"""

    # Overall scores (0-100)
    overall_score: float = 0.0
    completeness_score: float = 0.0
    consistency_score: float = 0.0
    accuracy_score: float = 0.0

    # Detailed metrics
    missing_data_ratio: float = 0.0
    duplicate_rows_ratio: float = 0.0
    outlier_ratio: float = 0.0

    # Column-specific quality
    column_quality: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    # Issues and recommendations
    critical_issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    # Business value assessment
    business_value_indicators: Dict[str, Any] = field(default_factory=dict)
    ai_readiness_score: float = 0.0


class DataProfiler:
    """
    Comprehensive data profiler for structured data

    Provides detailed statistical analysis, quality assessment,
    and business intelligence insights for AI-ready data preparation.
    """

    def __init__(
        self, sample_size: int = 10000, outlier_threshold: float = 3.0, enum_threshold: int = 10
    ):
        """
        Initialize the data profiler

        Args:
            sample_size: Maximum number of rows to analyze for large datasets
            outlier_threshold: Z-score threshold for outlier detection
            enum_threshold: Max unique values to consider column as enum-like
        """
        self.sample_size = sample_size
        self.outlier_threshold = outlier_threshold
        self.enum_threshold = enum_threshold

    def generate_profile(self, file_path: str, **kwargs) -> Dict[str, Any]:
        """
        Generate comprehensive data profile

        Args:
            file_path: Path to data file
            **kwargs: Additional profiling options

        Returns:
            dict: Complete profiling results
        """
        from .analyzer import DataAnalyzer

        # First get basic analysis
        analyzer = DataAnalyzer()
        base_analysis = analyzer.analyze_file(file_path, **kwargs)

        if "error" in base_analysis:
            return base_analysis

        # Load data for detailed profiling
        df = self._load_data_for_profiling(file_path, base_analysis["data_type"])

        if df is None:
            return {"error": "Could not load data for profiling"}

        # Generate comprehensive profile
        schema_info = self._analyze_schema(df)
        quality_metrics = self._assess_quality(df, schema_info)
        statistical_summary = self._generate_statistical_summary(df)
        business_insights = self._extract_business_insights(df, schema_info)
        ai_recommendations = self._generate_ai_recommendations(df, schema_info, quality_metrics)

        return {
            "file_path": file_path,
            "data_overview": {
                "rows": len(df),
                "columns": len(df.columns),
                "memory_usage_mb": df.memory_usage(deep=True).sum() / (1024 * 1024),
                "data_types": df.dtypes.value_counts().to_dict(),
            },
            "schema_info": schema_info,
            "quality_metrics": quality_metrics,
            "statistical_summary": statistical_summary,
            "business_insights": business_insights,
            "ai_recommendations": ai_recommendations,
            "column_profiles": self._generate_column_profiles(df),
        }

    def _load_data_for_profiling(self, file_path: str, data_type_info) -> Optional[pd.DataFrame]:
        """Load data appropriate for profiling"""
        file_path = Path(file_path)
        file_ext = file_path.suffix.lower()

        try:
            if file_ext in [".xlsx", ".xls"]:
                # For Excel, load first sheet or combine if multiple
                excel_file = pd.ExcelFile(file_path)
                if len(excel_file.sheet_names) == 1:
                    return pd.read_excel(file_path)
                else:
                    # Load and combine multiple sheets
                    dfs = []
                    for sheet in excel_file.sheet_names[:3]:  # Limit to first 3 sheets
                        df = pd.read_excel(file_path, sheet_name=sheet)
                        df["_sheet_source"] = sheet
                        dfs.append(df)
                    return pd.concat(dfs, ignore_index=True)

            elif file_ext == ".csv":
                return pd.read_csv(file_path, nrows=self.sample_size)

            elif file_ext == ".tsv":
                return pd.read_csv(file_path, delimiter="\t", nrows=self.sample_size)

            elif file_ext == ".parquet":
                return pd.read_parquet(file_path)

            elif file_ext == ".json":
                # Try to load as DataFrame
                data = pd.read_json(file_path)
                if isinstance(data, pd.DataFrame):
                    return data
                else:
                    # Convert to DataFrame if possible
                    if isinstance(data, list) and data and isinstance(data[0], dict):
                        return pd.DataFrame(data)

            return None

        except Exception as e:
            logger.error(f"Error loading data for profiling: {e}")
            return None

    def _analyze_schema(self, df: pd.DataFrame) -> SchemaInfo:
        """Analyze data schema in detail"""
        schema = SchemaInfo()

        # Basic structure
        schema.total_columns = len(df.columns)
        schema.column_names = list(df.columns)
        schema.column_types = {col: str(dtype) for col, dtype in df.dtypes.items()}

        # Infer semantic types
        schema.inferred_types = self._infer_semantic_types(df)

        # Identify key candidates
        schema.primary_key_candidates = self._find_primary_key_candidates(df)
        schema.unique_columns = self._find_unique_columns(df)

        # Column characteristics
        schema.nullable_columns = [col for col in df.columns if df[col].isnull().any()]
        schema.constant_columns = [col for col in df.columns if df[col].nunique() <= 1]
        schema.enum_like_columns = self._find_enum_like_columns(df)

        # Business patterns
        schema.date_columns = self._identify_date_columns(df)
        schema.monetary_columns = self._identify_monetary_columns(df)
        schema.identifier_columns = self._identify_identifier_columns(df)
        schema.measurement_columns = self._identify_measurement_columns(df)

        return schema

    def _assess_quality(self, df: pd.DataFrame, schema: SchemaInfo) -> QualityMetrics:
        """Comprehensive quality assessment"""
        metrics = QualityMetrics()

        # Calculate basic ratios
        total_cells = len(df) * len(df.columns)
        missing_cells = df.isnull().sum().sum()
        duplicate_rows = df.duplicated().sum()

        metrics.missing_data_ratio = missing_cells / total_cells if total_cells > 0 else 0
        metrics.duplicate_rows_ratio = duplicate_rows / len(df) if len(df) > 0 else 0

        # Calculate scores
        metrics.completeness_score = max(0, 100 * (1 - metrics.missing_data_ratio))
        metrics.consistency_score = self._calculate_consistency_score(df)
        metrics.accuracy_score = self._calculate_accuracy_score(df, schema)

        # Overall score (weighted average)
        metrics.overall_score = (
            0.4 * metrics.completeness_score
            + 0.3 * metrics.consistency_score
            + 0.3 * metrics.accuracy_score
        )

        # Column-specific quality
        metrics.column_quality = self._assess_column_quality(df)

        # Issues and recommendations
        metrics.critical_issues = self._identify_critical_issues(df, schema)
        metrics.warnings = self._identify_warnings(df, schema)
        metrics.recommendations = self._generate_quality_recommendations(metrics, schema)

        # Business value assessment
        metrics.business_value_indicators = self._assess_business_value(df, schema)
        metrics.ai_readiness_score = self._calculate_ai_readiness_score(metrics, schema)

        return metrics

    def _generate_statistical_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate comprehensive statistical summary"""
        numeric_df = df.select_dtypes(include=[np.number])
        categorical_df = df.select_dtypes(include=["object", "category"])

        summary = {
            "numeric_columns": len(numeric_df.columns),
            "categorical_columns": len(categorical_df.columns),
            "datetime_columns": len(df.select_dtypes(include=["datetime"]).columns),
        }

        # Numeric statistics
        if not numeric_df.empty:
            summary["numeric_stats"] = {
                "mean": numeric_df.mean().to_dict(),
                "median": numeric_df.median().to_dict(),
                "std": numeric_df.std().to_dict(),
                "min": numeric_df.min().to_dict(),
                "max": numeric_df.max().to_dict(),
                "quartiles": {
                    "q25": numeric_df.quantile(0.25).to_dict(),
                    "q75": numeric_df.quantile(0.75).to_dict(),
                },
            }

            # Correlation analysis
            if len(numeric_df.columns) > 1:
                corr_matrix = numeric_df.corr()
                summary["correlations"] = {
                    "strong_positive": self._find_strong_correlations(corr_matrix, 0.7, 1.0),
                    "strong_negative": self._find_strong_correlations(corr_matrix, -1.0, -0.7),
                    "moderate_positive": self._find_strong_correlations(corr_matrix, 0.4, 0.7),
                    "moderate_negative": self._find_strong_correlations(corr_matrix, -0.7, -0.4),
                }

        # Categorical statistics
        if not categorical_df.empty:
            summary["categorical_stats"] = {}
            for col in categorical_df.columns:
                value_counts = categorical_df[col].value_counts()
                summary["categorical_stats"][col] = {
                    "unique_count": len(value_counts),
                    "most_frequent": value_counts.index[0] if len(value_counts) > 0 else None,
                    "most_frequent_count": value_counts.iloc[0] if len(value_counts) > 0 else 0,
                    "distribution": value_counts.head(10).to_dict(),  # Top 10 values
                }

        return summary

    def _extract_business_insights(self, df: pd.DataFrame, schema: SchemaInfo) -> Dict[str, Any]:
        """Extract business intelligence insights from data"""
        insights = {
            "data_patterns": [],
            "potential_relationships": [],
            "business_rules": [],
            "anomalies": [],
            "trends": {},
        }

        # Identify data patterns
        if schema.date_columns and schema.monetary_columns:
            insights["data_patterns"].append("time_series_financial_data")

        if schema.identifier_columns and len(df.columns) > 3:
            insights["data_patterns"].append("transactional_data")

        if len(schema.enum_like_columns) > len(df.columns) * 0.3:
            insights["data_patterns"].append("categorical_heavy_data")

        # Potential relationships
        for col in schema.identifier_columns:
            if col.lower().endswith("_id") or col.lower().startswith("id_"):
                table_name = col.lower().replace("_id", "").replace("id_", "")
                insights["potential_relationships"].append(f"foreign_key_to_{table_name}")

        # Business rules detection
        for col in df.columns:
            if df[col].dtype in ["int64", "float64"]:
                if df[col].min() >= 0:
                    insights["business_rules"].append(f"{col}_non_negative")
                if df[col].max() <= 100 and df[col].min() >= 0:
                    insights["business_rules"].append(f"{col}_percentage_like")

        # Simple anomaly detection
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            z_scores = np.abs((df[col] - df[col].mean()) / df[col].std())
            outliers = (z_scores > self.outlier_threshold).sum()
            if outliers > 0:
                insights["anomalies"].append(
                    {
                        "column": col,
                        "outlier_count": int(outliers),
                        "outlier_percentage": float(outliers / len(df) * 100),
                    }
                )

        return insights

    def _generate_ai_recommendations(
        self, df: pd.DataFrame, schema: SchemaInfo, quality: QualityMetrics
    ) -> Dict[str, Any]:
        """Generate AI-specific recommendations for data usage"""
        recommendations = {
            "preprocessing_steps": [],
            "feature_engineering": [],
            "model_suitability": [],
            "safety_considerations": [],
        }

        # Preprocessing recommendations
        if quality.missing_data_ratio > 0.1:
            recommendations["preprocessing_steps"].append("handle_missing_values")

        if quality.duplicate_rows_ratio > 0.05:
            recommendations["preprocessing_steps"].append("remove_duplicates")

        if schema.constant_columns:
            recommendations["preprocessing_steps"].append("remove_constant_columns")

        # Feature engineering suggestions
        if schema.date_columns:
            recommendations["feature_engineering"].append("extract_temporal_features")

        if schema.monetary_columns:
            recommendations["feature_engineering"].append("normalize_monetary_values")

        if len(schema.enum_like_columns) > 0:
            recommendations["feature_engineering"].append("encode_categorical_variables")

        # Model suitability
        numeric_ratio = len(df.select_dtypes(include=[np.number]).columns) / len(df.columns)
        if numeric_ratio > 0.7:
            recommendations["model_suitability"].extend(
                ["regression", "clustering", "anomaly_detection"]
            )

        if len(schema.enum_like_columns) > 0:
            recommendations["model_suitability"].append("classification")

        if schema.date_columns:
            recommendations["model_suitability"].append("time_series_analysis")

        # Safety considerations
        if schema.identifier_columns:
            recommendations["safety_considerations"].append("protect_identifiers")

        if schema.monetary_columns:
            recommendations["safety_considerations"].append("sensitive_financial_data")

        return recommendations

    def _generate_column_profiles(self, df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """Generate detailed profiles for each column"""
        profiles = {}

        for col in df.columns:
            series = df[col]
            profile = {
                "name": col,
                "dtype": str(series.dtype),
                "null_count": int(series.isnull().sum()),
                "null_percentage": float(series.isnull().sum() / len(series) * 100),
                "unique_count": int(series.nunique()),
                "unique_percentage": float(series.nunique() / len(series) * 100),
                "memory_usage": int(series.memory_usage(deep=True)),
            }

            # Type-specific analysis
            if pd.api.types.is_numeric_dtype(series):
                profile.update(self._profile_numeric_column(series))
            elif pd.api.types.is_datetime64_any_dtype(series):
                profile.update(self._profile_datetime_column(series))
            else:
                profile.update(self._profile_categorical_column(series))

            profiles[col] = profile

        return profiles

    # Helper methods
    def _infer_semantic_types(self, df: pd.DataFrame) -> Dict[str, str]:
        """Infer semantic types for columns"""
        semantic_types = {}

        for col in df.columns:
            col_lower = col.lower()
            series = df[col]

            # Check column name patterns
            if any(pattern in col_lower for pattern in ["id", "key", "identifier"]):
                semantic_types[col] = "identifier"
            elif any(pattern in col_lower for pattern in ["date", "time", "created", "updated"]):
                semantic_types[col] = "temporal"
            elif any(pattern in col_lower for pattern in ["price", "cost", "amount", "value", "$"]):
                semantic_types[col] = "monetary"
            elif any(pattern in col_lower for pattern in ["email", "mail"]):
                semantic_types[col] = "email"
            elif any(pattern in col_lower for pattern in ["phone", "tel"]):
                semantic_types[col] = "phone"
            elif any(pattern in col_lower for pattern in ["url", "link", "website"]):
                semantic_types[col] = "url"
            else:
                # Infer from data patterns
                if pd.api.types.is_numeric_dtype(series):
                    semantic_types[col] = "numeric"
                elif pd.api.types.is_datetime64_any_dtype(series):
                    semantic_types[col] = "temporal"
                elif series.nunique() / len(series) < 0.5:
                    semantic_types[col] = "categorical"
                else:
                    semantic_types[col] = "text"

        return semantic_types

    def _find_primary_key_candidates(self, df: pd.DataFrame) -> List[str]:
        """Find potential primary key columns"""
        candidates = []

        for col in df.columns:
            # Must be unique and non-null
            if df[col].nunique() == len(df) and df[col].notna().all():
                candidates.append(col)

        return candidates

    def _find_unique_columns(self, df: pd.DataFrame) -> List[str]:
        """Find columns with all unique values"""
        return [col for col in df.columns if df[col].nunique() == len(df)]

    def _find_enum_like_columns(self, df: pd.DataFrame) -> Dict[str, List[Any]]:
        """Find columns that behave like enums"""
        enum_cols = {}

        for col in df.columns:
            unique_count = df[col].nunique()
            if 2 <= unique_count <= self.enum_threshold:
                enum_cols[col] = df[col].unique().tolist()[: self.enum_threshold]

        return enum_cols

    def _identify_date_columns(self, df: pd.DataFrame) -> List[str]:
        """Identify date/datetime columns"""
        date_cols = []

        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                date_cols.append(col)
            elif col.lower() in ["date", "time", "created_at", "updated_at"]:
                date_cols.append(col)

        return date_cols

    def _identify_monetary_columns(self, df: pd.DataFrame) -> List[str]:
        """Identify monetary/financial columns"""
        monetary_cols = []

        for col in df.columns:
            col_lower = col.lower()
            if any(
                term in col_lower
                for term in ["price", "cost", "amount", "value", "salary", "revenue"]
            ):
                monetary_cols.append(col)

        return monetary_cols

    def _identify_identifier_columns(self, df: pd.DataFrame) -> List[str]:
        """Identify identifier columns"""
        id_cols = []

        for col in df.columns:
            col_lower = col.lower()
            if any(term in col_lower for term in ["id", "key", "identifier", "uuid"]):
                id_cols.append(col)

        return id_cols

    def _identify_measurement_columns(self, df: pd.DataFrame) -> List[str]:
        """Identify measurement/metric columns"""
        measurement_cols = []

        for col in df.columns:
            col_lower = col.lower()
            if pd.api.types.is_numeric_dtype(df[col]) and any(
                term in col_lower
                for term in ["count", "total", "sum", "avg", "mean", "rate", "ratio"]
            ):
                measurement_cols.append(col)

        return measurement_cols

    def _calculate_consistency_score(self, df: pd.DataFrame) -> float:
        """Calculate data consistency score"""
        # Simple consistency check based on data type consistency
        inconsistencies = 0
        total_checks = 0

        for col in df.columns:
            if df[col].dtype == "object":
                # Check for mixed types in object columns
                sample = df[col].dropna().head(100)
                if len(sample) > 0:
                    types = set(type(x).__name__ for x in sample)
                    if len(types) > 1:
                        inconsistencies += 1
                    total_checks += 1

        if total_checks == 0:
            return 100.0

        return max(0, 100 * (1 - inconsistencies / total_checks))

    def _calculate_accuracy_score(self, df: pd.DataFrame, schema: SchemaInfo) -> float:
        """Calculate data accuracy score"""
        # Basic accuracy assessment based on data patterns
        accuracy_score = 100.0

        # Penalize for obvious data issues
        for col in df.columns:
            if col in schema.monetary_columns:
                if df[col].min() < 0 and not any(
                    term in col.lower() for term in ["change", "diff", "delta"]
                ):
                    accuracy_score -= 5  # Negative monetary values (might be legitimate)

        return max(0, accuracy_score)

    def _assess_column_quality(self, df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """Assess quality for each column"""
        column_quality = {}

        for col in df.columns:
            series = df[col]
            quality = {
                "completeness": 100 * (1 - series.isnull().sum() / len(series)),
                "uniqueness": 100 * (series.nunique() / len(series)),
                "issues": [],
            }

            # Identify specific issues
            if series.isnull().sum() > len(series) * 0.5:
                quality["issues"].append("high_missing_rate")

            if series.nunique() == 1:
                quality["issues"].append("constant_value")

            if pd.api.types.is_numeric_dtype(series):
                z_scores = np.abs((series - series.mean()) / series.std()).fillna(0)
                outliers = (z_scores > self.outlier_threshold).sum()
                if outliers > len(series) * 0.05:
                    quality["issues"].append("high_outlier_rate")

            column_quality[col] = quality

        return column_quality

    def _identify_critical_issues(self, df: pd.DataFrame, schema: SchemaInfo) -> List[str]:
        """Identify critical data quality issues"""
        issues = []

        if len(schema.constant_columns) > len(df.columns) * 0.2:
            issues.append("too_many_constant_columns")

        missing_ratio = df.isnull().sum().sum() / (len(df) * len(df.columns))
        if missing_ratio > 0.5:
            issues.append("excessive_missing_data")

        if df.duplicated().sum() > len(df) * 0.5:
            issues.append("excessive_duplicates")

        return issues

    def _identify_warnings(self, df: pd.DataFrame, schema: SchemaInfo) -> List[str]:
        """Identify data quality warnings"""
        warnings = []

        if not schema.primary_key_candidates:
            warnings.append("no_primary_key_found")

        if len(schema.nullable_columns) == len(df.columns):
            warnings.append("all_columns_nullable")

        return warnings

    def _generate_quality_recommendations(
        self, metrics: QualityMetrics, schema: SchemaInfo
    ) -> List[str]:
        """Generate quality improvement recommendations"""
        recommendations = []

        if metrics.missing_data_ratio > 0.1:
            recommendations.append("implement_missing_value_strategy")

        if metrics.duplicate_rows_ratio > 0.05:
            recommendations.append("investigate_and_remove_duplicates")

        if schema.constant_columns:
            recommendations.append("remove_constant_columns")

        if not schema.primary_key_candidates:
            recommendations.append("establish_primary_key")

        return recommendations

    def _assess_business_value(self, df: pd.DataFrame, schema: SchemaInfo) -> Dict[str, Any]:
        """Assess business value indicators"""
        indicators = {
            "data_richness": len(df.columns) / 10,  # Normalized by typical table size
            "temporal_coverage": len(schema.date_columns) > 0,
            "financial_relevance": len(schema.monetary_columns) > 0,
            "analytical_potential": len(df.select_dtypes(include=[np.number]).columns)
            / len(df.columns),
            "relationship_complexity": len(schema.primary_key_candidates) > 0,
        }

        return indicators

    def _calculate_ai_readiness_score(self, metrics: QualityMetrics, schema: SchemaInfo) -> float:
        """Calculate AI readiness score"""
        base_score = metrics.overall_score

        # Bonuses for AI-friendly characteristics
        if schema.primary_key_candidates:
            base_score += 5

        if len(schema.enum_like_columns) > 0:
            base_score += 5

        if schema.date_columns:
            base_score += 3

        # Penalties for AI-unfriendly characteristics
        if len(schema.constant_columns) > 0:
            base_score -= 10

        return min(100, max(0, base_score))

    def _find_strong_correlations(
        self, corr_matrix: pd.DataFrame, min_corr: float, max_corr: float
    ) -> List[Dict[str, Any]]:
        """Find correlations within specified range"""
        correlations = []

        for i in range(len(corr_matrix.columns)):
            for j in range(i + 1, len(corr_matrix.columns)):
                corr_value = corr_matrix.iloc[i, j]
                if min_corr <= corr_value <= max_corr:
                    correlations.append(
                        {
                            "column1": corr_matrix.columns[i],
                            "column2": corr_matrix.columns[j],
                            "correlation": float(corr_value),
                        }
                    )

        return correlations

    def _profile_numeric_column(self, series: pd.Series) -> Dict[str, Any]:
        """Profile numeric column"""
        return {
            "type": "numeric",
            "min": float(series.min()) if pd.notna(series.min()) else None,
            "max": float(series.max()) if pd.notna(series.max()) else None,
            "mean": float(series.mean()) if pd.notna(series.mean()) else None,
            "median": float(series.median()) if pd.notna(series.median()) else None,
            "std": float(series.std()) if pd.notna(series.std()) else None,
            "zeros_count": int((series == 0).sum()),
            "negative_count": (
                int((series < 0).sum()) if series.dtype in ["int64", "float64"] else 0
            ),
        }

    def _profile_datetime_column(self, series: pd.Series) -> Dict[str, Any]:
        """Profile datetime column"""
        return {
            "type": "datetime",
            "min_date": str(series.min()) if pd.notna(series.min()) else None,
            "max_date": str(series.max()) if pd.notna(series.max()) else None,
            "date_range_days": (
                (series.max() - series.min()).days
                if pd.notna(series.max()) and pd.notna(series.min())
                else None
            ),
        }

    def _profile_categorical_column(self, series: pd.Series) -> Dict[str, Any]:
        """Profile categorical column"""
        value_counts = series.value_counts()

        return {
            "type": "categorical",
            "most_frequent": str(value_counts.index[0]) if len(value_counts) > 0 else None,
            "most_frequent_count": int(value_counts.iloc[0]) if len(value_counts) > 0 else 0,
            "least_frequent": str(value_counts.index[-1]) if len(value_counts) > 0 else None,
            "least_frequent_count": int(value_counts.iloc[-1]) if len(value_counts) > 0 else 0,
            "top_values": value_counts.head(5).to_dict(),
        }
