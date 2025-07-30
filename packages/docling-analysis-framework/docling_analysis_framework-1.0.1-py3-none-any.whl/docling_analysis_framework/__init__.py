"""
Docling Analysis Framework

AI-ready analysis framework for PDF and Office documents using Docling.
Simple API for document analysis, chunking, and AI/ML preparation.

Quick Start:
    import docling_analysis_framework as daf

    # Basic analysis
    result = daf.analyze("document.pdf")

    # Smart chunking
    chunks = daf.chunk("document.pdf")

    # Enhanced analysis with chunking
    enhanced = daf.analyze_enhanced("document.pdf")
"""

import json
import logging
from typing import Dict, List, Any, Union
from pathlib import Path

from .core.analyzer import DoclingAnalyzer, DocumentTypeInfo, SpecializedAnalysis
from .core.chunking import (DoclingChunkingOrchestrator, DocumentChunk,
                            ChunkingConfig, StructuralChunkingStrategy,
                            TableAwareChunkingStrategy,
                            PageAwareChunkingStrategy)

# Package version
__version__ = "1.0.0"

# Setup logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Global instances for simple API
_analyzer = None
_orchestrator = None


def _get_analyzer() -> DoclingAnalyzer:
    """Get global analyzer instance"""
    global _analyzer
    if _analyzer is None:
        _analyzer = DoclingAnalyzer()
    return _analyzer


def _get_orchestrator() -> DoclingChunkingOrchestrator:
    """Get global orchestrator instance"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = DoclingChunkingOrchestrator()
    return _orchestrator


def analyze(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Analyze a document using Docling extraction

    Args:
        file_path: Path to the document file

    Returns:
        Dictionary containing analysis results

    Example:
        result = daf.analyze("document.pdf")
        print(f"Type: {result['document_type'].type_name}")
        print(f"Pages: {result['document_type'].pages}")
    """
    analyzer = _get_analyzer()
    return analyzer.analyze_document(str(file_path))


def chunk(file_path: Union[str, Path], strategy: str = "auto",
          max_chunk_size: int = 2000, overlap_size: int = 200) -> List[DocumentChunk]:
    """
    Chunk a document into AI-ready pieces

    Args:
        file_path: Path to the document file
        strategy: Chunking strategy ("auto", "structural", "table_aware", "page_aware")
        max_chunk_size: Maximum size of each chunk in characters
        overlap_size: Overlap between chunks in characters

    Returns:
        List of DocumentChunk objects

    Example:
        chunks = daf.chunk("document.pdf", strategy="structural")
        for chunk in chunks:
            print(f"Chunk {chunk.chunk_id}: {chunk.token_count} tokens")
    """
    # First analyze the document
    analyzer = _get_analyzer()
    result = analyzer.analyze_document(str(file_path))

    if 'error' in result:
        raise ValueError(f"Cannot analyze document for chunking: {result['error']}")

    # Create orchestrator with custom parameters
    orchestrator = DoclingChunkingOrchestrator(
        max_chunk_size=max_chunk_size,
        overlap_size=overlap_size
    )

    # Mock docling result for chunking (in practice, this would be passed from analyzer)
    class MockDoclingResult:
        def __init__(self, markdown_content, pages=None):
            self.markdown_content = markdown_content
            self.pages = pages or []

    mock_docling_result = MockDoclingResult(
        result.get('markdown_content', ''),
        [1] * (result['document_type'].pages or 1)
    )

    # Convert analysis format for chunking
    chunking_analysis = {
        'document_type': {
            'type_name': result['document_type'].type_name,
            'confidence': result['document_type'].confidence
        },
        'analysis': result['analysis']
    }

    return orchestrator.chunk_document(
        str(file_path),
        result.get('markdown_content', ''),
        mock_docling_result,
        chunking_analysis,
        strategy=strategy
    )


