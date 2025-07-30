"""
AI Agent Interface for Safe Structured Data Interaction

This is the core differentiator of the data-analysis-framework.
Instead of chunking documents, this provides safe APIs for AI agents
to query, filter, and analyze structured data with built-in safety constraints.

Key Features:
- Natural language query translation
- Safe data access with constraints
- Automatic result formatting
- Business intelligence report generation
- Query optimization and caching
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Union, Callable
from pathlib import Path
import pandas as pd
import numpy as np
import json
import re
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@dataclass
class SafeQuery:
    """Represents a safe, validated query for structured data"""

    query_id: str
    original_request: str  # Natural language request
    query_type: str  # "filter", "aggregate", "sort", "join", etc.

    # Parsed query components
    filters: Dict[str, Any] = field(default_factory=dict)
    aggregations: Dict[str, str] = field(default_factory=dict)
    sort_by: List[Dict[str, str]] = field(default_factory=list)
    columns: Optional[List[str]] = None
    limit: Optional[int] = None

    # Safety constraints
    max_results: int = 1000
    allowed_columns: List[str] = field(default_factory=list)
    restricted_columns: List[str] = field(default_factory=list)

    # Query metadata
    estimated_cost: str = "low"  # low, medium, high
    execution_time_estimate: float = 0.0
    requires_approval: bool = False

    def __str__(self):
        return f"SafeQuery({self.query_type}: '{self.original_request[:50]}...')"


@dataclass
class QueryResult:
    """Results from executing a safe query"""

    query_id: str
    success: bool

    # Results
    data: Optional[pd.DataFrame] = None
    summary: Dict[str, Any] = field(default_factory=dict)
    row_count: int = 0

    # Execution metadata
    execution_time_ms: float = 0.0
    columns_returned: List[str] = field(default_factory=list)
    data_quality_score: float = 0.0

    # Insights and recommendations
    insights: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    # Safety and compliance
    warnings: List[str] = field(default_factory=list)
    data_masked: bool = False
    sensitive_data_detected: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary for API responses"""
        result_dict = {
            "query_id": self.query_id,
            "success": self.success,
            "row_count": self.row_count,
            "execution_time_ms": self.execution_time_ms,
            "columns_returned": self.columns_returned,
            "summary": self.summary,
            "insights": self.insights,
            "recommendations": self.recommendations,
            "warnings": self.warnings,
            "data_quality_score": self.data_quality_score,
        }

        if self.data is not None:
            result_dict["data"] = self.data.to_dict(orient="records")

        return result_dict


