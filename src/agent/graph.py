from typing import Dict, Any
from langgraph.graph import StateGraph, END

from .state import AgentState
from .nodes import AgentNodes
from ..utils.logger import get_logger

logger = get_logger(__name__)


class CodeGenAgent:
    """Main agent for library code generation."""
    
    def __init__(self):
        self.nodes = AgentNodes()
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the agent workflow graph."""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("analyze_query", self.nodes.analyze_query)
        workflow.add_node("search_documentation", self.nodes.search_documentation)
        workflow.add_node("crawl_documentation", self.nodes.crawl_documentation)
        workflow.add_node("analyze_github", self.nodes.analyze_github)
        workflow.add_node("extract_examples", self.nodes.extract_examples)
        workflow.add_node("manage_context", self.nodes.manage_context)
        workflow.add_node("generate_code", self.nodes.generate_code)
        workflow.add_node("validate_code", self.nodes.validate_code)
        
        # Set entry point
        workflow.set_entry_point("analyze_query")
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "analyze_query",
            self.nodes.should_continue,
            {
                "search_documentation": "search_documentation",
                "end": END
            }
        )
        
        workflow.add_conditional_edges(
            "search_documentation",
            self.nodes.should_continue,
            {
                "crawl_documentation": "crawl_documentation",
                "analyze_github": "analyze_github",
                "end": END
            }
        )
        
        workflow.add_conditional_edges(
            "crawl_documentation",
            self.nodes.should_continue,
            {
                "analyze_github": "analyze_github",
                "end": END
            }
        )
        
        workflow.add_conditional_edges(
            "analyze_github",
            self.nodes.should_continue,
            {
                "extract_examples": "extract_examples",
                "end": END
            }
        )
        
        workflow.add_conditional_edges(
            "extract_examples",
            self.nodes.should_continue,
            {
                "manage_context": "manage_context",
                "end": END
            }
        )
        
        workflow.add_conditional_edges(
            "manage_context",
            self.nodes.should_continue,
            {
                "generate_code": "generate_code",
                "end": END
            }
        )
        
        workflow.add_conditional_edges(
            "generate_code",
            self.nodes.should_continue,
            {
                "validate_code": "validate_code",
                "end": END
            }
        )
        
        workflow.add_edge("validate_code", END)
        
        return workflow.compile()
    
    async def generate_code(
        self,
        library_name: str,
        task: str
    ) -> Dict[str, Any]:
        """Generate code for a library and task."""
        logger.info(f"Starting code generation for {library_name}: {task}")
        
        initial_state = {
            "library_name": library_name,
            "task": task,
            "messages": [],
            "iteration_count": 0,
            "confidence_score": 0.0,
        }
        
        result = await self.graph.ainvoke(initial_state)
        
        return {
            "code": result.get("generated_code"),
            "explanation": result.get("explanation"),
            "confidence": result.get("confidence_score"),
            "context_used": result.get("relevant_context"),
        }