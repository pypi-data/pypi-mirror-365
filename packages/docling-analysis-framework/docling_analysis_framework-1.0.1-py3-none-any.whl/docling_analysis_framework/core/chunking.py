"""
Docling Document Chunking Strategies
Optimized for documents processed through Docling extraction
"""

import re
import hashlib
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ChunkingConfig:
    """Configuration for document chunking"""
    max_chunk_size: int = 2000
    min_chunk_size: int = 300
    overlap_size: int = 200
    preserve_structure: bool = True
    token_estimation_method: str = "simple"  # "simple" or "precise"

    def __post_init__(self):
        """Validate configuration"""
        if self.max_chunk_size <= self.min_chunk_size:
            raise ValueError("max_chunk_size must be greater than min_chunk_size")
        if self.overlap_size >= self.max_chunk_size:
            raise ValueError("overlap_size must be less than max_chunk_size")


@dataclass
class DocumentChunk:
    """Represents a chunk of document content"""
    chunk_id: str
    content: str
    chunk_type: str
    metadata: Dict[str, Any]
    start_position: Optional[int] = None
    end_position: Optional[int] = None
    token_count: Optional[int] = None


class DoclingChunkingStrategy(ABC):
    """Abstract base class for Docling document chunking strategies"""

    def __init__(self, config: Optional[ChunkingConfig] = None):
        self.config = config or ChunkingConfig()

    @abstractmethod
    def chunk_document(self, file_path: str, markdown_content: str,
                       docling_result: Any,
                       specialized_analysis: Optional[Dict[str, Any]] = None
                       ) -> List[DocumentChunk]:
        """Chunk the document content into smaller pieces"""
        pass

    def estimate_tokens(self, text: str) -> int:
        """Estimate token count using the configured method"""
        if self.config.token_estimation_method == "simple":
            # Simple estimation: ~4 characters per token on average
            return len(text) // 4
        else:
            # More precise estimation (could integrate with actual tokenizer)
            # For now, use the same simple method
            return len(text) // 4

    def generate_chunk_id(self, content: str, index: int) -> str:
        """Generate a unique ID for a chunk"""
        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        return f"chunk_{index}_{content_hash}"