class AgentQueryInterface:
    """
    Safe AI Agent Interface for Structured Data

    This is the key innovation of the data-analysis-framework.
    Provides a safe, intelligent interface for AI agents to interact
    with structured data without direct database/file access.
    """

    def __init__(
        self,
        max_query_results: int = 1000,
        enable_caching: bool = True,
        safety_level: str = "standard",
    ):
        """
        Initialize the agent interface

        Args:
            max_query_results: Maximum rows to return per query
            enable_caching: Enable query result caching
            safety_level: "strict" | "standard" | "permissive"
        """
        self.max_query_results = max_query_results
        self.enable_caching = enable_caching
        self.safety_level = safety_level

        # Internal state
        self.data: Optional[pd.DataFrame] = None
        self.data_schema: Dict[str, Any] = {}
        self.query_cache: Dict[str, QueryResult] = {}
        self.query_history: List[SafeQuery] = []

        # Safety configuration
        self.restricted_columns: List[str] = []
        self.sensitive_patterns = [
            r".*id$",
            r".*_id$",
            r"id_.*",  # IDs
            r".*ssn.*",
            r".*social.*",  # SSN
            r".*email.*",
            r".*mail.*",  # Email
            r".*phone.*",
            r".*tel.*",  # Phone
        ]

        # Query processing components
        self.query_parser = QueryParser()
        self.query_executor = QueryExecutor()
        self.result_formatter = ResultFormatter()

    def load_data(self, file_path: str, **kwargs) -> Dict[str, Any]:
        """
        Load structured data for agent interaction

        Args:
            file_path: Path to data file
            **kwargs: Loading options

        Returns:
            dict: Loading status and data summary
        """
        from .analyzer import DataAnalyzer
        from .profiler import DataProfiler

        try:
            # Analyze the data first
            analyzer = DataAnalyzer()
            analysis = analyzer.analyze_file(file_path, **kwargs)

            if "error" in analysis:
                return analysis

            # Load data for querying
            self.data = self._load_queryable_data(file_path, analysis["data_type"])

            if self.data is None:
                return {"error": "Could not load data for querying"}

            # Generate schema information
            profiler = DataProfiler()
            profile = profiler.generate_profile(file_path, **kwargs)

            self.data_schema = {
                "columns": list(self.data.columns),
                "dtypes": {col: str(dtype) for col, dtype in self.data.dtypes.items()},
                "row_count": len(self.data),
                "profile": profile,
            }

            # Identify restricted columns based on safety level
            self._identify_restricted_columns()

            return {
                "status": "success",
                "data_loaded": True,
                "rows": len(self.data),
                "columns": len(self.data.columns),
                "restricted_columns": len(self.restricted_columns),
                "query_capabilities": self._get_query_capabilities(),
                "recommended_queries": self._suggest_initial_queries(),
            }

        except Exception as e:
            logger.error(f"Error loading data for agent interface: {e}")
            return {"error": f"Failed to load data: {str(e)}"}

    def execute_query(self, natural_language_request: str, **kwargs) -> QueryResult:
        """
        Execute a natural language query against the loaded data

        Args:
            natural_language_request: Human-readable query request
            **kwargs: Additional query options

        Returns:
            QueryResult: Structured query results with insights

        Example:
            >>> interface = AgentQueryInterface()
            >>> interface.load_data("cars.xlsx")
            >>> result = interface.execute_query("Find all cars under $25000 with good condition")
            >>> print(f"Found {result.row_count} cars")
        """
        start_time = datetime.now()

        try:
            # Parse natural language into safe query
            safe_query = self.query_parser.parse(
                natural_language_request, self.data_schema, safety_level=self.safety_level, **kwargs
            )

            # Check cache first
            if self.enable_caching and safe_query.query_id in self.query_cache:
                cached_result = self.query_cache[safe_query.query_id]
                logger.info(f"Returning cached result for query: {safe_query.query_id}")
                return cached_result

            # Execute the safe query
            result = self.query_executor.execute(safe_query, self.data)

            # Add execution metadata
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            result.execution_time_ms = execution_time

            # Generate insights and recommendations
            result.insights = self._generate_insights(safe_query, result)
            result.recommendations = self._generate_recommendations(safe_query, result)

            # Cache the result
            if self.enable_caching:
                self.query_cache[safe_query.query_id] = result

            # Add to query history
            self.query_history.append(safe_query)

            return result

        except Exception as e:
            logger.error(f"Error executing query: {e}")
            return QueryResult(
                query_id="error", success=False, warnings=[f"Query execution failed: {str(e)}"]
            )

    def generate_report(
        self, query_results: List[QueryResult], report_title: str, report_type: str = "summary"
    ) -> Dict[str, Any]:
        """
        Generate a business intelligence report from query results

        Args:
            query_results: List of query results to include
            report_title: Title for the report
            report_type: "summary" | "detailed" | "executive"

        Returns:
            dict: Formatted business report

        Example:
            >>> cars_result = interface.execute_query("Find budget cars under $25000")
            >>> report = interface.generate_report([cars_result], "Budget Car Analysis")
        """
        return self.result_formatter.generate_report(
            query_results, report_title, report_type, self.data_schema
        )

    def get_query_suggestions(self, context: str = "") -> List[Dict[str, Any]]:
        """
        Get AI-powered query suggestions based on data and context

        Args:
            context: Optional context for suggestions

        Returns:
            list: Suggested queries with descriptions
        """
        suggestions = []

        if self.data is None:
            return [{"query": "No data loaded", "description": "Load data first"}]

        # Basic exploration suggestions
        suggestions.extend(
            [
                {
                    "query": "Show me a summary of the data",
                    "description": "Get overview statistics and data quality metrics",
                    "complexity": "simple",
                },
                {
                    "query": "What are the top 10 records?",
                    "description": "View sample data to understand structure",
                    "complexity": "simple",
                },
            ]
        )

        # Schema-based suggestions
        numeric_cols = self.data.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            col = numeric_cols[0]
            suggestions.append(
                {
                    "query": f"What is the average {col}?",
                    "description": f"Calculate average for {col} column",
                    "complexity": "simple",
                }
            )

        # Date-based suggestions
        date_cols = self.data.select_dtypes(include=["datetime"]).columns
        if len(date_cols) > 0:
            col = date_cols[0]
            suggestions.append(
                {
                    "query": f"Show trends over time for {col}",
                    "description": f"Analyze temporal patterns in {col}",
                    "complexity": "moderate",
                }
            )

        # Categorical suggestions
        categorical_cols = self.data.select_dtypes(include=["object"]).columns
        if len(categorical_cols) > 0:
            col = categorical_cols[0]
            suggestions.append(
                {
                    "query": f"What are the most common values in {col}?",
                    "description": f"Analyze distribution of {col}",
                    "complexity": "simple",
                }
            )

        return suggestions[:10]  # Limit to top 10 suggestions

    def get_data_overview(self) -> Dict[str, Any]:
        """Get a comprehensive overview of the loaded data"""
        if self.data is None:
            return {"error": "No data loaded"}

        return {
            "shape": self.data.shape,
            "columns": list(self.data.columns),
            "data_types": self.data.dtypes.to_dict(),
            "missing_data": self.data.isnull().sum().to_dict(),
            "memory_usage": self.data.memory_usage(deep=True).sum(),
            "sample_data": self.data.head(3).to_dict(orient="records"),
            "basic_stats": (
                self.data.describe().to_dict()
                if len(self.data.select_dtypes(include=[np.number]).columns) > 0
                else {}
            ),
            "query_capabilities": self._get_query_capabilities(),
        }

    # Internal helper methods
    def _load_queryable_data(self, file_path: str, data_type_info) -> Optional[pd.DataFrame]:
        """Load data in a format suitable for querying"""
        # Reuse the profiler's loading logic
        from .profiler import DataProfiler

        profiler = DataProfiler()
        return profiler._load_data_for_profiling(file_path, data_type_info)

    def _identify_restricted_columns(self):
        """Identify columns that should be restricted based on safety level"""
        if self.data is None:
            return

        self.restricted_columns = []

        for col in self.data.columns:
            col_lower = col.lower()

            # Check against sensitive patterns
            for pattern in self.sensitive_patterns:
                if re.match(pattern, col_lower):
                    self.restricted_columns.append(col)
                    break

            # Safety level specific restrictions
            if self.safety_level == "strict":
                # In strict mode, restrict any potentially identifying information
                if any(term in col_lower for term in ["name", "address", "location"]):
                    self.restricted_columns.append(col)

    def _get_query_capabilities(self) -> List[str]:
        """Get list of available query capabilities"""
        capabilities = ["filter", "sort", "aggregate", "count", "summary"]

        if self.data is not None:
            numeric_cols = self.data.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                capabilities.extend(["statistical_analysis", "outlier_detection"])

            categorical_cols = self.data.select_dtypes(include=["object"]).columns
            if len(categorical_cols) > 0:
                capabilities.extend(["distribution_analysis", "category_breakdown"])

            date_cols = self.data.select_dtypes(include=["datetime"]).columns
            if len(date_cols) > 0:
                capabilities.extend(["time_series_analysis", "trend_analysis"])

        return capabilities

    def _suggest_initial_queries(self) -> List[str]:
        """Suggest initial queries based on data characteristics"""
        if self.data is None:
            return []

        suggestions = [
            "Show me a summary of this data",
            "What are the key patterns in this dataset?",
        ]

        # Add column-specific suggestions
        if len(self.data.columns) > 0:
            first_col = self.data.columns[0]
            suggestions.append(f"What are the unique values in {first_col}?")

        return suggestions[:5]

    def _generate_insights(self, query: SafeQuery, result: QueryResult) -> List[str]:
        """Generate AI insights from query results"""
        insights = []

        if result.data is not None and len(result.data) > 0:
            insights.append(f"Query returned {len(result.data)} records")

            # Data quality insights
            if result.data_quality_score > 0.8:
                insights.append("High data quality detected in results")
            elif result.data_quality_score < 0.6:
                insights.append("Some data quality issues found in results")

            # Pattern detection
            numeric_cols = result.data.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                for col in numeric_cols:
                    if result.data[col].std() == 0:
                        insights.append(f"Column {col} has constant values")
                    elif result.data[col].std() > result.data[col].mean():
                        insights.append(f"Column {col} shows high variability")

        return insights

    def _generate_recommendations(self, query: SafeQuery, result: QueryResult) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        if result.data is not None:
            # Size-based recommendations
            if len(result.data) == query.max_results:
                recommendations.append(
                    "Results may be truncated. Consider refining your query "
                    "for more specific results."
                )

            if len(result.data) < 10 and query.query_type == "filter":
                recommendations.append(
                    "Few results found. Consider broadening your search criteria."
                )

            # Data exploration recommendations
            if query.query_type == "filter":
                recommendations.append("Try aggregating these results for summary insights.")

            if query.query_type == "aggregate" and len(result.data) > 1:
                recommendations.append(
                    "Consider creating a visualization of these aggregated results."
                )

        return recommendations


