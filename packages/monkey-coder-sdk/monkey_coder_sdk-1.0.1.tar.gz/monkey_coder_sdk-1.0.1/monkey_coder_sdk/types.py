"""
Type definitions for Monkey Coder Python SDK.

This module provides all the data models and type definitions
used throughout the SDK, including request/response models,
configuration objects, and enumerations.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union, Callable
import uuid


class TaskType(str, Enum):
    """Task type enumeration."""
    CODE_GENERATION = "code_generation"
    CODE_ANALYSIS = "code_analysis"
    CODE_REVIEW = "code_review"
    DOCUMENTATION = "documentation"
    TESTING = "testing"
    DEBUGGING = "debugging"
    REFACTORING = "refactoring"
    CUSTOM = "custom"


class PersonaType(str, Enum):
    """SuperClaude persona types."""
    DEVELOPER = "developer"
    ARCHITECT = "architect"
    REVIEWER = "reviewer"
    SECURITY_ANALYST = "security_analyst"
    PERFORMANCE_EXPERT = "performance_expert"
    TESTER = "tester"
    TECHNICAL_WRITER = "technical_writer"
    CUSTOM = "custom"


class ProviderType(str, Enum):
    """AI provider type enumeration."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    QWEN = "qwen"


class TaskStatus(str, Enum):
    """Task execution status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ExecutionContext:
    """Execution context for task processing."""
    user_id: str
    session_id: Optional[str] = None
    workspace_id: Optional[str] = None
    environment: str = "production"
    timeout: int = 300
    max_tokens: int = 4096
    temperature: float = 0.1

    def __post_init__(self):
        if not (1 <= self.timeout <= 3600):
            raise ValueError("Timeout must be between 1 and 3600 seconds")
        if not (0.0 <= self.temperature <= 2.0):
            raise ValueError("Temperature must be between 0.0 and 2.0")


@dataclass
class SuperClaudeConfig:
    """Configuration for SuperClaude slash-command & persona router."""
    persona: PersonaType
    slash_commands: List[str] = field(default_factory=list)
    context_window: int = 32768
    use_markdown_spec: bool = True
    custom_instructions: Optional[str] = None


@dataclass
class Monkey1Config:
    """Configuration for monkey1 multi-agent orchestrator."""
    agent_count: int = 3
    coordination_strategy: str = "collaborative"
    consensus_threshold: float = 0.7
    enable_reflection: bool = True
    max_iterations: int = 5

    def __post_init__(self):
        if not (1 <= self.agent_count <= 10):
            raise ValueError("Agent count must be between 1 and 10")


@dataclass
class Gary8DConfig:
    """Configuration for Gary8D functional-quantum executor."""
    parallel_futures: bool = True
    collapse_strategy: str = "weighted_average"
    quantum_coherence: float = 0.8
    execution_branches: int = 3
    uncertainty_threshold: float = 0.1

    def __post_init__(self):
        if not (0.0 <= self.quantum_coherence <= 1.0):
            raise ValueError("Quantum coherence must be between 0.0 and 1.0")


@dataclass
class FileData:
    """File data for task execution."""
    path: str
    content: str
    type: Optional[str] = None


@dataclass
class ExecuteRequest:
    """Request model for task execution."""
    task_type: TaskType
    prompt: str
    context: ExecutionContext
    superclause_config: SuperClaudeConfig
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    files: Optional[List[FileData]] = None
    monkey1_config: Optional[Monkey1Config] = None
    gary8d_config: Optional[Gary8DConfig] = None
    preferred_providers: Optional[List[ProviderType]] = None
    model_preferences: Optional[Dict[ProviderType, str]] = None

    def __post_init__(self):
        if not self.prompt or len(self.prompt.strip()) < 10:
            raise ValueError("Prompt must be at least 10 characters long")
        self.prompt = self.prompt.strip()


@dataclass
class UsageMetrics:
    """Usage metrics for task execution."""
    tokens_used: int
    tokens_input: int
    tokens_output: int
    provider_breakdown: Dict[str, int]
    cost_estimate: float
    execution_time: float


@dataclass
class ExecutionResult:
    """Result of task execution."""
    result: Any
    metadata: Dict[str, Any] = field(default_factory=dict)
    artifacts: List[Dict[str, Any]] = field(default_factory=list)
    confidence_score: float = 0.0
    quantum_collapse_info: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecuteResponse:
    """Response model for task execution."""
    execution_id: str
    task_id: str
    status: TaskStatus
    result: Optional[ExecutionResult] = None
    error: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    completed_at: Optional[str] = None
    usage: Optional[UsageMetrics] = None
    execution_time: Optional[float] = None
    superclause_routing: Dict[str, Any] = field(default_factory=dict)
    monkey1_orchestration: Dict[str, Any] = field(default_factory=dict)
    gary8d_execution: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StreamProgress:
    """Progress information for streaming events."""
    step: str
    percentage: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class StreamError:
    """Error information for streaming events."""
    message: str
    code: Optional[str] = None


@dataclass
class StreamEvent:
    """Streaming event data."""
    type: str  # 'start', 'progress', 'result', 'error', 'complete'
    data: Optional[Any] = None
    progress: Optional[StreamProgress] = None
    error: Optional[StreamError] = None


@dataclass
class UsageRequest:
    """Request model for usage metrics."""
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    granularity: str = "daily"
    include_details: bool = False

    def __post_init__(self):
        if self.granularity not in ['hourly', 'daily', 'weekly', 'monthly']:
            raise ValueError("Granularity must be one of: hourly, daily, weekly, monthly")


@dataclass
class HealthResponse:
    """Health check response model."""
    status: str
    version: str
    timestamp: str
    components: Dict[str, str]


@dataclass
class MonkeyCoderClientConfig:
    """Configuration for MonkeyCoderClient."""
    base_url: str = "http://localhost:8000"
    api_key: Optional[str] = None
    timeout: float = 300.0  # 5 minutes default
    retries: int = 3
    retry_delay: float = 1.0
    max_retry_delay: float = 10.0
    retry_condition: Optional[Callable[[Exception], bool]] = None
    on_retry: Optional[Callable[[int, Exception], None]] = None


# Exception classes
class MonkeyCoderError(Exception):
    """Base exception for Monkey Coder SDK errors."""
    
    def __init__(
        self, 
        message: str, 
        code: Optional[str] = None, 
        status_code: Optional[int] = None, 
        details: Optional[Any] = None
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details


class MonkeyCoderAPIError(MonkeyCoderError):
    """API-specific error."""
    pass


class MonkeyCoderNetworkError(MonkeyCoderError):
    """Network-related error."""
    pass


class MonkeyCoderStreamError(MonkeyCoderError):
    """Streaming-related error."""
    pass
