from typing import Dict, Any, List
from .base import BaseTool
from .documentation_crawler import DocumentationCrawler
from .github_analyzer import GitHubAnalyzer
from .code_example_extractor import CodeExampleExtractor


class MCPServer:
    """Model Context Protocol server for managing tools."""
    
    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}
        self._register_default_tools()
    
    def _register_default_tools(self):
        """Register default tools."""
        self.register_tool(DocumentationCrawler())
        self.register_tool(GitHubAnalyzer())
        self.register_tool(CodeExampleExtractor())
    
    def register_tool(self, tool: BaseTool):
        """Register a new tool."""
        self.tools[tool.name] = tool
    
    def get_tool(self, name: str) -> BaseTool:
        """Get a tool by name."""
        return self.tools.get(name)
    
    def list_tools(self) -> List[Dict[str, str]]:
        """List all available tools."""
        return [
            {
                "name": tool.name,
                "description": tool.description
            }
            for tool in self.tools.values()
        ]
    
    async def execute_tool(self, tool_name: str, **kwargs: Any) -> Dict[str, Any]:
        """Execute a tool by name."""
        tool = self.get_tool(tool_name)
        if not tool:
            raise ValueError(f"Tool '{tool_name}' not found")
        
        return await tool.run(**kwargs)