class QueryParser:
    """Parses natural language queries into safe, structured queries"""

    def __init__(self):
        self.filter_patterns = [
            (r".*under (\$?[\d,]+)", "less_than"),
            (r".*over (\$?[\d,]+)", "greater_than"),
            (r".*between (\$?[\d,]+) and (\$?[\d,]+)", "between"),
            (r".*equal to (\w+)", "equals"),
            (r".*contains? (\w+)", "contains"),
        ]

        self.aggregation_patterns = [
            (r".*average.*", "mean"),
            (r".*sum.*", "sum"),
            (r".*count.*", "count"),
            (r".*maximum.*|.*max.*", "max"),
            (r".*minimum.*|.*min.*", "min"),
        ]

    def parse(self, request: str, schema: Dict[str, Any], **kwargs) -> SafeQuery:
        """Parse natural language request into safe query"""
        query_id = f"query_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Basic query type detection
        request_lower = request.lower()

        if any(word in request_lower for word in ["find", "show", "get", "list"]):
            query_type = "filter"
        elif any(word in request_lower for word in ["average", "sum", "count", "total"]):
            query_type = "aggregate"
        elif any(word in request_lower for word in ["sort", "order"]):
            query_type = "sort"
        else:
            query_type = "explore"

        # Create safe query
        safe_query = SafeQuery(
            query_id=query_id,
            original_request=request,
            query_type=query_type,
            max_results=kwargs.get("max_results", 1000),
            allowed_columns=schema.get("columns", []),
        )

        # Parse filters, aggregations, etc.
        safe_query.filters = self._parse_filters(request, schema)
        safe_query.aggregations = self._parse_aggregations(request, schema)
        safe_query.sort_by = self._parse_sorting(request, schema)

        return safe_query

    def _parse_filters(self, request: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Parse filter conditions from natural language"""
        filters = {}

        for pattern, filter_type in self.filter_patterns:
            match = re.search(pattern, request, re.IGNORECASE)
            if match:
                if filter_type == "less_than":
                    value = self._parse_numeric_value(match.group(1))
                    filters["numeric_filter"] = {"type": "lt", "value": value}
                elif filter_type == "greater_than":
                    value = self._parse_numeric_value(match.group(1))
                    filters["numeric_filter"] = {"type": "gt", "value": value}
                # Add more filter types as needed

        return filters

    def _parse_aggregations(self, request: str, schema: Dict[str, Any]) -> Dict[str, str]:
        """Parse aggregation operations"""
        aggregations = {}

        for pattern, agg_type in self.aggregation_patterns:
            if re.search(pattern, request, re.IGNORECASE):
                aggregations["operation"] = agg_type
                break

        return aggregations

    def _parse_sorting(self, request: str, schema: Dict[str, Any]) -> List[Dict[str, str]]:
        """Parse sorting instructions"""
        sort_by = []

        if re.search(r"sort.*by (\w+)", request, re.IGNORECASE):
            match = re.search(r"sort.*by (\w+)", request, re.IGNORECASE)
            column = match.group(1)
            if column in schema.get("columns", []):
                direction = "desc" if "descending" in request.lower() else "asc"
                sort_by.append({"column": column, "direction": direction})

        return sort_by

    def _parse_numeric_value(self, value_str: str) -> float:
        """Parse numeric value from string"""
        # Remove currency symbols and commas
        clean_str = re.sub(r"[\$,]", "", value_str)
        return float(clean_str)


class QueryExecutor:
    """Executes safe queries against pandas DataFrames"""

    def execute(self, query: SafeQuery, data: pd.DataFrame) -> QueryResult:
        """Execute a safe query and return results"""
        result = QueryResult(query_id=query.query_id, success=True)

        try:
            # Start with full dataset
            filtered_data = data.copy()

            # Apply filters
            if query.filters:
                filtered_data = self._apply_filters(filtered_data, query.filters)

            # Apply sorting
            if query.sort_by:
                filtered_data = self._apply_sorting(filtered_data, query.sort_by)

            # Apply aggregations
            if query.aggregations:
                filtered_data = self._apply_aggregations(filtered_data, query.aggregations)

            # Apply column selection
            if query.columns:
                available_cols = [col for col in query.columns if col in filtered_data.columns]
                if available_cols:
                    filtered_data = filtered_data[available_cols]

            # Apply row limit
            if query.limit:
                filtered_data = filtered_data.head(query.limit)
            elif len(filtered_data) > query.max_results:
                filtered_data = filtered_data.head(query.max_results)
                result.warnings.append(f"Results limited to {query.max_results} rows")

            # Set result data
            result.data = filtered_data
            result.row_count = len(filtered_data)
            result.columns_returned = list(filtered_data.columns)

            # Generate summary
            result.summary = self._generate_summary(filtered_data, query)

            # Calculate data quality score
            result.data_quality_score = self._calculate_quality_score(filtered_data)

        except Exception as e:
            result.success = False
            result.warnings.append(f"Execution error: {str(e)}")

        return result

    def _apply_filters(self, data: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
        """Apply filter conditions"""
        if "numeric_filter" in filters:
            nf = filters["numeric_filter"]
            numeric_cols = data.select_dtypes(include=[np.number]).columns

            if len(numeric_cols) > 0:
                col = numeric_cols[0]  # Use first numeric column
                if nf["type"] == "lt":
                    data = data[data[col] < nf["value"]]
                elif nf["type"] == "gt":
                    data = data[data[col] > nf["value"]]

        return data

    def _apply_sorting(self, data: pd.DataFrame, sort_by: List[Dict[str, str]]) -> pd.DataFrame:
        """Apply sorting"""
        for sort_item in sort_by:
            col = sort_item["column"]
            direction = sort_item["direction"]
            if col in data.columns:
                ascending = direction == "asc"
                data = data.sort_values(by=col, ascending=ascending)

        return data

    def _apply_aggregations(self, data: pd.DataFrame, aggregations: Dict[str, str]) -> pd.DataFrame:
        """Apply aggregation operations"""
        operation = aggregations.get("operation", "count")

        if operation == "count":
            return pd.DataFrame({"count": [len(data)]})
        elif operation == "mean":
            numeric_data = data.select_dtypes(include=[np.number])
            if not numeric_data.empty:
                return pd.DataFrame(numeric_data.mean()).T
        elif operation == "sum":
            numeric_data = data.select_dtypes(include=[np.number])
            if not numeric_data.empty:
                return pd.DataFrame(numeric_data.sum()).T

        return data

    def _generate_summary(self, data: pd.DataFrame, query: SafeQuery) -> Dict[str, Any]:
        """Generate summary of results"""
        summary = {
            "total_rows": len(data),
            "total_columns": len(data.columns),
            "query_type": query.query_type,
        }

        if query.query_type == "aggregate":
            summary["aggregation_results"] = True

        return summary

    def _calculate_quality_score(self, data: pd.DataFrame) -> float:
        """Calculate data quality score for results"""
        if data.empty:
            return 0.0

        # Simple quality score based on completeness
        total_cells = len(data) * len(data.columns)
        missing_cells = data.isnull().sum().sum()
        completeness = 1 - (missing_cells / total_cells) if total_cells > 0 else 0

        return completeness


class ResultFormatter:
    """Formats query results into business reports"""

    def generate_report(
        self, results: List[QueryResult], title: str, report_type: str, schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate formatted business report"""
        report = {
            "title": title,
            "generated_at": datetime.now().isoformat(),
            "report_type": report_type,
            "executive_summary": self._generate_executive_summary(results),
            "key_findings": self._extract_key_findings(results),
            "recommendations": self._compile_recommendations(results),
            "data_quality_assessment": self._assess_overall_quality(results),
            "appendix": {
                "queries_executed": len(results),
                "total_records_analyzed": sum(r.row_count for r in results),
                "data_sources": schema.get("columns", []),
            },
        }

        if report_type == "detailed":
            report["detailed_results"] = [r.to_dict() for r in results]

        return report

    def _generate_executive_summary(self, results: List[QueryResult]) -> str:
        """Generate executive summary"""
        total_records = sum(r.row_count for r in results)
        successful_queries = sum(1 for r in results if r.success)

        return (
            f"Analysis completed with {successful_queries} successful queries "
            f"examining {total_records:,} total records. "
            f"Key insights and recommendations are provided below."
        )

    def _extract_key_findings(self, results: List[QueryResult]) -> List[str]:
        """Extract key findings from all results"""
        findings = []

        for result in results:
            findings.extend(result.insights)

        # Deduplicate and prioritize
        unique_findings = list(set(findings))
        return unique_findings[:10]  # Top 10 findings

    def _compile_recommendations(self, results: List[QueryResult]) -> List[str]:
        """Compile recommendations from all results"""
        recommendations = []

        for result in results:
            recommendations.extend(result.recommendations)

        # Deduplicate
        return list(set(recommendations))

    def _assess_overall_quality(self, results: List[QueryResult]) -> Dict[str, Any]:
        """Assess overall data quality across results"""
        if not results:
            return {"overall_score": 0.0, "assessment": "No data analyzed"}

        avg_quality = sum(r.data_quality_score for r in results) / len(results)

        return {
            "overall_score": avg_quality,
            "assessment": "High" if avg_quality > 0.8 else "Medium" if avg_quality > 0.6 else "Low",
            "queries_analyzed": len(results),
        }
