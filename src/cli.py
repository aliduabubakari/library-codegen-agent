import asyncio
import argparse
from src.agent.graph import CodeGenAgent
from src.utils.logger import get_logger

logger = get_logger(__name__)


def main():
    """Command line interface for the agent."""
    parser = argparse.ArgumentParser(
        description="Generate code for unknown Python libraries"
    )
    parser.add_argument(
        "library",
        help="Name of the Python library"
    )
    parser.add_argument(
        "task",
        help="Description of what you want to do"
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output file for generated code",
        default=None
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    async def run():
        agent = CodeGenAgent()
        
        print(f"\n🔍 Searching for documentation on '{args.library}'...")
        print(f"📝 Task: {args.task}\n")
        
        result = await agent.generate_code(
            library_name=args.library,
            task=args.task
        )
        
        print("\n" + "="*80)
        print("GENERATED CODE:")
        print("="*80)
        print(result["code"])
        print("\n" + "="*80)
        print(f"Confidence Score: {result['confidence']:.2%}")
        print("="*80)
        
        if args.output:
            with open(args.output, "w") as f:
                f.write(result["code"])
            print(f"\n✅ Code saved to {args.output}")
        
        if args.verbose and result.get("context_used"):
            print("\n📚 Context Sources Used:")
            for i, ctx in enumerate(result["context_used"][:3], 1):
                print(f"\n{i}. {ctx[:300]}...")
    
    asyncio.run(run())


if __name__ == "__main__":
    main()