# **Implementation Standards: QVF System**
**Quantified Value Framework - Concrete Technical Specifications**

---

## **1. Technology Stack Specifications**

### **1.1 Core Python Environment**
```yaml
python_version: ">=3.9,<3.12"  # EXACT: Python 3.9, 3.10, or 3.11 only
packaging_format: "wheel"       # EXACT: Use wheel distribution
package_manager: "pip"          # EXACT: Standard pip (not conda/poetry)
virtual_env: "required"         # EXACT: Isolated environment mandatory
```

### **1.2 Core Dependencies (requirements.txt)**
```toml
# EXACT versions - DO NOT use ranges
pydantic = "2.5.3"                    # Data validation and serialization
pydantic-settings = "2.1.0"          # Configuration management
fastapi = "0.104.1"                   # REST API framework
uvicorn = "0.24.0"                    # ASGI server
pandas = "2.1.4"                      # Data manipulation
numpy = "1.24.4"                      # Numerical computing
scikit-learn = "1.3.2"               # ML algorithms (AHP implementation)
click = "8.1.7"                       # CLI framework
jinja2 = "3.1.2"                      # Template rendering
python-multipart = "0.0.6"           # File upload support
```

### **1.3 Ollama Integration**
```yaml
ollama_version: "0.1.17"             # EXACT: Latest stable as of Jan 2024
ollama_api_version: "v1"             # EXACT: API version to use
ollama_endpoint: "http://localhost:11434"  # DEFAULT: Standard local endpoint
ollama_models:                       # EXACT: Required models
  - "llama2:7b-chat"                 # Primary reasoning model
  - "codellama:7b-instruct"          # Code generation model
  - "mistral:7b-instruct"            # Fallback model
ollama_timeout_seconds: 30           # EXACT: Request timeout
ollama_max_tokens: 4096              # EXACT: Maximum response length
ollama_temperature: 0.3              # EXACT: Deterministic but creative
```

### **1.4 ChromaDB Configuration**
```yaml
chromadb_version: "0.4.18"           # EXACT: Stable vector database
chromadb_host: "localhost"           # DEFAULT: Local deployment
chromadb_port: 8000                  # EXACT: Default ChromaDB port
chromadb_collection_name: "qvf_embeddings"  # EXACT: Primary collection
chromadb_distance_metric: "cosine"   # EXACT: Similarity calculation method
chromadb_embedding_dimension: 384    # EXACT: sentence-transformers/all-MiniLM-L6-v2
chromadb_max_batch_size: 100         # EXACT: Batch processing limit
chromadb_persistence_path: "./data/chroma_db"  # EXACT: Data storage location
```

### **1.5 SQLite Configuration**
```yaml
sqlite_version: ">=3.35.0"           # MINIMUM: For JSON support
sqlite_database_path: "./data/qvf.sqlite"  # EXACT: Primary database location
sqlite_wal_mode: true                # EXACT: Write-Ahead Logging enabled
sqlite_busy_timeout: 5000            # EXACT: 5 second timeout in milliseconds
sqlite_page_size: 4096               # EXACT: Page size in bytes
sqlite_cache_size: 10000             # EXACT: Pages to cache in memory
sqlite_journal_mode: "WAL"           # EXACT: Write-Ahead Logging
sqlite_synchronous: "NORMAL"         # EXACT: Balance performance/safety
```

### **1.6 React/TypeScript Frontend**
```json
{
  "react": "18.2.0",
  "typescript": "5.2.2",
  "@types/react": "18.2.43",
  "@types/react-dom": "18.2.17",
  "next": "14.0.4",
  "tailwindcss": "3.3.6",
  "@headlessui/react": "1.7.17",
  "@heroicons/react": "2.0.18",
  "recharts": "2.8.0",
  "@tremor/react": "3.13.0",
  "lucide-react": "0.294.0",
  "react-hot-toast": "2.4.1",
  "axios": "1.6.2",
  "swr": "2.2.4",
  "framer-motion": "10.16.16"
}
```

### **1.7 Azure DevOps API**
```yaml
ado_api_version: "7.1"               # EXACT: REST API version
ado_base_url_pattern: "https://dev.azure.com/{organization}"
ado_authentication: "PAT"            # EXACT: Personal Access Token only
ado_pat_scopes:                      # EXACT: Required permissions
  - "vso.work_full"                  # Full work item access
  - "vso.project"                    # Project access
  - "vso.analytics"                  # Analytics service access
ado_max_batch_size: 200              # EXACT: API batch limit
ado_rate_limit_delay: 100            # EXACT: Milliseconds between requests
ado_timeout_seconds: 30              # EXACT: Request timeout
```

---

## **2. Data Models and Schemas**

### **2.1 Core QVF TypeScript Interfaces**
```typescript
// File: src/types/qvf-core.ts
interface QVFCriterion {
  readonly id: string;                // UUID v4 format
  readonly name: string;              // 1-50 characters, alphanumeric + spaces
  readonly description: string;       // 1-200 characters
  readonly weight: number;            // 0.0001 to 0.9999, sum of all = 1.0
  readonly category: 'business' | 'technical' | 'strategic' | 'operational';
  readonly isActive: boolean;
  readonly createdAt: string;         // ISO 8601 format: YYYY-MM-DDTHH:mm:ss.sssZ
  readonly updatedAt: string;         // ISO 8601 format: YYYY-MM-DDTHH:mm:ss.sssZ
}

interface QVFWorkItem {
  readonly id: string;                // ADO work item ID as string
  readonly title: string;             // ADO title field, 1-255 characters
  readonly type: 'Epic' | 'Feature' | 'PIO' | 'User Story';
  readonly state: 'New' | 'Active' | 'Closed' | 'Resolved';
  readonly assignedTo?: string;       // ADO user email or null
  readonly teamProject: string;       // ADO team project name
  readonly areaPath: string;          // ADO area path
  readonly iterationPath: string;     // ADO iteration path
  readonly businessValue?: number;    // ADO business value field (0-999999)
  readonly storyPoints?: number;      // ADO story points field (0-999)
  readonly priority: number;          // ADO priority field (1-4)
  readonly qvfScores: QVFScore[];     // Calculated QVF scores per criterion
  readonly qvfTotalScore: number;     // Final calculated QVF score (0.0-100.0)
  readonly semanticAlignment: number; // Semantic alignment score (0.0-1.0)
  readonly lastAnalyzed: string;      // ISO 8601 timestamp
}

interface QVFScore {
  readonly criterionId: string;       // References QVFCriterion.id
  readonly rawScore: number;          // User input or calculated score (0-100)
  readonly normalizedScore: number;   // Weight-adjusted score (0.0-1.0)
  readonly confidence: number;        // Confidence level (0.0-1.0)
  readonly evidence?: string;         // Supporting rationale, max 500 chars
  readonly calculatedAt: string;      // ISO 8601 timestamp
}

interface QVFComparison {
  readonly id: string;                // UUID v4
  readonly stakeholderId: string;     // User identifier
  readonly criterionA: string;        // QVFCriterion.id
  readonly criterionB: string;        // QVFCriterion.id
  readonly preference: number;        // AHP scale: 1, 3, 5, 7, 9 (A over B)
  readonly consistency: number;       // Consistency ratio (0.0-0.10)
  readonly createdAt: string;         // ISO 8601 timestamp
}
```

### **2.2 SQLite Database Schema**
```sql
-- File: migrations/001_initial_schema.sql

-- QVF Criteria Definition
CREATE TABLE qvf_criteria (
    id TEXT PRIMARY KEY,              -- UUID v4 format
    name TEXT NOT NULL CHECK(LENGTH(name) BETWEEN 1 AND 50),
    description TEXT NOT NULL CHECK(LENGTH(description) BETWEEN 1 AND 200),
    weight REAL NOT NULL CHECK(weight > 0.0001 AND weight < 0.9999),
    category TEXT NOT NULL CHECK(category IN ('business', 'technical', 'strategic', 'operational')),
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Ensure weights sum to 1.0 across active criteria
CREATE TRIGGER validate_criteria_weights 
    BEFORE UPDATE OF weight ON qvf_criteria
BEGIN
    SELECT CASE 
        WHEN (SELECT SUM(weight) FROM qvf_criteria WHERE is_active = 1 AND id != NEW.id) + NEW.weight > 1.0001 
        THEN RAISE(ABORT, 'Total weights cannot exceed 1.0')
    END;
END;

-- ADO Work Items Cache
CREATE TABLE ado_work_items (
    id TEXT PRIMARY KEY,              -- ADO work item ID
    title TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('Epic', 'Feature', 'PIO', 'User Story')),
    state TEXT NOT NULL,
    assigned_to TEXT,
    team_project TEXT NOT NULL,
    area_path TEXT NOT NULL,
    iteration_path TEXT NOT NULL,
    business_value INTEGER CHECK(business_value >= 0 AND business_value <= 999999),
    story_points INTEGER CHECK(story_points >= 0 AND story_points <= 999),
    priority INTEGER CHECK(priority >= 1 AND priority <= 4),
    qvf_total_score REAL CHECK(qvf_total_score >= 0.0 AND qvf_total_score <= 100.0),
    semantic_alignment REAL CHECK(semantic_alignment >= 0.0 AND semantic_alignment <= 1.0),
    last_analyzed TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- QVF Scores for each work item-criterion pair
CREATE TABLE qvf_scores (
    id TEXT PRIMARY KEY,              -- UUID v4
    work_item_id TEXT NOT NULL REFERENCES ado_work_items(id),
    criterion_id TEXT NOT NULL REFERENCES qvf_criteria(id),
    raw_score REAL NOT NULL CHECK(raw_score >= 0 AND raw_score <= 100),
    normalized_score REAL NOT NULL CHECK(normalized_score >= 0.0 AND normalized_score <= 1.0),
    confidence REAL NOT NULL CHECK(confidence >= 0.0 AND confidence <= 1.0),
    evidence TEXT CHECK(LENGTH(evidence) <= 500),
    calculated_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(work_item_id, criterion_id)
);

-- AHP Pairwise Comparisons
CREATE TABLE ahp_comparisons (
    id TEXT PRIMARY KEY,              -- UUID v4
    stakeholder_id TEXT NOT NULL,
    criterion_a TEXT NOT NULL REFERENCES qvf_criteria(id),
    criterion_b TEXT NOT NULL REFERENCES qvf_criteria(id),
    preference REAL NOT NULL CHECK(preference IN (1, 3, 5, 7, 9)),
    consistency REAL CHECK(consistency >= 0.0 AND consistency <= 0.10),
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(stakeholder_id, criterion_a, criterion_b)
);

-- Indexes for performance
CREATE INDEX idx_qvf_scores_work_item ON qvf_scores(work_item_id);
CREATE INDEX idx_qvf_scores_criterion ON qvf_scores(criterion_id);
CREATE INDEX idx_ado_items_type_state ON ado_work_items(type, state);
CREATE INDEX idx_ado_items_project ON ado_work_items(team_project);
CREATE INDEX idx_ahp_stakeholder ON ahp_comparisons(stakeholder_id);
```

