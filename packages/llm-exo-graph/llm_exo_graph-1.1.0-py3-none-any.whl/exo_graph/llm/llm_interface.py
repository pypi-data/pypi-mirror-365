"""
LLM interface for Knowledge Graph Engine v2
"""
import json
import re
from typing import List, Dict, Any, Optional, Union
from openai import OpenAI
from ..models import ExtractedInfo, ParsedQuery, SearchType
from ..utils.date_parser import parse_date
from .llm_config import LLMConfig
from .llm_client_factory import LLMClientFactory
import logging
import json_repair


def parse_json_response(content: str) -> Union[Dict, List]:
    """
    Parse JSON from LLM response content.
    
    Args:
        content: Raw response content from LLM
        
    Returns:
        Parsed JSON object (dict or list)
        
    Raises:
        json.JSONDecodeError: If JSON parsing fails
    """
    # Clean up the response to get just the JSON
    if content.startswith('```json'):
        content = content[7:-3].strip()
    elif content.startswith('```'):
        content = content[3:-3].strip()

    try:
        # Parse JSON response
        result = json.loads(content)

    except json.JSONDecodeError as e:
        logging.warning(f"Failed to parse LLM response: {e}\r\nContent: {content}")
        repaired_json = json_repair.loads(content)
        if not repaired_json:
            raise Exception(f"Failed to parse LLM response: {e}\r\nContent: {content}")

        result = repaired_json

    logging.debug(f'Extracted: \r\n {result}')

    return result

