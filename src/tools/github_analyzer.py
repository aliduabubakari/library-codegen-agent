import aiohttp
from typing import Dict, Any, Optional
from .base import BaseTool
from ..utils.logger import get_logger

logger = get_logger(__name__)


class GitHubAnalyzer(BaseTool):
    """Tool for analyzing GitHub repositories."""
    
    @property
    def name(self) -> str:
        return "github_analyzer"
    
    @property
    def description(self) -> str:
        return "Analyzes GitHub repositories to extract structure and examples"
    
    async def search_repository(self, library_name: str) -> Optional[str]:
        """Search for the library's GitHub repository."""
        url = f"https://api.github.com/search/repositories?q={library_name}+language:python&sort=stars&order=desc"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        items = data.get("items", [])
                        if items:
                            return items[0].get("html_url")
        except Exception as e:
            logger.error(f"GitHub search error: {e}")
        
        return None
    
    async def get_readme(self, repo_url: str) -> Optional[str]:
        """Fetch repository README."""
        # Extract owner/repo from URL
        parts = repo_url.rstrip("/").split("/")
        if len(parts) < 2:
            return None
        
        owner, repo = parts[-2], parts[-1]
        url = f"https://api.github.com/repos/{owner}/{repo}/readme"
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Accept": "application/vnd.github.v3.raw"}
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        return await response.text()
        except Exception as e:
            logger.error(f"README fetch error: {e}")
        
        return None
    
    async def get_repository_structure(self, repo_url: str) -> Dict[str, Any]:
        """Get basic repository structure."""
        parts = repo_url.rstrip("/").split("/")
        if len(parts) < 2:
            return {}
        
        owner, repo = parts[-2], parts[-1]
        url = f"https://api.github.com/repos/{owner}/{repo}/contents"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        contents = await response.json()
                        return {
                            "files": [item["name"] for item in contents],
                            "has_examples": any("example" in item["name"].lower() for item in contents),
                            "has_docs": any("doc" in item["name"].lower() for item in contents)
                        }
        except Exception as e:
            logger.error(f"Structure fetch error: {e}")
        
        return {}
    
    async def analyze(self, library_name: str) -> Dict[str, Any]:
        """Analyze a library's GitHub repository."""
        logger.info(f"Analyzing GitHub for: {library_name}")
        
        repo_url = await self.search_repository(library_name)
        if not repo_url:
            return {"found": False}
        
        readme = await self.get_readme(repo_url)
        structure = await self.get_repository_structure(repo_url)
        
        return {
            "found": True,
            "repository_url": repo_url,
            "readme": readme,
            "structure": structure
        }
    
    async def run(self, **kwargs: Any) -> Dict[str, Any]:
        """Execute GitHub analysis."""
        library_name = kwargs.get("library_name")
        return await self.analyze(library_name)