#!/usr/bin/env python3
"""
Bible Text Processing Example using LiteLLM with KG Engine v2

This example demonstrates batch processing of Biblical text to extract 
entities and relationships using LiteLLM as the LLM provider.

Prerequisites:
- Set LITELLM_BEARER_TOKEN environment variable
- Set LITELLM_BASE_URL environment variable  
- Neo4j database running and configured
"""

import os
import sys
import time
import logging
from pathlib import Path
from typing import List, Dict, Any

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from exo_graph.core.engine import ExoGraphEngine
from exo_graph.models import InputItem
from exo_graph.config import Neo4jConfig
from exo_graph.llm.llm_config import LiteLLMConfig
from exo_graph.llm.llm_client_factory import LLMClientFactory

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Disable tokenizer parallelism warning
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Configuration
DEFAULT_BATCH_SIZE = 5
DEFAULT_NUM_BATCHES = 10
DEFAULT_BATCH_OFFSET = 50
DEFAULT_DELAY_SECONDS = 0
BIBLE_PATH = Path(__file__).parent / "sample_documents" / "bible.txt"


class BibleProcessor:
    """Bible text processor using KG Engine v2 with LiteLLM"""

    def __init__(self, bearer_token: str = None, base_url: str = None, model: str = "gpt-4o-mini"):
        """
        Initialize the Bible processor
        
        Args:
            bearer_token: LiteLLM bearer token
            base_url: LiteLLM base URL
            model: Model name to use
        """
        self.bearer_token = bearer_token or os.getenv("LITELLM_BEARER_TOKEN")
        self.base_url = base_url or os.getenv("LITELLM_BASE_URL")
        self.model = model

        if not self.bearer_token or not self.base_url:
            raise ValueError(
                "LITELLM_BEARER_TOKEN and LITELLM_BASE_URL environment variables must be set, "
                "or pass them as parameters"
            )

        self.engine = None
        self.verses = []

    def setup_engine(self):
        """Initialize the KG Engine with LiteLLM configuration"""
        print("🔧 Setting up KG Engine with LiteLLM...")

        # Create LiteLLM configuration
        litellm_config = LiteLLMConfig(
            bearer_token=self.bearer_token,
            model=self.model,
            base_url=self.base_url,
            additional_headers={"X-Application": "kg-engine-bible-example"}
        )

        # Create Neo4j configuration
        neo4j_config = Neo4jConfig()

        # Verify Neo4j connectivity
        if not neo4j_config.verify_connectivity():
            raise ConnectionError("Cannot connect to Neo4j database")

        # Initialize the engine
        self.engine = ExoGraphEngine(
            llm_config=litellm_config,
            neo4j_config=neo4j_config
        )

        # self.clear_data()

        print(f"✅ KG Engine initialized")
        print(f"   LLM Provider: {self.engine.llm.config.provider}")
        print(f"   Model: {self.engine.llm.model}")
        print(f"   Base URL: {self.base_url}")

    def load_bible_text(self):
        """Load and parse Bible text into verses"""
        print("📖 Loading Bible text...")

        if not BIBLE_PATH.exists():
            raise FileNotFoundError(f"Bible text file not found: {BIBLE_PATH}")

        with open(BIBLE_PATH, 'r', encoding='utf-8') as f:
            content = f.read()

        # Split into verses (lines with verse numbers like "1:1", "1:2", etc.)
        lines = content.split('\n')
        verses = []

        for line in lines:
            line = line.strip()
            if line and ':' in line and any(char.isdigit() for char in line.split(':')[0]):
                verses.append(line)

        self.verses = verses
        print(f"📖 Loaded {len(verses)} verses from Bible")
        print(f"   First verse: {verses[0][:100]}..." if verses else "   No verses found")
        print(f"   Last verse: {verses[-1][:100]}..." if verses else "")

    def process_batches(self,
                        batch_size: int = DEFAULT_BATCH_SIZE,
                        num_batches: int = DEFAULT_NUM_BATCHES,
                        batch_offset: int = DEFAULT_BATCH_OFFSET,
                        delay: float = DEFAULT_DELAY_SECONDS) -> Dict[str, Any]:
        """
        Process Bible verses in batches
        
        Args:
            batch_size: Number of verses per batch
            num_batches: Maximum number of batches to process
            batch_offset: Offset in batches (skip first n batches)
            delay: Delay between batches in seconds
            
        Returns:
            Dictionary with processing statistics
        """
        if not self.verses:
            raise ValueError("No verses loaded. Call load_bible_text() first.")

        if not self.engine:
            raise ValueError("Engine not initialized. Call setup_engine() first.")

        print("🔄 Starting Bible batch processing...")

        # Calculate batches
        total_possible_batches = len(self.verses) // batch_size
        batches_to_process = min(num_batches, total_possible_batches)

        print(f"⚙️ Configuration:")
        print(f"   Batch size: {batch_size} verses")
        print(f"   Batches to process: {batches_to_process}")
        print(f"   Total verses to process: {batches_to_process * batch_size}")
        print(f"   Delay between batches: {delay}s")
        print()

        # Initialize statistics
        stats = {
            "processed_items": 0,
            "new_edges": 0,
            "updated_edges": 0,
            "obsoleted_edges": 0,
            "duplicates_ignored": 0,
            "errors": [],
            "processing_time_ms": 0,
            "batches_completed": 0,
            "batch_results": []
        }

        start_time = time.time()

        verses_to_process = self.verses[(batch_offset * batch_size):]
        # Process batches
        for batch_num in range(batches_to_process):
            batch_start_time = time.time()
            start_idx = batch_num * batch_size
            end_idx = start_idx + batch_size

            # Get verses for this batch
            batch_verses = verses_to_process[start_idx:end_idx]

            # Create InputItems with metadata
            input_items = [
                InputItem(
                    description=verse,
                    metadata={
                        "source": "bible",
                        "batch_number": batch_num + 1,
                        "verse_index": start_idx + i,
                        "chapter_verse": verse.split()[0] if verse.split() else f"unknown:{i}"
                    }
                )
                for i, verse in enumerate(batch_verses)
            ]

            print(f"📦 Batch {batch_num + 1}/{batches_to_process}")
            print(f"   Verses {start_idx + 1}-{end_idx}")
            print(f"   Sample: {batch_verses[0][:80]}...")

            try:
                # Process the batch
                results = self.engine.process_input(input_items)
                batch_time = (time.time() - batch_start_time) * 1000

                # Update statistics
                stats["processed_items"] += results.get("processed_items", 0)
                stats["new_edges"] += results.get("new_edges", 0)
                stats["updated_edges"] += results.get("updated_edges", 0)
                stats["obsoleted_edges"] += results.get("obsoleted_edges", 0)
                stats["duplicates_ignored"] += results.get("duplicates_ignored", 0)

                if results.get("errors"):
                    stats["errors"].extend(results["errors"])

                # Store batch result
                stats["batch_results"].append({
                    "batch_number": batch_num + 1,
                    "processing_time_ms": batch_time,
                    "results": results
                })

                stats["batches_completed"] += 1

                print(f"   ✅ Completed in {batch_time:.1f}ms")
                print(f"   New edges: {results.get('new_edges', 0)}")
                print(f"   Errors: {len(results.get('errors', []))}")

            except Exception as e:
                error_msg = f"Batch {batch_num + 1} failed: {str(e)}"
                print(f"   ❌ {error_msg}")
                stats["errors"].append(error_msg)
                logger.error(f"Batch processing error: {e}")

            # Delay between batches (except for the last one)
            if batch_num < batches_to_process - 1 and delay > 0:
                print(f"   ⏸️ Waiting {delay}s...")
                time.sleep(delay)

            print()  # Empty line between batches

        stats["processing_time_ms"] = (time.time() - start_time) * 1000
        return stats

    def print_statistics(self, stats: Dict[str, Any]):
        """Print processing statistics"""
        print("📊 Final Processing Statistics:")
        print("=" * 50)
        print(f"   Total batches completed: {stats['batches_completed']}")
        print(f"   Total items processed: {stats['processed_items']}")
        print(f"   Total new edges: {stats['new_edges']}")
        print(f"   Total updated edges: {stats['updated_edges']}")
        print(f"   Total obsoleted edges: {stats['obsoleted_edges']}")
        print(f"   Total duplicates ignored: {stats['duplicates_ignored']}")
        print(f"   Total errors: {len(stats['errors'])}")
        print(f"   Total processing time: {stats['processing_time_ms']:.1f}ms")

        if stats['batches_completed'] > 0:
            avg_time = stats['processing_time_ms'] / stats['batches_completed']
            print(f"   Average time per batch: {avg_time:.1f}ms")

        # Show sample errors
        if stats['errors']:
            print(f"\n⚠️ Sample errors (first 3):")
            for i, error in enumerate(stats['errors'][:3]):
                print(f"   {i + 1}. {error}")

    def show_graph_stats(self):
        """Show current graph database statistics"""
        if not self.engine:
            print("❌ Engine not initialized")
            return

        print("\n📈 Current Graph Statistics:")
        print("=" * 30)

        try:
            stats = self.engine.get_stats()
            print(f"   Total entities: {stats.get('entities', 0)}")
            print(f"   Active edges: {stats.get('graph_stats', {}).get('active_edges', 0)}")
            print(f"   Total edges: {stats.get('graph_stats', {}).get('total_edges', 0)}")
            print(f"   Relationship types: {stats.get('graph_stats', {}).get('relationship_types', 0)}")

            # Show sample relationships
            relationships = stats.get('relationships', [])
            if relationships:
                print(f"\n📋 Sample relationship types (first 10):")
                for rel in relationships[:10]:
                    print(f"   - {rel}")
        except Exception as e:
            print(f"   Error getting stats: {e}")

    def test_queries(self):
        """Test some sample queries on the processed data"""
        if not self.engine:
            print("❌ Engine not initialized")
            return

        test_queries = [
            "Who created the heaven and earth?",
            "What did God create on the first day?",
            "What is the firmament?",
            "What did God call the light?",
            "What did God see that was good?"
        ]

        print("\n🔍 Testing queries on processed Bible data:")
        print("=" * 50)

        for i, query in enumerate(test_queries):
            print(f"\n{i + 1}. Q: {query}")
            try:
                response = self.engine.search(query)
                print(f"   A: {response.answer}")
                print(f"   ({len(response.results)} results, {response.query_time_ms:.1f}ms)")
            except Exception as e:
                print(f"   ❌ Error: {e}")

    def clear_data(self):
        """Clear all data from the knowledge graph"""
        if not self.engine:
            print("❌ Engine not initialized")
            return

        print("\n🧹 Clearing all data...")
        try:
            success = self.engine.clear_all_data()
            if success:
                print("✅ All data cleared")
            else:
                print("⚠️ Data clearing may have been incomplete")
        except Exception as e:
            print(f"❌ Error clearing data: {e}")


