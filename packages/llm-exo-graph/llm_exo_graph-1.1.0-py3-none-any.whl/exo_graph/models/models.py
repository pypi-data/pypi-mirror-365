"""
Data models for Knowledge Graph Engine v2
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
import uuid


class RelationshipStatus(Enum):
    ACTIVE = "active"
    OBSOLETE = "obsolete"


class SearchType(Enum):
    DIRECT = "direct"
    SEMANTIC = "semantic"
    BOTH = "both"


@dataclass
class InputItem:
    description: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EdgeMetadata:
    summary: str
    created_at: datetime = field(default_factory=datetime.now)
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    obsolete: bool = False
    result: Optional[str] = None
    status: RelationshipStatus = RelationshipStatus.ACTIVE
    confidence: float = 1.0
    source: Optional[str] = None
    user_id: Optional[str] = None  # User ID (GUID) for multi-tenant support
    category: Optional[str] = None  # Classifier category (location, business, relations, etc.)
    additional_metadata: Dict[str, Any] = field(default_factory=dict)  # For extra metadata

    def to_dict(self) -> Dict[str, Any]:
        base_dict = {
            'summary': self.summary,
            'created_at': self.created_at.isoformat(),
            'from_date': self.from_date.isoformat() if self.from_date else None,
            'to_date': self.to_date.isoformat() if self.to_date else None,
            'obsolete': self.obsolete,
            'result': self.result,
            'status': self.status.value,
            'confidence': self.confidence,
            'source': self.source,
            'user_id': self.user_id,
            'category': self.category
        }
        # Merge additional metadata
        base_dict.update(self.additional_metadata)
        return base_dict


@dataclass
class GraphEdge:
    """
    Represents an edge in the knowledge graph.
    
    In Neo4j, edges are stored with specific relationship types:
    (subject:Entity) -[:WORKS_AT {edge_id, metadata...}]-> (object:Entity)
    """
    edge_id: Optional[str]
    metadata: EdgeMetadata
    subject: str
    relationship: str
    object: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'edge_id': self.edge_id,
            'metadata': self.metadata.to_dict(),
            'subject': self.subject,
            'relationship': self.relationship,
            'object': self.object
        }


@dataclass
class GraphTriplet:
    edge: GraphEdge
    vector_id: Optional[str] = None
    embedding: Optional[List[float]] = None
    vector_text: Optional[str] = None


# EdgeData class removed - use GraphEdge directly


@dataclass
class ExtractedInfo:
    subject: str
    relationship: str
    object: str
    summary: str
    is_negation: bool = False
    confidence: float = 1.0
    from_date: Optional[str] = None
    to_date: Optional[str] = None
    category: Optional[str] = None


@dataclass
class ParsedQuery:
    entities: List[str]
    relationships: List[str]
    search_type: SearchType
    query_intent: str = "search"  # search, count, exists, etc.
    temporal_context: Optional[str] = None


@dataclass
class SearchResult:
    triplet: GraphTriplet
    score: float
    source: str  # "graph", "vector", "hybrid"
    explanation: Optional[str] = None


@dataclass
class QueryResponse:
    results: List[SearchResult]
    total_found: int
    query_time_ms: float
    answer: Optional[str] = None
    confidence: float = 1.0