### **2.3 Python Pydantic Models**
```python
# File: src/datascience_platform/qvf/models.py
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict
from pydantic import BaseModel, Field, validator
import uuid

class CriterionCategory(str, Enum):
    BUSINESS = "business"
    TECHNICAL = "technical"
    STRATEGIC = "strategic"
    OPERATIONAL = "operational"

class WorkItemType(str, Enum):
    EPIC = "Epic"
    FEATURE = "Feature"
    PIO = "PIO"
    USER_STORY = "User Story"

class WorkItemState(str, Enum):
    NEW = "New"
    ACTIVE = "Active"
    CLOSED = "Closed"
    RESOLVED = "Resolved"

class QVFCriterion(BaseModel):
    """QVF evaluation criterion with validation."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., min_length=1, max_length=50)
    description: str = Field(..., min_length=1, max_length=200)
    weight: float = Field(..., ge=0.0001, le=0.9999)
    category: CriterionCategory
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @validator('name')
    def validate_name(cls, v):
        """Ensure name contains only alphanumeric characters and spaces."""
        if not v.replace(' ', '').isalnum():
            raise ValueError('Name must contain only alphanumeric characters and spaces')
        return v

class QVFScore(BaseModel):
    """Individual criterion score for a work item."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    work_item_id: str
    criterion_id: str
    raw_score: float = Field(..., ge=0, le=100)
    normalized_score: float = Field(..., ge=0.0, le=1.0)
    confidence: float = Field(..., ge=0.0, le=1.0)
    evidence: Optional[str] = Field(None, max_length=500)
    calculated_at: datetime = Field(default_factory=datetime.utcnow)

class QVFWorkItem(BaseModel):
    """Complete work item with QVF analysis."""
    id: str
    title: str = Field(..., min_length=1, max_length=255)
    type: WorkItemType
    state: WorkItemState
    assigned_to: Optional[str] = None
    team_project: str
    area_path: str
    iteration_path: str
    business_value: Optional[int] = Field(None, ge=0, le=999999)
    story_points: Optional[int] = Field(None, ge=0, le=999)
    priority: int = Field(..., ge=1, le=4)
    qvf_scores: List[QVFScore] = []
    qvf_total_score: float = Field(..., ge=0.0, le=100.0)
    semantic_alignment: float = Field(..., ge=0.0, le=1.0)
    last_analyzed: datetime = Field(default_factory=datetime.utcnow)

class AHPComparison(BaseModel):
    """AHP pairwise comparison between criteria."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    stakeholder_id: str
    criterion_a: str
    criterion_b: str
    preference: float = Field(..., regex=r'^(1|3|5|7|9)$')  # AHP scale values only
    consistency: Optional[float] = Field(None, ge=0.0, le=0.10)
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

---

## **3. API Contracts**

### **3.1 REST Endpoint Specifications**

```yaml
# File: api_contracts.yaml
base_url: "http://localhost:8000/api/v1"
content_type: "application/json"
authentication: "Bearer {token}"  # Optional for local development

endpoints:
  # Criteria Management
  GET /criteria:
    description: "Retrieve all QVF criteria"
    parameters: 
      active_only: boolean  # Query param, default: true
    response: 
      type: "array"
      items: "QVFCriterion"
      status: 200
    
  POST /criteria:
    description: "Create new QVF criterion"
    body: "QVFCriterion" 
    response:
      type: "QVFCriterion"
      status: 201
    errors:
      400: "Validation error"
      409: "Weight constraint violation"

  PUT /criteria/{id}:
    description: "Update existing criterion"
    parameters:
      id: string  # Path param, UUID v4
    body: "QVFCriterion"
    response:
      type: "QVFCriterion" 
      status: 200
    errors:
      404: "Criterion not found"
      409: "Weight constraint violation"

  # Work Item Analysis
  GET /workitems:
    description: "Retrieve work items with QVF scores"
    parameters:
      project: string      # Query param, ADO project name
      type: WorkItemType   # Query param, optional filter
      limit: integer       # Query param, default: 100, max: 1000
      offset: integer      # Query param, default: 0
    response:
      type: "object"
      properties:
        items: array<QVFWorkItem>
        total: integer
        limit: integer
        offset: integer
      status: 200

  POST /workitems/analyze:
    description: "Analyze work items and calculate QVF scores"
    body:
      type: "object"
      properties:
        work_item_ids: array<string>  # Max 50 items per batch
        force_refresh: boolean        # Default: false
    response:
      type: "object" 
      properties:
        analyzed_count: integer
        failed_count: integer
        results: array<QVFWorkItem>
      status: 202  # Accepted for processing
    errors:
      400: "Invalid work item IDs or batch too large"
      429: "Rate limit exceeded"

  # AHP Comparisons  
  POST /comparisons:
    description: "Submit pairwise criterion comparison"
    body: "AHPComparison"
    response:
      type: "object"
      properties:
        comparison: "AHPComparison"
        consistency_ratio: number
        weights_updated: boolean
      status: 201
    errors:
      400: "Invalid comparison values"
      409: "Consistency ratio too high (>0.10)"

  GET /comparisons/{stakeholder_id}:
    description: "Get comparisons for stakeholder"
    parameters:
      stakeholder_id: string
    response:
      type: "array"
      items: "AHPComparison"
      status: 200

  # AI Enhancement (Optional - Ollama)
  POST /ai/enhance:
    description: "AI-enhanced scoring (requires Ollama)"
    body:
      type: "object"
      properties:
        work_item_id: string
        context: string           # Business context, max 1000 chars
        criteria_focus: array<string>  # Criterion IDs to focus on
    response:
      type: "object"
      properties:
        enhanced_scores: array<QVFScore>
        reasoning: string         # AI explanation
        confidence: number        # Overall confidence (0.0-1.0)
      status: 200
    errors:
      503: "AI service unavailable"
      422: "Context too long or invalid"
```

### **3.2 WebSocket Message Formats**

```yaml
# File: websocket_contracts.yaml
connection_url: "ws://localhost:8000/ws"
protocols: ["qvf-v1"]

message_types:
  # Real-time scoring updates
  scoring_update:
    type: "scoring_update"
    payload:
      work_item_id: string
      scores: array<QVFScore>
      total_score: number
      timestamp: string  # ISO 8601

  # Consistency monitoring
  consistency_alert:
    type: "consistency_alert"
    payload:
      stakeholder_id: string
      consistency_ratio: number
      threshold_exceeded: boolean
      affected_comparisons: array<string>  # Comparison IDs
      
  # Batch processing status
  batch_progress:
    type: "batch_progress"
    payload:
      batch_id: string
      processed: integer
      total: integer
      failed: integer
      estimated_completion: string  # ISO 8601

client_messages:
  # Subscribe to updates
  subscribe:
    type: "subscribe"
    payload:
      channels: array<string>  # ["scoring", "consistency", "batch"]
      work_item_ids: array<string>  # Optional filter
```

### **3.3 Azure DevOps API Integration**

```yaml
# File: ado_integration.yaml
ado_endpoints:
  work_items: "https://dev.azure.com/{organization}/_apis/wit/workitems"
  wiql: "https://dev.azure.com/{organization}/_apis/wit/wiql"
  fields: "https://dev.azure.com/{organization}/_apis/wit/fields"

custom_fields:
  qvf_total_score:
    name: "Custom.QVFTotalScore"
    type: "System.Double"
    description: "QVF calculated priority score"
    
  qvf_semantic_alignment:
    name: "Custom.QVFSemanticAlignment"
    type: "System.Double"
    description: "Semantic alignment with strategic objectives"
    
  qvf_last_analyzed:
    name: "Custom.QVFLastAnalyzed"
    type: "System.DateTime"
    description: "Timestamp of last QVF analysis"

wiql_queries:
  active_epics: |
    SELECT [System.Id], [System.Title], [System.WorkItemType], 
           [System.State], [Microsoft.VSTS.Common.BusinessValue]
    FROM WorkItems 
    WHERE [System.WorkItemType] = 'Epic' 
      AND [System.State] IN ('New', 'Active')
      AND [System.TeamProject] = '@project'
    ORDER BY [System.Id]

