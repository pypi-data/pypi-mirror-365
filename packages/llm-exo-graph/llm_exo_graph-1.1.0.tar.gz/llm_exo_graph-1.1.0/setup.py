"""Setup script for KG Engine v2 - Advanced Knowledge Graph Engine"""

from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Advanced Knowledge Graph Engine with semantic search and temporal tracking"

setup(
    name="llm-exo-graph",
    version="1.1.0",
    description="Advanced Knowledge Graph Engine with Document Processing, Semantic Search and Multi-LLM Integration",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="Maksims Gavrilovs",
    author_email="acidpictures@gmail.com",
    url="https://github.com/dasein108/llm-exo-graph/",
    project_urls={
        "Documentation": "hhttps://github.com/dasein108/llm-exo-graph/docs",
        "Source": "hhttps://github.com/dasein108/llm-exo-graph/",
        "Bug Tracker": "https://github.com/dasein108/llm-exo-graph/issues",
        "API Reference": "https://github.com/dasein108/llm-exo-graph/blob/main/API_Reference.md",
    },
    
    # Package configuration
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    
    # Python version requirement
    python_requires=">=3.8",
    
    # Core dependencies
    install_requires=[
        "neo4j>=5.0.0",
        "openai>=1.0.0", 
        "sentence-transformers>=2.2.0",
        "dateparser>=1.1.0",
        "numpy>=1.21.0",
        "python-dotenv>=0.19.0"
    ],
    
    # Optional dependencies
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=0.991",
            "pre-commit>=2.20.0"
        ],
        "api": [
            "fastapi>=0.104.0",
            "uvicorn>=0.24.0",
            "pydantic>=2.0.0"
        ],
        "documents": [
            "langchain>=0.0.350",
            "pypdf>=3.17.0",
            "langchain-community>=0.3.27",
            "unstructured==0.18.11",
            "json_repair==0.48.0"
        ],
        "docs": [
            "mkdocs>=1.5.0",
            "mkdocs-material>=9.0.0"
        ],
        "all": [
            # Include all optional dependencies
            "pytest>=7.0.0", "pytest-cov>=4.0.0", "black>=22.0.0", "flake8>=5.0.0", "mypy>=0.991",
            "fastapi>=0.104.0", "uvicorn>=0.24.0", "pydantic>=2.0.0",
            "langchain>=0.0.350", "pypdf>=3.17.0", "unstructured>=0.10.0",
            "mkdocs>=1.5.0", "mkdocs-material>=9.0.0"
        ]
    },
    
    # Package metadata
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Database",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    
    # Keywords for discovery
    keywords=[
        "knowledge-graph", "neo4j", "llm", "openai", "semantic-search",
        "vector-search", "graph-database", "nlp", "ai", "machine-learning",
        "information-extraction", "relationship-extraction", "entity-recognition",
        "temporal-tracking", "conflict-resolution", "hybrid-search"
    ],
    
    # Zip safety
    zip_safe=False,
)