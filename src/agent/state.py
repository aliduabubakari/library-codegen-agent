from typing import TypedDict, List, Dict, Optional, Annotated
from langgraph.graph import add_messages


class AgentState(TypedDict):
    """State for the code generation agent."""
    
    # Input
    library_name: str
    task: str
    
    # Messages for conversation history
    messages: Annotated[list, add_messages]
    
    # Search and crawl results
    search_results: Optional[List[Dict]]
    crawled_documentation: Optional[Dict]
    github_info: Optional[Dict]
    code_examples: Optional[List[str]]
    
    # Context management
    indexed_content: Optional[List[str]]
    relevant_context: Optional[List[str]]
    context_summary: Optional[str]
    
    # Generation
    generated_code: Optional[str]
    explanation: Optional[str]
    
    # Metadata
    confidence_score: float
    iteration_count: int
    error_message: Optional[str]
    
    # Control flow
    next_action: Optional[str]