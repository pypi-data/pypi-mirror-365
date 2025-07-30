"""Unified interface compatibility layer for docling-analysis-framework.

This module provides a consistent interface wrapper that ensures all analysis 
results have the same access patterns regardless of the underlying implementation.
"""

from typing import Dict, Any, Optional, List


class UnifiedAnalysisResult:
    """Wrapper to provide consistent interface for docling-analysis-framework results.
    
    This class provides:
    - Dictionary-style access: result['key']
    - Attribute access: result.key
    - Consistent method interface: result.to_dict()
    """
    
    def __init__(self, docling_result: Dict[str, Any]):
        """Initialize with a docling analysis result dictionary.
        
        Args:
            docling_result: The raw analysis result from DoclingAnalyzer.analyze_document()
        """
        self._raw = docling_result
        self._dict_cache = None
    
    @property
    def document_type(self) -> str:
        """Get the document type."""
        # Navigate the nested structure: result['document_type'].type_name
        if isinstance(self._raw, dict) and 'document_type' in self._raw:
            doc_type_obj = self._raw['document_type']
            if hasattr(doc_type_obj, 'type_name'):
                return doc_type_obj.type_name
            elif isinstance(doc_type_obj, dict):
                return doc_type_obj.get('type_name', 'unknown')
        return 'unknown'
    
    @property
    def confidence(self) -> float:
        """Get the confidence score."""
        # Direct confidence field or from document_type
        if 'confidence' in self._raw:
            return float(self._raw['confidence'])
        elif 'document_type' in self._raw:
            doc_type_obj = self._raw['document_type']
            if hasattr(doc_type_obj, 'confidence'):
                return float(doc_type_obj.confidence)
            elif isinstance(doc_type_obj, dict):
                return float(doc_type_obj.get('confidence', 1.0))
        return 1.0
    
    @property
    def metadata(self) -> Dict[str, Any]:
        """Get metadata dictionary."""
        # Combine various metadata fields
        metadata = {}
        
        # Add file metadata
        if 'file_path' in self._raw:
            metadata['file_path'] = self._raw['file_path']
        if 'file_size' in self._raw:
            metadata['file_size'] = self._raw['file_size']
        if 'processing_time' in self._raw:
            metadata['processing_time'] = self._raw['processing_time']
        if 'processing_duration_seconds' in self._raw:
            metadata['processing_duration_seconds'] = self._raw['processing_duration_seconds']
        
        # Add document type metadata
        if 'document_type' in self._raw:
            doc_type_obj = self._raw['document_type']
            if hasattr(doc_type_obj, 'pages') and doc_type_obj.pages:
                metadata['pages'] = doc_type_obj.pages
            elif isinstance(doc_type_obj, dict) and 'pages' in doc_type_obj:
                metadata['pages'] = doc_type_obj['pages']
            
            if hasattr(doc_type_obj, 'version') and doc_type_obj.version:
                metadata['version'] = doc_type_obj.version
            elif isinstance(doc_type_obj, dict) and 'version' in doc_type_obj:
                metadata['version'] = doc_type_obj['version']
        
        # Add analysis metadata if available
        if 'analysis' in self._raw:
            analysis_obj = self._raw['analysis']
            if hasattr(analysis_obj, 'metadata') and analysis_obj.metadata:
                metadata.update(analysis_obj.metadata)
            elif isinstance(analysis_obj, dict) and 'metadata' in analysis_obj:
                metadata.update(analysis_obj['metadata'])
        
        return metadata
    
    @property
    def content(self) -> str:
        """Get extracted content."""
        # Use markdown_content if available
        if 'markdown_content' in self._raw:
            return self._raw['markdown_content']
        
        # Fallback to content from analysis
        if 'analysis' in self._raw:
            analysis_obj = self._raw['analysis']
            if hasattr(analysis_obj, 'content'):
                return analysis_obj.content
            elif isinstance(analysis_obj, dict) and 'content' in analysis_obj:
                return analysis_obj['content']
        
        return ''
    
    @property
    def ai_opportunities(self) -> List[str]:
        """Get AI processing opportunities."""
        # Get from analysis.ai_use_cases
        if 'analysis' in self._raw:
            analysis_obj = self._raw['analysis']
            if hasattr(analysis_obj, 'ai_use_cases'):
                return analysis_obj.ai_use_cases
            elif isinstance(analysis_obj, dict) and 'ai_use_cases' in analysis_obj:
                return analysis_obj['ai_use_cases']
        return []
    
    @property
    def framework(self) -> str:
        """Get the framework name."""
        return 'docling-analysis-framework'
    
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
                if key not in self._dict_cache and key not in ['markdown_content']:
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