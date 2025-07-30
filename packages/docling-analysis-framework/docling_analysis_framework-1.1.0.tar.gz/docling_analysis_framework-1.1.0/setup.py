#!/usr/bin/env python3
"""
Setup script for Docling Analysis Framework
"""

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="docling-analysis-framework",
    version="1.1.0",
    author="Wes Jackson",
    author_email="wjackson@redhat.com",
    description="AI-ready analysis framework for PDF and Office documents using Docling for content extraction",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rdwj/docling-analysis-framework",
    project_urls={
        "Bug Reports": "https://github.com/rdwj/docling-analysis-framework/issues",
        "Source": "https://github.com/rdwj/docling-analysis-framework",
        "Documentation": "https://github.com/rdwj/docling-analysis-framework/blob/main/README.md",
    },
    packages=[
        "docling_analysis_framework",
        "docling_analysis_framework.core"
    ],
    package_dir={"docling_analysis_framework": "src/docling_analysis_framework"},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: General",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Office/Business :: Office Suites",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "docling>=1.0.0",  # Main dependency for document processing
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
        "docs": [
            "sphinx>=3.0",
            "sphinx_rtd_theme>=0.5",
        ],
    },
    entry_points={
        "console_scripts": [
            "docling-analyze=src.docling_analysis_framework.examples.basic_analysis:main",
            "docling-analyze-enhanced=src.docling_analysis_framework.examples.enhanced_analysis:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)