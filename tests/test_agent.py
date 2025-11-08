import pytest
from src.agent.graph import CodeGenAgent
from src.agent.state import AgentState


@pytest.mark.asyncio
async def test_agent_initialization():
    """Test agent initialization."""
    agent = CodeGenAgent()
    assert agent is not None
    assert agent.graph is not None


@pytest.mark.asyncio
async def test_code_generation():
    """Test basic code generation."""
    agent = CodeGenAgent()
    
    result = await agent.generate_code(
        library_name="requests",
        task="Make a GET request to an API"
    )
    
    assert result is not None
    assert "code" in result
    assert result["code"] is not None
    assert result["confidence"] >= 0


@pytest.mark.asyncio
async def test_unknown_library():
    """Test handling of unknown library."""
    agent = CodeGenAgent()
    
    result = await agent.generate_code(
        library_name="nonexistent_library_xyz123",
        task="Do something"
    )
    
    # Should still return a result, but with lower confidence
    assert result is not None
    assert "code" in result