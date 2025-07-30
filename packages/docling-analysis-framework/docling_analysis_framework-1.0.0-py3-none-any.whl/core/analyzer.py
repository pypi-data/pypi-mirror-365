#!/usr/bin/env python3
"""
Docling Analysis Framework - Core Analyzer
Leverages Docling for document extraction with AI preparation layer
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
import traceback

try:
    from docling.document_converter import DocumentConverter
    DOCLING_AVAILABLE = True
except ImportError:
    DOCLING_AVAILABLE = False
    DocumentConverter = None

# Setup logging with better formatting
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class DocumentTypeInfo:
    """Information about detected document type"""
    type_name: str
    confidence: float
    category: str
    version: Optional[str] = None
    subtype: Optional[str] = None
    encoding: Optional[str] = None
    pages: Optional[int] = None
    extraction_method: Optional[str] = None


@dataclass
class SpecializedAnalysis:
    """Specialized analysis results for AI/ML processing"""
    document_type: str
    category: str
    key_findings: Dict[str, Any]
    ai_use_cases: List[str]
    quality_metrics: Optional[Dict[str, float]] = None
    structured_data: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    extraction_quality: Optional[Dict[str, Any]] = None


class DoclingHandler(ABC):
    """Abstract base class for Docling-based document handlers"""

    @abstractmethod
    def can_handle(self, file_path: str, file_extension: str) -> Tuple[bool, float]:
        """
        Determine if this handler can process the document
        Returns: (can_handle, confidence_score)
        """
        pass

    @abstractmethod
    def detect_type(self, file_path: str, docling_result: Any) -> DocumentTypeInfo:
        """Detect specific document type information from Docling result"""
        pass

    @abstractmethod
    def analyze(self, file_path: str, docling_result: Any) -> SpecializedAnalysis:
        """Perform specialized analysis of the document using Docling extraction"""
        pass

    @abstractmethod
    def extract_key_data(self, file_path: str, docling_result: Any) -> Dict[str, Any]:
        """Extract key structured data from Docling result"""
        pass


class PDFHandler(DoclingHandler):
    """Handler for PDF documents using Docling"""

    def can_handle(self, file_path: str, file_extension: str) -> Tuple[bool, float]:
        if file_extension.lower() == '.pdf':
            return True, 0.95
        return False, 0.0

    def detect_type(self, file_path: str, docling_result: Any) -> DocumentTypeInfo:
        # Extract metadata from Docling result
        pages = len(docling_result.pages) if hasattr(docling_result, 'pages') else None

        # Try to determine PDF subtype based on content
        markdown_content = docling_result.document.export_to_markdown()
        subtype = self._detect_pdf_subtype(markdown_content)

        return DocumentTypeInfo(
            type_name="PDF Document",
            confidence=0.95,
            category="office",
            subtype=subtype,
            pages=pages,
            extraction_method="docling"
        )

    def _detect_pdf_subtype(self, content: str) -> str:
        """Detect PDF subtype from extracted content"""
        content_lower = content.lower()

        # Check for academic paper indicators
        if any(term in content_lower for term in ['abstract', 'introduction',
                                                  'methodology', 'references',
                                                  'bibliography']):
            return "academic_paper"

        # Check for report indicators
        if any(term in content_lower for term in ['executive summary', 'findings',
                                                  'recommendations', 'conclusion']):
            return "report"

        # Check for financial document indicators
        if any(term in content_lower for term in ['financial', 'balance sheet',
                                                  'income statement', 'cash flow']):
            return "financial"

        # Check for legal document indicators
        if any(term in content_lower for term in ['whereas', 'therefore',
                                                  'party of the first part',
                                                  'contract', 'agreement']):
            return "legal"

        return "general"

    def analyze(self, file_path: str, docling_result: Any) -> SpecializedAnalysis:
        findings = self.extract_key_data(file_path, docling_result)

        # Analyze extraction quality
        extraction_quality = self._assess_extraction_quality(docling_result)

        return SpecializedAnalysis(
            document_type="PDF Document",
            category="office",
            key_findings=findings,
            ai_use_cases=[
                "Document classification and categorization",
                "Content extraction and indexing",
                "Semantic search and retrieval",
                "Document summarization",
                "Question answering over documents",
                "Citation and reference extraction",
                "Table and figure analysis",
                "Multi-modal document understanding",
                "Compliance and regulatory analysis",
                "Knowledge graph construction"
            ],
            quality_metrics={
                "extraction_quality": extraction_quality.get("overall_score", 0.8),
                "text_coverage": extraction_quality.get("text_coverage", 0.9),
                "structure_preservation": extraction_quality.get("structure_score", 0.7),
                "ai_readiness": 0.9
            },
            structured_data=findings,
            extraction_quality=extraction_quality
        )

    def extract_key_data(self, file_path: str, docling_result: Any) -> Dict[str, Any]:
        data = {
            "file_size": os.path.getsize(file_path),
            "format": "PDF",
            "extraction_method": "docling"
        }

        # Extract basic document info
        if hasattr(docling_result, 'pages'):
            data["page_count"] = len(docling_result.pages)

        # Export to markdown for analysis
        markdown_content = docling_result.document.export_to_markdown()
        data["extracted_text_length"] = len(markdown_content)
        data["word_count"] = len(markdown_content.split())

        # Analyze document structure from markdown
        lines = markdown_content.split('\n')
        data["line_count"] = len(lines)

        # Count structural elements
        headers = [line for line in lines if line.startswith('#')]
        data["header_count"] = len(headers)

        # Count tables (Docling converts tables to markdown format)
        table_indicators = [line for line in lines if '|' in line and line.count('|') > 2]
        data["table_rows"] = len(table_indicators)

        # Check for figures/images
        figure_indicators = [line for line in lines if line.startswith('![')]
        data["figure_count"] = len(figure_indicators)

        # Extract metadata if available
        if hasattr(docling_result.document, 'meta'):
            meta = docling_result.document.meta
            if hasattr(meta, 'title') and meta.title:
                data["title"] = meta.title
            if hasattr(meta, 'authors') and meta.authors:
                data["authors"] = meta.authors

        return data

    def _assess_extraction_quality(self, docling_result: Any) -> Dict[str, Any]:
        """Assess the quality of Docling's extraction"""
        quality = {
            "overall_score": 0.8,  # Default score
            "text_coverage": 0.9,
            "structure_score": 0.7,
            "confidence": 0.85
        }

        # Check if we have actual content
        markdown_content = docling_result.document.export_to_markdown()
        if len(markdown_content.strip()) < 100:
            quality["overall_score"] = 0.3
            quality["text_coverage"] = 0.2

        # Check for structural elements
        if '#' in markdown_content:  # Headers preserved
            quality["structure_score"] += 0.1
        if '|' in markdown_content:  # Tables preserved
            quality["structure_score"] += 0.1
        if '![' in markdown_content:  # Images/figures referenced
            quality["structure_score"] += 0.1

        quality["structure_score"] = min(quality["structure_score"], 1.0)

        return quality


