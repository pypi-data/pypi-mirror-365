# Docling Analysis Framework

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docling Powered](https://img.shields.io/badge/Docling-Powered-blue.svg)](https://github.com/DS4SD/docling)
[![AI Ready](https://img.shields.io/badge/AI%20Ready-✓-green.svg)](https://github.com/redhat-ai-americas/docling-analysis-framework)

AI-ready analysis framework for **PDF and Office documents** using Docling for content extraction. Transforms Docling's output into optimized chunks and structured analysis for AI/ML pipelines.

> **📝 For text, code, and configuration files**, use our companion [document-analysis-framework](https://github.com/redhat-ai-americas/document-analysis-framework) which uses only Python standard library.

## 🚀 Quick Start

### Simple API - Get Started in Seconds

```python
import docling_analysis_framework as daf

# 🎯 One-line analysis with Docling extraction
result = daf.analyze("document.pdf")
print(f"Document type: {result['document_type'].type_name}")
print(f"Pages: {result['document_type'].pages}")
print(f"Handler used: {result['handler_used']}")

# ✂️ Smart chunking for AI/ML
chunks = daf.chunk("document.pdf", strategy="auto")
print(f"Created {len(chunks)} optimized chunks")

# 🚀 Enhanced analysis with both analysis and chunking
enhanced = daf.analyze_enhanced("document.pdf", chunking_strategy="structural")
print(f"Document: {enhanced['analysis']['document_type'].type_name}")
print(f"Chunks: {len(enhanced['chunks'])}")

# 💾 Save chunks to JSON
daf.save_chunks_to_json(chunks, "chunks_output.json")

# 💾 Save analysis to JSON  
daf.save_analysis_to_json(result, "analysis_output.json")
```

### Advanced Usage

```python
import docling_analysis_framework as daf

# Enhanced analysis with full results
enhanced = daf.analyze_enhanced("research_paper.pdf")

print(f"Type: {enhanced['analysis']['document_type'].type_name}")
print(f"Confidence: {enhanced['analysis']['confidence']:.2f}")
print(f"AI use cases: {len(enhanced['analysis']['analysis'].ai_use_cases)}")
if enhanced['analysis']['analysis'].quality_metrics:
    for metric, score in enhanced['analysis']['analysis'].quality_metrics.items():
        print(f"{metric}: {score:.2f}")

# Different chunking strategies
hierarchical_chunks = daf.chunk("document.pdf", strategy="structural")
table_aware_chunks = daf.chunk("document.pdf", strategy="table_aware") 
page_aware_chunks = daf.chunk("document.pdf", strategy="page_aware")

# Process chunks
for chunk in hierarchical_chunks:
    print(f"Chunk {chunk.chunk_id}: {chunk.token_count} tokens")
    print(f"Type: {chunk.chunk_type}")
    # Send to your AI model...

# 💾 Save different strategies to separate files
strategies = {
    "structural": hierarchical_chunks,
    "table_aware": table_aware_chunks,
    "page_aware": page_aware_chunks
}

for strategy_name, chunks in strategies.items():
    daf.save_chunks_to_json(chunks, f"chunks_{strategy_name}.json")
    print(f"Saved {len(chunks)} chunks to chunks_{strategy_name}.json")
```

### Expert Usage - Direct Class Access

```python
# For advanced customization, use the classes directly
from docling_analysis_framework import DoclingAnalyzer, DoclingChunkingOrchestrator, ChunkingConfig

analyzer = DoclingAnalyzer(max_file_size_mb=100)
result = analyzer.analyze_document("document.pdf")

# Custom chunking with config
config = ChunkingConfig(
    max_chunk_size=1500,
    min_chunk_size=200,
    overlap_size=100,
    preserve_structure=True
)

orchestrator = DoclingChunkingOrchestrator(config=config)
# Note: In advanced usage, you'd pass the actual docling_result object
```

## 📋 Supported Document Types

| Format | Extensions | Confidence | Powered By |
|--------|------------|------------|------------|
| **📄 PDF Documents** | .pdf | 95% | Docling extraction |
| **📝 Word Documents** | .docx | 95% | Docling extraction |
| **📊 Spreadsheets** | .xlsx | 70% | Docling extraction |
| **📅 Presentations** | .pptx | 70% | Docling extraction |
| **🖼️ Images with Text** | .png, .jpg, .tiff | 70% | Docling OCR |

## 🎯 Key Features

### **🔍 Docling-Powered Extraction**
- **PDF text extraction** - High-quality content extraction
- **Table detection** - Preserves table structure in markdown
- **Figure references** - Maintains image/figure relationships  
- **Header hierarchy** - Document structure preservation

### **🤖 AI Preparation Layer**
- **Quality assessment** - Extraction quality scoring
- **Structure analysis** - Document type detection and analysis
- **Chunk optimization** - AI-ready segmentation strategies
- **Rich metadata** - Page counts, figures, tables, quality metrics

### **⚡ Smart Chunking Strategies**
- **Structural chunking** - Respects document hierarchy (headers, sections)
- **Table-aware chunking** - Separates tables from text content
- **Page-aware chunking** - Considers original page boundaries
- **Auto-selection** - Document-type-aware strategy selection

### **📊 Extraction Quality Analysis**
- **Text coverage** - How much text was successfully extracted
- **Structure preservation** - Whether headers, lists, tables are maintained
- **Overall confidence** - Combined quality score for AI processing

## 🎉 Framework Status - COMPLETED

The Docling Analysis Framework is now **fully functional** and follows the same successful patterns as the XML Analysis Framework:

### ✅ Completed Features

- **🎯 Simple API**: One-line functions for `analyze()`, `chunk()`, `analyze_enhanced()`
- **🔧 Advanced API**: Direct class access for customization with `DoclingAnalyzer`, `DoclingChunkingOrchestrator`
- **⚙️ Configurable Chunking**: `ChunkingConfig` class for fine-tuning chunk parameters
- **📦 Multiple Strategies**: Structural, table-aware, page-aware, and auto-selection chunking
- **💾 JSON Export**: Easy export of analysis results and chunks to JSON files
- **🛡️ Enhanced Error Handling**: Comprehensive logging and error reporting
- **📊 Quality Metrics**: Extraction quality assessment and content analysis
- **🧪 Testing Framework**: Complete Jupyter notebook for validation
- **📚 Documentation**: Comprehensive README with examples and usage patterns

### 🚀 Ready for AI/ML Integration

The framework provides everything needed for AI/ML pipelines:

- **Token-optimized chunks** sized for LLM context windows
- **Rich metadata** with document structure and quality metrics  
- **JSON export** for vector database ingestion
- **Multiple chunking strategies** for different document types
- **Quality assessment** to determine AI suitability

### 🔄 Comparison with XML Framework

| Feature | XML Framework | Docling Framework | Status |
|---------|---------------|-------------------|---------|
| Simple API | ✅ | ✅ | Complete |
| Advanced Classes | ✅ | ✅ | Complete |
| Multiple Strategies | ✅ | ✅ | Complete |
| Configuration | ✅ | ✅ | Complete |
| JSON Export | ✅ | ✅ | Complete |
| Error Handling | ✅ | ✅ | Complete |
| Testing Notebooks | ✅ | ✅ | Complete |
| Quality Metrics | ✅ | ✅ | Complete |

Both frameworks now provide identical API patterns and functionality!

## 🔧 Installation

```bash
# Install Docling first
pip install docling

# Install framework
git clone https://github.com/redhat-ai-americas/docling-analysis-framework.git
cd docling-analysis-framework  
pip install -e .
```

## 📖 Usage Examples

### Document Analysis with Quality Assessment
```python
from core.analyzer import DoclingAnalyzer

analyzer = DoclingAnalyzer()
result = analyzer.analyze_document("contract.pdf")

# Access extraction quality
quality = result['analysis'].extraction_quality
print(f"Text coverage: {quality['text_coverage']:.2f}")
print(f"Structure score: {quality['structure_score']:.2f}")
print(f"Overall quality: {quality['overall_score']:.2f}")

# Access document insights
findings = result['analysis'].key_findings
print(f"Pages: {findings['page_count']}")
print(f"Tables: {findings['table_rows']}")
print(f"Figures: {findings['figure_count']}")
```

### Advanced Chunking for Academic Papers
```python
# Perfect for research papers with complex structure
chunks = orchestrator.chunk_document(
    "paper.pdf",
    markdown_content,
    docling_result,
    strategy='structural'
)

# Chunks respect paper structure
for chunk in chunks:
    if chunk.chunk_type == 'section':
        print(f"Section: {chunk.metadata['section_title']}")
    elif chunk.chunk_type == 'table':
        print(f"Table data: {len(chunk.content)} chars")
    elif chunk.chunk_type == 'figure':
        print(f"Figure reference preserved")
```

### File Size Management
```python
from core.analyzer import DoclingAnalyzer

# Large PDF processing with limits
analyzer = DoclingAnalyzer(max_file_size_mb=100.0)

result = analyzer.analyze_document("large_manual.pdf")
if 'error' in result:
    print(f"File too large: {result['error']}")
else:
    print(f"Successfully processed {result['file_size']} bytes")
```

## 🧪 Framework Ecosystem

This framework is part of a larger document analysis ecosystem:

- **`xml-analysis-framework`** - Specialized XML document analysis
- **`docling-analysis-framework`** - PDF and Office documents (this package)
- **`document-analysis-framework`** - Text, code, and configuration files  
- **`unified-analysis-orchestrator`** - Routes documents to appropriate frameworks

## 🔗 Integration with Docling

This framework acts as an **AI preparation layer** on top of Docling:

1. **Docling** handles the heavy lifting of document extraction
2. **Our framework** adds AI-specific analysis and chunking
3. **Result** is AI-ready structured data and optimized chunks

```python
# What Docling provides:
docling_result = docling.convert("document.pdf")
markdown_content = docling_result.document.export_to_markdown()

# What we add:
ai_analysis = our_analyzer.analyze(docling_result)
ai_chunks = our_chunker.chunk(markdown_content, ai_analysis)
quality_scores = our_quality_assessor.assess(docling_result)
```

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Powered by [Docling](https://github.com/DS4SD/docling) for document extraction
- Built for modern AI/ML development workflows
- Part of the **AI Building Blocks** initiative