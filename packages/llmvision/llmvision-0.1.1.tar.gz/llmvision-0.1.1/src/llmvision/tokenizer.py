from typing import List, Protocol, Dict, Optional, Tuple
import re
import regex
import unicodedata
from collections import Counter
import json


class Tokenizer(Protocol):
    def tokenize(self, text: str) -> List[str]:
        ...


class SimpleTokenizer:
    def tokenize(self, text: str) -> List[str]:
        # Use regex for better Unicode support (handles grapheme clusters)
        pattern = r'(\w+|[^\w\s]|\s+)'
        tokens = regex.findall(pattern, text)
        return [token for token in tokens if token.strip() or token.isspace()]


class WordTokenizer:
    def tokenize(self, text: str) -> List[str]:
        return text.split()


class CharTokenizer:
    def tokenize(self, text: str) -> List[str]:
        return list(text)


def visualize_tokens(
    tokens: List[str], 
    separator: str = "│",
    show_indices: bool = False,
    highlight_spaces: bool = True,
    max_width: Optional[int] = None
) -> str:
    escaped_tokens = []
    
    for i, token in enumerate(tokens):
        # Handle special characters
        if token == "\n":
            display = "⏎" if highlight_spaces else "\\n"
        elif token == "\t":
            display = "⇥" if highlight_spaces else "\\t"
        elif token == "\r":
            display = "⏎" if highlight_spaces else "\\r"
        elif token == " ":
            display = "␣" if highlight_spaces else " "
        elif token == "\\":
            display = "\\\\"
        elif len(token) == 1:
            category = unicodedata.category(token)
            if category.startswith('C'):  # Control characters
                display = f"\\u{ord(token):04x}"
            elif category == 'Zs':  # Various Unicode spaces
                display = "⎵" if highlight_spaces else token
            elif category == 'Cf':  # Format characters (like ZWJ)
                display = f"\\u{ord(token):04x}"
            else:
                display = token
        else:
            display = token
        
        if show_indices:
            display = f"{i}:{display}"
        
        escaped_tokens.append(display)
    
    result = separator.join(escaped_tokens)
    
    # Truncate if max_width is specified
    if max_width and len(result) > max_width:
        result = result[:max_width-3] + "..."
    
    return result


class GraphemeTokenizer:
    """Tokenizes text into grapheme clusters (user-perceived characters)."""
    def tokenize(self, text: str) -> List[str]:
        # Use regex to split on grapheme boundaries
        return regex.findall(r'\X', text)


class SubwordTokenizer:
    """Simple subword tokenizer that splits on common prefixes/suffixes."""
    def __init__(self, min_length: int = 3):
        self.min_length = min_length
        self.common_prefixes = {'un', 're', 'pre', 'dis', 'over', 'under', 'mis'}
        self.common_suffixes = {'ing', 'ed', 'er', 'est', 'ly', 'tion', 'ment'}
    
    def tokenize(self, text: str) -> List[str]:
        # First split like SimpleTokenizer
        simple = SimpleTokenizer()
        word_tokens = simple.tokenize(text)
        
        result = []
        for token in word_tokens:
            if len(token) <= self.min_length or not token.isalpha():
                result.append(token)
                continue
            
            # Try to split on common patterns
            parts = self._split_subwords(token.lower())
            if len(parts) > 1:
                result.extend(parts)
            else:
                result.append(token)
        
        return result
    
    def _split_subwords(self, word: str) -> List[str]:
        # Check for common prefixes
        for prefix in self.common_prefixes:
            if word.startswith(prefix) and len(word) > len(prefix) + 2:
                return [prefix, word[len(prefix):]]
        
        # Check for common suffixes
        for suffix in self.common_suffixes:
            if word.endswith(suffix) and len(word) > len(suffix) + 2:
                return [word[:-len(suffix)], suffix]
        
        return [word]


def analyze_tokens(tokens: List[str]) -> Dict[str, any]:
    """Analyze tokenization statistics."""
    total = len(tokens)
    if total == 0:
        return {'total': 0}
    
    # Count character types
    char_count = sum(len(t) for t in tokens)
    unique_tokens = len(set(tokens))
    
    # Token frequency
    freq = Counter(tokens)
    most_common = freq.most_common(10)
    
    # Character categories
    categories = Counter()
    for token in tokens:
        if token.isspace():
            categories['space'] += 1
        elif token.isalpha():
            categories['alpha'] += 1
        elif token.isdigit():
            categories['digit'] += 1
        elif len(token) == 1:
            cat = unicodedata.category(token)
            categories[cat] += 1
        else:
            categories['mixed'] += 1
    
    return {
        'total_tokens': total,
        'unique_tokens': unique_tokens,
        'total_chars': char_count,
        'avg_token_length': char_count / total,
        'token_categories': dict(categories),
        'most_common': most_common
    }


def tokenize_and_visualize(
    text: str, 
    tokenizer: Tokenizer = None,
    show_indices: bool = False,
    show_stats: bool = False,
    **kwargs
) -> str:
    """Tokenize and visualize text with optional statistics."""
    if tokenizer is None:
        tokenizer = SimpleTokenizer()
    
    tokens = tokenizer.tokenize(text)
    result = visualize_tokens(tokens, show_indices=show_indices, **kwargs)
    
    if show_stats:
        stats = analyze_tokens(tokens)
        stats_str = f"\n\nStatistics:\n"
        stats_str += f"  Total tokens: {stats['total_tokens']}\n"
        stats_str += f"  Unique tokens: {stats['unique_tokens']}\n"
        stats_str += f"  Average length: {stats['avg_token_length']:.2f}"
        result += stats_str
    
    return result