def main():
    """Main execution function"""
    print("📜 Bible Processing Example with LiteLLM")
    print("=" * 50)

    # Check environment variables
    bearer_token = os.getenv("LITELLM_BEARER_TOKEN")
    base_url = os.getenv("LITELLM_BASE_URL")

    if not bearer_token or not base_url:
        print("❌ Missing required environment variables:")
        print("   - LITELLM_BEARER_TOKEN: Your LiteLLM bearer token")
        print("   - LITELLM_BASE_URL: Your LiteLLM base URL")
        print("\nExample:")
        print("   export LITELLM_BEARER_TOKEN='your-token-here'")
        print("   export LITELLM_BASE_URL='https://api.litellm.ai/v1'")
        return 1

    try:
        # Initialize processor
        processor = BibleProcessor(model=os.getenv("LITELLM_MODEL"))  # Use cost-effective model

        # Setup components
        processor.setup_engine()
        processor.load_bible_text()

        # Process Bible text in batches
        print(f"🚀 Starting processing with LiteLLM...")
        stats = processor.process_batches(
            batch_size=3,  # Small batches for this example
            num_batches=50,  # Process first 5 batches (15 verses)
            batch_offset=50,
        )

        # Show results
        processor.print_statistics(stats)
        processor.show_graph_stats()
        processor.test_queries()

        # Optional: Clear data for next run
        # processor.clear_data()

        print("\n🎉 Bible processing example completed!")
        return 0

    except Exception as e:
        print(f"❌ Fatal error: {e}")
        logger.error(f"Fatal error in main: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
