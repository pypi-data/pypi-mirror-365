# Document Processing Guide

Complete guide to processing documents with Knowledge Graph Engine v2.

## Overview

The `DocumentProcessor` class enables you to extract knowledge from various document types and automatically store it in your knowledge graph. It uses LangChain for document loading and text splitting, then processes the content through the KG engine.

## Installation

Install the document processing dependencies:

```bash
# Install with document processing support
pip install kg-engine-v2[documents]

# Or install individual dependencies
pip install langchain>=0.0.350 pypdf>=3.17.0 unstructured>=0.10.0
```

## Quick Start

```python
from exo_graph import DocumentProcessor

# Initialize processor (uses environment LLM configuration)
processor = DocumentProcessor()

# Process a PDF
result = processor.process_pdf("research_paper.pdf")
print(f"Created {result.total_relationships} relationships from {result.processed_chunks} chunks")

# Search the extracted knowledge
response = processor.search("What were the main findings?")
print(response.answer)
```

## Supported Document Types

### PDF Files
```python
# Process PDF with metadata
result = processor.process_pdf(
    "company_report.pdf",
    source_metadata={
        "document_type": "annual_report",
        "year": 2024,
        "department": "finance"
    }
)
```

### Text Files
```python
# Process plain text files
result = processor.process_text_file(
    "meeting_notes.txt",
    source_metadata={
        "meeting_date": "2024-01-15",
        "attendees": ["Alice", "Bob", "Carol"]
    }
)
```

### HTML Files
```python
# Process HTML documents
result = processor.process_html_file(
    "team_page.html",
    source_metadata={
        "source_url": "https://company.com/team",
        "last_updated": "2024-01-10"
    }
)
```

### Raw Text Content
```python
# Process string content directly
content = "Alice works as a senior engineer at TechCorp..."
result = processor.process_text_content(
    content,
    source_metadata={
        "source": "interview_notes",
        "interviewer": "Bob Smith"
    }
)
```

## Batch Processing

### Process Entire Directories
```python
# Process all supported files in a directory
results = processor.process_directory(
    "./documents/",
    file_extensions=['.pdf', '.txt', '.html'],
    recursive=True
)

# Review results
for file_path, result in results.items():
    print(f"{file_path}: {result.processed_chunks} chunks, {result.total_relationships} relationships")
```

## Configuration Options

### Text Chunking
```python
processor = DocumentProcessor(
    chunk_size=1000,      # Characters per chunk
    chunk_overlap=100,    # Overlap between chunks
)
```

### Custom KG Engine

```python
from exo_graph import ExoGraphEngine, OllamaConfig

# Create custom KG engine
kg_engine = ExoGraphEngine(
    llm_config=OllamaConfig(model="phi3:mini")
)

# Use with document processor
processor = DocumentProcessor(kg_engine=kg_engine)
```

### LLM Configuration

```python
from exo_graph import OpenAIConfig

processor = DocumentProcessor(
    llm_config=OpenAIConfig(
        api_key="your-key",
        model="gpt-4o-mini"
    ),
    chunk_size=750,
    chunk_overlap=75
)
```

## Processing Results

The `ProcessingResult` dataclass contains:

```python
@dataclass
class ProcessingResult:
    success: bool                    # Whether processing succeeded
    processed_chunks: int           # Number of text chunks processed
    total_relationships: int        # Number of relationships created
    errors: List[str]              # Any errors encountered
    metadata: Dict[str, Any]       # Processing metadata
```

### Example Usage
```python
result = processor.process_pdf("document.pdf")

if result.success:
    print(f"✅ Success: {result.processed_chunks} chunks → {result.total_relationships} relationships")
else:
    print(f"❌ Failed: {result.errors}")

# Access metadata
print(f"Source file: {result.metadata['source_file']}")
print(f"Total pages: {result.metadata.get('total_pages', 'N/A')}")
```

## Best Practices

### Chunk Size Guidelines
- **Small documents (< 10 pages)**: 300-500 characters
- **Medium documents (10-50 pages)**: 500-800 characters  
- **Large documents (> 50 pages)**: 800-1200 characters
- **Technical documents**: 400-600 characters (preserve context)

### Overlap Recommendations
- **General use**: 10-20% of chunk size
- **Technical content**: 15-25% of chunk size
- **Narrative content**: 5-15% of chunk size

