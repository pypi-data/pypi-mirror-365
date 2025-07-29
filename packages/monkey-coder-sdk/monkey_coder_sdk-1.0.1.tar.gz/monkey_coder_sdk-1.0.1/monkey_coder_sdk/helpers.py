"""
Helper functions for common use cases with the Monkey Coder SDK.

This module provides convenience functions to create common request configurations
and simplify the SDK usage for typical scenarios.
"""

from typing import List, Optional, Dict
from .types import (
    ExecuteRequest,
    ExecutionContext,
    SuperClaudeConfig,
    Monkey1Config,
    Gary8DConfig,
    TaskType,
    PersonaType,
    ProviderType,
    FileData,
)


def create_execute_request(
    task_type: TaskType,
    prompt: str,
    context: ExecutionContext,
    persona: PersonaType = PersonaType.DEVELOPER,
    **kwargs
) -> ExecuteRequest:
    """
    Create a basic ExecuteRequest with common defaults.
    
    Args:
        task_type: Type of task to execute
        prompt: Task prompt or description
        context: Execution context
        persona: SuperClaude persona type
        **kwargs: Additional ExecuteRequest fields
    
    Returns:
        ExecuteRequest object
    """
    superclause_config = SuperClaudeConfig(persona=persona)
    
    return ExecuteRequest(
        task_type=task_type,
        prompt=prompt,
        context=context,
        superclause_config=superclause_config,
        **kwargs
    )


def create_code_generation_request(
    prompt: str,
    user_id: str,
    language: Optional[str] = None,
    temperature: float = 0.1,
    max_tokens: int = 4096,
    **kwargs
) -> ExecuteRequest:
    """
    Create a code generation request with sensible defaults.
    
    Args:
        prompt: Code generation prompt
        user_id: User identifier
        language: Programming language (optional)
        temperature: Model temperature (0.0-2.0)
        max_tokens: Maximum tokens to generate
        **kwargs: Additional ExecuteRequest fields
    
    Returns:
        ExecuteRequest configured for code generation
    """
    context = ExecutionContext(
        user_id=user_id,
        temperature=temperature,
        max_tokens=max_tokens
    )
    
    # Add language to prompt if specified
    full_prompt = prompt
    if language:
        full_prompt = f"Generate {language} code: {prompt}"
    
    return create_execute_request(
        task_type=TaskType.CODE_GENERATION,
        prompt=full_prompt,
        context=context,
        persona=PersonaType.DEVELOPER,
        **kwargs
    )


def create_code_review_request(
    prompt: str,
    user_id: str,
    files: List[FileData],
    focus_areas: Optional[List[str]] = None,
    **kwargs
) -> ExecuteRequest:
    """
    Create a code review request with files and optional focus areas.
    
    Args:
        prompt: Review prompt or instructions
        user_id: User identifier
        files: List of files to review
        focus_areas: Optional list of focus areas (e.g., ['security', 'performance'])
        **kwargs: Additional ExecuteRequest fields
    
    Returns:
        ExecuteRequest configured for code review
    """
    context = ExecutionContext(user_id=user_id)
    
    # Enhance prompt with focus areas if provided
    full_prompt = prompt
    if focus_areas:
        focus_text = ", ".join(focus_areas)
        full_prompt = f"{prompt}\n\nPlease focus on: {focus_text}"
    
    return create_execute_request(
        task_type=TaskType.CODE_REVIEW,
        prompt=full_prompt,
        context=context,
        persona=PersonaType.REVIEWER,
        files=files,
        **kwargs
    )


def create_documentation_request(
    prompt: str,
    user_id: str,
    files: Optional[List[FileData]] = None,
    doc_type: str = "API documentation",
    **kwargs
) -> ExecuteRequest:
    """
    Create a documentation generation request.
    
    Args:
        prompt: Documentation prompt
        user_id: User identifier
        files: Optional files to document
        doc_type: Type of documentation to generate
        **kwargs: Additional ExecuteRequest fields
    
    Returns:
        ExecuteRequest configured for documentation
    """
    context = ExecutionContext(user_id=user_id)
    
    full_prompt = f"Generate {doc_type}: {prompt}"
    
    return create_execute_request(
        task_type=TaskType.DOCUMENTATION,
        prompt=full_prompt,
        context=context,
        persona=PersonaType.TECHNICAL_WRITER,
        files=files,
        **kwargs
    )


