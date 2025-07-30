# Security Policy

## Overview

The Docling Analysis Framework is designed with security as a priority. We leverage Docling's secure document processing capabilities and follow security best practices throughout the codebase.

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Security Features

### 1. Secure Document Processing

The framework provides security through:

- **Docling Integration**
  - Uses Docling's secure document parsing
  - Prevents malicious document exploits
  - Sandboxed content extraction

- **File Size Validation**
  - Configurable file size limits
  - Prevents resource exhaustion attacks
  - Memory usage controls

- **Path Validation**
  - Secure file path handling
  - Prevents directory traversal attacks
  - Input sanitization

### 2. Safe Document Handling

All document processing uses secure practices:

```python
# Safe - uses secure Docling processing
analyzer = DoclingAnalyzer(max_file_size_mb=100.0)
result = analyzer.analyze_document("document.pdf")

# File size validation is built-in
if not analyzer._validate_file_size(file_path):
    raise ValueError(f"File too large: {file_path}")
```

### 3. Security Exception Handling

The framework gracefully handles security issues:

```python
{
    "error": "File too large: document.pdf (150.0 MB, max: 100.0 MB)",
    "file_path": "document.pdf",
    "security_issue": true,
    "processing_time": "2025-01-15T10:30:00"
}
```

## Security Best Practices

### For Framework Users

1. **File Size Validation**
   ```python
   # Set appropriate limits for your use case
   analyzer = DoclingAnalyzer(max_file_size_mb=50.0)
   
   # Or validate manually
   def validate_file_size(file_path, max_mb=100):
       size_mb = os.path.getsize(file_path) / (1024 * 1024)
       if size_mb > max_mb:
           raise ValueError(f"File too large: {size_mb}MB")
   ```

2. **Path Validation**
   ```python
   import os
   from pathlib import Path
   
   def validate_file_path(file_path):
       # Resolve to absolute path
       abs_path = Path(file_path).resolve()
       
       # Ensure file exists and is readable
       if not abs_path.exists():
           raise FileNotFoundError(f"File not found: {abs_path}")
       
       # Ensure it's a file, not a directory
       if not abs_path.is_file():
           raise ValueError(f"Not a file: {abs_path}")
       
       return str(abs_path)
   ```

3. **Input Sanitization**
   - Always validate and sanitize file paths
   - Implement rate limiting for analysis requests
   - Log security events for monitoring
   - Use allowed file extensions whitelist

4. **Resource Management**
   ```python
   # Configure appropriate limits
   config = ChunkingConfig(
       max_chunk_size=2000,  # Reasonable chunk size
       min_chunk_size=300,
       overlap_size=100
   )
   
   # Monitor processing time and memory usage
   orchestrator = DoclingChunkingOrchestrator(
       max_file_size_mb=50.0,
       config=config
   )
   ```

### For Framework Contributors

1. **Secure File Handling**
   - Always validate file paths and sizes
   - Use secure file operations
   - Implement proper error handling

2. **Security Testing**
   - Test new handlers with various document types
   - Verify protection against malformed documents
   - Ensure graceful error handling

3. **Dependency Management**
   - Keep Docling updated to latest version
   - Monitor security advisories
   - Minimize additional dependencies

## Reporting Security Vulnerabilities

If you discover a security vulnerability, please:

1. **DO NOT** create a public issue
2. Email security details to: wjackson@redhat.com
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if available)

We will acknowledge receipt within 48 hours and provide a detailed response within 5 business days.

## Security Checklist for Deployments

- [ ] Implement file size limits appropriate for your use case
- [ ] Validate all file paths before processing
- [ ] Set up monitoring for security exceptions
- [ ] Keep the framework and Docling updated
- [ ] Review and restrict file system access permissions
- [ ] Implement rate limiting for API endpoints
- [ ] Log all security events for audit trails
- [ ] Regular security scans of processed documents
- [ ] Use allowlists for accepted file extensions
- [ ] Monitor resource usage (CPU, memory, disk)

## Testing Security

Test the framework's security with these examples:

```python
import docling_analysis_framework as daf

# Test file size protection
try:
    # This should fail for files exceeding the limit
    analyzer = DoclingAnalyzer(max_file_size_mb=10.0)
    result = analyzer.analyze_document("very_large_file.pdf")
except ValueError as e:
    print(f"Security protection working: {e}")

# Test path validation
try:
    result = daf.analyze("../../../etc/passwd")
except FileNotFoundError as e:
    print(f"Path protection working: {e}")

# Test with various document types
safe_extensions = ['.pdf', '.docx', '.pptx', '.xlsx']
for ext in safe_extensions:
    try:
        result = daf.analyze(f"test_document{ext}")
        print(f"Extension {ext} processed safely")
    except Exception as e:
        print(f"Protection for {ext}: {e}")
```

## Security Updates

Stay informed about security updates:

- Watch the [GitHub repository](https://github.com/redhat-ai-americas/docling-analysis-framework)
- Monitor [Docling security advisories](https://github.com/DS4SD/docling)
- Review release notes for security fixes
- Subscribe to security notifications

## Compliance

This framework's security measures help with compliance for:

- **OWASP Top 10** - A05:2021 Security Misconfiguration
- **CWE-22** - Improper Limitation of a Pathname to a Restricted Directory
- **CWE-400** - Uncontrolled Resource Consumption
- **ISO 27001** - Information Security Management

## Document Security Considerations

### PDF Security
- PDFs can contain embedded JavaScript, forms, and multimedia
- Docling safely extracts text content without executing embedded code
- Framework focuses on text extraction, not PDF rendering

### Office Document Security
- DOCX/PPTX/XLSX files are ZIP archives with XML content
- Docling handles these securely without executing macros
- Framework extracts text and structure data only

### Image Security
- Image files processed through Docling's OCR capabilities
- No direct image rendering or processing by framework
- Text extraction only from image content

## Monitoring and Logging

Implement security monitoring:

```python
import logging

# Configure security logging
security_logger = logging.getLogger('docling_security')
security_logger.setLevel(logging.WARNING)

# Log security events
def log_security_event(event_type, file_path, details):
    security_logger.warning(f"Security Event: {event_type} - {file_path} - {details}")

# Monitor for suspicious activity
def analyze_with_monitoring(file_path):
    try:
        result = daf.analyze(file_path)
        return result
    except ValueError as e:
        if "too large" in str(e):
            log_security_event("FILE_SIZE_EXCEEDED", file_path, str(e))
        raise
    except Exception as e:
        log_security_event("ANALYSIS_ERROR", file_path, str(e))
        raise
```

This framework leverages Docling's secure document processing while adding additional security layers for production deployments. 