batch_operations:
  max_batch_size: 200
  rate_limit_ms: 100
  timeout_seconds: 30
  retry_attempts: 3
  retry_backoff_ms: 1000
```

---

## **4. Error Handling Patterns**

### **4.1 Standard Error Codes and Messages**

```python
# File: src/datascience_platform/qvf/exceptions.py
from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel

class QVFErrorCode(str, Enum):
    """Standardized QVF error codes."""
    
    # Validation Errors (4000-4099)
    VALIDATION_FAILED = "QVF4001"
    INVALID_CRITERION_WEIGHT = "QVF4002"
    WEIGHT_CONSTRAINT_VIOLATION = "QVF4003"
    INVALID_WORK_ITEM_ID = "QVF4004"
    CONSISTENCY_RATIO_EXCEEDED = "QVF4005"
    BATCH_SIZE_EXCEEDED = "QVF4006"
    
    # External Service Errors (5000-5099)
    ADO_CONNECTION_FAILED = "QVF5001"
    ADO_AUTHENTICATION_FAILED = "QVF5002"
    ADO_RATE_LIMIT_EXCEEDED = "QVF5003"
    OLLAMA_UNAVAILABLE = "QVF5004"
    CHROMADB_CONNECTION_FAILED = "QVF5005"
    
    # Processing Errors (6000-6099)
    SEMANTIC_ANALYSIS_FAILED = "QVF6001"
    AHP_CALCULATION_ERROR = "QVF6002"
    SCORE_NORMALIZATION_ERROR = "QVF6003"
    BATCH_PROCESSING_FAILED = "QVF6004"
    
    # Configuration Errors (7000-7099)
    MISSING_CONFIGURATION = "QVF7001"
    INVALID_DATABASE_SCHEMA = "QVF7002"
    INSUFFICIENT_PERMISSIONS = "QVF7003"

class QVFError(Exception):
    """Base QVF exception with structured error information."""
    
    def __init__(
        self,
        code: QVFErrorCode,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        user_message: Optional[str] = None,
        retry_after_seconds: Optional[int] = None
    ):
        self.code = code
        self.message = message
        self.details = details or {}
        self.user_message = user_message or self._get_default_user_message(code)
        self.retry_after_seconds = retry_after_seconds
        super().__init__(f"{code}: {message}")
    
    def _get_default_user_message(self, code: QVFErrorCode) -> str:
        """User-friendly error messages."""
        messages = {
            QVFErrorCode.VALIDATION_FAILED: "Please check your input and try again.",
            QVFErrorCode.INVALID_CRITERION_WEIGHT: "Criterion weights must be between 0.01% and 99.99%.",
            QVFErrorCode.WEIGHT_CONSTRAINT_VIOLATION: "Total criterion weights cannot exceed 100%.",
            QVFErrorCode.CONSISTENCY_RATIO_EXCEEDED: "Your comparisons are inconsistent. Please review and adjust.",
            QVFErrorCode.ADO_CONNECTION_FAILED: "Unable to connect to Azure DevOps. Please check your connection.",
            QVFErrorCode.OLLAMA_UNAVAILABLE: "AI enhancement is temporarily unavailable. Basic analysis will proceed.",
            QVFErrorCode.BATCH_PROCESSING_FAILED: "Some work items could not be processed. Please try again later."
        }
        return messages.get(code, "An unexpected error occurred. Please contact support.")

class ErrorResponse(BaseModel):
    """Standardized API error response format."""
    error: bool = True
    code: str
    message: str
    user_message: str
    details: Dict[str, Any] = {}
    timestamp: str
    retry_after_seconds: Optional[int] = None
    support_id: str  # UUID for support tracking
```

### **4.2 Retry Strategies**

```python
# File: src/datascience_platform/qvf/retry.py
import time
import asyncio
from typing import Callable, Any, Optional, List
from functools import wraps
import logging

class RetryConfig:
    """Retry configuration for different operations."""
    
    # ADO API calls
    ADO_API = {
        'max_attempts': 3,
        'base_delay_ms': 1000,
        'max_delay_ms': 10000,
        'backoff_multiplier': 2.0,
        'retryable_errors': ['ConnectionError', 'Timeout', 'HTTPError'],
        'retryable_status_codes': [429, 500, 502, 503, 504]
    }
    
    # Ollama LLM calls
    OLLAMA_API = {
        'max_attempts': 2,  # Fewer attempts for optional service
        'base_delay_ms': 2000,
        'max_delay_ms': 8000,
        'backoff_multiplier': 2.0,
        'retryable_errors': ['ConnectionError', 'Timeout'],
        'retryable_status_codes': [429, 500, 502, 503]
    }
    
    # ChromaDB operations
    CHROMADB = {
        'max_attempts': 3,
        'base_delay_ms': 500,
        'max_delay_ms': 5000,
        'backoff_multiplier': 2.0,
        'retryable_errors': ['ConnectionError', 'Timeout'],
        'retryable_status_codes': [429, 500, 502, 503]
    }
    
    # Database operations
    DATABASE = {
        'max_attempts': 3,
        'base_delay_ms': 100,
        'max_delay_ms': 1000,
        'backoff_multiplier': 2.0,
        'retryable_errors': ['OperationalError', 'TimeoutError'],
        'retryable_status_codes': []
    }

def with_retry(config_name: str):
    """Decorator for automatic retry with exponential backoff."""
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            config = getattr(RetryConfig, config_name)
            last_exception = None
            
            for attempt in range(config['max_attempts']):
                try:
                    return await func(*args, **kwargs)
                    
                except Exception as e:
                    last_exception = e
                    
                    # Check if error is retryable
                    if not _is_retryable_error(e, config):
                        raise e
                    
                    # Calculate delay for next attempt
                    if attempt < config['max_attempts'] - 1:
                        delay = min(
                            config['base_delay_ms'] * (config['backoff_multiplier'] ** attempt),
                            config['max_delay_ms']
                        ) / 1000  # Convert to seconds
                        
                        logging.warning(f"Attempt {attempt + 1} failed, retrying in {delay}s: {e}")
                        await asyncio.sleep(delay)
                        
            # All attempts failed
            raise last_exception
            
        return wrapper
    return decorator

def _is_retryable_error(error: Exception, config: dict) -> bool:
    """Check if an error should trigger a retry."""
    error_name = error.__class__.__name__
    
    # Check error type
    if error_name in config['retryable_errors']:
        return True
        
    # Check HTTP status code if available
    if hasattr(error, 'status_code'):
        if error.status_code in config['retryable_status_codes']:
            return True
            
    return False
```

### **4.3 Fallback Chains**

```python
# File: src/datascience_platform/qvf/fallbacks.py
from typing import Optional, Dict, Any, List
from enum import Enum
import logging

class FallbackStrategy(str, Enum):
    """Available fallback strategies."""
    AI_TO_COACHING = "ai_to_coaching"           # Ollama -> Coaching questions
    COACHING_TO_MATHEMATICAL = "coaching_to_math"  # Coaching -> Pure AHP
    FULL_CHAIN = "full_chain"                   # AI -> Coaching -> Math
    MATHEMATICAL_ONLY = "mathematical_only"     # Skip AI/Coaching entirely