class StructuralChunkingStrategy(DoclingChunkingStrategy):
    """Chunking strategy that preserves document structure from Docling extraction"""

    def chunk_document(self, file_path: str, markdown_content: str,
                       docling_result: Any,
                       specialized_analysis: Optional[Dict[str, Any]] = None
                       ) -> List[DocumentChunk]:
        chunks = []

        # Split by major structural elements
        sections = self._identify_sections(markdown_content)

        chunk_index = 0
        for section in sections:
            if len(section['content']) <= self.config.max_chunk_size:
                # Section fits in one chunk
                chunk = DocumentChunk(
                    chunk_id=self.generate_chunk_id(section['content'], chunk_index),
                    content=section['content'],
                    chunk_type=section['type'],
                    metadata={
                        "section_title": section.get('title', ''),
                        "section_level": section.get('level', 0),
                        "chunk_index": chunk_index,
                        "strategy": "structural"
                    },
                    token_count=self.estimate_tokens(section['content'])
                )
                chunks.append(chunk)
                chunk_index += 1
            else:
                # Section is too large, split further
                sub_chunks = self._split_large_section(section, chunk_index)
                chunks.extend(sub_chunks)
                chunk_index += len(sub_chunks)

        return chunks

    def _identify_sections(self, markdown_content: str) -> List[Dict[str, Any]]:
        """Identify document sections from markdown structure"""
        lines = markdown_content.split('\n')
        sections = []
        current_section = {
            'type': 'content',
            'title': '',
            'level': 0,
            'content': '',
            'start_line': 0
        }

        for i, line in enumerate(lines):
            # Check for headers
            header_match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if header_match:
                # Save previous section if it has content
                if current_section['content'].strip():
                    sections.append(current_section.copy())

                # Start new section
                level = len(header_match.group(1))
                title = header_match.group(2)
                current_section = {
                    'type': 'section',
                    'title': title,
                    'level': level,
                    'content': line + '\n',
                    'start_line': i
                }
            else:
                current_section['content'] += line + '\n'

        # Add final section
        if current_section['content'].strip():
            sections.append(current_section)

        return sections

    def _split_large_section(self, section: Dict[str, Any],
                             start_index: int) -> List[DocumentChunk]:
        """Split a large section into smaller chunks while preserving context"""
        chunks = []
        content = section['content']

        # Try to split by paragraphs first
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]

        current_chunk = ""
        chunk_index = start_index

        for paragraph in paragraphs:
            # If adding this paragraph would exceed max size
            if len(current_chunk) + len(paragraph) > self.config.max_chunk_size and current_chunk:
                # Create chunk from current content
                chunk = DocumentChunk(
                    chunk_id=self.generate_chunk_id(current_chunk, chunk_index),
                    content=current_chunk.strip(),
                    chunk_type=f"{section['type']}_partial",
                    metadata={
                        "section_title": section.get('title', ''),
                        "section_level": section.get('level', 0),
                        "chunk_index": chunk_index,
                        "strategy": "structural",
                        "is_partial": True
                    },
                    token_count=self.estimate_tokens(current_chunk)
                )
                chunks.append(chunk)

                # Start new chunk with overlap if possible
                if self.config.overlap_size > 0:
                    overlap_text = current_chunk[-self.config.overlap_size:]
                    current_chunk = overlap_text + "\n\n" + paragraph
                else:
                    current_chunk = paragraph
                chunk_index += 1
            else:
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                else:
                    current_chunk = paragraph

        # Add final chunk
        if current_chunk.strip():
            chunk = DocumentChunk(
                chunk_id=self.generate_chunk_id(current_chunk, chunk_index),
                content=current_chunk.strip(),
                chunk_type=f"{section['type']}_partial",
                metadata={
                    "section_title": section.get('title', ''),
                    "section_level": section.get('level', 0),
                    "chunk_index": chunk_index,
                    "strategy": "structural",
                    "is_partial": True
                },
                token_count=self.estimate_tokens(current_chunk)
            )
            chunks.append(chunk)

        return chunks


class TableAwareChunkingStrategy(DoclingChunkingStrategy):
    """Chunking strategy that handles tables and figures specially"""

    def chunk_document(self, file_path: str, markdown_content: str,
                       docling_result: Any,
                       specialized_analysis: Optional[Dict[str, Any]] = None
                       ) -> List[DocumentChunk]:
        chunks = []

        # Identify tables and figures
        elements = self._identify_structured_elements(markdown_content)

        chunk_index = 0
        current_text = ""

        for element in elements:
            if element['type'] == 'text':
                # Regular text content
                if len(current_text) + len(element['content']) <= self.config.max_chunk_size:
                    current_text += element['content']
                else:
                    # Flush current text as chunk
                    if current_text.strip():
                        chunk = DocumentChunk(
                            chunk_id=self.generate_chunk_id(current_text, chunk_index),
                            content=current_text.strip(),
                            chunk_type="text",
                            metadata={
                                "chunk_index": chunk_index,
                                "strategy": "table_aware"
                            },
                            token_count=self.estimate_tokens(current_text)
                        )
                        chunks.append(chunk)
                        chunk_index += 1

                    current_text = element['content']

            elif element['type'] in ['table', 'figure']:
                # Flush any pending text
                if current_text.strip():
                    chunk = DocumentChunk(
                        chunk_id=self.generate_chunk_id(current_text, chunk_index),
                        content=current_text.strip(),
                        chunk_type="text",
                        metadata={
                            "chunk_index": chunk_index,
                            "strategy": "table_aware"
                        },
                        token_count=self.estimate_tokens(current_text)
                    )
                    chunks.append(chunk)
                    chunk_index += 1
                    current_text = ""

                # Create separate chunk for table/figure
                chunk = DocumentChunk(
                    chunk_id=self.generate_chunk_id(element['content'], chunk_index),
                    content=element['content'],
                    chunk_type=element['type'],
                    metadata={
                        "chunk_index": chunk_index,
                        "strategy": "table_aware",
                        "element_type": element['type']
                    },
                    token_count=self.estimate_tokens(element['content'])
                )
                chunks.append(chunk)
                chunk_index += 1

        # Add final text chunk
        if current_text.strip():
            chunk = DocumentChunk(
                chunk_id=self.generate_chunk_id(current_text, chunk_index),
                content=current_text.strip(),
                chunk_type="text",
                metadata={
                    "chunk_index": chunk_index,
                    "strategy": "table_aware"
                },
                token_count=self.estimate_tokens(current_text)
            )
            chunks.append(chunk)

        return chunks

    def _identify_structured_elements(self, markdown_content: str) -> List[Dict[str, Any]]:
        """Identify tables, figures, and text sections"""
        elements = []
        lines = markdown_content.split('\n')

        current_element = {'type': 'text', 'content': ''}

        for line in lines:
            # Check for table rows
            if '|' in line and line.count('|') >= 2:
                if current_element['type'] != 'table':
                    # Save previous element
                    if current_element['content'].strip():
                        elements.append(current_element)
                    current_element = {'type': 'table', 'content': line + '\n'}
                else:
                    current_element['content'] += line + '\n'

            # Check for figures/images
            elif line.startswith('!['):
                # Save previous element
                if current_element['content'].strip():
                    elements.append(current_element)

                # Create figure element
                elements.append({'type': 'figure', 'content': line})
                current_element = {'type': 'text', 'content': ''}

            else:
                # Regular text
                if current_element['type'] != 'text':
                    # Save previous element
                    if current_element['content'].strip():
                        elements.append(current_element)
                    current_element = {'type': 'text', 'content': line + '\n'}
                else:
                    current_element['content'] += line + '\n'

        # Add final element
        if current_element['content'].strip():
            elements.append(current_element)

        return elements


