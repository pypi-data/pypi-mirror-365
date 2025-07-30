"""
Document processor for Knowledge Graph Engine v2

Processes various document types (PDF, text, web pages) and extracts knowledge
into the graph using LangChain for document loading and text splitting.
"""
import os
import logging
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
from dataclasses import dataclass

# LangChain imports
from langchain_community.document_loaders import PyPDFLoader, TextLoader, UnstructuredHTMLLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document


from .core import ExoGraphEngine
from .models import InputItem
from .config import Neo4jConfig
from .llm import LLMConfig

logger = logging.getLogger(__name__)


@dataclass
class ProcessingResult:
    """Result of document processing"""
    success: bool
    processed_chunks: int
    total_relationships: int
    errors: List[str]
    metadata: Dict[str, Any]


class DocumentProcessor:
    """
    Document processor that extracts knowledge from various document types
    and stores it in the knowledge graph.
    """
    
    def __init__(self,
                 kg_engine: Optional[ExoGraphEngine] = None,
                 chunk_size: int = 500,
                 chunk_overlap: int = 50):
        """
        Initialize document processor.
        
        Args:
            kg_engine: Existing KG engine instance (optional)
            llm_config: LLM configuration (optional, uses env if not provided)
            neo4j_config: Neo4j configuration (optional, uses default if not provided)
            chunk_size: Size of text chunks for processing
            chunk_overlap: Overlap between chunks
        """

        self.kg_engine = kg_engine

        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        logger.info(f"📄 Document Processor initialized (chunk_size={chunk_size}, overlap={chunk_overlap})")
    
    def process_pdf(self, 
                   pdf_path: Union[str, Path], 
                   source_metadata: Optional[Dict[str, Any]] = None) -> ProcessingResult:
        """
        Process a PDF document and extract knowledge.
        
        Args:
            pdf_path: Path to PDF file
            source_metadata: Additional metadata to include
            
        Returns:
            ProcessingResult with processing statistics
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            return ProcessingResult(
                success=False,
                processed_chunks=0,
                total_relationships=0,
                errors=[f"PDF file not found: {pdf_path}"],
                metadata={}
            )
        
        try:
            logger.info(f"📖 Processing PDF: {pdf_path}")
            
            # Load PDF
            loader = PyPDFLoader(str(pdf_path))
            pages = loader.load()
            
            # Split into chunks
            docs = self.text_splitter.split_documents(pages)
            
            # Process chunks
            return self._process_documents(docs, {
                "source_type": "pdf",
                "source_file": str(pdf_path),
                "total_pages": len(pages),
                **(source_metadata or {})
            })
            
        except Exception as e:
            logger.error(f"Error processing PDF {pdf_path}: {e}")
            return ProcessingResult(
                success=False,
                processed_chunks=0,
                total_relationships=0,
                errors=[str(e)],
                metadata={"source_file": str(pdf_path)}
            )
    
    def process_text_file(self, 
                         text_path: Union[str, Path],
                         source_metadata: Optional[Dict[str, Any]] = None) -> ProcessingResult:
        """
        Process a text file and extract knowledge.
        
        Args:
            text_path: Path to text file
            source_metadata: Additional metadata to include
            
        Returns:
            ProcessingResult with processing statistics
        """
        text_path = Path(text_path)
        if not text_path.exists():
            return ProcessingResult(
                success=False,
                processed_chunks=0,
                total_relationships=0,
                errors=[f"Text file not found: {text_path}"],
                metadata={}
            )
        
        try:
            logger.info(f"📝 Processing text file: {text_path}")
            
            # Load text file
            loader = TextLoader(str(text_path))
            documents = loader.load()
            
            # Split into chunks
            docs = self.text_splitter.split_documents(documents)
            
            # Process chunks
            return self._process_documents(docs, {
                "source_type": "text",
                "source_file": str(text_path),
                **(source_metadata or {})
            })
            
        except Exception as e:
            logger.error(f"Error processing text file {text_path}: {e}")
            return ProcessingResult(
                success=False,
                processed_chunks=0,
                total_relationships=0,
                errors=[str(e)],
                metadata={"source_file": str(text_path)}
            )
    
    def process_html_file(self, 
                         html_path: Union[str, Path],
                         source_metadata: Optional[Dict[str, Any]] = None) -> ProcessingResult:
        """
        Process an HTML file and extract knowledge.
        
        Args:
            html_path: Path to HTML file
            source_metadata: Additional metadata to include
            
        Returns:
            ProcessingResult with processing statistics
        """
        html_path = Path(html_path)
        if not html_path.exists():
            return ProcessingResult(
                success=False,
                processed_chunks=0,
                total_relationships=0,
                errors=[f"HTML file not found: {html_path}"],
                metadata={}
            )
        
        try:
            logger.info(f"🌐 Processing HTML file: {html_path}")
            
            # Load HTML file
            loader = UnstructuredHTMLLoader(str(html_path))
            documents = loader.load()
            
            # Split into chunks
            docs = self.text_splitter.split_documents(documents)
            
            # Process chunks
            return self._process_documents(docs, {
                "source_type": "html",
                "source_file": str(html_path),
                **(source_metadata or {})
            })
            
        except Exception as e:
            logger.error(f"Error processing HTML file {html_path}: {e}")
            return ProcessingResult(
                success=False,
                processed_chunks=0,
                total_relationships=0,
                errors=[str(e)],
                metadata={"source_file": str(html_path)}
            )
    
    def process_text_content(self, 
                           content: str,
                           source_metadata: Optional[Dict[str, Any]] = None) -> ProcessingResult:
        """
        Process raw text content and extract knowledge.
        
        Args:
            content: Raw text content
            source_metadata: Additional metadata to include
            
        Returns:
            ProcessingResult with processing statistics
        """
        try:
            logger.info(f"📄 Processing text content ({len(content)} characters)")
            
            # Create document from content
            doc = Document(page_content=content, metadata=source_metadata or {})
            
            # Split into chunks
            docs = self.text_splitter.split_documents([doc])
            
            # Process chunks
            return self._process_documents(docs, {
                "source_type": "text_content",
                "content_length": len(content),
                **(source_metadata or {})
            })
            
        except Exception as e:
            logger.error(f"Error processing text content: {e}")
            return ProcessingResult(
                success=False,
                processed_chunks=0,
                total_relationships=0,
                errors=[str(e)],
                metadata={"content_length": len(content)}
            )
    
    def process_directory(self, 
                         directory_path: Union[str, Path],
                         file_extensions: Optional[List[str]] = None,
                         recursive: bool = True) -> Dict[str, ProcessingResult]:
        """
        Process all supported files in a directory.
        
        Args:
            directory_path: Path to directory
            file_extensions: List of extensions to process (default: ['.pdf', '.txt', '.html'])
            recursive: Whether to process subdirectories
            
        Returns:
            Dictionary mapping file paths to ProcessingResults
        """
        directory_path = Path(directory_path)
        if not directory_path.exists() or not directory_path.is_dir():
            logger.error(f"Directory not found or not a directory: {directory_path}")
            return {}
        
        if file_extensions is None:
            file_extensions = ['.pdf', '.txt', '.html', '.htm']
        
        results = {}
        
        # Find files to process
        pattern = "**/*" if recursive else "*"
        for file_path in directory_path.glob(pattern):
            if file_path.is_file() and file_path.suffix.lower() in file_extensions:
                logger.info(f"📁 Processing file: {file_path}")
                
                # Process based on file type
                if file_path.suffix.lower() == '.pdf':
                    result = self.process_pdf(file_path)
                elif file_path.suffix.lower() in ['.txt']:
                    result = self.process_text_file(file_path)
                elif file_path.suffix.lower() in ['.html', '.htm']:
                    result = self.process_html_file(file_path)
                else:
                    continue
                
                results[str(file_path)] = result
        
        logger.info(f"📁 Processed {len(results)} files from {directory_path}")
        return results
    
    def _process_documents(self, 
                          docs: List[Document], 
                          base_metadata: Dict[str, Any]) -> ProcessingResult:
        """
        Process a list of LangChain documents through the KG engine.
        
        Args:
            docs: List of LangChain Document objects
            base_metadata: Base metadata to include with all chunks
            
        Returns:
            ProcessingResult with processing statistics
        """
        if not docs:
            return ProcessingResult(
                success=False,
                processed_chunks=0,
                total_relationships=0,
                errors=["No content to process"],
                metadata=base_metadata
            )
        
        # Convert documents to InputItems
        input_items = []
        for i, doc in enumerate(docs):
            # Combine document metadata with base metadata
            chunk_metadata = {
                **base_metadata,
                "chunk_index": i,
                "chunk_length": len(doc.page_content),
                **doc.metadata
            }
            
            input_items.append(InputItem(
                description=doc.page_content,
                metadata=chunk_metadata
            ))
        
        logger.info(f"🔄 Processing {len(input_items)} chunks through KG engine")
        
        try:
            # Process through KG engine
            results = self.kg_engine.process_input(input_items)
            
            return ProcessingResult(
                success=True,
                processed_chunks=len(input_items),
                total_relationships=len(results.get('edge_results', [])),
                errors=results.get('errors', []),
                metadata={
                    **base_metadata,
                    "kg_engine_results": results
                }
            )
            
        except Exception as e:
            logger.error(f"Error processing documents through KG engine: {e}")
            return ProcessingResult(
                success=False,
                processed_chunks=0,
                total_relationships=0,
                errors=[str(e)],
                metadata=base_metadata
            )
    

    def search(self, query: str, **kwargs) -> Any:
        """Search the knowledge graph."""
        return self.kg_engine.search(query, **kwargs)