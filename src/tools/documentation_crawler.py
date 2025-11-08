from typing import Dict, Any, List, Optional
from tavily import TavilyClient

from .base import BaseTool
from ..utils.logger import get_logger
from config.settings import settings

logger = get_logger(__name__)


class DocumentationCrawler(BaseTool):
    """Tool for searching and crawling documentation."""
    
    def __init__(self):
        self.client = TavilyClient(api_key=settings.tavily_api_key)
    
    @property
    def name(self) -> str:
        return "documentation_crawler"
    
    @property
    def description(self) -> str:
        return "Searches for and crawls library documentation websites"
    
    async def search(
        self,
        library_name: str,
        task: Optional[str] = None,
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """Search for library documentation."""
        query = f"{library_name} python documentation tutorial"
        if task:
            query += f" {task}"
        
        logger.info(f"Searching with query: {query}")
        
        try:
            response = self.client.search(
                query=query,
                max_results=max_results,
                search_depth="advanced"
            )
            
            return response.get("results", [])
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []
    
    async def crawl(
        self,
        url: str,
        instructions: str,
        max_breadth: int = 20
    ) -> Dict[str, Any]:
        """Crawl a documentation website."""
        logger.info(f"Crawling URL: {url}")
        
        try:
            response = self.client.crawl(
                url=url,
                instructions=instructions,
                max_breadth=max_breadth,
                extract_depth="advanced"
            )
            
            return response
        except Exception as e:
            logger.error(f"Crawl error: {e}")
            return {}
    
    async def run(self, **kwargs: Any) -> Dict[str, Any]:
        """Execute search and crawl."""
        library_name = kwargs.get("library_name")
        task = kwargs.get("task")
        
        # Search first
        search_results = await self.search(library_name, task)
        
        # Crawl top result
        crawled_data = {}
        if search_results:
            top_url = search_results[0].get("url")
            if top_url:
                crawled_data = await self.crawl(
                    url=top_url,
                    instructions=f"Extract API documentation for {library_name}"
                )
        
        return {
            "search_results": search_results,
            "crawled_data": crawled_data
        }