class QVFScoreCalculator:
    """Primary scoring system with intelligent fallbacks."""
    
    def __init__(self, ollama_client=None, coaching_engine=None, ahp_engine=None):
        self.ollama_client = ollama_client
        self.coaching_engine = coaching_engine  
        self.ahp_engine = ahp_engine  # Always available
        
    async def calculate_scores(
        self, 
        work_item: dict, 
        criteria: List[dict],
        context: Optional[str] = None,
        strategy: FallbackStrategy = FallbackStrategy.FULL_CHAIN
    ) -> Dict[str, Any]:
        """Calculate QVF scores with fallback chain."""
        
        result = {
            'scores': [],
            'method_used': None,
            'fallback_reasons': [],
            'confidence': 0.0
        }
        
        if strategy == FallbackStrategy.MATHEMATICAL_ONLY:
            return await self._mathematical_scoring(work_item, criteria, result)
            
        # Try AI enhancement first (if available and strategy allows)
        if (self.ollama_client and 
            strategy in [FallbackStrategy.AI_TO_COACHING, FallbackStrategy.FULL_CHAIN]):
            
            try:
                ai_result = await self._ai_enhanced_scoring(work_item, criteria, context)
                result.update(ai_result)
                result['method_used'] = 'ai_enhanced'
                result['confidence'] = 0.9  # High confidence for AI
                return result
                
            except Exception as e:
                logging.warning(f"AI scoring failed: {e}")
                result['fallback_reasons'].append(f"AI unavailable: {str(e)}")
        
        # Fallback to coaching questions
        if (self.coaching_engine and 
            strategy in [FallbackStrategy.AI_TO_COACHING, FallbackStrategy.COACHING_TO_MATHEMATICAL, FallbackStrategy.FULL_CHAIN]):
            
            try:
                coaching_result = await self._coaching_guided_scoring(work_item, criteria)
                result.update(coaching_result)
                result['method_used'] = 'coaching_guided'
                result['confidence'] = 0.7  # Medium-high confidence
                return result
                
            except Exception as e:
                logging.warning(f"Coaching scoring failed: {e}")
                result['fallback_reasons'].append(f"Coaching failed: {str(e)}")
        
        # Final fallback to pure mathematical/AHP approach
        return await self._mathematical_scoring(work_item, criteria, result)
    
    async def _ai_enhanced_scoring(self, work_item: dict, criteria: List[dict], context: str) -> Dict[str, Any]:
        """AI-enhanced scoring using Ollama."""
        prompt = self._build_ai_scoring_prompt(work_item, criteria, context)
        
        # Use exact Ollama configuration
        response = await self.ollama_client.generate(
            model="llama2:7b-chat",
            prompt=prompt,
            options={
                'temperature': 0.3,    # EXACT: From tech specs
                'max_tokens': 4096,    # EXACT: From tech specs
                'timeout': 30          # EXACT: From tech specs
            }
        )
        
        # Parse AI response into structured scores
        return self._parse_ai_response(response)
    
    async def _coaching_guided_scoring(self, work_item: dict, criteria: List[dict]) -> Dict[str, Any]:
        """Interactive coaching questions for score elicitation."""
        scores = []
        
        coaching_questions = {
            'business': [
                "What is the estimated revenue impact of this feature?",
                "How many users/customers will this directly affect?", 
                "What is the strategic importance to company objectives?"
            ],
            'technical': [
                "What is the technical complexity (1-10 scale)?",
                "How much technical debt will this create or resolve?",
                "What are the integration dependencies?"
            ],
            'operational': [
                "How will this impact operational efficiency?",
                "What are the maintenance and support implications?",
                "How does this affect team velocity and capacity?"
            ]
        }
        
        # Generate guided questions and collect responses
        # Implementation would integrate with coaching_engine
        
        return {
            'scores': scores,
            'method_used': 'coaching_guided',
            'confidence': 0.7
        }
    
    async def _mathematical_scoring(self, work_item: dict, criteria: List[dict], result: dict) -> Dict[str, Any]:
        """Pure mathematical scoring using AHP and existing fields."""
        scores = []
        
        # Use existing ADO fields as basis for scoring
        business_value = work_item.get('business_value', 0)
        story_points = work_item.get('story_points', 0)  
        priority = work_item.get('priority', 1)
        
        # Apply criterion weights to normalize scores
        for criterion in criteria:
            if criterion['category'] == 'business':
                raw_score = min(business_value / 1000 * 100, 100)  # Normalize to 0-100
            elif criterion['category'] == 'technical':
                raw_score = max(100 - (story_points * 10), 0)  # Lower complexity = higher score
            else:
                raw_score = max(100 - (priority * 20), 20)  # Lower priority number = higher score
                
            normalized_score = raw_score * criterion['weight']
            
            scores.append({
                'criterion_id': criterion['id'],
                'raw_score': raw_score,
                'normalized_score': normalized_score,
                'confidence': 0.5,  # Lower confidence for mathematical approach
                'evidence': 'Calculated from existing ADO fields'
            })
        
        result.update({
            'scores': scores,
            'method_used': 'mathematical',
            'confidence': 0.5,  # Conservative confidence
            'fallback_reasons': result.get('fallback_reasons', [])
        })
        
        return result
```

---

## **5. Performance Requirements**

### **5.1 Response Time Targets**

```yaml
# File: performance_requirements.yaml
api_response_times:
  # Core CRUD operations (milliseconds)
  GET_criteria: 50                    # EXACT: Must respond within 50ms
  POST_criteria: 200                  # EXACT: Create criterion within 200ms
  PUT_criteria: 200                   # EXACT: Update criterion within 200ms
  
  # Work item operations  
  GET_workitems_list: 500            # EXACT: List 100 items within 500ms
  GET_workitems_detail: 100          # EXACT: Single item within 100ms
  POST_workitems_analyze: 2000       # EXACT: Single item analysis within 2s
  POST_workitems_batch: 30000        # EXACT: 50-item batch within 30s
  
  # AHP operations
  POST_comparison: 100               # EXACT: Record comparison within 100ms
  GET_consistency_check: 200         # EXACT: Calculate CR within 200ms
  
  # AI enhancement (optional, higher tolerance)
  POST_ai_enhance: 15000            # EXACT: AI scoring within 15s
  ollama_model_load: 60000          # EXACT: Model loading within 60s

database_operations:
  # SQLite query performance (milliseconds)
  simple_select: 10                 # EXACT: Basic SELECT queries
  complex_join: 100                 # EXACT: Multi-table JOINs
  insert_single: 5                  # EXACT: Single record INSERT
  insert_batch_100: 200             # EXACT: 100-record batch INSERT
  update_single: 10                 # EXACT: Single record UPDATE
  
memory_requirements:
  # Memory usage limits (MB)
  base_application: 256             # EXACT: Base app memory footprint
  per_work_item_analysis: 2         # EXACT: Memory per work item
  ollama_model_7b: 8000            # EXACT: 7B model memory usage
  chromadb_embeddings_1m: 1500     # EXACT: 1M embeddings storage
  sqlite_connection_pool: 50        # EXACT: Connection pool memory
  
throughput_requirements:
  # Operations per second
  work_item_analysis: 10            # EXACT: Items analyzed per second
  ahp_comparisons: 100             # EXACT: Comparisons processed per second
  api_requests: 1000               # EXACT: Total API requests per second
  concurrent_users: 50             # EXACT: Simultaneous active users
  
cache_specifications:
  # TTL values in seconds
  criterion_list: 3600             # EXACT: Cache criteria for 1 hour
  work_item_scores: 1800           # EXACT: Cache scores for 30 minutes  
  ahp_weights: 7200                # EXACT: Cache weights for 2 hours
  semantic_embeddings: 86400       # EXACT: Cache embeddings for 24 hours
  
  # Cache size limits
  max_work_items_cached: 10000     # EXACT: Maximum cached work items
  max_embeddings_cached: 100000    # EXACT: Maximum cached embeddings
  memory_cache_size_mb: 512        # EXACT: In-memory cache size
```

### **5.2 Batch Processing Specifications**

```python
# File: src/datascience_platform/qvf/batch_config.py
class BatchConfig:
    """Exact batch processing parameters."""
    
    # Work Item Analysis Batches
    WORK_ITEM_BATCH_SIZE = 50           # EXACT: Items per batch
    WORK_ITEM_MAX_PARALLEL = 5          # EXACT: Concurrent batches
    WORK_ITEM_RETRY_DELAY_MS = 2000     # EXACT: Delay between retries
    
    # ADO API Batches  
    ADO_BATCH_SIZE = 200                # EXACT: ADO API batch limit
    ADO_RATE_LIMIT_DELAY_MS = 100       # EXACT: Delay between calls
    ADO_MAX_CONCURRENT = 3              # EXACT: Concurrent ADO requests
    
    # Embedding Generation Batches
    EMBEDDING_BATCH_SIZE = 32           # EXACT: Optimal for sentence-transformers
    EMBEDDING_MAX_SEQUENCE_LENGTH = 512  # EXACT: Model input limit
    
    # Database Batch Operations
    DB_INSERT_BATCH_SIZE = 100          # EXACT: SQLite batch inserts
    DB_UPDATE_BATCH_SIZE = 50           # EXACT: SQLite batch updates
    
    # Memory Management
    MAX_ITEMS_IN_MEMORY = 1000          # EXACT: Items before disk write
    MEMORY_CHECK_INTERVAL_ITEMS = 100   # EXACT: Check memory every N items
```

---

## **6. Testing Standards**

### **6.1 Unit Test Patterns**

```python
# File: tests/unit/test_qvf_core.py
import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
import uuid

from datascience_platform.qvf.models import QVFCriterion, QVFScore, AHPComparison
from datascience_platform.qvf.exceptions import QVFError, QVFErrorCode

class TestQVFCriterion:
    """Test QVF criterion validation and business logic."""
    
    def test_criterion_creation_valid(self):
        """Test valid criterion creation."""
        # EXACT: Test all required fields
        criterion = QVFCriterion(
            name="Business Value",
            description="Direct business impact measurement", 
            weight=0.25,
            category="business"
        )
        
        # EXACT: Verify all fields
        assert len(criterion.id) == 36  # UUID v4 length
        assert criterion.name == "Business Value"
        assert criterion.weight == 0.25
        assert criterion.is_active is True
        assert isinstance(criterion.created_at, datetime)
    
    def test_criterion_weight_validation(self):
        """Test weight constraint validation."""
        # Test minimum weight boundary  
        with pytest.raises(ValueError, match="weight"):
            QVFCriterion(
                name="Test",
                description="Test description",
                weight=0.0001,  # EXACT: Below minimum
                category="business"
            )
        
        # Test maximum weight boundary
        with pytest.raises(ValueError, match="weight"):
            QVFCriterion(
                name="Test", 
                description="Test description",
                weight=0.9999,  # EXACT: Above maximum
                category="business"
            )
    
    def test_criterion_name_validation(self):
        """Test name format validation."""
        # Valid alphanumeric with spaces
        criterion = QVFCriterion(
            name="Business Value 2024",
            description="Test description",
            weight=0.25,
            category="business"
        )
        assert criterion.name == "Business Value 2024"
        
        # Invalid special characters
        with pytest.raises(ValueError, match="alphanumeric"):
            QVFCriterion(
                name="Business-Value!",  # EXACT: Special chars not allowed
                description="Test description", 
                weight=0.25,
                category="business"
            )

