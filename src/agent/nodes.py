import asyncio
from typing import Dict, Any
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from ..tools.documentation_crawler import DocumentationCrawler
from ..tools.github_analyzer import GitHubAnalyzer
from ..tools.code_example_extractor import CodeExampleExtractor
from ..context.manager import ContextManager
from ..llm.azure_client import AzureLLMClient
from ..utils.logger import get_logger

logger = get_logger(__name__)


class AgentNodes:
    """Node functions for the agent graph."""
    
    def __init__(self):
        self.doc_crawler = DocumentationCrawler()
        self.github_analyzer = GitHubAnalyzer()
        self.example_extractor = CodeExampleExtractor()
        self.context_manager = ContextManager()
        self.llm_client = AzureLLMClient()
    
    async def analyze_query(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the user query to determine what information is needed."""
        logger.info(f"Analyzing query for library: {state['library_name']}")
        
        system_prompt = """You are an expert at analyzing code generation requests.
Determine what information would be needed to generate code for an unknown library.
Consider: documentation, API references, code examples, GitHub repository."""
        
        analysis_prompt = f"""
Library: {state['library_name']}
Task: {state['task']}

What information should we gather? Respond with a JSON object containing:
- needs_documentation: bool
- needs_github_analysis: bool
- needs_code_examples: bool
- search_query: str (optimized search query for documentation)
"""
        
        response = await self.llm_client.generate(
            messages=[
                SystemMessage(content=system_prompt),
                HumanMessage(content=analysis_prompt)
            ]
        )
        
        # Parse response (simplified - add proper JSON parsing)
        state["messages"] = [HumanMessage(content=analysis_prompt), AIMessage(content=response)]
        state["next_action"] = "search_documentation"
        
        return state
    
    async def search_documentation(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Search for library documentation."""
        logger.info(f"Searching documentation for: {state['library_name']}")
        
        search_results = await self.doc_crawler.search(
            library_name=state["library_name"],
            task=state["task"]
        )
        
        state["search_results"] = search_results
        state["next_action"] = "crawl_documentation"
        
        return state
    
    async def crawl_documentation(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Crawl documentation websites."""
        logger.info("Crawling documentation")
        
        if not state.get("search_results"):
            state["next_action"] = "analyze_github"
            return state
        
        # Get top result
        top_url = state["search_results"][0].get("url")
        if not top_url:
            state["next_action"] = "analyze_github"
            return state
        
        crawled_data = await self.doc_crawler.crawl(
            url=top_url,
            instructions=f"Extract API documentation and usage examples for {state['library_name']}"
        )
        
        state["crawled_documentation"] = crawled_data
        state["next_action"] = "analyze_github"
        
        return state
    
    async def analyze_github(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze GitHub repository."""
        logger.info(f"Analyzing GitHub for: {state['library_name']}")
        
        github_info = await self.github_analyzer.analyze(
            library_name=state["library_name"]
        )
        
        state["github_info"] = github_info
        state["next_action"] = "extract_examples"
        
        return state
    
    async def extract_examples(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Extract code examples."""
        logger.info("Extracting code examples")
        
        examples = await self.example_extractor.extract(
            crawled_data=state.get("crawled_documentation"),
            github_info=state.get("github_info")
        )
        
        state["code_examples"] = examples
        state["next_action"] = "manage_context"
        
        return state
    
    async def manage_context(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Manage and optimize context."""
        logger.info("Managing context")
        
        # Index all collected information
        await self.context_manager.index_content(
            documentation=state.get("crawled_documentation"),
            github_info=state.get("github_info"),
            code_examples=state.get("code_examples")
        )
        
        # Retrieve most relevant context
        relevant_context = await self.context_manager.retrieve_relevant_context(
            query=state["task"],
            library_name=state["library_name"]
        )
        
        state["relevant_context"] = relevant_context
        state["next_action"] = "generate_code"
        
        return state
    
    async def generate_code(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate code based on collected context."""
        logger.info("Generating code")
        
        system_prompt = """You are an expert Python developer. Generate clean, working code
based on the provided documentation and examples. Include proper error handling and comments."""
        
        context_text = "\n\n".join(state.get("relevant_context", []))
        
        generation_prompt = f"""
Library: {state['library_name']}
Task: {state['task']}

Available Documentation and Examples:
{context_text}

Generate Python code to accomplish the task. Include:
1. Required imports
2. Main implementation
3. Example usage
4. Brief explanation of how it works
"""
        
        response = await self.llm_client.generate(
            messages=[
                SystemMessage(content=system_prompt),
                HumanMessage(content=generation_prompt)
            ]
        )
        
        state["generated_code"] = response
        state["messages"].append(AIMessage(content=response))
        state["next_action"] = "validate_code"
        
        return state
    
    async def validate_code(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Validate generated code."""
        logger.info("Validating generated code")
        
        # Basic validation (can be extended)
        code = state.get("generated_code", "")
        
        # Check if code contains the library name
        if state["library_name"].lower() not in code.lower():
            state["confidence_score"] = 0.3
            state["error_message"] = "Generated code may not use the specified library"
        else:
            state["confidence_score"] = 0.8
        
        state["next_action"] = "end"
        
        return state
    
    def should_continue(self, state: Dict[str, Any]) -> str:
        """Determine next step in the graph."""
        next_action = state.get("next_action", "end")
        
        if state.get("iteration_count", 0) >= 10:
            return "end"
        
        return next_action