def create_security_analysis_request(
    prompt: str,
    user_id: str,
    files: List[FileData],
    security_standards: Optional[List[str]] = None,
    **kwargs
) -> ExecuteRequest:
    """
    Create a security analysis request.
    
    Args:
        prompt: Security analysis prompt
        user_id: User identifier
        files: Files to analyze for security issues
        security_standards: Optional security standards to check against
        **kwargs: Additional ExecuteRequest fields
    
    Returns:
        ExecuteRequest configured for security analysis
    """
    context = ExecutionContext(user_id=user_id)
    
    full_prompt = f"Perform security analysis: {prompt}"
    if security_standards:
        standards_text = ", ".join(security_standards)
        full_prompt += f"\n\nCheck against standards: {standards_text}"
    
    return create_execute_request(
        task_type=TaskType.CODE_ANALYSIS,
        prompt=full_prompt,
        context=context,
        persona=PersonaType.SECURITY_ANALYST,
        files=files,
        **kwargs
    )


def create_testing_request(
    prompt: str,
    user_id: str,
    files: List[FileData],
    test_framework: Optional[str] = None,
    coverage_target: Optional[float] = None,
    **kwargs
) -> ExecuteRequest:
    """
    Create a test generation request.
    
    Args:
        prompt: Testing prompt
        user_id: User identifier
        files: Files to generate tests for
        test_framework: Preferred testing framework
        coverage_target: Target test coverage percentage
        **kwargs: Additional ExecuteRequest fields
    
    Returns:
        ExecuteRequest configured for test generation
    """
    context = ExecutionContext(user_id=user_id)
    
    full_prompt = f"Generate tests: {prompt}"
    if test_framework:
        full_prompt += f"\n\nUse testing framework: {test_framework}"
    if coverage_target:
        full_prompt += f"\n\nTarget coverage: {coverage_target}%"
    
    return create_execute_request(
        task_type=TaskType.TESTING,
        prompt=full_prompt,
        context=context,
        persona=PersonaType.TESTER,
        files=files,
        **kwargs
    )


def create_performance_optimization_request(
    prompt: str,
    user_id: str,
    files: List[FileData],
    performance_metrics: Optional[List[str]] = None,
    **kwargs
) -> ExecuteRequest:
    """
    Create a performance optimization request.
    
    Args:
        prompt: Performance optimization prompt
        user_id: User identifier
        files: Files to optimize
        performance_metrics: Metrics to focus on (e.g., ['latency', 'memory', 'throughput'])
        **kwargs: Additional ExecuteRequest fields
    
    Returns:
        ExecuteRequest configured for performance optimization
    """
    context = ExecutionContext(user_id=user_id)
    
    full_prompt = f"Optimize performance: {prompt}"
    if performance_metrics:
        metrics_text = ", ".join(performance_metrics)
        full_prompt += f"\n\nFocus on: {metrics_text}"
    
    return create_execute_request(
        task_type=TaskType.REFACTORING,
        prompt=full_prompt,
        context=context,
        persona=PersonaType.PERFORMANCE_EXPERT,
        files=files,
        **kwargs
    )


def create_multi_agent_config(
    agent_count: int = 3,
    coordination_strategy: str = "collaborative",
    consensus_threshold: float = 0.7,
    enable_reflection: bool = True,
    max_iterations: int = 5
) -> Monkey1Config:
    """
    Create a multi-agent configuration for complex tasks.
    
    Args:
        agent_count: Number of agents to use
        coordination_strategy: How agents coordinate
        consensus_threshold: Threshold for agent consensus
        enable_reflection: Whether agents can reflect on results
        max_iterations: Maximum orchestration iterations
    
    Returns:
        Monkey1Config object
    """
    return Monkey1Config(
        agent_count=agent_count,
        coordination_strategy=coordination_strategy,
        consensus_threshold=consensus_threshold,
        enable_reflection=enable_reflection,
        max_iterations=max_iterations
    )


def create_quantum_config(
    parallel_futures: bool = True,
    collapse_strategy: str = "weighted_average",
    quantum_coherence: float = 0.8,
    execution_branches: int = 3,
    uncertainty_threshold: float = 0.1
) -> Gary8DConfig:
    """
    Create a quantum execution configuration.
    
    Args:
        parallel_futures: Enable parallel execution
        collapse_strategy: Strategy for quantum collapse
        quantum_coherence: Coherence level (0.0-1.0)
        execution_branches: Number of execution branches
        uncertainty_threshold: Threshold for uncertainty handling
    
    Returns:
        Gary8DConfig object
    """
    return Gary8DConfig(
        parallel_futures=parallel_futures,
        collapse_strategy=collapse_strategy,
        quantum_coherence=quantum_coherence,
        execution_branches=execution_branches,
        uncertainty_threshold=uncertainty_threshold
    )


def create_file_data(file_path: str, content: str, file_type: Optional[str] = None) -> FileData:
    """
    Create a FileData object from file path and content.
    
    Args:
        file_path: Path to the file
        content: File content
        file_type: Optional file type/extension
    
    Returns:
        FileData object
    """
    if not file_type and '.' in file_path:
        file_type = file_path.split('.')[-1]
    
    return FileData(path=file_path, content=content, type=file_type)
