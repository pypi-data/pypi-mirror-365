"""
Data Analysis Framework

AI-powered analysis framework for structured data files and databases.
Provides intelligent schema detection, data profiling, and safe AI-agent interaction APIs.

Unlike document frameworks, this focuses on structured data interaction rather than chunking,
enabling AI agents to safely query and analyze tabular data, databases, and configuration files.
"""

__version__ = "1.0.0"
__author__ = "AI Building Blocks"

# Core components
from .core.analyzer import DataAnalyzer, DataTypeInfo, StructuredAnalysis
from .core.profiler import DataProfiler, SchemaInfo, QualityMetrics
from .core.agent_interface import AgentQueryInterface, SafeQuery, QueryResult


# Simple API functions
def analyze(file_path: str, **kwargs):
    """
    🎯 One-line analysis for structured data files

    Args:
        file_path: Path to data file (Excel, CSV, SQL, JSON, etc.)
        **kwargs: Additional analysis options

    Returns:
        dict: Complete analysis results with schema, quality metrics, and insights

    Example:
        >>> result = analyze("sales_data.xlsx")
        >>> print(f"Detected {len(result['tables'])} tables")
        >>> print(f"Quality score: {result['quality_score']:.2f}")
    """
    analyzer = DataAnalyzer()
    return analyzer.analyze_file(file_path, **kwargs)


def profile_data(file_path: str, **kwargs):
    """
    📊 Generate comprehensive data profile

    Args:
        file_path: Path to data file
        **kwargs: Profiling options (include_samples, detect_pii, etc.)

    Returns:
        dict: Detailed data profile with statistics, distributions, and patterns
    """
    profiler = DataProfiler()
    return profiler.generate_profile(file_path, **kwargs)


def create_agent_interface(file_path: str, **kwargs):
    """
    🤖 Create safe AI-agent interaction interface

    Args:
        file_path: Path to data file
        **kwargs: Interface configuration options

    Returns:
        AgentQueryInterface: Safe query interface for AI agents

    Example:
        >>> interface = create_agent_interface("inventory.xlsx")
        >>> result = interface.execute_query("Find cars under $25000 with good condition")
        >>> report = interface.generate_report(result, "Budget car recommendations")
    """
    interface = AgentQueryInterface()
    interface.load_data(file_path, **kwargs)
    return interface


def get_supported_formats():
    """
    📋 List all supported data formats

    Returns:
        list: Supported file extensions and data sources
    """
    return [
        # Spreadsheets & Tables
        ".xlsx",
        ".xls",
        ".csv",
        ".tsv",
        ".parquet",
        # Structured Data
        ".json",
        ".jsonl",
        ".yaml",
        ".yml",
        ".toml",
        ".ini",
        # Database
        ".sqlite",
        ".db",
        ".sql",
        # Configuration
        ".env",
        ".conf",
        ".cfg",
    ]


# Export main classes and functions
__all__ = [
    # Simple API
    "analyze",
    "profile_data",
    "create_agent_interface",
    "get_supported_formats",
    # Core classes
    "DataAnalyzer",
    "DataProfiler",
    "AgentQueryInterface",
    # Data structures
    "DataTypeInfo",
    "StructuredAnalysis",
    "SchemaInfo",
    "QualityMetrics",
    "SafeQuery",
    "QueryResult",
    # Version info
    "__version__",
    "__author__",
]