class LLMInterface:
    """Interface for LLM-powered entity and relationship extraction"""

    def __init__(self, 
                 llm_config: Optional[LLMConfig] = None,
                 api_key: Optional[str] = None, 
                 model: Optional[str] = None,
                 base_url: Optional[str] = None, 
                 bearer_token: Optional[str] = None):
        """
        Initialize LLM Interface with configuration.
        
        Args:
            llm_config: Direct LLMConfig instance (preferred)
            api_key: Legacy parameter for backward compatibility
            model: Legacy parameter for backward compatibility
            base_url: Legacy parameter for backward compatibility
            bearer_token: Legacy parameter for backward compatibility
        """
        if llm_config:
            self.config = llm_config
        elif api_key or model or base_url or bearer_token:
            # Legacy parameter support
            self.config = LLMClientFactory.create_from_params(
                api_key=api_key,
                model=model,
                base_url=base_url,
                bearer_token=bearer_token
            )
        else:
            # Use environment-based configuration
            self.config = LLMClientFactory.create_from_env()
        
        # Create client and get model name from config
        self.client = self.config.create_client()
        self.model = self.config.get_model_name()
        
        # Log initialization
        config_type = self.config.provider
        print(f"🤖 LLM Interface initialized: {self.model} via {config_type}")

    def extract_entities_relationships(self, text: str) -> List[ExtractedInfo]:
        """Extract entities and relationships from text using LLM"""

        extraction_prompt = f"""

Extract entities and relationships from the following text.  
Return a **JSON array** of relationship objects.  
Only return **valid JSON**. Do **not** include explanations, markdown, or extra text.

---

Each JSON object must include:

- `subject`: the main entity (person, place, or thing). Use the **singular form**, exactly as in the input (e.g., "engineer", "company", "Emma").
- `relationship`: the **action or state**, written in **UPPERCASE_WITH_UNDERSCORES** (e.g., `WORKS_AT`, `LIVES_IN`, `HAS_STATUS`)
- `object`: the target entity (use **singular** form)
- `summary`: short natural-language description (**same language** as the input)
- `category`: semantic category for the relationship (e.g., "employment", "location", "activity", "personal", "business", "education", "communication", "status")
- `is_negation`: `true` if the sentence negates or ends a fact (e.g., “no longer works”), else `false`
- `confidence`: a float from `0.0` to `1.0`, expressing confidence in the relation
- `from_date`: ISO format (`YYYY-MM-DD`) if a start date is mentioned, else `null`
- `to_date`: ISO format (`YYYY-MM-DD`) if an end date is mentioned, else `null`

---

### 🌐 Language

- Keep **subject, object, summary** in the **same language** as the input.
- Keep **relationship** always English

Examples:
"Emma speaks English" -> 
[{{
  "subject": "Emma",
  "relationship": "SPEAKS",
  "object": "English", 
  "summary": "Emma speaks English",
  "category": "communication",
  "is_negation": false,
  "confidence": 0.95,
  "from_date": null,
  "to_date": null
}}]

"Company A was founded" ->
[{{
  "subject": "Company A",
  "relationship": "HAS_STATUS",
  "object": "founded",
  "summary": "Company A was founded",
  "category": "status",
  "is_negation": false,
  "confidence": 0.9,
  "from_date": null,
  "to_date": null
}}]


"John moved to Paris from London" ->
[{{
  "subject": "John",
  "relationship": "LIVES_IN", 
  "object": "Paris",
  "summary": "John lives in Paris",
  "category": "location",
  "is_negation": false,
  "confidence": 0.9,
  "from_date": null,
  "to_date": null
}},
{{
  "subject": "John",
  "relationship": "MOVED_FROM",
  "object": "London", 
  "summary": "John moved from London",
  "category": "location",
  "is_negation": false,
  "confidence": 0.85,
  "from_date": null,
  "to_date": null
}}]

"Emma no longer works at TechCorp" ->
[{{
  "subject": "Emma",
  "relationship": "WORKS_AT",
  "object": "TechCorp",
  "summary": "Emma no longer works at TechCorp", 
  "category": "employment",
  "is_negation": true,
  "confidence": 0.9,
  "from_date": null,
  "to_date": null
}}]

"Alice worked at Microsoft from 2020 to 2023" ->
[{{
  "subject": "Alice",
  "relationship": "WORKS_AT",
  "object": "Microsoft",
  "summary": "Alice worked at Microsoft from 2020 to 2023",
  "category": "employment",
  "is_negation": false,
  "confidence": 0.95,
  "from_date": "2020-01-01",
  "to_date": "2023-12-31"
}}]

"Bob started at Google in January 2022" ->
[{{
  "subject": "Bob",
  "relationship": "WORKS_AT",
  "object": "Google",
  "summary": "Bob started at Google in January 2022",
  "category": "employment",
  "is_negation": false,
  "confidence": 0.9,
  "from_date": "2022-01-01",
  "to_date": null
}}]

Text to analyze: "{text}"

Return only valid JSON array, no other text:
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system",
                     "content": "You are an expert at extracting structured information from text. Always return valid JSON."},
                    {"role": "user", "content": extraction_prompt}
                ],
                temperature=0.1
            )

            content = response.choices[0].message.content.strip()

            # Parse JSON response
            relationships = parse_json_response(content)

            # Convert to ExtractedInfo objects
            extracted = []
            def extract_relationships(rel: Dict[str, Any], obj: str=None):
               return ExtractedInfo(
                    subject=rel.get('subject'),
                    relationship=rel.get('relationship', 'RELATED_TO'),
                    object=obj or rel.get('object'),
                    summary=rel.get('summary', ''),
                    is_negation=rel.get('is_negation', False),
                    confidence=rel.get('confidence', 1.0),
                    from_date=parse_date(rel.get('from_date')),
                    to_date=parse_date(rel.get('to_date')),
                    category=rel.get('category', "unknown")  # Include LLM-provided category
                )
            for rel in relationships:
                # Validate required fields
                try:
                    # some llm model return object as list, let it be...
                    if isinstance(rel.get('object', None),List):
                        for obj in rel.get('object'):
                            extracted.append(extract_relationships(rel, obj))
                    else:
                        extracted.append(extract_relationships(rel))

                except Exception as e:
                    logging.warning(f"Parse result error {e} for {content[:100]}....")

            return extracted

        except Exception as e:
            print(f"Error in LLM extraction: {e}")
            raise e

    def parse_query(self, query: str, existing_relationships: List[str] = None) -> ParsedQuery:
        """Parse natural language query into structured search parameters using LLM intuition"""

        query_prompt = f"""
