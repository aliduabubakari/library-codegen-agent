import asyncio
from src.agent.graph import CodeGenAgent
from src.utils.logger import get_logger

logger = get_logger(__name__)


async def main():
    """Basic usage example."""
    # Initialize agent
    agent = CodeGenAgent()
    
    # Generate code for unknown library
    result = await agent.generate_code(
        library_name="semt",
        task="Load a CSV file and perform semantic type detection on the columns"
    )
    
    # Print results
    print("\n" + "="*80)
    print("GENERATED CODE:")
    print("="*80)
    print(result["code"])
    print("\n" + "="*80)
    print(f"CONFIDENCE: {result['confidence']:.2f}")
    print("="*80)
    
    if result.get("context_used"):
        print("\nCONTEXT SOURCES:")
        for i, context in enumerate(result["context_used"][:3], 1):
            print(f"\n{i}. {context[:200]}...")


if __name__ == "__main__":
    asyncio.run(main())