def analyze_enhanced(file_path: Union[str, Path],
                     chunking_strategy: str = "auto") -> Dict[str, Any]:
    """
    Perform enhanced analysis with both document analysis and chunking

    Args:
        file_path: Path to the document file
        chunking_strategy: Strategy for chunking ("auto", "structural",
                           "table_aware", "page_aware")

    Returns:
        Dictionary containing both analysis and chunks

    Example:
        enhanced = daf.analyze_enhanced("document.pdf")
        print(f"Document: {enhanced['analysis']['document_type'].type_name}")
        print(f"Chunks: {len(enhanced['chunks'])}")
    """
    # Get analysis
    analysis_result = analyze(file_path)

    if 'error' in analysis_result:
        return analysis_result

    # Get chunks
    chunks = chunk(file_path, strategy=chunking_strategy)

    # Combine results
    return {
        'file_path': str(file_path),
        'analysis': analysis_result,
        'chunks': chunks,
        'chunk_count': len(chunks),
        'total_tokens': sum(chunk.token_count or 0 for chunk in chunks),
        'chunking_strategy': chunking_strategy
    }


def get_supported_formats() -> List[str]:
    """
    Get list of supported document formats

    Returns:
        List of supported file extensions
    """
    analyzer = _get_analyzer()
    return analyzer.get_supported_formats()


def save_chunks_to_json(chunks: List[DocumentChunk], output_path: Union[str, Path],
                        include_metadata: bool = True) -> None:
    """
    Save chunks to JSON file

    Args:
        chunks: List of DocumentChunk objects
        output_path: Path to save JSON file
        include_metadata: Whether to include chunk metadata

    Example:
        chunks = daf.chunk("document.pdf")
        daf.save_chunks_to_json(chunks, "chunks.json")
    """
    chunks_data = []

    for chunk in chunks:
        chunk_dict = {
            "chunk_id": chunk.chunk_id,
            "content": chunk.content,
            "chunk_type": chunk.chunk_type,
            "token_count": chunk.token_count,
            "start_position": chunk.start_position,
            "end_position": chunk.end_position
        }

        if include_metadata:
            chunk_dict["metadata"] = chunk.metadata

        chunks_data.append(chunk_dict)

    # Create output data
    output_data = {
        "total_chunks": len(chunks_data),
        "framework": "docling-analysis-framework",
        "version": __version__,
        "chunks": chunks_data
    }

    # Write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)


def save_analysis_to_json(analysis_result: Dict[str, Any],
                          output_path: Union[str, Path]) -> None:
    """
    Save analysis result to JSON file

    Args:
        analysis_result: Result from analyze() or analyze_enhanced()
        output_path: Path to save JSON file

    Example:
        result = daf.analyze("document.pdf")
        daf.save_analysis_to_json(result, "analysis.json")
    """
    # Convert analysis to JSON-serializable format
    serializable_data = _make_serializable(analysis_result)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(serializable_data, f, indent=2, ensure_ascii=False)


def _make_serializable(obj: Any) -> Any:
    """Convert objects to JSON-serializable format"""
    if isinstance(obj, dict):
        return {key: _make_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [_make_serializable(item) for item in obj]
    elif isinstance(obj, (DocumentTypeInfo, SpecializedAnalysis)):
        return obj.__dict__
    elif isinstance(obj, DocumentChunk):
        return {
            "chunk_id": obj.chunk_id,
            "content": obj.content,
            "chunk_type": obj.chunk_type,
            "metadata": obj.metadata,
            "token_count": obj.token_count,
            "start_position": obj.start_position,
            "end_position": obj.end_position
        }
    else:
        return obj


# Export main classes for advanced usage
__all__ = [
    # Simple API functions
    'analyze',
    'chunk',
    'analyze_enhanced',
    'get_supported_formats',
    'save_chunks_to_json',
    'save_analysis_to_json',

    # Core classes for advanced usage
    'DoclingAnalyzer',
    'DoclingChunkingOrchestrator',
    'DocumentChunk',
    'ChunkingConfig',
    'DocumentTypeInfo',
    'SpecializedAnalysis',

    # Chunking strategies
    'StructuralChunkingStrategy',
    'TableAwareChunkingStrategy',
    'PageAwareChunkingStrategy',

    # Version
    '__version__'
]
