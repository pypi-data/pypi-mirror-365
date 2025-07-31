"""
Models for the SPT Neo RAG Client.

These Pydantic models mirror the API's data models.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from uuid import UUID
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict, EmailStr


class AllowedWebhookMethods(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"

class KnowledgeGraphExtractionStrategy(str, Enum):
    LLM = "llm"
    SPACY = "spacy"
    CUSTOM = "custom"

class Token(BaseModel):
    """Authentication token response model."""
    access_token: str
    token_type: str
    expires_at: datetime
    user_id: str


class UserCreate(BaseModel):
    """User creation model."""
    email: str
    password: str
    name: str


class UserResponse(BaseModel):
    """User response model."""
    id: UUID
    email: str
    name: str
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None


class UserUpdate(BaseModel):
    """User update model."""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    # Note: is_superuser is typically handled server-side, not updated by user/client
    # is_superuser: Optional[bool] = None


class UserResponseMinimal(BaseModel):
    """Minimal user response for team context."""
    id: UUID
    name: str
    email: EmailStr


class ApiKeyCreate(BaseModel):
    """API key creation model."""
    name: str
    scopes: str = "query"
    expires_in_days: Optional[int] = None


class ApiKeyResponse(BaseModel):
    """API key response model."""
    id: UUID
    name: str
    key_prefix: str
    scopes: str
    is_active: bool
    created_at: datetime
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    

class ApiKeyFullResponse(ApiKeyResponse):
    """API key response with full key (only returned at creation)."""
    api_key: str


class ApiKeyUpdate(BaseModel):
    """API key update model."""
    name: Optional[str] = None
    scopes: Optional[str] = None
    is_active: Optional[bool] = None
    expires_in_days: Optional[int] = None


class KnowledgeBaseCreate(BaseModel):
    """Knowledge base creation model."""
    name: str
    description: Optional[str] = None
    kb_type: str = "default"
    config: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    credentials: Optional[List[str]] = None


class KnowledgeBaseUpdate(BaseModel):
    """Knowledge base update model."""
    name: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    credentials: Optional[List[str]] = None


class KnowledgeBaseConfigUpdate(BaseModel):
    """Knowledge base configuration update model."""
    config: Dict[str, Any]


class KnowledgeBaseResponse(BaseModel):
    """Knowledge base response model."""
    id: UUID
    name: str
    description: Optional[str] = None
    kb_type: str
    config: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    credentials: Optional[List[str]] = ["ALL"]
    created_at: datetime
    updated_at: Optional[datetime] = None
    documents_count: Optional[int] = None
    
    # Webhook configuration
    webhook_url: Optional[str] = None
    is_webhook_enabled: bool = False
    webhook_method: AllowedWebhookMethods = AllowedWebhookMethods.POST
    webhook_secret_is_set: bool = False
    
    # Knowledge Graph configuration
    enable_knowledge_graph: bool = False
    kg_extraction_strategy: str = "llm"
    kg_confidence_threshold: float = 0.7
    kg_entity_count: Optional[int] = 0
    kg_relationship_count: Optional[int] = 0


class KnowledgeBaseResponseMinimal(BaseModel):
    """Minimal KB response for team context."""
    id: UUID
    name: str


class DocumentCreate(BaseModel):
    """Document creation model (used internally)."""
    name: str
    knowledge_base_id: UUID
    description: Optional[str] = None
    source: Optional[str] = None
    doc_metadata: Optional[Dict[str, Any]] = None
    processor_type: str = "langchain"
    processor_config: Optional[Dict[str, Any]] = None
    credentials: Optional[List[str]] = None
    structured_content_type: Optional[str] = None
    structured_content: Optional[bool] = False


class DocumentUpdate(BaseModel):
    """Document update model."""
    name: Optional[str] = None
    description: Optional[str] = None
    source: Optional[str] = None
    doc_metadata: Optional[Dict[str, Any]] = None
    credentials: Optional[List[str]] = None
    structured_content_type: Optional[str] = None
    structured_content: Optional[bool] = False


class BoundingBox(BaseModel):
    """Bounding box model for document page images."""
    x0: float
    y0: float
    x1: float
    y1: float


class DocumentPageImageResponse(BaseModel):
    """Document page image response model."""
    id: UUID
    document_id: UUID
    page_number: int
    image_url: str
    width: int
    height: int
    created_at: datetime


class DocumentChunkResponse(BaseModel):
    """Document chunk response model."""
    id: UUID
    document_id: UUID
    content: str
    chunk_index: int
    page_number: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
    embedding: Optional[List[float]] = None
    bounding_box: Optional[BoundingBox] = None
    created_at: datetime
    

class DocumentResponse(BaseModel):
    """Document response model."""
    id: UUID
    name: str
    knowledge_base_id: UUID
    description: Optional[str] = None
    source: Optional[str] = None
    doc_metadata: Optional[Dict[str, Any]] = None
    file_name: str
    file_size: int
    file_type: str
    page_count: int
    chunk_count: int
    status: str
    credentials: Optional[List[str]] = ["ALL"]
    created_at: datetime
    updated_at: Optional[datetime] = None
    download_url: Optional[str] = None
    structured_content_type: Optional[str] = None
    structured_content: Optional[bool] = False
    structured_content_path: Optional[str] = None


class QueryResultSource(BaseModel):
    """Source in query result."""
    document_id: UUID
    chunk_id: UUID
    document_name: str
    content: str
    page_number: Optional[int] = None
    relevance_score: float
    metadata: Optional[Dict[str, Any]] = None
    
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )


class QueryResult(BaseModel):
    """Query result model."""
    query: str
    answer: str
    sources: Optional[List[QueryResultSource]] = Field(
        default_factory=list
    )
    
    model_config = ConfigDict(
        populate_by_name=True,
    )


class QueryResponse(BaseModel):
    """Query response model."""
    result: QueryResult
    knowledge_base_id: UUID
    processing_time_ms: float
    token_usage: Optional[Dict[str, int]] = None
    
    model_config = ConfigDict(
        populate_by_name=True,
    )


class TaskResponse(BaseModel):
    """Task response model."""
    id: UUID
    task_type: str
    status: str
    progress: float
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class DocumentContentResponse(BaseModel):
    """Response for raw document content (can be large)."""
    content: bytes # Or str, depending on how server streams it


class CountResponse(BaseModel):
    """Generic response for count endpoints."""
    count: int


class StringListResponse(BaseModel):
    """Generic response for endpoints returning a list of strings."""
    items: List[str]


# --- Structured Schema Models ---

class StructuredSchemaCreateRequest(BaseModel):
    """Request to create a structured schema."""
    name: str
    description: Optional[str] = None
    schema_definition: Dict[str, Any]


class StructuredSchemaUpdateRequest(BaseModel):
    """Request to update a structured schema."""
    name: Optional[str] = None
    description: Optional[str] = None
    schema_definition: Optional[Dict[str, Any]] = None


class StructuredSchemaResponse(BaseModel):
    """Response for a structured schema."""
    id: UUID
    name: str
    description: Optional[str] = None
    schema_definition: Dict[str, Any]
    created_at: datetime
    updated_at: Optional[datetime] = None


# --- Admin Models ---

class SystemStatisticsResponse(BaseModel):
    """Response model for system statistics."""
    status: str
    timestamp: datetime
    components: Dict[str, Any]
    document_stats: Optional[Dict[str, Any]] = None
    storage_stats: Optional[Dict[str, Any]] = None
    embedding_stats: Optional[Dict[str, Any]] = None
    query_stats: Optional[Dict[str, Any]] = None


class TokenUsageRecord(BaseModel):
    """Record for token usage."""
    period_start: datetime
    model: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    cost: float


class TokenUsageResponse(BaseModel):
    """Response model for token usage."""
    status: str
    period: str
    usage_data: List[TokenUsageRecord]
    summary: Dict[str, Any]


class MaintenanceResponse(BaseModel):
    """Generic response for maintenance tasks."""
    status: str
    message: str
    details: Optional[Dict[str, Any]] = None


class AuditRecordResponse(BaseModel):
    """Response for audit records."""
    id: str
    entity_type: str
    entity_id: str
    status: str
    created_at: datetime
    details: Optional[Dict[str, Any]] = None


class AuditCheckResponse(BaseModel):
    """Response for checking deletion audit."""
    status: str
    message: str
    audit_record: Optional[AuditRecordResponse] = None


class AuditCleanupResponse(BaseModel):
    """Response for cleaning up audited resources."""
    status: str
    message: str
    resources_cleaned: List[str]
    errors: List[str]


class LicenseStatusResponse(BaseModel):
    """License status response model."""
    valid: bool
    customer_name: str = ""
    license_type: str = ""
    days_remaining: int = 0
    expires_at: str = ""
    features: Dict[str, Any] = {}
    error: Optional[str] = None


# --- Team Models ---

class TeamCreate(BaseModel):
    """Team creation model."""
    name: str
    description: Optional[str] = None


class TeamUpdate(BaseModel):
    """Team update model."""
    name: Optional[str] = None
    description: Optional[str] = None


class TeamResponse(BaseModel):
    """Team response model."""
    id: UUID
    name: str
    description: Optional[str] = None
    owner_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None


class TeamDetailResponse(TeamResponse):
    """Detailed team response including members and KBs."""
    users: List[UserResponseMinimal]
    knowledge_bases: List[KnowledgeBaseResponseMinimal]


# --- Health Models ---

class HealthCheckComponent(BaseModel):
    """Component status for detailed health check."""
    status: str
    message: Optional[str] = None


class HealthCheckResponse(BaseModel):
    """Simple health check response."""
    status: str
    api_version: str
    service: str


class DetailedHealthCheckResponse(HealthCheckResponse):
    """Detailed health check response."""
    components: Dict[str, HealthCheckComponent]
    checks: List[Dict[str, str]]
    execution_time_ms: float


# --- Query Strategy Models ---

class QueryStrategyResponse(BaseModel):
    """Response for query strategies."""
    strategies: List[str]


# --- Password Reset Model ---

class PasswordResetRequest(BaseModel):
    email: EmailStr


class GenericStatusResponse(BaseModel):
    """Generic response indicating success/failure message."""
    status: str
    message: str
    details: Optional[Dict[str, Any]] = None


# Knowledge Graph Models
class KnowledgeGraphCreate(BaseModel):
    """Model for creating knowledge graph metadata."""
    knowledge_base_id: UUID
    extraction_strategy: str = "llm"
    confidence_threshold: float = 0.7
    # LLM-specific configuration (only used when extraction_strategy is "llm")
    llm_provider: Optional[str] = Field(default=None, description="LLM provider for knowledge graph extraction (only used when extraction_strategy is 'llm')")
    llm_model: Optional[str] = Field(default=None, description="LLM model for knowledge graph extraction (only used when extraction_strategy is 'llm')")
    kg_schema: Dict[str, Any] = Field(default={}, alias="schema")


class KnowledgeGraphUpdate(BaseModel):
    """Model for updating knowledge graph metadata."""
    extraction_strategy: Optional[str] = None
    confidence_threshold: Optional[float] = None
    # LLM-specific configuration (only used when extraction_strategy is "llm")
    llm_provider: Optional[str] = Field(default=None, description="LLM provider for knowledge graph extraction (only used when extraction_strategy is 'llm')")
    llm_model: Optional[str] = Field(default=None, description="LLM model for knowledge graph extraction (only used when extraction_strategy is 'llm')")
    kg_schema: Optional[Dict[str, Any]] = Field(default=None, alias="schema")


class KnowledgeGraphResponse(BaseModel):
    """Knowledge graph metadata response model."""
    id: UUID
    knowledge_base_id: UUID
    entity_count: int = 0
    relationship_count: int = 0
    entity_types: List[str] = []
    relationship_types: List[str] = []
    extraction_strategy: str = "llm"
    confidence_threshold: float = 0.7
    # LLM-specific configuration (only used when extraction_strategy is "llm")
    llm_provider: Optional[str] = None
    llm_model: Optional[str] = None
    kg_schema: Dict[str, Any] = Field(default={}, alias="schema")
    created_at: datetime
    last_updated: datetime


class KGProcessedDocumentResponse(BaseModel):
    """Response for document processing for knowledge graph."""
    entities_extracted: int
    relationships_extracted: int
    status: str
    message: Optional[str] = None


class KGEntityResponse(BaseModel):
    """Knowledge graph entity response model."""
    id: str
    name: str
    entity_type: str
    properties: Dict[str, Any]


class KGRelationshipNode(BaseModel):
    """Knowledge graph relationship node model."""
    id: str
    type: str
    name: Optional[str] = None


class KGRelationshipInfo(BaseModel):
    """Knowledge graph relationship info model."""
    type: str
    properties: Optional[Dict[str, Any]] = None


class KGRelationshipDetailResponse(BaseModel):
    """Knowledge graph relationship detail response model."""
    source: KGRelationshipNode
    relationship: KGRelationshipInfo
    target: KGRelationshipNode
    is_outgoing_from_queried_entity: bool


class KGPathSegment(BaseModel):
    """Knowledge graph path segment model."""
    type: str  # "node" or "relationship"
    # Node specific
    node_id: Optional[str] = None
    node_type: Optional[str] = None
    # Relationship specific
    relationship_type: Optional[str] = None
    # Common
    properties: Optional[Dict[str, Any]] = None


class PaginatedKGEntityResponse(BaseModel):
    """Paginated knowledge graph entity response model."""
    total: int
    entities: List[KGEntityResponse]


# Webhook Models
class AllowedWebhookMethods(str, Enum):
    """Allowed webhook HTTP methods."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"


class KnowledgeBaseWebhookConfigUpdate(BaseModel):
    """Model for updating knowledge base webhook configuration."""
    webhook_url: Optional[str] = None
    webhook_secret: Optional[str] = None
    is_webhook_enabled: Optional[bool] = None
    webhook_method: Optional[AllowedWebhookMethods] = None


# Model Info
class ModelInfo(BaseModel):
    """Model information response."""
    name: str
    provider: str
    type: str
    description: Optional[str] = None
    max_tokens: Optional[int] = None
    context_length: Optional[int] = None