class DOCXHandler(DoclingHandler):
    """Handler for DOCX documents using Docling"""

    def can_handle(self, file_path: str, file_extension: str) -> Tuple[bool, float]:
        if file_extension.lower() == '.docx':
            return True, 0.95
        return False, 0.0

    def detect_type(self, file_path: str, docling_result: Any) -> DocumentTypeInfo:
        return DocumentTypeInfo(
            type_name="DOCX Document",
            confidence=0.95,
            category="office",
            subtype="wordprocessing",
            extraction_method="docling"
        )

    def analyze(self, file_path: str, docling_result: Any) -> SpecializedAnalysis:
        findings = self.extract_key_data(file_path, docling_result)

        return SpecializedAnalysis(
            document_type="DOCX Document",
            category="office",
            key_findings=findings,
            ai_use_cases=[
                "Document content extraction and analysis",
                "Template identification and processing",
                "Style and formatting analysis",
                "Document conversion and transformation",
                "Contract and legal document processing",
                "Academic writing analysis",
                "Corporate document management",
                "Content versioning and tracking"
            ],
            quality_metrics={
                "extraction_quality": 0.9,
                "structure_preservation": 0.85,
                "ai_readiness": 0.9
            },
            structured_data=findings
        )

    def extract_key_data(self, file_path: str, docling_result: Any) -> Dict[str, Any]:
        data = {
            "file_size": os.path.getsize(file_path),
            "format": "DOCX",
            "extraction_method": "docling"
        }

        # Extract content
        markdown_content = docling_result.document.export_to_markdown()
        data["extracted_text_length"] = len(markdown_content)
        data["word_count"] = len(markdown_content.split())

        # Analyze structure
        lines = markdown_content.split('\n')
        headers = [line for line in lines if line.startswith('#')]
        data["header_count"] = len(headers)

        return data