Convert this natural language query into graph search parameters using your intuition.
Do NOT rely on existing relationship types - infer the most suitable relationships.

Query: "{query}"

Return JSON with:
- entities: list of entity names mentioned or implied
- relationships: list of relationship objects with:
  - name: the **action or state**, written in **UPPERCASE_WITH_UNDERSCORES** (e.g., `WORKS_AT`, `LIVES_IN`, `HAS_STATUS`)
  - category: relationship category (e.g., "employment", "location", "language", "personal")
  - summary: brief description of what this relationship represents
- query_intent: "search", "count", "exists", "list", "compare"

Examples:

"Where does Emma live?" ->
{{
  "entities": ["Emma"],
  "relationships": [
    {{
      "name": "lives in",
      "category": "location", 
      "summary": "residential location relationship"
    }},
    {{
      "name": "resides in",
      "category": "location",
      "summary": "permanent residence relationship"
    }}
  ],
  "query_intent": "search"
}}

"Who works at TechCorp?" ->
{{
  "entities": ["TechCorp"],
  "relationships": [
    {{
      "name": "works at",
      "category": "employment",
      "summary": "employment relationship"
    }},
    {{
      "name": "employed by",
      "category": "employment", 
      "summary": "employer-employee relationship"
    }}
  ],
  "query_intent": "list"
}}

"What languages does John speak?" ->
{{
  "entities": ["John"],
  "relationships": [
    {{
      "name": "speaks",
      "category": "language",
      "summary": "language proficiency relationship"
    }}
  ],
  "query_intent": "list"
}}

Return only valid JSON, no other text:
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system",
                 "content": "You are an expert at understanding search queries. Always return valid JSON."},
                {"role": "user", "content": query_prompt}
            ],
            temperature=0.1
        )

        content = response.choices[0].message.content.strip()

        parsed = parse_json_response(content)

        # Convert relationship objects to simple list for backward compatibility
        relationship_names = []
        if 'relationships' in parsed:
            for rel in parsed['relationships']:
                if isinstance(rel, dict):
                    relationship_names.append(rel.get('name', ''))
                else:
                    relationship_names.append(str(rel))

        # Store raw relationship data for standardization
        self._last_parsed_relationships = parsed.get('relationships', [])
        
        return ParsedQuery(
            entities=parsed.get('entities', []),
            relationships=relationship_names,
            search_type=SearchType.DIRECT,
            query_intent=parsed.get('query_intent', 'search'),
        )
    
    def get_raw_relationships(self) -> List[Dict[str, str]]:
        """Get the raw relationship objects from the last parse_query call"""
        return getattr(self, '_last_parsed_relationships', [])

    def generate_answer(self, query: str, search_results: List[Union[Dict, str]]) -> str:
        """Generate natural language answer from search results"""

        if not search_results:
            return "I don't have information to answer that question."

        # Format results for LLM
        formatted_results = []
        for result in search_results[:5]:  # Limit to top 5 results
            if isinstance(result, dict):
                formatted_results.append(f"- {result.get('summary', 'No summary available')}")
            else:
                formatted_results.append(f"- {str(result)}")

        results_text = "\\n".join(formatted_results)

        answer_prompt = f"""
Based on the following search results, provide a clear, concise answer to the user's question.

Question: "{query}"

Search Results:
{results_text}

Guidelines:
- Be factual and direct
- If multiple answers exist, mention the most relevant ones
- If information is uncertain, say so
- Keep the answer conversational but informative
- Don't mention "search results" or "according to the data"

Answer:
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system",
                     "content": "You are a helpful assistant that answers questions based on knowledge graph data."},
                    {"role": "user", "content": answer_prompt}
                ],
                temperature=0.3
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"Error generating answer: {e}")
            # Fallback to simple concatenation
            if search_results:
                first_result = search_results[0]
                if isinstance(first_result, dict):
                    return first_result.get('summary', 'Found relevant information.')
            return "I found some information but couldn't process it properly."

    def resolve_node_merge(self, node1_data: Dict[str, Any], node2_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use LLM to intelligently resolve how to merge two nodes.
        
        Args:
            node1_data: First node's properties
            node2_data: Second node's properties
            
        Returns:
            Dictionary with merge decisions: name, metadata, confidence, reasoning
        """
        merge_prompt = f"""
Analyze these two nodes that represent the same entity and decide how to merge them optimally.

Node 1: {node1_data}
Node 2: {node2_data}

Return a JSON response with:
- merged_name: The best name for the merged node (choose most complete/formal)
- merged_metadata: Combined metadata with resolved conflicts
- confidence: 0.0-1.0 confidence in merge decisions
- reasoning: Brief explanation of decisions made
- name_source: "node1", "node2", or "combined" indicating name choice
- metadata_conflicts: List of any conflicting properties and how resolved

Guidelines:
- Choose the most complete, formal, or commonly used name
- Combine metadata intelligently (prefer more recent dates, higher quality data)
- For conflicts, choose the most reliable or recent information
- If names are very different, consider if they truly represent the same entity

Examples:

Input: Node 1: {{"name": "John Smith", "type": "Person", "email": "john@example.com"}}
       Node 2: {{"name": "J. Smith", "type": "Person", "phone": "555-1234"}}

Output: {{
  "merged_name": "John Smith",
  "merged_metadata": {{
    "type": "Person",
    "email": "john@example.com", 
    "phone": "555-1234"
  }},
  "confidence": 0.95,
  "reasoning": "Full name 'John Smith' is more complete than 'J. Smith'. Combined contact information.",
  "name_source": "node1",
  "metadata_conflicts": []
}}

Return only valid JSON:
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system",
                 "content": "You are an expert at intelligent data merging. Always return valid JSON."},
                {"role": "user", "content": merge_prompt}
            ],
            temperature=0.1
        )

        content = response.choices[0].message.content.strip()

        # Parse JSON response
        merge_result = parse_json_response(content)
        return merge_result

    def estimate_category_for_predicate(self, predicate: str) -> Optional[str]:
        """
        Use LLM to imagine and estimate the most suitable category for a predicate.
        Does not rely on existing categories - creates intelligent category suggestions.
        
        Args:
            predicate: The relationship type to classify
            
        Returns:
            LLM-estimated category name or None if LLM fails
        """
        try:
            category_prompt = f"""Your task is to determine the BEST semantic category for the relationship type "{predicate}".

