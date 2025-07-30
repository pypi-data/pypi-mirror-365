# Contributing to Docling Analysis Framework

Thank you for your interest in contributing to the Docling Analysis Framework! This document provides guidelines and information for contributors.

## 🎯 Project Vision

The Docling Analysis Framework is designed to be a comprehensive, production-ready system for analyzing PDF and Office documents with AI/ML processing support. We aim to:

- Provide a simple API that matches our XML Analysis Framework patterns
- Support enterprise document formats (PDF, DOCX, PPTX, XLSX) through Docling
- Generate high-quality semantic chunks for AI applications
- Enable easy integration with vector stores and LLM systems
- Maintain consistent API design across document analysis frameworks

## 🚀 Getting Started

### Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/redhat-ai-americas/docling-analysis-framework.git
   cd docling-analysis-framework
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies:**
   ```bash
   pip install docling
   pip install -e ".[dev]"
   ```

4. **Run tests to verify setup:**
   ```bash
   python -m pytest tests/
   ```

### Project Structure

```
docling-analysis-framework/
├── src/                          # Main source code
│   ├── __init__.py              # Simple API functions
│   └── core/                    # Core analysis and chunking logic
│       ├── analyzer.py          # DoclingAnalyzer + handlers
│       └── chunking.py          # Chunking strategies + config
├── examples/                    # Usage examples and demos
├── notebooks/                   # Testing and validation notebooks
├── tests/                       # Test suite (when added)
└── docs/                        # Documentation (when added)
```

## 🛠️ Development Guidelines

### Code Style

- **Python Style**: Follow PEP 8 with these specifics:
  - Line length: 100 characters maximum
  - Use type hints for all public functions
  - Docstrings: Google style format

- **Formatting**: Use Black for code formatting:
  ```bash
  black src/ tests/ examples/
  ```

- **Linting**: Use flake8 for linting:
  ```bash
  flake8 src/ tests/ examples/
  ```

### Testing Requirements

All contributions must include appropriate tests:

- **Unit Tests**: Test individual components and handlers
- **Integration Tests**: Test with real PDF/Office documents
- **Regression Tests**: Ensure existing functionality isn't broken

**Running Tests:**
```bash
# Run all tests (when test suite is added)
python -m pytest tests/

# Test the framework manually
python test_framework.py

# Run the testing notebook
jupyter notebook notebooks/01_testing_documentation_examples.ipynb
```

## 🚀 Using the Framework

### Simple API for End Users
```python
import docling_analysis_framework as daf

# One-line analysis with Docling extraction
result = daf.analyze("document.pdf")
print(f"Document: {result['document_type'].type_name}")

# Smart chunking for AI/ML
chunks = daf.chunk("document.pdf", strategy="auto")
print(f"Created {len(chunks)} chunks")

# Enhanced analysis with both analysis and chunking
enhanced = daf.analyze_enhanced("document.pdf")
print(f"Chunks: {len(enhanced['chunks'])}")

# JSON export
daf.save_chunks_to_json(chunks, "chunks.json")
daf.save_analysis_to_json(result, "analysis.json")
```

### Advanced API for Contributors
```python
from docling_analysis_framework import DoclingAnalyzer, ChunkingConfig

# Custom configurations for testing/development
config = ChunkingConfig(
    max_chunk_size=1500,
    min_chunk_size=300,
    overlap_size=100,
    preserve_structure=True
)

analyzer = DoclingAnalyzer(max_file_size_mb=100)
result = analyzer.analyze_document("test_file.pdf")

# Test custom chunking strategies
from docling_analysis_framework import DoclingChunkingOrchestrator
orchestrator = DoclingChunkingOrchestrator(config=config)
```

## 📝 Contributing Types

### 1. Enhancing Document Handlers

We welcome improvements to document analysis! Here's how to enhance handlers:

#### Handler Requirements
- Must extend the base `DoclingHandler` interface
- Implement all required methods: `can_handle()`, `detect_type()`, `analyze()`, `extract_key_data()`
- Include comprehensive docstrings
- Handle edge cases gracefully
- Provide meaningful AI use case suggestions

#### Handler Template
```python
#!/usr/bin/env python3
"""
[Document Type] Handler

Handles [document type description] using Docling extraction.
Common file patterns: *.pdf, *.docx, etc.
"""

from typing import Dict, List, Optional, Any, Tuple
from ..base import DocumentTypeInfo, SpecializedAnalysis, DoclingHandler

class YourDocumentHandler(DoclingHandler):
    """Handler for [Document Type] using Docling"""
    
    def can_handle(self, file_path: str, file_extension: str) -> Tuple[bool, float]:
        """Check if this handler can process the document"""
        # Implementation here
        pass
    
    def detect_type(self, file_path: str, docling_result: Any) -> DocumentTypeInfo:
        """Detect and classify the document type"""
        # Implementation here
        pass
    
    def analyze(self, file_path: str, docling_result: Any) -> SpecializedAnalysis:
        """Perform specialized analysis"""
        # Implementation here
        pass
    
    def extract_key_data(self, file_path: str, docling_result: Any) -> Dict[str, Any]:
        """Extract key structured data"""
        # Implementation here
        pass
```

