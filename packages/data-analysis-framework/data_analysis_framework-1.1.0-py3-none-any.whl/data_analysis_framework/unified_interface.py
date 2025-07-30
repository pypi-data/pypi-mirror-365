"""Unified interface compatibility layer for data-analysis-framework.

This module provides a consistent interface wrapper that ensures all analysis 
results have the same access patterns regardless of the underlying implementation.
"""

from typing import Dict, Any, Optional, List


class UnifiedAnalysisResult:
    """Wrapper to provide consistent interface for data-analysis-framework results.
    
    This class provides:
    - Dictionary-style access: result['key']
    - Attribute access: result.key
    - Consistent method interface: result.to_dict()
    """
    
    def __init__(self, data_analysis_result: Dict[str, Any]):
        """Initialize with a data analysis result dictionary.
        
        Args:
            data_analysis_result: The raw analysis result from DataAnalyzer.analyze_file()
        """
        self._raw = data_analysis_result
        self._dict_cache = None
    
    @property
    def document_type(self) -> str:
        """Get the document type."""
        # Map from data_type.type_name
        if isinstance(self._raw, dict) and 'data_type' in self._raw:
            data_type_obj = self._raw['data_type']
            if hasattr(data_type_obj, 'type_name'):
                # Convert data types to more descriptive names
                type_name = data_type_obj.type_name
                type_map = {
                    'excel': 'Excel Spreadsheet',
                    'csv': 'CSV Data',
                    'json': 'JSON Data',
                    'sql': 'SQL Database',
                    'parquet': 'Parquet Data',
                    'xml': 'XML Data'
                }
                return type_map.get(type_name, f'{type_name.title()} Data')
            elif isinstance(data_type_obj, dict):
                type_name = data_type_obj.get('type_name', 'unknown')
                return f'{type_name.title()} Data'
        return 'unknown'
    
    @property
    def confidence(self) -> float:
        """Get the confidence score."""
        # For structured data, confidence is based on quality score
        if 'analysis' in self._raw:
            analysis_obj = self._raw['analysis']
            if hasattr(analysis_obj, 'quality_score'):
                return float(analysis_obj.quality_score)
            elif isinstance(analysis_obj, dict) and 'quality_score' in analysis_obj:
                return float(analysis_obj['quality_score'])
        return 0.8  # Default confidence for structured data
    
    @property
    def metadata(self) -> Dict[str, Any]:
        """Get metadata dictionary."""
        metadata = {}
        
        # Add file metadata
        if 'file_path' in self._raw:
            metadata['file_path'] = self._raw['file_path']
        
        # Add data type metadata
        if 'data_type' in self._raw:
            data_type_obj = self._raw['data_type']
            if hasattr(data_type_obj, 'tables_count'):
                metadata['tables_count'] = data_type_obj.tables_count
            if hasattr(data_type_obj, 'total_rows'):
                metadata['total_rows'] = data_type_obj.total_rows
            if hasattr(data_type_obj, 'total_columns'):
                metadata['total_columns'] = data_type_obj.total_columns
            if hasattr(data_type_obj, 'file_size_mb'):
                metadata['file_size_mb'] = data_type_obj.file_size_mb
            if hasattr(data_type_obj, 'sheets_or_tables') and data_type_obj.sheets_or_tables:
                metadata['sheets_or_tables'] = data_type_obj.sheets_or_tables
            if hasattr(data_type_obj, 'encoding'):
                metadata['encoding'] = data_type_obj.encoding
        
        # Add analysis metadata
        if 'analysis' in self._raw:
            analysis_obj = self._raw['analysis']
            if hasattr(analysis_obj, 'completeness_ratio'):
                metadata['completeness_ratio'] = analysis_obj.completeness_ratio
            if hasattr(analysis_obj, 'query_complexity'):
                metadata['query_complexity'] = analysis_obj.query_complexity
        
        # Add AI readiness
        if 'ai_readiness' in self._raw:
            metadata['ai_readiness'] = self._raw['ai_readiness']
        
        return metadata
    
    @property
    def content(self) -> str:
        """Get extracted content."""
        # For structured data, provide a summary instead of raw content
        content_parts = []
        
        if 'data_type' in self._raw:
            data_type_obj = self._raw['data_type']
            content_parts.append(f"Data Type: {self.document_type}")
            
            if hasattr(data_type_obj, 'total_rows') and hasattr(data_type_obj, 'total_columns'):
                content_parts.append(f"Shape: {data_type_obj.total_rows} rows × {data_type_obj.total_columns} columns")
            
            if hasattr(data_type_obj, 'column_types') and data_type_obj.column_types:
                content_parts.append(f"Columns: {', '.join(list(data_type_obj.column_types.keys())[:5])}")
                if len(data_type_obj.column_types) > 5:
                    content_parts.append(f"... and {len(data_type_obj.column_types) - 5} more columns")
        
        if 'analysis' in self._raw:
            analysis_obj = self._raw['analysis']
            if hasattr(analysis_obj, 'detected_patterns') and analysis_obj.detected_patterns:
                content_parts.append(f"Patterns: {', '.join(analysis_obj.detected_patterns[:3])}")
            if hasattr(analysis_obj, 'business_metrics') and analysis_obj.business_metrics:
                content_parts.append(f"Metrics: {len(analysis_obj.business_metrics)} business metrics detected")
        
        return '\n'.join(content_parts) if content_parts else 'No content summary available'
    
    @property
    def ai_opportunities(self) -> List[str]:
        """Get AI processing opportunities."""
        opportunities = []
        
        # Get from analysis.recommended_operations
        if 'analysis' in self._raw:
            analysis_obj = self._raw['analysis']
            if hasattr(analysis_obj, 'recommended_operations'):
                opportunities.extend(analysis_obj.recommended_operations)
            elif isinstance(analysis_obj, dict) and 'recommended_operations' in analysis_obj:
                opportunities.extend(analysis_obj['recommended_operations'])
        
        # Add from agent_capabilities
        if 'agent_capabilities' in self._raw and isinstance(self._raw['agent_capabilities'], list):
            opportunities.extend(self._raw['agent_capabilities'])
        
        # Add generic opportunities based on data type
        if not opportunities and 'data_type' in self._raw:
            data_type_obj = self._raw['data_type']
            if hasattr(data_type_obj, 'type_name'):
                type_name = data_type_obj.type_name
                if type_name in ['excel', 'csv']:
                    opportunities = [
                        'Data profiling and quality assessment',
                        'Statistical analysis and visualization',
                        'Anomaly detection',
                        'Predictive modeling'
                    ]
                elif type_name == 'json':
                    opportunities = [
                        'Schema validation',
                        'Data transformation',
                        'API integration',
                        'Configuration management'
                    ]
        
        return opportunities
    
    @property
    def framework(self) -> str:
        """Get the framework name."""
        return 'data-analysis-framework'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for compatibility."""
        if self._dict_cache is None:
            self._dict_cache = {
                'document_type': self.document_type,
                'confidence': self.confidence,
                'metadata': self.metadata,
                'content': self.content,
                'ai_opportunities': self.ai_opportunities,
                'framework': self.framework,
                'raw_analysis': self._raw
            }
            
            # Add top-level fields from raw that aren't already included
            for key, value in self._raw.items():
                if key not in self._dict_cache:
                    # Only include serializable values
                    if isinstance(value, (str, int, float, bool, list, dict, type(None))):
                        self._dict_cache[key] = value
        
        return self._dict_cache
    
    def get(self, key: str, default=None):
        """Dict-like access with default value."""
        return self.to_dict().get(key, default)
    
    def __getitem__(self, key: str):
        """Support result['key'] syntax."""
        return self.to_dict()[key]
    
    def __contains__(self, key: str) -> bool:
        """Support 'key in result' syntax."""
        return key in self.to_dict()
    
    def keys(self):
        """Get dictionary keys."""
        return self.to_dict().keys()
    
    def values(self):
        """Get dictionary values."""
        return self.to_dict().values()
    
    def items(self):
        """Get dictionary items."""
        return self.to_dict().items()
    
    def __getattr__(self, name):
        """Proxy attribute access to the raw object."""
        # First check if it's in the raw dict
        if isinstance(self._raw, dict) and name in self._raw:
            return self._raw[name]
        # Otherwise raise AttributeError
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
    
    def __repr__(self):
        """String representation."""
        return f"UnifiedAnalysisResult(document_type='{self.document_type}', framework='{self.framework}')" 