class GenericDoclingHandler(DoclingHandler):
    """Fallback handler for documents that Docling can process"""

    def can_handle(self, file_path: str, file_extension: str) -> Tuple[bool, float]:
        # This is a fallback, so low confidence
        supported_extensions = ['.pptx', '.xlsx', '.png', '.jpg', '.jpeg', '.tiff']
        if file_extension.lower() in supported_extensions:
            return True, 0.3
        return False, 0.0

    def detect_type(self, file_path: str, docling_result: Any) -> DocumentTypeInfo:
        file_ext = Path(file_path).suffix.lower()

        type_mapping = {
            '.pptx': 'PowerPoint Presentation',
            '.xlsx': 'Excel Spreadsheet',
            '.png': 'PNG Image',
            '.jpg': 'JPEG Image',
            '.jpeg': 'JPEG Image',
            '.tiff': 'TIFF Image'
        }

        type_name = type_mapping.get(file_ext, f"Document ({file_ext})")

        return DocumentTypeInfo(
            type_name=type_name,
            confidence=0.7,
            category="office",
            extraction_method="docling"
        )

    def analyze(self, file_path: str, docling_result: Any) -> SpecializedAnalysis:
        findings = self.extract_key_data(file_path, docling_result)

        return SpecializedAnalysis(
            document_type=findings.get("document_type", "Unknown Document"),
            category="office",
            key_findings=findings,
            ai_use_cases=[
                "Content extraction and indexing",
                "Document classification",
                "Multi-modal analysis",
                "Information extraction"
            ],
            quality_metrics={"ai_readiness": 0.7},
            structured_data=findings
        )

    def extract_key_data(self, file_path: str, docling_result: Any) -> Dict[str, Any]:
        file_ext = Path(file_path).suffix.lower()

        data = {
            "file_size": os.path.getsize(file_path),
            "format": file_ext.upper().lstrip('.'),
            "extraction_method": "docling",
            "document_type": f"Document ({file_ext})"
        }

        # Try to extract content
        try:
            markdown_content = docling_result.document.export_to_markdown()
            data["extracted_text_length"] = len(markdown_content)
            data["word_count"] = len(markdown_content.split())
        except Exception:
            data["extracted_text_length"] = 0
            data["word_count"] = 0

        return data