@pytest.mark.asyncio
class TestQVFScoreCalculation:
    """Test QVF scoring calculations."""
    
    @pytest.fixture
    def sample_work_item(self):
        """Sample work item for testing."""
        return {
            'id': '12345',
            'title': 'Implement user authentication',
            'type': 'Feature',
            'business_value': 500,
            'story_points': 8,
            'priority': 2
        }
    
    @pytest.fixture
    def sample_criteria(self):
        """Sample criteria for testing."""
        return [
            {
                'id': str(uuid.uuid4()),
                'name': 'Business Value',
                'weight': 0.4,
                'category': 'business'
            },
            {
                'id': str(uuid.uuid4()),
                'name': 'Technical Complexity',  
                'weight': 0.3,
                'category': 'technical'
            },
            {
                'id': str(uuid.uuid4()),
                'name': 'Strategic Alignment',
                'weight': 0.3, 
                'category': 'strategic'
            }
        ]
    
    async def test_mathematical_scoring_calculation(self, sample_work_item, sample_criteria):
        """Test pure mathematical scoring logic."""
        from datascience_platform.qvf.fallbacks import QVFScoreCalculator
        
        calculator = QVFScoreCalculator(
            ollama_client=None,  # Force mathematical fallback
            coaching_engine=None,
            ahp_engine=Mock()
        )
        
        result = await calculator.calculate_scores(
            sample_work_item,
            sample_criteria,
            strategy="mathematical_only"
        )
        
        # EXACT: Verify calculation results
        assert result['method_used'] == 'mathematical'
        assert len(result['scores']) == 3
        assert all(0 <= score['raw_score'] <= 100 for score in result['scores'])
        assert all(0 <= score['normalized_score'] <= 1.0 for score in result['scores'])
        assert result['confidence'] == 0.5  # EXACT: Mathematical confidence level
    
    async def test_ai_fallback_chain(self, sample_work_item, sample_criteria):
        """Test AI to mathematical fallback."""
        # Mock failing Ollama client
        mock_ollama = Mock()
        mock_ollama.generate = AsyncMock(side_effect=ConnectionError("Ollama unavailable"))
        
        calculator = QVFScoreCalculator(
            ollama_client=mock_ollama,
            coaching_engine=None,
            ahp_engine=Mock()
        )
        
        result = await calculator.calculate_scores(
            sample_work_item,
            sample_criteria,
            strategy="full_chain"
        )
        
        # EXACT: Verify fallback occurred
        assert result['method_used'] == 'mathematical'
        assert len(result['fallback_reasons']) == 1
        assert 'Ollama unavailable' in result['fallback_reasons'][0]

class TestAHPCalculations:
    """Test Analytic Hierarchy Process calculations."""
    
    def test_consistency_ratio_calculation(self):
        """Test consistency ratio validation."""
        from datascience_platform.qvf.ahp import AHPEngine
        
        # EXACT: Test with known consistent matrix
        comparisons = [
            {'criterion_a': 'A', 'criterion_b': 'B', 'preference': 3},
            {'criterion_a': 'A', 'criterion_b': 'C', 'preference': 5}, 
            {'criterion_a': 'B', 'criterion_b': 'C', 'preference': 3}
        ]
        
        engine = AHPEngine()
        cr = engine.calculate_consistency_ratio(comparisons)
        
        # EXACT: CR should be <= 0.10 for acceptable consistency
        assert 0.0 <= cr <= 0.10
    
    def test_weight_calculation(self):
        """Test criterion weight calculation from comparisons."""
        from datascience_platform.qvf.ahp import AHPEngine
        
        comparisons = [
            {'criterion_a': 'A', 'criterion_b': 'B', 'preference': 3},
            {'criterion_a': 'A', 'criterion_b': 'C', 'preference': 5},
            {'criterion_a': 'B', 'criterion_b': 'C', 'preference': 3}
        ]
        
        engine = AHPEngine()
        weights = engine.calculate_weights(comparisons)
        
        # EXACT: Weights must sum to 1.0
        assert abs(sum(weights.values()) - 1.0) < 0.0001
        assert all(0 < w < 1 for w in weights.values())
```

### **6.2 Integration Test Scenarios**

```python
# File: tests/integration/test_qvf_workflow.py
import pytest
import asyncio
from httpx import AsyncClient
import sqlite3

@pytest.mark.integration
class TestQVFWorkflow:
    """End-to-end QVF workflow integration tests."""
    
    @pytest.fixture
    async def test_client(self):
        """Test client with test database."""
        from datascience_platform.main import app
        async with AsyncClient(app=app, base_url="http://test") as client:
            yield client
    
    @pytest.fixture
    def test_database(self, tmp_path):
        """Isolated test database."""
        db_path = tmp_path / "test_qvf.sqlite"
        
        # EXACT: Initialize with schema
        conn = sqlite3.connect(str(db_path))
        with open("migrations/001_initial_schema.sql") as f:
            conn.executescript(f.read())
        conn.close()
        
        return str(db_path)
    
    async def test_complete_qvf_workflow(self, test_client, test_database):
        """Test complete QVF analysis workflow."""
        
        # Step 1: Create criteria
        criteria_data = [
            {
                "name": "Business Value",
                "description": "Direct business impact",
                "weight": 0.4,
                "category": "business"
            },
            {
                "name": "Technical Risk", 
                "description": "Implementation complexity",
                "weight": 0.3,
                "category": "technical"
            },
            {
                "name": "Strategic Fit",
                "description": "Alignment with strategy", 
                "weight": 0.3,
                "category": "strategic"
            }
        ]
        
        created_criteria = []
        for criterion in criteria_data:
            response = await test_client.post("/api/v1/criteria", json=criterion)
            assert response.status_code == 201  # EXACT: Created status
            created_criteria.append(response.json())
        
        # Step 2: Submit AHP comparisons
        stakeholder_id = "test_stakeholder_123"
        comparisons = [
            {
                "stakeholder_id": stakeholder_id,
                "criterion_a": created_criteria[0]['id'],
                "criterion_b": created_criteria[1]['id'], 
                "preference": 3  # Business Value moderately more important than Technical Risk
            },
            {
                "stakeholder_id": stakeholder_id,
                "criterion_a": created_criteria[0]['id'],
                "criterion_b": created_criteria[2]['id'],
                "preference": 5  # Business Value strongly more important than Strategic Fit
            },
            {
                "stakeholder_id": stakeholder_id,
                "criterion_a": created_criteria[1]['id'],
                "criterion_b": created_criteria[2]['id'],
                "preference": 3  # Technical Risk moderately more important than Strategic Fit
            }
        ]
        
        for comparison in comparisons:
            response = await test_client.post("/api/v1/comparisons", json=comparison)
            assert response.status_code == 201
            
            # EXACT: Verify consistency ratio
            result = response.json()
            assert result['consistency_ratio'] <= 0.10
        
        # Step 3: Analyze work items
        work_items = [
            {
                "id": "12345",
                "title": "User authentication system",
                "type": "Feature",
                "business_value": 800,
                "story_points": 13,
                "priority": 1
            },
            {
                "id": "12346", 
                "title": "Data visualization dashboard",
                "type": "Feature",
                "business_value": 600,
                "story_points": 8,
                "priority": 2
            }
        ]
        
        analysis_request = {
            "work_item_ids": [item["id"] for item in work_items],
            "force_refresh": True
        }
        
        response = await test_client.post("/api/v1/workitems/analyze", json=analysis_request)
        assert response.status_code == 202  # EXACT: Accepted for processing
        
        result = response.json()
        assert result['analyzed_count'] == 2
        assert result['failed_count'] == 0
        assert len(result['results']) == 2
        
        # EXACT: Verify scoring results
        for work_item in result['results']:
            assert 0.0 <= work_item['qvf_total_score'] <= 100.0
            assert len(work_item['qvf_scores']) == 3  # One per criterion
            assert work_item['last_analyzed'] is not None

@pytest.mark.integration  
class TestADOIntegration:
    """Test Azure DevOps API integration."""
    
    @pytest.fixture
    def mock_ado_client(self):
        """Mock ADO client for testing."""
        from unittest.mock import Mock
        client = Mock()
        
        # Mock successful work item retrieval
        client.get_work_items.return_value = [
            {
                'id': '12345',
                'fields': {
                    'System.Title': 'Test Feature',
                    'System.WorkItemType': 'Feature',
                    'System.State': 'New',
                    'Microsoft.VSTS.Common.BusinessValue': 500,
                    'Microsoft.VSTS.Scheduling.StoryPoints': 8,
                    'System.Priority': 2
                }
            }
        ]
        
        return client
    
    async def test_ado_work_item_sync(self, mock_ado_client):
        """Test synchronization with ADO work items."""
        from datascience_platform.qvf.ado_sync import ADOSynchronizer
        
        sync = ADOSynchronizer(mock_ado_client)
        
        # EXACT: Test batch synchronization
        result = await sync.sync_work_items(
            project="TestProject",
            work_item_types=["Feature", "Epic"],
            batch_size=50  # EXACT: From batch config
        )
        
        assert result['synced_count'] > 0
        assert result['failed_count'] == 0
        assert 'last_sync_time' in result
```

### **6.3 Performance Test Benchmarks**

```python
# File: tests/performance/test_qvf_performance.py
import pytest
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor
import psutil
import os