### Metadata Best Practices
```python
# Include relevant metadata for better organization
source_metadata = {
    "document_type": "research_paper",
    "authors": ["Dr. Alice Smith", "Dr. Bob Jones"],
    "publication_date": "2024-01-15",
    "journal": "AI Research Quarterly",
    "department": "computer_science",
    "keywords": ["machine_learning", "nlp", "transformers"]
}
```

## Performance Considerations

### Memory Usage
- Large PDFs are processed in chunks to manage memory
- Use smaller chunk sizes for memory-constrained environments
- Consider processing large directories in batches

### Processing Speed
- PDF processing: ~1-5 seconds per page
- Text processing: ~1-2 seconds per page
- HTML processing: ~2-3 seconds per page
- LLM extraction: ~2-10 seconds per chunk (model dependent)

### Optimization Tips
```python
# For large document sets, use batch processing
import os
from pathlib import Path

def process_large_directory(processor, directory, batch_size=10):
    files = list(Path(directory).rglob("*.pdf"))
    
    for i in range(0, len(files), batch_size):
        batch = files[i:i+batch_size]
        print(f"Processing batch {i//batch_size + 1}: {len(batch)} files")
        
        for file_path in batch:
            result = processor.process_pdf(file_path)
            if not result.success:
                print(f"Failed to process {file_path}: {result.errors}")
```

## Error Handling

### Common Issues

```python
# Handle missing files
try:
    result = processor.process_pdf("nonexistent.pdf")
except FileNotFoundError:
    print("File not found")

# Check for processing errors
result = processor.process_pdf("document.pdf")
if not result.success:
    for error in result.errors:
        print(f"Error: {error}")

# Handle LangChain dependency issues
try:
    from exo_graph import DocumentProcessor
except ImportError as e:
    print("Install document processing dependencies:")
    print("pip install kg-engine-v2[documents]")
```

### Troubleshooting

**LangChain not found:**
```bash
pip install langchain>=0.0.350
```

**PDF processing fails:**
```bash
pip install pypdf>=3.17.0
```

**HTML processing fails:**
```bash
pip install unstructured>=0.10.0
```

**Memory issues with large PDFs:**
```python
# Use smaller chunk sizes
processor = DocumentProcessor(chunk_size=300, chunk_overlap=30)
```

## Integration Examples

### With FastAPI

```python
from fastapi import FastAPI, UploadFile
from exo_graph import DocumentProcessor

app = FastAPI()
processor = DocumentProcessor()


@app.post("/upload-document")
async def upload_document(file: UploadFile):
    # Save uploaded file
    with open(f"temp_{file.filename}", "wb") as f:
        content = await file.read()
        f.write(content)

    # Process document
    if file.filename.endswith('.pdf'):
        result = processor.process_pdf(f"temp_{file.filename}")
    elif file.filename.endswith('.txt'):
        result = processor.process_text_file(f"temp_{file.filename}")

    return {
        "success": result.success,
        "chunks": result.processed_chunks,
        "relationships": result.total_relationships
    }
```

### With Jupyter Notebooks

```python
# Install in notebook cell
!pip
install
kg - engine - v2[documents]

from exo_graph import DocumentProcessor
import matplotlib.pyplot as plt

# Initialize processor
processor = DocumentProcessor()

# Process documents and visualize results
results = processor.process_directory("./research_papers/")

# Plot processing statistics
chunks = [r.processed_chunks for r in results.values()]
relationships = [r.total_relationships for r in results.values()]

plt.scatter(chunks, relationships)
plt.xlabel("Chunks Processed")
plt.ylabel("Relationships Created")
plt.title("Document Processing Results")
plt.show()
```

## Advanced Usage

### Custom Text Splitters
```python
from langchain.text_splitter import CharacterTextSplitter

# Create processor with custom splitter
class CustomDocumentProcessor(DocumentProcessor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text_splitter = CharacterTextSplitter(
            separator="\n\n",
            chunk_size=500,
            chunk_overlap=50
        )
```

### Metadata Enrichment
```python
def enrich_metadata(processor, file_path, base_metadata):
    """Add file system metadata"""
    from pathlib import Path
    import os
    
    path = Path(file_path)
    enriched_metadata = {
        **base_metadata,
        "file_size": os.path.getsize(file_path),
        "file_modified": path.stat().st_mtime,
        "file_extension": path.suffix,
        "parent_directory": path.parent.name
    }
    
    return enriched_metadata
```

---

**Next Steps:**
- Try the examples in `examples/document_processing_example.py`
- Experiment with different chunk sizes for your content type
- Integrate with your existing document workflow
- Explore the extracted knowledge through search queries