class DoclingAnalyzer:
    """Main document analysis engine using Docling"""

    def __init__(self, max_file_size_mb: Optional[float] = None):
        if not DOCLING_AVAILABLE:
            raise ImportError("Docling is not available. Please install with: pip install docling")

        self.max_file_size_mb = max_file_size_mb
        self.handlers = []
        self._initialize_handlers()

        # Initialize Docling converter
        self.converter = DocumentConverter()

    def _initialize_handlers(self):
        """Initialize all available handlers"""
        self.handlers = [
            PDFHandler(),
            DOCXHandler(),
            GenericDoclingHandler(),  # Fallback for other Docling-supported formats
        ]

    def _validate_file_size(self, file_path: str) -> bool:
        """Check if file size is within limits"""
        if self.max_file_size_mb is None:
            return True

        try:
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            return file_size_mb <= self.max_file_size_mb
        except OSError:
            return False

    def _find_best_handler(self, file_path: str) -> DoclingHandler:
        """Find the handler with highest confidence"""
        file_extension = Path(file_path).suffix
        best_handler = None
        best_confidence = 0.0

        for handler in self.handlers:
            try:
                can_handle, confidence = handler.can_handle(file_path, file_extension)
                if can_handle and confidence > best_confidence:
                    best_handler = handler
                    best_confidence = confidence
            except Exception as e:
                logger.warning(f"Handler {handler.__class__.__name__} failed: {e}")

        return best_handler or self.handlers[-1]  # Fallback to generic

    def analyze_document(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze a document and return comprehensive results using Docling
        """
        start_time = datetime.now()
        logger.info(f"Starting analysis of document: {file_path}")

        try:
            # Validate file exists and size
            if not os.path.exists(file_path):
                error_msg = f"File not found: {file_path}"
                logger.error(error_msg)
                raise FileNotFoundError(error_msg)

            if not self._validate_file_size(file_path):
                file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
                error_msg = (f"File too large: {file_path} ({file_size_mb:.1f} MB, "
                             f"max: {self.max_file_size_mb} MB)")
                logger.error(error_msg)
                raise ValueError(error_msg)

            logger.info(f"File validation passed for: {file_path}")

            # Use Docling to extract document content
            try:
                logger.info("Starting Docling extraction...")
                docling_result = self.converter.convert(file_path)
                logger.info("Docling extraction completed successfully")
            except Exception as e:
                error_msg = f"Docling extraction failed for {file_path}: {str(e)}"
                logger.error(error_msg)
                raise RuntimeError(error_msg) from e

            # Find best handler
            handler = self._find_best_handler(file_path)
            logger.info(f"Selected handler: {handler.__class__.__name__}")

            # Perform analysis
            try:
                document_type = handler.detect_type(file_path, docling_result)
                analysis = handler.analyze(file_path, docling_result)
                logger.info(f"Handler analysis completed: {document_type.type_name}")
            except Exception as e:
                error_msg = f"Handler analysis failed: {str(e)}"
                logger.error(error_msg)
                raise RuntimeError(error_msg) from e

            # Extract markdown content for additional metadata
            try:
                markdown_content = docling_result.document.export_to_markdown()
                logger.info(f"Extracted {len(markdown_content)} characters of markdown content")
            except Exception as e:
                logger.warning(f"Failed to extract markdown content: {str(e)}")
                markdown_content = ""

            processing_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"Document analysis completed successfully in "
                        f"{processing_time:.2f} seconds")

            return {
                "file_path": file_path,
                "document_type": document_type,
                "handler_used": handler.__class__.__name__,
                "confidence": document_type.confidence,
                "analysis": analysis,
                "file_size": os.path.getsize(file_path),
                "markdown_content": markdown_content,
                "processing_time": datetime.now().isoformat(),
                "processing_duration_seconds": processing_time,
                "docling_version": "1.0.0"  # Would be dynamic in real implementation
            }

        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            error_details = {
                "error_type": type(e).__name__,
                "error_message": str(e),
                "traceback": traceback.format_exc()
            }

            logger.error(f"Error analyzing document {file_path} after "
                         f"{processing_time:.2f}s: {error_details}")

            return {
                "file_path": file_path,
                "error": str(e),
                "error_details": error_details,
                "processing_time": datetime.now().isoformat(),
                "processing_duration_seconds": processing_time
            }

    def get_supported_formats(self) -> List[str]:
        """Get list of supported document formats"""
        return [".pdf", ".docx", ".pptx", ".xlsx", ".png", ".jpg", ".jpeg", ".tiff"]

    def get_handler_info(self) -> Dict[str, Any]:
        """Get information about loaded handlers"""
        return {
            "total_handlers": len(self.handlers),
            "docling_available": DOCLING_AVAILABLE,
            "supported_formats": self.get_supported_formats(),
            "handlers": [
                {
                    "name": handler.__class__.__name__,
                    "type": "docling_based"
                }
                for handler in self.handlers
            ]
        }
