"""Utility functions."""

import re
from typing import Optional


def count_chinese_chars(text: str) -> int:
    """Count Chinese characters in text.
    
    Args:
        text: Input text
        
    Returns:
        Number of Chinese characters
    """
    return sum(1 for c in text if '\u4e00' <= c <= '\u9fff')


def count_english_words(text: str) -> int:
    """Count English words in text.
    
    Args:
        text: Input text
        
    Returns:
        Number of English words
    """
    return len(re.findall(r'[a-zA-Z]+', text))


def count_words(text: str) -> int:
    """Count total words (Chinese + English) in text.
    
    Args:
        text: Input text
        
    Returns:
        Total word count
    """
    return count_chinese_chars(text) + count_english_words(text)


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to max length.
    
    Args:
        text: Input text
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def format_number(num: int) -> str:
    """Format number with Chinese units.
    
    Args:
        num: Number to format
        
    Returns:
        Formatted string
    """
    if num < 10000:
        return str(num)
    elif num < 100000000:
        return f"{num / 10000:.1f}万"
    else:
        return f"{num / 100000000:.1f}亿"


def clean_text(text: str) -> str:
    """Clean text by removing extra whitespace.
    
    Args:
        text: Input text
        
    Returns:
        Cleaned text
    """
    # Normalize line breaks
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")
    
    # Remove multiple consecutive blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Remove leading/trailing whitespace per line
    lines = [line.strip() for line in text.split('\n')]
    
    # Remove empty lines at start and end
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()
    
    return '\n'.join(lines)


def extract_numbers(text: str) -> list[int]:
    """Extract all numbers from text.
    
    Args:
        text: Input text
        
    Returns:
        List of numbers
    """
    return [int(n) for n in re.findall(r'\d+', text)]


def is_chinese(text: str) -> bool:
    """Check if text is primarily Chinese.
    
    Args:
        text: Input text
        
    Returns:
        True if primarily Chinese
    """
    chinese_count = count_chinese_chars(text)
    return chinese_count > len(text) / 2


def split_paragraphs(text: str) -> list[str]:
    """Split text into paragraphs.
    
    Args:
        text: Input text
        
    Returns:
        List of paragraphs
    """
    # Normalize
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")
    
    # Split
    paragraphs = text.split('\n')
    
    # Clean
    paragraphs = [p.strip() for p in paragraphs if p.strip()]
    
    return paragraphs