@pytest.mark.performance
class TestQVFPerformance:
    """Performance benchmarks for QVF operations."""
    
    async def test_api_response_times(self, test_client):
        """Test API response time requirements."""
        
        # EXACT: Test GET criteria endpoint (50ms requirement)
        start = time.perf_counter()
        response = await test_client.get("/api/v1/criteria")
        end = time.perf_counter()
        
        response_time_ms = (end - start) * 1000
        assert response.status_code == 200
        assert response_time_ms <= 50  # EXACT: 50ms requirement
    
    async def test_work_item_analysis_performance(self, test_client):
        """Test work item analysis performance."""
        
        # Single work item analysis (2s requirement)
        analysis_request = {
            "work_item_ids": ["12345"],
            "force_refresh": True
        }
        
        start = time.perf_counter()
        response = await test_client.post("/api/v1/workitems/analyze", json=analysis_request)
        end = time.perf_counter()
        
        response_time_ms = (end - start) * 1000
        assert response.status_code == 202
        assert response_time_ms <= 2000  # EXACT: 2s requirement
    
    async def test_batch_processing_performance(self, test_client):
        """Test batch processing performance."""
        
        # 50-item batch (30s requirement)
        work_item_ids = [f"item_{i}" for i in range(50)]  # EXACT: 50 items
        analysis_request = {
            "work_item_ids": work_item_ids,
            "force_refresh": True
        }
        
        start = time.perf_counter()
        response = await test_client.post("/api/v1/workitems/analyze", json=analysis_request)
        end = time.perf_counter()
        
        response_time_ms = (end - start) * 1000
        assert response.status_code == 202
        assert response_time_ms <= 30000  # EXACT: 30s requirement
    
    def test_memory_usage_limits(self):
        """Test memory usage stays within limits."""
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Simulate large work item processing
        # ... processing simulation ...
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # EXACT: Should not exceed 2MB per work item for 50 items
        assert memory_increase <= 100  # 50 items * 2MB per item
    
    async def test_concurrent_user_performance(self):
        """Test concurrent user capacity."""
        
        async def simulate_user_session(user_id: int):
            """Simulate typical user session."""
            async with AsyncClient(base_url="http://test") as client:
                # Typical user workflow
                await client.get("/api/v1/criteria")  # View criteria
                await client.get("/api/v1/workitems?limit=10")  # View work items
                
                # Submit comparison
                comparison = {
                    "stakeholder_id": f"user_{user_id}",
                    "criterion_a": "criterion_1",
                    "criterion_b": "criterion_2", 
                    "preference": 3
                }
                await client.post("/api/v1/comparisons", json=comparison)
        
        # EXACT: Test 50 concurrent users
        start = time.perf_counter()
        tasks = [simulate_user_session(i) for i in range(50)]
        await asyncio.gather(*tasks)
        end = time.perf_counter()
        
        total_time = end - start
        # All 50 user sessions should complete within reasonable time
        assert total_time <= 10  # 10 seconds for 50 concurrent users
```

---

## **7. File Naming and Structure**

### **7.1 Directory Structure (EXACT)**

```
src/datascience_platform/qvf/
├── __init__.py                           # Package initialization
├── models.py                             # Pydantic data models
├── exceptions.py                         # QVF-specific exceptions
├── config.py                             # QVF configuration settings
│
├── api/                                  # REST API endpoints
│   ├── __init__.py
│   ├── criteria.py                       # /api/v1/criteria endpoints
│   ├── workitems.py                      # /api/v1/workitems endpoints
│   ├── comparisons.py                    # /api/v1/comparisons endpoints
│   ├── admin.py                          # /api/v1/admin endpoints
│   └── websocket.py                      # WebSocket handlers
│
├── core/                                 # Core business logic
│   ├── __init__.py
│   ├── calculator.py                     # QVF score calculations
│   ├── ahp.py                           # AHP engine implementation
│   ├── semantic.py                      # Semantic alignment analysis
│   └── fallbacks.py                     # Fallback chain logic
│
├── integrations/                         # External service integrations
│   ├── __init__.py
│   ├── ado_client.py                    # Azure DevOps REST client
│   ├── ado_sync.py                      # ADO synchronization logic
│   ├── ollama_client.py                 # Ollama LLM client
│   └── chromadb_client.py               # ChromaDB vector store client
│
├── storage/                             # Data persistence layer
│   ├── __init__.py
│   ├── sqlite_manager.py                # SQLite database operations
│   ├── repositories.py                  # Data access repositories
│   └── migrations/                      # Database migrations
│       ├── 001_initial_schema.sql
│       ├── 002_add_indexes.sql
│       └── 003_add_audit_fields.sql
│
├── coaching/                            # Coaching question engine
│   ├── __init__.py
│   ├── question_generator.py            # Dynamic question generation
│   ├── response_analyzer.py             # Response analysis and scoring
│   └── templates/                       # Question templates
│       ├── business_questions.json
│       ├── technical_questions.json
│       └── strategic_questions.json
│
├── ui/                                  # Frontend components (TypeScript/React)
│   ├── components/                      # React components
│   │   ├── CriteriaManager.tsx
│   │   ├── WorkItemList.tsx
│   │   ├── ComparisonMatrix.tsx
│   │   ├── QVFDashboard.tsx
│   │   └── AdminInterface.tsx
│   ├── types/                          # TypeScript type definitions
│   │   ├── qvf-core.ts
│   │   ├── api-responses.ts
│   │   └── ui-state.ts
│   ├── hooks/                          # React hooks
│   │   ├── useQVFData.ts
│   │   ├── useWebSocket.ts
│   │   └── useErrorHandling.ts
│   ├── pages/                          # Next.js pages
│   │   ├── index.tsx                   # Main dashboard
│   │   ├── criteria.tsx                # Criteria management
│   │   ├── comparisons.tsx             # AHP comparisons interface
│   │   └── admin.tsx                   # Admin interface
│   └── styles/                         # Tailwind CSS styles
│       ├── globals.css
│       └── components.css
│
└── utils/                              # Utility functions
    ├── __init__.py
    ├── validation.py                   # Input validation utilities
    ├── retry.py                        # Retry logic implementation
    ├── logging.py                      # Structured logging setup
    └── batch.py                        # Batch processing utilities

tests/
├── unit/                               # Unit tests
│   ├── test_models.py
│   ├── test_calculator.py
│   ├── test_ahp.py
│   └── test_validation.py
├── integration/                        # Integration tests
│   ├── test_qvf_workflow.py
│   ├── test_ado_integration.py
│   └── test_api_endpoints.py
├── performance/                        # Performance tests
│   ├── test_qvf_performance.py
│   └── test_batch_processing.py
└── fixtures/                           # Test data
    ├── sample_criteria.json
    ├── sample_workitems.json
    └── sample_comparisons.json

docs/bmad/                              # Documentation
├── implementation-standards-qvf.md     # This document
├── api-specification.yaml              # OpenAPI specification
├── database-schema.md                  # Database documentation
└── deployment-guide.md                 # Production deployment guide

data/                                   # Data directory
├── qvf.sqlite                          # Main SQLite database
├── chroma_db/                          # ChromaDB persistence
└── logs/                               # Application logs
    ├── qvf-application.log
    └── qvf-performance.log
```

### **7.2 Import/Export Conventions**

```python
# File: src/datascience_platform/qvf/__init__.py
"""QVF package initialization with controlled exports."""

# EXACT: Public API exports (semver compatibility)
from .models import (
    QVFCriterion,
    QVFScore, 
    QVFWorkItem,
    AHPComparison,
    CriterionCategory,
    WorkItemType,
    WorkItemState
)

from .exceptions import (
    QVFError,
    QVFErrorCode,
    ErrorResponse
)

from .core.calculator import QVFScoreCalculator
from .core.ahp import AHPEngine
from .integrations.ado_client import ADOClient

# EXACT: Version information
__version__ = "1.0.0"
__api_version__ = "v1"

# EXACT: Package metadata
__all__ = [
    # Models
    "QVFCriterion",
    "QVFScore", 
    "QVFWorkItem",
    "AHPComparison",
    "CriterionCategory",
    "WorkItemType",
    "WorkItemState",
    
    # Exceptions
    "QVFError",
    "QVFErrorCode", 
    "ErrorResponse",
    
    # Core classes
    "QVFScoreCalculator",
    "AHPEngine",
    "ADOClient",
    
    # Metadata
    "__version__",
    "__api_version__"
]

# EXACT: Lazy loading for optional dependencies
def _get_ollama_client():
    """Lazy load Ollama client to handle optional dependency."""
    try:
        from .integrations.ollama_client import OllamaClient
        return OllamaClient
    except ImportError:
        return None

def _get_chromadb_client():
    """Lazy load ChromaDB client to handle optional dependency.""" 
    try:
        from .integrations.chromadb_client import ChromaDBClient
        return ChromaDBClient
    except ImportError:
        return None

# Optional exports (only available if dependencies installed)
OllamaClient = _get_ollama_client()
ChromaDBClient = _get_chromadb_client()

if OllamaClient:
    __all__.append("OllamaClient")
    
if ChromaDBClient:
    __all__.append("ChromaDBClient")
```

### **7.3 Configuration File Formats**

```yaml
# File: config/qvf-production.yaml
application:
  name: "QVF Production"
  version: "1.0.0"
  debug: false
  log_level: "INFO"
  
database:
  type: "sqlite"
  path: "/data/qvf-production.sqlite"
  connection_pool_size: 10
  query_timeout_seconds: 30
  wal_mode: true
  
api:
  host: "0.0.0.0"
  port: 8000
  cors_origins: 
    - "https://qvf.company.com"
    - "https://devops.company.com"
  rate_limit:
    requests_per_minute: 1000
    burst_size: 100
    
azure_devops:
  organization: "company-devops"
  base_url: "https://dev.azure.com/company-devops"
  api_version: "7.1"
  timeout_seconds: 30
  batch_size: 200
  rate_limit_delay_ms: 100
  
ollama:
  enabled: true
  endpoint: "http://localhost:11434"
  models:
    primary: "llama2:7b-chat"
    fallback: "mistral:7b-instruct"
  timeout_seconds: 30
  max_tokens: 4096
  temperature: 0.3
  
chromadb:
  enabled: true
  host: "localhost"
  port: 8000
  collection_name: "qvf_embeddings"
  distance_metric: "cosine"
  persistence_path: "/data/chroma_db"
  
performance:
  max_concurrent_requests: 100
  work_item_batch_size: 50
  memory_limit_mb: 2048
  cache_ttl_seconds:
    criteria: 3600
    scores: 1800
    embeddings: 86400
