# Library Code Generation Agent

An intelligent agent that generates Python code for unknown or poorly-documented libraries by automatically discovering and learning from documentation, GitHub repositories, and code examples.

## Features

- 🔍 **Automatic Documentation Discovery**: Searches and crawls library documentation using Tavily
- 📚 **GitHub Analysis**: Analyzes repository structure, READMEs, and code examples
- 🧠 **Semantic Context Management**: Uses embeddings and vector search for relevant context retrieval
- 🤖 **Azure OpenAI Integration**: Powered by GPT-5-mini with optimized prompting
- 📊 **SQLite Vector Database**: Efficient storage and retrieval of indexed content
- 🔄 **LangGraph Workflow**: Stateful agent orchestration with conditional routing
- 🛠️ **MCP Tool Protocol**: Standardized tool management and execution

## Architecture
```
┌─────────────────────────────────────────────────────────┐
│                  LangGraph Agent                        │
│  (analyze → search → crawl → index → generate)          │
└─────────────────────────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Tavily Tools │  │  GitHub API  │  │   Context    │
│   (Search/   │  │  (Analyzer)  │  │   Manager    │
│    Crawl)    │  │              │  │  (SQLite +   │
│              │  │              │  │  Embeddings) │
└──────────────┘  └──────────────┘  └──────────────┘
```

## Installation

### Prerequisites

- Python 3.10+
- Azure OpenAI API access
- Tavily API key

### Setup

1. **Clone the repository:**
```bash
git clone <repository-url>
cd library-codegen-agent
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables:**
```bash
cp .env.example .env
```

Edit `.env` with your API keys:
```env
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_KEY=your-api-key
AZURE_OPENAI_DEPLOYMENT=gpt-5-mini
TAVILY_API_KEY=your-tavily-key
```

5. **Initialize database:**
```bash
mkdir -p data
```

## Usage

### Basic Usage
```python
import asyncio
from src.agent.graph import CodeGenAgent

async def main():
    agent = CodeGenAgent()
    
    result = await agent.generate_code(
        library_name="semt",
        task="Load a CSV file and perform semantic type detection"
    )
    
    print(result["code"])
    print(f"Confidence: {result['confidence']}")

asyncio.run(main())
```

### Advanced Usage
```python
from src.agent.graph import CodeGenAgent
from src.context.manager import ContextManager

async def advanced_example():
    agent = CodeGenAgent()
    
    # Generate code with detailed context
    result = await agent.generate_code(
        library_name="polars",
        task="Read CSV, filter rows, compute statistics"
    )
    
    # Access context used
    for context in result.get("context_used", [])[:3]:
        print(f"Source: {context[:200]}...")
    
    # Check indexed content
    context_manager = ContextManager()
    count = await context_manager.db.count()
    print(f"Indexed chunks: {count}")
```

### Command Line
```bash
# Run basic example
python examples/basic_usage.py

# Run advanced examples
python examples/advanced_usage.py
```

## Project Structure
```
library-codegen-agent/
├── config/                 # Configuration and settings
│   ├── __init__.py
│   └── settings.py        # Pydantic settings with env vars
├── src/
│   ├── agent/             # Agent graph and nodes
│   │   ├── graph.py       # Main agent workflow
│   │   ├── nodes.py       # Individual node functions
│   │   └── state.py       # Agent state definition
│   ├── tools/             # Tool implementations
│   │   ├── documentation_crawler.py
│   │   ├── github_analyzer.py
│   │   ├── code_example_extractor.py
│   │   └── mcp_server.py
│   ├── context/           # Context management
│   │   ├── manager.py     # Main context manager
│   │   ├── chunker.py     # Semantic text chunking
│   │   ├── embeddings.py  # Embedding service
│   │   └── database.py    # SQLite vector DB
│   ├── llm/               # LLM integration
│   │   └── azure_client.py
│   └── utils/             # Utilities
│       ├── logger.py
│       └── helpers.py
├── tests/                 # Unit tests
├── examples/              # Usage examples
└── data/                  # Database storage
```

## Key Components

### 1. Agent Graph (LangGraph)

The agent uses a stateful graph workflow:
```python
analyze_query → search_docs → crawl_docs → analyze_github 
    → extract_examples → manage_context → generate_code → validate
```

Each node can conditionally route to the next based on state.

### 2. Tools (MCP Protocol)

- **DocumentationCrawler**: Searches and crawls documentation using Tavily
- **GitHubAnalyzer**: Fetches repository structure and READMEs
- **CodeExampleExtractor**: Extracts code snippets from various sources

### 3. Context Management

- **SemanticChunker**: Splits text by semantic boundaries (paragraphs, functions)
- **EmbeddingService**: Generates embeddings using sentence-transformers
- **VectorDatabase**: SQLite-based vector storage with cosine similarity search

### 4. Azure OpenAI Client

Configured for Azure with:
- Fixed temperature = 1.0 (Azure requirement)
- `max_completion_tokens` instead of `max_tokens`
- Proper message format conversion

## Configuration

All settings are in `config/settings.py` and can be overridden via environment variables:
```python
# Azure OpenAI
AZURE_OPENAI_ENDPOINT=...
AZURE_OPENAI_KEY=...
AZURE_OPENAI_DEPLOYMENT=gpt-5-mini
AZURE_OPENAI_API_VERSION=2024-12-01-preview