### 2. Improving Chunking Strategies

The framework supports multiple chunking strategies for different use cases:

- **Structural**: Preserves document hierarchy (headers, sections)
- **Table-Aware**: Handles tables and figures specially
- **Page-Aware**: Considers original page boundaries when available
- **Auto**: Automatically selects best strategy based on document type

**Contributing Chunking Improvements:**
- Enhance existing strategies in `src/core/chunking.py`
- Add new chunking algorithms
- Improve chunk quality metrics
- Optimize chunk size distribution for AI/ML models

### 3. Test Coverage Improvements

Help us maintain high quality:

- Add test cases for edge cases
- Contribute PDF/Office files from real-world scenarios
- Create synthetic test data for complex scenarios
- Improve test automation

### 4. Documentation Enhancements

- API documentation improvements
- Usage examples and tutorials
- Integration guides for AI/ML pipelines
- Best practices guides

## 📋 Submission Process

### Pull Request Guidelines

1. **Fork and Branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**:
   - Follow coding standards
   - Add comprehensive tests
   - Update documentation as needed

3. **Test Your Changes**:
   ```bash
   # Test the framework
   python test_framework.py
   
   # Run linting
   flake8 src/ examples/
   black --check src/ examples/
   
   # Test with real documents
   jupyter notebook notebooks/01_testing_documentation_examples.ipynb
   ```

4. **Commit with Clear Messages**:
   ```bash
   git commit -m "Add enhanced PDF table extraction
   
   - Improves table detection in complex PDF layouts
   - Adds table-aware chunking strategy enhancements
   - Includes comprehensive test coverage with sample files
   - Generates AI use cases for document analysis"
   ```

5. **Create Pull Request**:
   - Use descriptive title and detailed description
   - Reference any related issues
   - Include test results and examples

### Pull Request Template

```markdown
## Description
Brief description of changes and motivation.

## Type of Change
- [ ] New document handler enhancement
- [ ] Bug fix
- [ ] Performance improvement
- [ ] Documentation update
- [ ] Test coverage improvement
- [ ] Chunking strategy improvement

## Testing
- [ ] Framework test script passes
- [ ] Manual testing completed
- [ ] New test files added (if applicable)
- [ ] Jupyter notebook testing completed

## Sample Documents
List any new test documents added or existing documents that benefit from this change.

## AI Use Cases
Describe potential AI/ML applications enabled by this contribution.

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Changes don't break existing functionality
```

## 🐛 Bug Reports

### Before Reporting
1. Check existing issues for duplicates
2. Test with the latest version
3. Try to reproduce with minimal example

### Bug Report Template
```markdown
**Describe the Bug**
Clear description of the problem.

**Document Details**
- File type/format: 
- File size:
- Document characteristics:

**Expected Behavior**
What should happen.

**Actual Behavior**
What actually happens.

**Error Messages**
Full error traceback if applicable.

**Environment**
- Python version:
- Operating system:
- Framework version:
- Docling version:

**Reproduction Steps**
1. Step one
2. Step two
3. ...
```

## 💡 Feature Requests

We welcome suggestions for new features! Please include:

- **Use Case**: Why is this feature needed?
- **Proposed Solution**: How should it work?
- **Document Types**: What formats would benefit?
- **AI Applications**: How would this enable AI/ML use cases?

## 🎖️ Recognition

Contributors are recognized in several ways:

- **README Credits**: Listed in the contributors section
- **Release Notes**: Contributions highlighted in release announcements
- **Handler Attribution**: Handler files include author information
- **Community Recognition**: Outstanding contributions featured in project updates

## 📞 Getting Help

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and community interaction
- **Documentation**: Check the README and examples for detailed guides

## 📄 Code of Conduct

This project follows a professional and inclusive environment:

- Be respectful and constructive in all interactions
- Focus on the technical aspects of contributions
- Help create a welcoming space for contributors of all backgrounds
- Follow GitHub's Community Guidelines

## 🎯 Contribution Priorities

Current high-priority areas for contributions:

1. **Enhanced Document Analysis**: Improved content extraction and analysis
2. **Chunking Optimizations**: Better chunking strategies for different document types
3. **Performance Improvements**: Large file handling and memory efficiency
4. **AI Integration**: Enhanced semantic analysis and quality metrics
5. **Test Coverage**: Comprehensive testing with diverse document types

## 🔗 Related Projects

This framework is part of the AI Building Blocks ecosystem:

- **XML Analysis Framework**: For XML document processing
- **Document Analysis Framework**: For text and configuration files
- **Unified Analysis Orchestrator**: Routes documents to appropriate frameworks

## 🏆 Success Metrics

We measure success by:

- **API Consistency**: Matching patterns with XML Analysis Framework
- **Document Coverage**: Supporting diverse PDF and Office formats
- **AI Readiness**: Producing high-quality chunks for AI/ML
- **Developer Experience**: Simple API with powerful customization options

---

Thank you for contributing to the Docling Analysis Framework! Your contributions help make document analysis more accessible and powerful for the AI/ML community. 