class PageAwareChunkingStrategy(DoclingChunkingStrategy):
    """Chunking strategy that considers original page boundaries when available"""

    def chunk_document(self, file_path: str, markdown_content: str,
                       docling_result: Any,
                       specialized_analysis: Optional[Dict[str, Any]] = None
                       ) -> List[DocumentChunk]:

        # Try to extract page information from docling_result
        if hasattr(docling_result, 'pages') and docling_result.pages:
            return self._chunk_by_pages(markdown_content, docling_result.pages)
        else:
            # Fall back to structural chunking
            return StructuralChunkingStrategy(self.config).chunk_document(
                file_path, markdown_content, docling_result, specialized_analysis
            )

    def _chunk_by_pages(self, markdown_content: str, pages: List[Any]) -> List[DocumentChunk]:
        """Chunk content respecting original page boundaries"""
        chunks = []

        # This is a simplified approach - in reality, we'd need to map
        # the markdown content back to original pages using Docling's metadata

        # For now, split content into approximately equal parts based on page count
        total_length = len(markdown_content)
        page_count = len(pages)
        approximate_page_size = total_length // page_count if page_count > 0 else total_length

        lines = markdown_content.split('\n')
        current_chunk = ""
        chunk_index = 0
        current_size = 0

        for line in lines:
            if current_size + len(line) > approximate_page_size and current_chunk.strip():
                # Create chunk
                chunk = DocumentChunk(
                    chunk_id=self.generate_chunk_id(current_chunk, chunk_index),
                    content=current_chunk.strip(),
                    chunk_type="page_section",
                    metadata={
                        "chunk_index": chunk_index,
                        "strategy": "page_aware",
                        "approximate_page": chunk_index + 1
                    },
                    token_count=self.estimate_tokens(current_chunk)
                )
                chunks.append(chunk)

                # Start new chunk
                current_chunk = line + '\n'
                current_size = len(line)
                chunk_index += 1
            else:
                current_chunk += line + '\n'
                current_size += len(line)

        # Add final chunk
        if current_chunk.strip():
            chunk = DocumentChunk(
                chunk_id=self.generate_chunk_id(current_chunk, chunk_index),
                content=current_chunk.strip(),
                chunk_type="page_section",
                metadata={
                    "chunk_index": chunk_index,
                    "strategy": "page_aware",
                    "approximate_page": chunk_index + 1
                },
                token_count=self.estimate_tokens(current_chunk)
            )
            chunks.append(chunk)

        return chunks