```

---

## **8. Code Style Guidelines**

### **8.1 Python Coding Standards**

```python
# File: src/datascience_platform/qvf/style_example.py
"""
QVF Python coding standards example.

This module demonstrates the exact coding standards that must be followed
in all QVF Python code.
"""

from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum
import logging

# EXACT: Import ordering
# 1. Standard library imports (alphabetical)
# 2. Third-party imports (alphabetical) 
# 3. Local application imports (alphabetical)

from pydantic import BaseModel, Field, validator
import pandas as pd
import numpy as np

from datascience_platform.qvf.exceptions import QVFError, QVFErrorCode
from datascience_platform.qvf.models import QVFCriterion


class ExampleService:
    """
    Example service demonstrating QVF coding standards.
    
    This class shows proper:
    - Docstring format (Google style)
    - Type annotations
    - Error handling
    - Logging practices
    - Method organization
    
    Args:
        config: Service configuration dictionary
        logger: Optional logger instance
        
    Attributes:
        is_initialized: Whether service has been initialized
        last_error: Most recent error encountered
    """
    
    def __init__(
        self, 
        config: Dict[str, Any],
        logger: Optional[logging.Logger] = None
    ) -> None:
        """Initialize the example service."""
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        self.is_initialized = False
        self.last_error: Optional[Exception] = None
        
        # EXACT: Validate configuration on initialization
        self._validate_config()
    
    async def process_work_items(
        self,
        work_items: List[Dict[str, Any]],
        criteria: List[QVFCriterion],
        force_refresh: bool = False,
        batch_size: int = 50
    ) -> Dict[str, Any]:
        """
        Process work items and calculate QVF scores.
        
        EXACT: Method demonstrates proper async/await usage, type annotations,
        parameter validation, error handling, and return value documentation.
        
        Args:
            work_items: List of work item dictionaries from ADO
            criteria: List of QVF criteria for scoring
            force_refresh: Whether to recalculate existing scores
            batch_size: Number of items to process in each batch (1-100)
            
        Returns:
            Dictionary containing:
                - processed_count: Number of successfully processed items
                - failed_count: Number of failed items
                - results: List of processed work items with scores
                - errors: List of error details for failed items
                
        Raises:
            QVFError: If validation fails or processing cannot continue
            ValueError: If batch_size is outside valid range
            
        Example:
            >>> service = ExampleService(config)
            >>> result = await service.process_work_items(
            ...     work_items=[{"id": "123", "title": "Feature"}],
            ...     criteria=[criterion1, criterion2],
            ...     batch_size=25
            ... )
            >>> print(f"Processed {result['processed_count']} items")
        """
        # EXACT: Input validation at method start
        if not work_items:
            raise QVFError(
                code=QVFErrorCode.VALIDATION_FAILED,
                message="work_items cannot be empty",
                details={"provided_count": 0}
            )
            
        if not (1 <= batch_size <= 100):
            raise ValueError(f"batch_size must be between 1 and 100, got {batch_size}")
        
        # EXACT: Early return for edge cases
        if not criteria:
            self.logger.warning("No criteria provided, returning empty results")
            return {
                "processed_count": 0,
                "failed_count": 0,
                "results": [],
                "errors": []
            }
        
        # EXACT: Initialize result structure
        result = {
            "processed_count": 0,
            "failed_count": 0,
            "results": [],
            "errors": []
        }
        
        # EXACT: Process in batches with proper error handling
        try:
            for i in range(0, len(work_items), batch_size):
                batch = work_items[i:i + batch_size]
                
                self.logger.info(
                    f"Processing batch {i // batch_size + 1}, items {i} to {i + len(batch)}"
                )
                
                batch_result = await self._process_batch(batch, criteria, force_refresh)
                
                # EXACT: Aggregate results
                result["processed_count"] += batch_result["processed_count"]
                result["failed_count"] += batch_result["failed_count"]
                result["results"].extend(batch_result["results"])
                result["errors"].extend(batch_result["errors"])
                
        except Exception as e:
            self.logger.error(f"Batch processing failed: {e}", exc_info=True)
            self.last_error = e
            
            # EXACT: Convert generic exceptions to QVF errors
            raise QVFError(
                code=QVFErrorCode.BATCH_PROCESSING_FAILED,
                message=f"Failed to process work items: {str(e)}",
                details={
                    "total_items": len(work_items),
                    "batch_size": batch_size,
                    "error_type": type(e).__name__
                }
            ) from e
        
        # EXACT: Log summary of results
        self.logger.info(
            f"Processing complete: {result['processed_count']} succeeded, "
            f"{result['failed_count']} failed"
        )
        
        return result
    
    def _validate_config(self) -> None:
        """
        Validate service configuration.
        
        EXACT: Private methods use single underscore prefix and handle
        validation logic separately from public interface.
        """
        required_keys = ["database_url", "batch_size", "timeout_seconds"]
        
        for key in required_keys:
            if key not in self.config:
                raise QVFError(
                    code=QVFErrorCode.MISSING_CONFIGURATION,
                    message=f"Required configuration key missing: {key}",
                    details={"missing_key": key, "available_keys": list(self.config.keys())}
                )
        
        # EXACT: Validate value ranges
        if not (1 <= self.config["batch_size"] <= 100):
            raise QVFError(
                code=QVFErrorCode.MISSING_CONFIGURATION,
                message="batch_size must be between 1 and 100",
                details={"provided_value": self.config["batch_size"]}
            )
            
        self.is_initialized = True
    
    async def _process_batch(
        self, 
        batch: List[Dict[str, Any]], 
        criteria: List[QVFCriterion],
        force_refresh: bool
    ) -> Dict[str, Any]:
        """Process a single batch of work items."""
        # Implementation details...
        return {"processed_count": len(batch), "failed_count": 0, "results": batch, "errors": []}
    
    def __repr__(self) -> str:
        """EXACT: Provide useful string representation."""
        return (
            f"ExampleService("
            f"initialized={self.is_initialized}, "
            f"config_keys={list(self.config.keys())}"
            f")"
        )


# EXACT: Constants use UPPER_CASE
DEFAULT_BATCH_SIZE = 50
MAX_RETRY_ATTEMPTS = 3
SUPPORTED_WORK_ITEM_TYPES = ["Epic", "Feature", "User Story", "PIO"]

# EXACT: Module-level functions use snake_case
def calculate_consistency_ratio(comparison_matrix: np.ndarray) -> float:
    """
    Calculate AHP consistency ratio for comparison matrix.
    
    EXACT: Function demonstrates proper parameter and return type annotations,
    clear docstring, and focused single responsibility.
    
    Args:
        comparison_matrix: Square numpy array of pairwise comparisons
        
    Returns:
        Consistency ratio between 0.0 and 1.0
        
    Raises:
        ValueError: If matrix is not square or contains invalid values
    """
    if comparison_matrix.shape[0] != comparison_matrix.shape[1]:
        raise ValueError("Comparison matrix must be square")
    
    # AHP consistency calculation logic
    eigenvalues = np.linalg.eigvals(comparison_matrix)
    max_eigenvalue = np.max(eigenvalues.real)
    
    n = comparison_matrix.shape[0]
    consistency_index = (max_eigenvalue - n) / (n - 1)
    
    # Random index values for AHP
    random_indices = {3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45}
    
    if n < 3 or n not in random_indices:
        return 0.0
    
    return consistency_index / random_indices[n]
```

### **8.2 TypeScript Coding Standards**

```typescript
// File: src/datascience_platform/qvf/ui/types/qvf-core.ts

/**
 * QVF TypeScript coding standards example.
 * 
 * This file demonstrates the exact TypeScript coding standards that must
 * be followed in all QVF frontend code.
 */

// EXACT: Import ordering (same as Python)
// 1. React/Next.js imports
// 2. Third-party library imports
// 3. Local component imports
// 4. Type-only imports

import React, { useState, useEffect, useCallback } from 'react';
import { NextPage } from 'next';
import axios from 'axios';
import { toast } from 'react-hot-toast';

import { Button, Card, LoadingSpinner } from '../components/ui';
import { useQVFData } from '../hooks/useQVFData';

import type { QVFCriterion, QVFWorkItem, APIResponse } from '../types/qvf-core';

// EXACT: Interface definitions with complete documentation
/**
 * Configuration for QVF criterion comparison interface.
 * 
 * @interface ComparisonConfig
 */
interface ComparisonConfig {
  /** Maximum number of comparisons to show at once (1-20) */
  readonly maxComparisons: number;
  
  /** Whether to show consistency ratio in real-time */
  readonly showConsistencyRatio: boolean;
  
  /** Threshold for acceptable consistency ratio (0.0-0.10) */
  readonly consistencyThreshold: number;
  
  /** Auto-save interval in milliseconds (min: 1000) */
  readonly autoSaveIntervalMs: number;
}

// EXACT: Enum definitions with explicit values
enum WorkItemPriority {
  CRITICAL = 1,
  HIGH = 2,
  MEDIUM = 3,
  LOW = 4
}

enum ProcessingState {
  IDLE = 'idle',
  LOADING = 'loading',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  ERROR = 'error'
}

// EXACT: Type definitions for API responses
type QVFScoreResponse = {
  readonly scores: ReadonlyArray<{
    readonly criterionId: string;
    readonly rawScore: number;
    readonly normalizedScore: number;
    readonly confidence: number;
    readonly evidence?: string;
  }>;
  readonly totalScore: number;
  readonly method: 'ai_enhanced' | 'coaching_guided' | 'mathematical';
  readonly calculatedAt: string;
};

type BatchProcessingResult = {
  readonly batchId: string;
  readonly processed: number;
  readonly total: number;
  readonly failed: number;
  readonly errors: ReadonlyArray<{
    readonly itemId: string;
    readonly error: string;
    readonly code: string;
  }>;
  readonly estimatedCompletion?: string;
};

