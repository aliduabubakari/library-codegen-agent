import re
from typing import List


def truncate_text(text: str, max_length: int = 1000) -> str:
    """Truncate text to maximum length."""
    if len(text) <= max_length:
        return text
    
    return text[:max_length] + "..."


def extract_urls(text: str) -> List[str]:
    """Extract URLs from text."""
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    return re.findall(url_pattern, text)


def clean_code(code: str) -> str:
    """Clean and format code string."""
    # Remove markdown code fences
    code = re.sub(r'```python\n?', '', code)
    code = re.sub(r'```\n?', '', code)
    
    # Remove extra whitespace
    lines = [line.rstrip() for line in code.split('\n')]
    
    # Remove leading/trailing empty lines
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()
    
    return '\n'.join(lines)


def estimate_tokens(text: str) -> int:
    """Rough token estimation."""
    # Approximate: 1 token ≈ 4 characters for English text
    return len(text) // 4


def format_context(contexts: List[str], max_length: int = 10000) -> str:
    """Format multiple context pieces into a single string."""
    formatted = []
    current_length = 0
    
    for i, context in enumerate(contexts, 1):
        header = f"\n--- Context {i} ---\n"
        piece = header + context + "\n"
        
        piece_length = len(piece)
        if current_length + piece_length > max_length:
            break
        
        formatted.append(piece)
        current_length += piece_length
    
    return ''.join(formatted)