# Tavily
TAVILY_API_KEY=...

# Agent Configuration
MAX_ITERATIONS=10
MAX_CONTEXT_TOKENS=8000
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K_RESULTS=5
TEMPERATURE=1.0  # Fixed for Azure
```

## Testing

Run all tests:
```bash
pytest tests/ -v
```

Run specific test file:
```bash
pytest tests/test_agent.py -v
```

Run with coverage:
```bash
pytest tests/ --cov=src --cov-report=html
```

## Workflow Example

For the query: `"Use semt library to detect semantic types in a CSV file"`

1. **analyze_query**: Determines need for documentation and examples
2. **search_documentation**: Searches for "semt python documentation"
3. **crawl_documentation**: Crawls top result (e.g., semt docs site)
4. **analyze_github**: Fetches GitHub repo, README, structure
5. **extract_examples**: Extracts code snippets from all sources
6. **manage_context**: 
   - Chunks all content semantically
   - Generates embeddings
   - Stores in SQLite vector DB
   - Retrieves top-k relevant chunks for query
7. **generate_code**: Uses Azure OpenAI with context to generate code
8. **validate_code**: Basic validation and confidence scoring

## Advanced Features

### Custom Chunking Strategy
```python
from src.context.chunker import SemanticChunker

chunker = SemanticChunker(
    chunk_size=1500,
    chunk_overlap=300
)

chunks = chunker.chunk_text(long_text)
```

### Direct Context Retrieval
```python
from src.context.manager import ContextManager

manager = ContextManager()

# Index custom content
await manager.index_content(
    documentation={"results": [...]},
    code_examples=[...]
)

# Retrieve relevant context
contexts = await manager.retrieve_relevant_context(
    query="How to load CSV?",
    library_name="pandas",
    top_k=5
)
```

### Custom Tool Integration
```python
from src.tools.base import BaseTool

class CustomTool(BaseTool):
    @property
    def name(self) -> str:
        return "custom_tool"
    
    @property
    def description(self) -> str:
        return "My custom tool"
    
    async def run(self, **kwargs):
        # Implementation
        return {"result": "..."}

# Register with MCP server
from src.tools.mcp_server import MCPServer

server = MCPServer()
server.register_tool(CustomTool())
```

## Troubleshooting

### Issue: "No documentation found"

**Solution**: The library may not have online docs. The agent will fall back to GitHub analysis and code extraction.

### Issue: "Context too large"

**Solution**: Adjust `MAX_CONTEXT_TOKENS` in settings or improve chunking:
```python
# config/settings.py
MAX_CONTEXT_TOKENS=6000  # Reduce if hitting limits
```

### Issue: "Low confidence score"

**Causes**:
- Library not found in any source
- Very sparse documentation
- Task too complex

**Solutions**:
- Provide more specific library name
- Break down complex tasks
- Check if library exists and is spelled correctly

### Issue: Azure OpenAI Rate Limits

**Solution**: Add retry logic or reduce request frequency:
```python
from tenacity import retry, wait_exponential

@retry(wait=wait_exponential(min=1, max=60))
async def generate_with_retry(...):
    return await llm.generate(...)
```

## Performance Optimization

### 1. Caching

Cache frequently accessed documentation:
```python
# In src/tools/documentation_crawler.py
import functools
from cachetools import TTLCache

cache = TTLCache(maxsize=100, ttl=3600)

@functools.lru_cache(maxsize=128)
async def search(self, library_name: str, ...):
    # Implementation
```

### 2. Parallel Tool Execution

Execute independent tools in parallel:
```python
import asyncio

async def parallel_gather(self, state):
    results = await asyncio.gather(
        self.search_documentation(state),
        self.analyze_github(state),
        return_exceptions=True
    )
    return results
```

### 3. Batch Embedding Generation

Process multiple texts at once:
```python
# Already implemented in embeddings.py
embeddings = await embedding_service.embed_texts(texts)
```

## Roadmap

- [ ] Add support for more programming languages
- [ ] Implement code validation and testing
- [ ] Add interactive refinement loop
- [ ] Support for private GitHub repositories
- [ ] Web UI for easier interaction
- [ ] Docker containerization
- [ ] Integration with VSCode extension
- [ ] Support for API documentation formats (OpenAPI, etc.)
- [ ] Code explanation and documentation generation
- [ ] Multi-turn conversation for iterative refinement

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup
```bash
# Install dev dependencies
pip install -e ".[dev]"

# Format code
black src/ tests/
isort src/ tests/

# Type checking
mypy src/

# Linting
flake8 src/ tests/
```

## License

MIT License - see LICENSE file for details

## Acknowledgments

- [LangGraph](https://github.com/langchain-ai/langgraph) for agent orchestration
- [Tavily](https://tavily.com) for web search and crawling
- [Sentence Transformers](https://www.sbert.net/) for embeddings
- Azure OpenAI for language model capabilities

## Contact

For questions or support, please open an issue on GitHub.

## Citation

If you use this project in your research, please cite:
```bibtex
@software{library_codegen_agent,
  title={Library Code Generation Agent},
  author={Alidu Abubakari},
  year={2024},
  url={https://github.com/aliduabubakari/library-codegen-agent.git}
}
```