// EXACT: React component with proper TypeScript patterns
interface CriteriaComparisonProps {
  /** List of criteria to compare */
  readonly criteria: ReadonlyArray<QVFCriterion>;
  
  /** Current stakeholder ID */
  readonly stakeholderId: string;
  
  /** Configuration for comparison interface */
  readonly config: ComparisonConfig;
  
  /** Callback when comparisons are submitted */
  readonly onComparisonsComplete: (
    comparisons: ReadonlyArray<AHPComparison>
  ) => Promise<void>;
  
  /** Optional callback for real-time consistency updates */
  readonly onConsistencyUpdate?: (ratio: number) => void;
}

/**
 * Criteria comparison component for AHP analysis.
 * 
 * EXACT: Component demonstrates proper TypeScript React patterns including:
 * - Proper interface definitions for props
 * - State management with correct typing
 * - Error handling with specific error types
 * - Performance optimization with useCallback/useMemo
 * - Accessibility considerations
 */
const CriteriaComparison: React.FC<CriteriaComparisonProps> = ({
  criteria,
  stakeholderId,
  config,
  onComparisonsComplete,
  onConsistencyUpdate
}) => {
  // EXACT: State definitions with explicit types
  const [comparisons, setComparisons] = useState<Map<string, number>>(new Map());
  const [processingState, setProcessingState] = useState<ProcessingState>(ProcessingState.IDLE);
  const [consistencyRatio, setConsistencyRatio] = useState<number>(0);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  
  // EXACT: Derived state with proper memoization
  const comparisonPairs = React.useMemo(() => {
    const pairs: Array<{ criterionA: QVFCriterion; criterionB: QVFCriterion; key: string }> = [];
    
    for (let i = 0; i < criteria.length; i++) {
      for (let j = i + 1; j < criteria.length; j++) {
        const key = `${criteria[i].id}-${criteria[j].id}`;
        pairs.push({
          criterionA: criteria[i],
          criterionB: criteria[j],
          key
        });
      }
    }
    
    return pairs;
  }, [criteria]);
  
  // EXACT: Event handlers with proper error handling and typing
  const handleComparisonChange = useCallback((
    pairKey: string,
    preference: number
  ): void => {
    // EXACT: Validate input parameters
    if (preference < 1 || preference > 9 || ![1, 3, 5, 7, 9].includes(preference)) {
      setErrorMessage(`Invalid preference value: ${preference}. Must be 1, 3, 5, 7, or 9.`);
      return;
    }
    
    setComparisons(prev => new Map(prev).set(pairKey, preference));
    setErrorMessage(null);
    
    // EXACT: Calculate consistency ratio if enough comparisons
    if (comparisons.size >= (criteria.length * (criteria.length - 1)) / 2) {
      void calculateConsistencyRatio();
    }
  }, [comparisons, criteria.length]);
  
  const calculateConsistencyRatio = useCallback(async (): Promise<void> => {
    try {
      setProcessingState(ProcessingState.PROCESSING);
      
      // EXACT: API call with proper error handling
      const response = await axios.post<{ consistencyRatio: number }>(
        '/api/v1/comparisons/consistency',
        {
          stakeholderId,
          comparisons: Array.from(comparisons.entries()).map(([key, preference]) => {
            const [criterionA, criterionB] = key.split('-');
            return { criterionA, criterionB, preference };
          })
        },
        {
          timeout: 5000, // EXACT: 5 second timeout
          headers: {
            'Content-Type': 'application/json'
          }
        }
      );
      
      const newRatio = response.data.consistencyRatio;
      setConsistencyRatio(newRatio);
      
      // EXACT: Notify parent component
      onConsistencyUpdate?.(newRatio);
      
      // EXACT: Show warning if consistency threshold exceeded
      if (newRatio > config.consistencyThreshold) {
        toast.error(
          `Consistency ratio (${newRatio.toFixed(3)}) exceeds threshold (${config.consistencyThreshold.toFixed(3)}). Please review your comparisons.`,
          { duration: 5000 }
        );
      }
      
      setProcessingState(ProcessingState.COMPLETED);
      
    } catch (error) {
      setProcessingState(ProcessingState.ERROR);
      
      // EXACT: Proper error handling with specific error types
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.user_message || error.message;
        setErrorMessage(`Failed to calculate consistency: ${message}`);
        toast.error(message);
      } else {
        setErrorMessage('An unexpected error occurred while calculating consistency.');
        console.error('Consistency calculation error:', error);
      }
    }
  }, [stakeholderId, comparisons, config.consistencyThreshold, onConsistencyUpdate]);
  
  const handleSubmitComparisons = useCallback(async (): Promise<void> => {
    try {
      setProcessingState(ProcessingState.LOADING);
      
      // EXACT: Validate all comparisons are complete
      const requiredComparisons = (criteria.length * (criteria.length - 1)) / 2;
      if (comparisons.size < requiredComparisons) {
        throw new Error(`Please complete all ${requiredComparisons} comparisons. Currently have ${comparisons.size}.`);
      }
      
      // EXACT: Convert to API format
      const apiComparisons = Array.from(comparisons.entries()).map(([key, preference]) => {
        const [criterionA, criterionB] = key.split('-');
        return {
          stakeholderId,
          criterionA,
          criterionB,
          preference,
          createdAt: new Date().toISOString()
        };
      });
      
      await onComparisonsComplete(apiComparisons);
      setProcessingState(ProcessingState.COMPLETED);
      
      toast.success('Comparisons submitted successfully!');
      
    } catch (error) {
      setProcessingState(ProcessingState.ERROR);
      
      const message = error instanceof Error ? error.message : 'Failed to submit comparisons';
      setErrorMessage(message);
      toast.error(message);
    }
  }, [criteria.length, comparisons, stakeholderId, onComparisonsComplete]);
  
  // EXACT: Component render with proper accessibility
  return (
    <Card className="w-full max-w-4xl mx-auto p-6">
      <div className="space-y-6">
        {/* EXACT: Header with clear instructions */}
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Criterion Comparison
          </h2>
          <p className="text-gray-600">
            Compare each pair of criteria using the scale: 1 (equal), 3 (moderate), 
            5 (strong), 7 (very strong), 9 (extreme)
          </p>
        </div>
        
        {/* EXACT: Error display */}
        {errorMessage && (
          <div 
            className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded"
            role="alert"
          >
            {errorMessage}
          </div>
        )}
        
        {/* EXACT: Consistency indicator */}
        {config.showConsistencyRatio && consistencyRatio > 0 && (
          <div className={`p-4 rounded ${
            consistencyRatio <= config.consistencyThreshold
              ? 'bg-green-50 border border-green-200 text-green-700'
              : 'bg-yellow-50 border border-yellow-200 text-yellow-700'
          }`}>
            <span className="font-medium">
              Consistency Ratio: {consistencyRatio.toFixed(3)}
            </span>
            {consistencyRatio > config.consistencyThreshold && (
              <p className="text-sm mt-1">
                Consider reviewing your comparisons for better consistency.
              </p>
            )}
          </div>
        )}
        
        {/* EXACT: Comparison pairs */}
        <div className="space-y-4">
          {comparisonPairs.slice(0, config.maxComparisons).map(({ criterionA, criterionB, key }) => (
            <div 
              key={key}
              className="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
            >
              <div className="flex-1">
                <span className="font-medium text-gray-900">
                  {criterionA.name}
                </span>
                <span className="mx-3 text-gray-500">vs</span>
                <span className="font-medium text-gray-900">
                  {criterionB.name}
                </span>
              </div>
              
              <div className="flex space-x-2">
                {[1, 3, 5, 7, 9].map((value) => (
                  <button
                    key={value}
                    type="button"
                    className={`px-3 py-2 rounded text-sm font-medium transition-colors ${
                      comparisons.get(key) === value
                        ? 'bg-blue-600 text-white'
                        : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
                    }`}
                    onClick={() => handleComparisonChange(key, value)}
                    aria-label={`Rate comparison as ${value}`}
                  >
                    {value}
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>
        
        {/* EXACT: Submit button with loading state */}
        <div className="flex justify-center">
          <Button
            onClick={handleSubmitComparisons}
            disabled={processingState === ProcessingState.LOADING || comparisons.size === 0}
            className="px-8 py-3"
          >
            {processingState === ProcessingState.LOADING && <LoadingSpinner className="mr-2" />}
            Submit Comparisons
          </Button>
        </div>
      </div>
    </Card>
  );
};

export default CriteriaComparison;

// EXACT: Export all types for external use
export type {
  ComparisonConfig,
  QVFScoreResponse,
  BatchProcessingResult,
  CriteriaComparisonProps
};

export {
  WorkItemPriority,
  ProcessingState
};
```

---

This comprehensive implementation standards document provides concrete, unambiguous specifications for the QVF system development. Every aspect is precisely defined with exact values, formats, and requirements to ensure consistent implementation across all development team members.

The standards cover all critical areas:
- **Technology Stack**: Exact versions and configurations for all dependencies
- **Data Models**: Complete TypeScript interfaces and SQLite schemas
- **API Contracts**: Detailed REST endpoints and WebSocket message formats
- **Error Handling**: Standardized error codes, retry strategies, and fallback chains
- **Performance**: Specific response time targets and throughput requirements
- **Testing**: Comprehensive unit, integration, and performance test patterns
- **File Structure**: Exact directory organization and naming conventions
- **Code Style**: Detailed Python and TypeScript coding standards with examples

These standards eliminate ambiguity and ensure that any developer can implement the exact same system when following this specification.