"""LLM-faithful tokenizers that show how real language models see text."""

from typing import List, Optional
import tiktoken
import regex
from .tokenizer import Tokenizer


class ByteLevelTokenizer(Tokenizer):
    """Shows raw byte-level representation of text, like GPT-2."""
    def tokenize(self, text: str) -> List[str]:
        # Convert to UTF-8 bytes and show each byte
        tokens = []
        for char in text:
            bytes_repr = char.encode('utf-8')
            if len(bytes_repr) == 1:
                tokens.append(char)
            else:
                # Multi-byte character - show the byte sequence
                for byte in bytes_repr:
                    tokens.append(f"<0x{byte:02x}>")
        return tokens


class GPT2Tokenizer(Tokenizer):
    """Actual GPT-2 tokenizer using tiktoken."""
    def __init__(self):
        self.enc = tiktoken.get_encoding("gpt2")
    
    def tokenize(self, text: str) -> List[str]:
        # Get token IDs
        token_ids = self.enc.encode(text)
        # Decode each token individually to see the actual pieces
        tokens = []
        for tid in token_ids:
            token_bytes = self.enc.decode_single_token_bytes(tid)
            try:
                # Try to decode as UTF-8
                token_str = token_bytes.decode('utf-8')
                tokens.append(token_str)
            except UnicodeDecodeError:
                # If not valid UTF-8, show as bytes
                tokens.append(f"<bytes:{token_bytes.hex()}>")
        return tokens


class GPT4Tokenizer(Tokenizer):
    """GPT-4 tokenizer (cl100k_base) using tiktoken."""
    def __init__(self):
        self.enc = tiktoken.get_encoding("cl100k_base")
    
    def tokenize(self, text: str) -> List[str]:
        token_ids = self.enc.encode(text)
        tokens = []
        for tid in token_ids:
            token_bytes = self.enc.decode_single_token_bytes(tid)
            try:
                token_str = token_bytes.decode('utf-8')
                tokens.append(token_str)
            except UnicodeDecodeError:
                tokens.append(f"<bytes:{token_bytes.hex()}>")
        return tokens


class LLMStyleTokenizer(Tokenizer):
    """
    Simulates common LLM tokenization patterns without using actual vocab.
    Shows the "weird" splits that LLMs often make.
    """
    def tokenize(self, text: str) -> List[str]:
        tokens = []
        i = 0
        
        while i < len(text):
            char = text[i]
            
            # Spaces often get special treatment
            if char == ' ':
                # In many LLMs, spaces attach to the next token
                if i + 1 < len(text) and text[i + 1].isalpha():
                    # Find the end of the word
                    j = i + 1
                    while j < len(text) and text[j].isalnum():
                        j += 1
                    tokens.append(text[i:j])
                    i = j
                    continue
                else:
                    tokens.append(char)
                    i += 1
                    continue
            
            # Common subword patterns
            if char.isalpha():
                # Look for common patterns
                remaining = text[i:]
                
                # Common prefixes that often get split
                prefixes = ['un', 're', 'dis', 'pre', 'non', 'anti', 'de']
                for prefix in prefixes:
                    if remaining.lower().startswith(prefix) and len(remaining) > len(prefix) + 2:
                        if i > 0 and text[i-1] == ' ':
                            # Already included space with this token
                            tokens.append(prefix)
                        else:
                            tokens.append(prefix)
                        i += len(prefix)
                        break
                else:
                    # Check for common suffixes
                    word_end = i
                    while word_end < len(text) and text[word_end].isalnum():
                        word_end += 1
                    
                    word = text[i:word_end]
                    
                    # Common suffixes that often get split
                    suffixes = ['ing', 'ed', 'er', 'est', 'ly', 'tion', 'ment', 's']
                    split = False
                    
                    for suffix in suffixes:
                        if len(word) > len(suffix) + 2 and word.lower().endswith(suffix):
                            base = word[:-len(suffix)]
                            tokens.append(base)
                            tokens.append(suffix)
                            i = word_end
                            split = True
                            break
                    
                    if not split:
                        # No pattern found, take the whole word
                        tokens.append(word)
                        i = word_end
                    continue
            
            # Numbers often stay together
            if char.isdigit():
                j = i
                while j < len(text) and (text[j].isdigit() or text[j] in '.,'):
                    j += 1
                tokens.append(text[i:j])
                i = j
                continue
            
            # Punctuation usually separate
            if not char.isalnum() and not char.isspace():
                tokens.append(char)
                i += 1
                continue
            
            # Default: single character
            tokens.append(char)
            i += 1
        
        return tokens


class SentencePieceStyleTokenizer(Tokenizer):
    """
    Simulates SentencePiece-style tokenization (used by LLaMA, T5, etc).
    Shows the underscore prefix for spaces and weird subword splits.
    """
    def tokenize(self, text: str) -> List[str]:
        # SentencePiece typically replaces spaces with ▁ (underscore)
        # and can split in the middle of words
        
        # First, mark word boundaries
        words = regex.findall(r'\S+|\s+', text)
        tokens = []
        
        for word in words:
            if word.isspace():
                # Spaces become special tokens
                for _ in word:
                    tokens.append('▁')
            else:
                # Simulate subword splitting
                if len(word) <= 3:
                    tokens.append(word)
                    continue
                
                # Simulate BPE-style splits
                # This is simplified but shows the concept
                i = 0
                while i < len(word):
                    # Try different chunk sizes
                    for size in [4, 3, 2, 1]:
                        if i + size <= len(word):
                            chunk = word[i:i+size]
                            
                            # Some patterns get split, others don't
                            # This simulates vocabulary-based splitting
                            if (chunk.lower() in ['ing', 'ed', 'er', 'ly', 'tion'] or
                                len(chunk) <= 2 or
                                i + size == len(word)):
                                
                                tokens.append(chunk)
                                i += size
                                break
                
        return tokens