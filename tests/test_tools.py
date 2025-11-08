import pytest
from src.tools.documentation_crawler import DocumentationCrawler
from src.tools.code_example_extractor import CodeExampleExtractor


@pytest.mark.asyncio
async def test_documentation_search():
    """Test documentation search."""
    crawler = DocumentationCrawler()
    
    results = await crawler.search(
        library_name="pandas",
        max_results=3
    )
    
    assert results is not None
    assert isinstance(results, list)


@pytest.mark.asyncio
async def test_code_extraction():
    """Test code example extraction."""
    extractor = CodeExampleExtractor()
    
    sample_markdown = """
    # Example
```python
    import pandas as pd
    df = pd.read_csv('data.csv')
    print(df.head())
```
    """
    
    examples = extractor.extract_from_markdown(sample_markdown)
    
    assert len(examples) > 0
    assert "pandas" in examples[0]