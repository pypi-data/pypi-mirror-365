#!/usr/bin/env python3
"""
Simple API Demo - Docling Analysis Framework
Demonstrates the completed simple API following XML framework patterns
"""

import sys
import os
from pathlib import Path

# Add src to path for local development
src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
sys.path.insert(0, src_path)

def main():
    """Demo the simple API functions"""
    
    print("🚀 Docling Analysis Framework - Simple API Demo")
    print("=" * 60)
    
    try:
        # Import with simple API - matches XML framework pattern
        import docling_analysis_framework as daf
        
        print(f"✅ Framework loaded successfully!")
        print(f"📦 Version: {daf.__version__}")
        print(f"🔧 Supported formats: {daf.get_supported_formats()}")
        
        # Test with a hypothetical document (user would provide real files)
        print(f"\n📄 Example Usage (add test files to actually run):")
        
        print(f"\n🎯 Basic Analysis:")
        print(f"  result = daf.analyze('document.pdf')")
        print(f"  print(result['document_type'].type_name)")
        
        print(f"\n✂️ Smart Chunking:")
        print(f"  chunks = daf.chunk('document.pdf', strategy='auto')")
        print(f"  print(f'Created {{len(chunks)}} chunks')")
        
        print(f"\n🚀 Enhanced Analysis:")
        print(f"  enhanced = daf.analyze_enhanced('document.pdf')")
        print(f"  print(enhanced['chunk_count'])")
        
        print(f"\n💾 JSON Export:")
        print(f"  daf.save_chunks_to_json(chunks, 'output.json')")
        print(f"  daf.save_analysis_to_json(result, 'analysis.json')")
        
        print(f"\n🔧 Advanced Usage:")
        print(f"  from docling_analysis_framework import DoclingAnalyzer, ChunkingConfig")
        print(f"  config = ChunkingConfig(max_chunk_size=1500)")
        print(f"  analyzer = DoclingAnalyzer(max_file_size_mb=100)")
        
        # Test the advanced imports
        from docling_analysis_framework import DoclingAnalyzer, DoclingChunkingOrchestrator, ChunkingConfig
        
        config = ChunkingConfig(max_chunk_size=1500, overlap_size=100)
        analyzer = DoclingAnalyzer(max_file_size_mb=50)
        orchestrator = DoclingChunkingOrchestrator(config=config)
        
        print(f"\n✅ Advanced classes loaded successfully!")
        print(f"  ChunkingConfig: max_chunk_size={config.max_chunk_size}")
        print(f"  DoclingAnalyzer: max_file_size_mb={analyzer.max_file_size_mb}")
        print(f"  DoclingChunkingOrchestrator: ready")
        
        print(f"\n🎉 Framework Status: COMPLETE")
        print(f"The Docling Analysis Framework is ready for use!")
        
        print(f"\n📝 Next Steps:")
        print(f"  1. Add PDF or DOCX files to test with")
        print(f"  2. Run the testing notebook: notebooks/01_testing_documentation_examples.ipynb")
        print(f"  3. Integrate with your AI/ML pipeline")
        print(f"  4. Use for vector database population")
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print(f"Make sure Docling is installed: pip install docling")
        return 1
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 