class DoclingChunkingOrchestrator:
    """Orchestrates different chunking strategies for Docling-processed documents"""

    def __init__(self, max_file_size_mb: Optional[float] = None,
                 config: Optional[ChunkingConfig] = None,
                 max_chunk_size: int = 2000, overlap_size: int = 200):
        self.max_file_size_mb = max_file_size_mb

        # Handle both old and new parameter styles for backwards compatibility
        if config is None:
            config = ChunkingConfig(
                max_chunk_size=max_chunk_size,
                overlap_size=overlap_size
            )

        self.config = config

        self.strategies = {
            'structural': StructuralChunkingStrategy(config),
            'table_aware': TableAwareChunkingStrategy(config),
            'page_aware': PageAwareChunkingStrategy(config),
            'auto': None  # Will be determined automatically
        }

    def _validate_file_size(self, file_path: str) -> bool:
        """Check if file size is within limits"""
        if self.max_file_size_mb is None:
            return True

        try:
            import os
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            return file_size_mb <= self.max_file_size_mb
        except OSError:
            return False

    def _determine_strategy(self, specialized_analysis: Optional[Dict[str, Any]],
                            markdown_content: str) -> str:
        """Determine the best chunking strategy based on document analysis"""
        if not specialized_analysis:
            return 'structural'

        doc_type = specialized_analysis.get('document_type', {})
        if isinstance(doc_type, dict):
            type_name = doc_type.get('type_name', '')
        else:
            type_name = str(doc_type)

        # Check content characteristics
        has_tables = '|' in markdown_content and markdown_content.count('|') > 10
        has_many_headers = markdown_content.count('#') > 5

        # Strategy selection logic
        if has_tables:
            return 'table_aware'
        elif 'PDF' in type_name and has_many_headers:
            return 'page_aware'
        else:
            return 'structural'

    def chunk_document(self, file_path: str, markdown_content: str,
                       docling_result: Any,
                       specialized_analysis: Optional[Dict[str, Any]] = None,
                       strategy: str = 'auto',
                       config: Optional[ChunkingConfig] = None
                       ) -> List[DocumentChunk]:
        """
        Chunk a Docling-processed document using the specified or automatically determined strategy
        """
        try:
            # Validate file size
            if not self._validate_file_size(file_path):
                raise ValueError(f"File too large: {file_path}")

            # Use provided config or fall back to instance config
            effective_config = config or self.config

            # Update strategies with new config if provided
            if config:
                for strategy_name, strategy_obj in self.strategies.items():
                    if strategy_obj:
                        strategy_obj.config = effective_config

            # Determine strategy
            if strategy == 'auto':
                strategy = self._determine_strategy(specialized_analysis, markdown_content)

            # Get chunking strategy
            chunking_strategy = self.strategies.get(strategy)
            if not chunking_strategy:
                logger.warning(f"Unknown strategy '{strategy}', using structural strategy")
                chunking_strategy = self.strategies['structural']

            # Chunk the document
            chunks = chunking_strategy.chunk_document(file_path, markdown_content,
                                                      docling_result, specialized_analysis)

            # Add file-level metadata to all chunks
            for chunk in chunks:
                chunk.metadata.update({
                    'file_path': file_path,
                    'total_chunks': len(chunks),
                    'file_size': len(markdown_content),
                    'docling_processed': True,
                    'chunking_config': {
                        'max_chunk_size': effective_config.max_chunk_size,
                        'overlap_size': effective_config.overlap_size,
                        'preserve_structure': effective_config.preserve_structure
                    }
                })

            return chunks

        except Exception as e:
            logger.error(f"Error chunking document {file_path}: {e}")
            # Return a single chunk with the error
            return [DocumentChunk(
                chunk_id="error_chunk",
                content=f"Error chunking document: {str(e)}",
                chunk_type="error",
                metadata={"error": str(e), "file_path": file_path}
            )]
