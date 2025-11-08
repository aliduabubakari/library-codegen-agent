import re
from typing import Dict, Any, List
from .base import BaseTool
from ..utils.logger import get_logger

logger = get_logger(__name__)


class CodeExampleExtractor(BaseTool):
    """Tool for extracting code examples from various sources."""
    
    @property
    def name(self) -> str:
        return "code_example_extractor"
    
    @property
    def description(self) -> str:
        return "Extracts Python code examples from documentation and repositories"
    
    def extract_from_markdown(self, text: str) -> List[str]:
        """Extract code blocks from markdown."""
        # Match ```python or ``` code blocks
        pattern = r"```(?:python)?\n(.*?)```"
        matches = re.findall(pattern, text, re.DOTALL)
        return [match.strip() for match in matches if match.strip()]
    
    def extract_from_html(self, html: str) -> List[str]:
        """Extract code from HTML."""
        # Simple extraction - can be enhanced with BeautifulSoup
        pattern = r"<code[^>]*>(.*?)</code>"
        matches = re.findall(pattern, html, re.DOTALL)
        
        # Filter for Python-like code
        python_code = []
        for match in matches:
            clean = match.strip()
            if any(keyword in clean for keyword in ["import ", "def ", "class ", "="]):
                python_code.append(clean)
        
        return python_code
    
    async def extract(
        self,
        crawled_data: Dict[str, Any] = None,
        github_info: Dict[str, Any] = None
    ) -> List[str]:
        """Extract code examples from all sources."""
        logger.info("Extracting code examples")
        
        examples = []
        
        # Extract from crawled documentation
        if crawled_data:
            results = crawled_data.get("results", [])
            for result in results:
                content = result.get("content", "")
                examples.extend(self.extract_from_markdown(content))
                examples.extend(self.extract_from_html(content))
        
        # Extract from GitHub README
        if github_info and github_info.get("readme"):
            readme = github_info["readme"]
            examples.extend(self.extract_from_markdown(readme))
        
        # Deduplicate and filter
        unique_examples = list(set(examples))
        
        # Filter out very short snippets
        filtered = [ex for ex in unique_examples if len(ex) > 50]
        
        logger.info(f"Extracted {len(filtered)} code examples")
        return filtered
    
    async def run(self, **kwargs: Any) -> Dict[str, Any]:
        """Execute example extraction."""
        crawled_data = kwargs.get("crawled_data")
        github_info = kwargs.get("github_info")
        
        examples = await self.extract(crawled_data, github_info)
        
        return {"examples": examples}