Relationship to classify: "{predicate}"

Your task:
- Analyze the semantic meaning of the relationship
- Determine what broad category this relationship belongs to
- Choose the most intuitive, commonly used category name
- Think about how humans would naturally group this type of relationship
Instructions:
- Return ONLY the category name (one or two words maximum)
- Use lowercase, simple, intuitive category names
- Choose the most specific yet broadly applicable category
- Think about the primary semantic domain of the relationship

Examples:
- "works at" → employment
- "lives in" → location
- "enjoys" → activity
- "manages" → employment
- "owns" → ownership
- "studies at" → education
- "married to" → personal
- "located in" → location
- "happened during" → temporal
- "speaks" → communication

Category:"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", 
                     "content": "You are an expert at semantic classification. Respond with only the category name, no explanation."},
                    {"role": "user", "content": category_prompt}
                ],
                temperature=0.1,
                max_tokens=10  # Limit response to just the category name
            )
            
            if response and response.choices:
                estimated_category = response.choices[0].message.content.strip().lower()
                
                # Clean up the response - remove any extra text
                # Take only the first word if multiple words returned
                estimated_category = estimated_category.split()[0] if estimated_category.split() else ""
                
                # Remove any punctuation
                estimated_category = re.sub(r'[^\w]', '', estimated_category)
                
                if estimated_category and len(estimated_category) > 1:
                    logging.info(f"LLM estimated category for '{predicate}': '{estimated_category}'")
                    return estimated_category
                else:
                    logging.warning(f"LLM returned invalid category '{estimated_category}' for '{predicate}'")
                    return None
            else:
                logging.warning(f"LLM returned empty response for predicate '{predicate}'")
                return None
                
        except Exception as e:
            logging.warning(f"LLM category estimation failed for '{predicate}': {e}")
            return None


