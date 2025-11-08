import asyncio
from src.agent.graph import CodeGenAgent
from src.context.manager import ContextManager
from src.utils.logger import get_logger

logger = get_logger(__name__)


async def main():
    """Advanced usage with custom configuration."""
    # Initialize components
    agent = CodeGenAgent()
    context_manager = ContextManager()
    
    # Example 1: Generate code for data processing library
    print("\n" + "="*80)
    print("EXAMPLE 1: Data Processing Library")
    print("="*80)
    
    result1 = await agent.generate_code(
        library_name="polars",
        task="Read a CSV file, filter rows where age > 25, and compute the mean of a numeric column"
    )
    
    print(f"\nCode:\n{result1['code']}")
    print(f"\nConfidence: {result1['confidence']:.2f}")
    
    # Example 2: Generate code for ML library
    print("\n" + "="*80)
    print("EXAMPLE 2: Machine Learning Library")
    print("="*80)
    
    result2 = await agent.generate_code(
        library_name="xgboost",
        task="Train a binary classification model with cross-validation"
    )
    
    print(f"\nCode:\n{result2['code']}")
    print(f"\nConfidence: {result2['confidence']:.2f}")
    
    # Example 3: Check indexed content count
    count = await context_manager.db.count()
    print(f"\n\nTotal indexed chunks: {count}")
    
    # Clean up
    await context_manager.clear()


if __name__ == "__main__":
    asyncio.run(main())