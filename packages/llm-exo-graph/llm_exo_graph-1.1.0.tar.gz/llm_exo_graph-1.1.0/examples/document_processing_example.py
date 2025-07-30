#!/usr/bin/env python3
"""
Document Processing Example for KG Engine v2

Demonstrates how to process PDF files, text files, and other documents
to extract knowledge and store it in the graph database.
"""
import os
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from exo_graph import DocumentProcessor, Neo4jConfig, ProcessingResult, ExoGraphEngine, OllamaConfig


def create_sample_content():
    """Create sample files for demonstration"""
    samples_dir = Path(__file__).parent / "sample_documents"
    samples_dir.mkdir(exist_ok=True)
    
    # Create sample text file
    text_file = samples_dir / "company_info.txt"
    text_content = """
    TechCorp Inc. Company Overview
    
    TechCorp Inc. is a leading technology company founded in 2015 by Alice Johnson and Bob Smith.
    The company is headquartered in San Francisco, California.
    
    Leadership Team:
    - Alice Johnson: CEO and Co-founder
    - Bob Smith: CTO and Co-founder  
    - Carol Williams: VP of Engineering
    - David Brown: VP of Sales
    
    TechCorp specializes in artificial intelligence and machine learning solutions.
    The company has partnerships with Google, Microsoft, and Amazon.
    
    Recent News:
    - TechCorp raised $50 million in Series B funding in 2023
    - The company expanded to Europe with a new office in London
    - Alice Johnson was featured in Forbes 30 Under 30 in 2022
    
    Products:
    - AI Assistant Platform: Used by over 10,000 businesses
    - Machine Learning SDK: Open source library with 50k downloads
    - Data Analytics Suite: Enterprise solution for Fortune 500 companies
    """
    
    with open(text_file, 'w') as f:
        f.write(text_content)
    
    # Create sample HTML file
    html_file = samples_dir / "team_bios.html"
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Team Biographies</title>
    </head>
    <body>
        <h1>TechCorp Team Biographies</h1>
        
        <div class="bio">
            <h2>Alice Johnson - CEO</h2>
            <p>Alice Johnson graduated from Stanford University with a degree in Computer Science. 
            She previously worked at Meta as a senior engineer before co-founding TechCorp.
            Alice is passionate about democratizing AI technology.</p>
        </div>
        
        <div class="bio">
            <h2>Bob Smith - CTO</h2>
            <p>Bob Smith holds a PhD in Machine Learning from MIT. He spent 5 years at Google
            working on search algorithms before joining Alice to start TechCorp.
            Bob leads the technical vision for all products.</p>
        </div>
        
        <div class="bio">
            <h2>Carol Williams - VP Engineering</h2>
            <p>Carol Williams is a seasoned engineering leader with 15 years of experience.
            She previously led engineering teams at Uber and Airbnb.
            Carol joined TechCorp in 2020 to scale the engineering organization.</p>
        </div>
    </body>
    </html>
    """
    
    with open(html_file, 'w') as f:
        f.write(html_content)
    
    return samples_dir, text_file, html_file


def example_process_text_file():
    """Example 1: Process a text file"""
    print("📝 Example 1: Processing Text File")
    print("=" * 50)
    
    try:
        # Create sample content
        samples_dir, text_file, _ = create_sample_content()
        
        # Initialize document processor
        kg_engine = ExoGraphEngine(llm_config=OllamaConfig(),
                                   neo4j_config=Neo4jConfig())

        # Initialize document processor
        processor = DocumentProcessor(
            kg_engine=kg_engine,
            chunk_size=400,
            chunk_overlap=30
        )
        
        # Process the text file
        result = processor.process_text_file(
            text_file,
            source_metadata={
                "document_type": "company_overview",
                "author": "TechCorp HR",
                "year": 2024
            }
        )
        
        print(f"✅ Processing completed")
        print(f"   Success: {result.success}")
        print(f"   Chunks processed: {result.processed_chunks}")
        print(f"   Relationships created: {result.total_relationships}")
        
        if result.errors:
            print(f"   Errors: {result.errors}")
        
        # Search for extracted information
        print(f"\n🔍 Testing search capabilities:")
        search_queries = [
            "Who is the CEO of TechCorp?",
            "Where is TechCorp headquartered?", 
            "What products does TechCorp offer?"
        ]
        
        for query in search_queries:
            response = processor.search(query)
            print(f"   Q: {query}")
            print(f"   A: {response.answer}\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()


def example_process_html_file():
    """Example 2: Process an HTML file"""
    print("🌐 Example 2: Processing HTML File")
    print("=" * 50)
    
    try:
        # Create sample content
        samples_dir, _, html_file = create_sample_content()
        kg_engine = ExoGraphEngine(llm_config=OllamaConfig(),
                                   neo4j_config=Neo4jConfig())

        # Initialize document processor
        processor = DocumentProcessor(
            kg_engine=kg_engine,
            chunk_size=400,
            chunk_overlap=30
        )
        
        # Process the HTML file
        result = processor.process_html_file(
            html_file,
            source_metadata={
                "document_type": "team_biographies",
                "source_url": "https://techcorp.com/team",
                "last_updated": "2024-01-15"
            }
        )
        
        print(f"✅ Processing completed")
        print(f"   Success: {result.success}")
        print(f"   Chunks processed: {result.processed_chunks}")
        print(f"   Relationships created: {result.total_relationships}")
        
        # Search for team information
        print(f"\n🔍 Testing team queries:")
        team_queries = [
            "Who is the CTO of TechCorp?",
            "Where did Alice Johnson go to school?",
            "What is Bob Smith's educational background?"
        ]
        
        for query in team_queries:
            response = processor.search(query)
            print(f"   Q: {query}")
            print(f"   A: {response.answer}\n")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()


def example_process_text_content():
    """Example 3: Process raw text content"""
    print("📄 Example 3: Processing Raw Text Content")
    print("=" * 50)
    
    try:
        # Sample content about recent news
        news_content = """
        TechCorp Quarterly Update - Q4 2024
        
        Financial Performance:
        TechCorp reported revenue of $25 million in Q4 2024, representing 150% growth year-over-year.
        The company achieved profitability for the first time with a net income of $2.3 million.
        
        Product Launches:
        - TechCorp AI 3.0 was released in December with enhanced natural language processing
        - The new Enterprise Dashboard gained 500 new customers in its first month
        - Mobile SDK beta launched with partnerships from Apple and Google
        
        Team Growth:
        The engineering team grew from 50 to 75 engineers during Q4.
        New hires include:
        - Emma Davis as Principal Data Scientist (formerly at Netflix)
        - Frank Miller as Senior Product Manager (formerly at Spotify)
        - Grace Lee as Director of Marketing (formerly at Salesforce)
        
        Future Plans:
        TechCorp plans to expand to Asia-Pacific region in 2025.
        The company is also exploring acquisition opportunities in the cybersecurity space.
        """
        
        # Initialize document processor
        kg_engine = ExoGraphEngine(llm_config=OllamaConfig(),
                                   neo4j_config=Neo4jConfig())

        # Initialize document processor
        processor = DocumentProcessor(
            kg_engine=kg_engine,
            chunk_size=400,
            chunk_overlap=30
        )
        
        # Process the content
        result = processor.process_text_content(
            news_content,
            source_metadata={
                "document_type": "quarterly_update",
                "quarter": "Q4 2024",
                "source": "internal_report"
            }
        )
        
        print(f"✅ Processing completed")
        print(f"   Success: {result.success}")
        print(f"   Chunks processed: {result.processed_chunks}")
        print(f"   Relationships created: {result.total_relationships}")
        
        # Search for recent information
        print(f"\n🔍 Testing recent updates:")
        update_queries = [
            "What was TechCorp's revenue in Q4 2024?",
            "Who joined TechCorp as Principal Data Scientist?",
            "What are TechCorp's expansion plans?"
        ]
        
        for query in update_queries:
            response = processor.search(query)
            print(f"   Q: {query}")
            print(f"   A: {response.answer}\n")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()


def example_process_directory():
    """Example 4: Process entire directory"""
    print("📁 Example 4: Processing Directory")
    print("=" * 50)
    
    try:
        # Create sample content
        samples_dir, _, _ = create_sample_content()
        
        # Initialize document processor
        kg_engine = ExoGraphEngine(llm_config=OllamaConfig(),
                                   neo4j_config=Neo4jConfig())

        # Initialize document processor
        processor = DocumentProcessor(
            kg_engine=kg_engine,
            chunk_size=400,
            chunk_overlap=30
        )
        
        # Process entire directory
        results = processor.process_directory(samples_dir)
        
        print(f"✅ Directory processing completed")
        print(f"   Files processed: {len(results)}")
        
        total_chunks = 0
        total_relationships = 0
        
        for file_path, result in results.items():
            print(f"\n   📄 {Path(file_path).name}:")
            print(f"      Success: {result.success}")
            print(f"      Chunks: {result.processed_chunks}")
            print(f"      Relationships: {result.total_relationships}")
            
            total_chunks += result.processed_chunks
            total_relationships += result.total_relationships
            
            if result.errors:
                print(f"      Errors: {result.errors}")
        
        print(f"\n📊 Total Statistics:")
        print(f"   Total chunks processed: {total_chunks}")
        print(f"   Total relationships created: {total_relationships}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()


def example_with_custom_kg_engine():
    """Example 5: Using with custom KG engine configuration"""
    print("⚙️  Example 5: Custom KG Engine Configuration")
    print("=" * 50)
    
    try:
        from exo_graph import ExoGraphEngine, OllamaConfig
        
        # Create custom LLM configuration
        llm_config = OllamaConfig(
            base_url="http://localhost:11434/v1"
        )
        
        # Create custom KG engine
        kg_engine = ExoGraphEngine(
            llm_config=llm_config,
            neo4j_config=Neo4jConfig()
        )
        
        # Create document processor with custom engine
        processor = DocumentProcessor(
            kg_engine=kg_engine,
            chunk_size=300,
            chunk_overlap=25
        )
        
        # Process some content
        content = """
        AI Research Update:
        Dr. Sarah Chen published a breakthrough paper on transformer architectures.
        The research was conducted at MIT in collaboration with Stanford University.
        The paper introduces a new attention mechanism that reduces computational costs by 40%.
        """
        
        result = processor.process_text_content(
            content,
            source_metadata={
                "document_type": "research_paper",
                "field": "artificial_intelligence",
                "institution": "MIT"
            }
        )
        
        print(f"✅ Processing with custom configuration completed")
        print(f"   Model used: {kg_engine.llm.model}")
        print(f"   Provider: {kg_engine.llm.config.provider}")
        print(f"   Chunks processed: {result.processed_chunks}")
        print(f"   Relationships created: {result.total_relationships}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("   Make sure Ollama is running with phi3:3.8b model")
    
    print()


if __name__ == "__main__":
    print("📚 Document Processing Examples for KG Engine v2")
    print("=" * 60)
    print()
    
    # Check dependencies
    try:
        import langchain
        print("✅ LangChain available")
    except ImportError:
        print("❌ LangChain not available - install with: pip install langchain pypdf")
        sys.exit(1)
    
    # Run examples
    example_process_text_file()
    example_process_html_file()
    example_process_text_content()
    example_process_directory()
    example_with_custom_kg_engine()
    
    print("🎉 All document processing examples completed!")
    print()
    print("💡 Next steps:")
    print("   - Try processing your own PDF files")
    print("   - Experiment with different chunk sizes")
    print("   - Explore the extracted knowledge graph")
    print("   - Use the search functionality to query your documents")