"""Side-by-side visualization of original text vs tokenized view."""

from typing import List, Tuple
import unicodedata
from .tokenizer import Tokenizer
from .llm_tokenizers import GPT4Tokenizer, GPT2Tokenizer, ByteLevelTokenizer


def create_side_by_side(
    text: str, 
    tokenizer: Tokenizer,
    width: int = 80,
    show_bytes: bool = True
) -> str:
    """Create a side-by-side view of original text and tokenized version."""
    
    tokens = tokenizer.tokenize(text)
    
    # Build the display
    lines = []
    
    # Header
    lines.append("┌" + "─" * (width // 2 - 2) + "┬" + "─" * (width // 2 - 2) + "┐")
    lines.append("│" + " Original Text ".center(width // 2 - 2) + "│" + " Tokenized View ".center(width // 2 - 2) + "│")
    lines.append("├" + "─" * (width // 2 - 2) + "┼" + "─" * (width // 2 - 2) + "┤")
    
    # Process text character by character
    original_chars = list(text)
    token_displays = []
    
    # Build token display with alignment info
    char_idx = 0
    for token in tokens:
        if token.startswith('<bytes:') or token.startswith('<0x'):
            # This is a byte representation
            token_displays.append((token, 'byte'))
        else:
            token_displays.append((token, 'text'))
    
    # Create rows
    original_line = ""
    token_line = ""
    
    i = 0
    for char in original_chars:
        # Add to original
        if char == '\n':
            display_char = '↵'
        elif char == '\t':
            display_char = '→'
        elif char == ' ':
            display_char = '·'
        elif ord(char) < 32:
            display_char = f'◌'
        else:
            display_char = char
            
        original_line += display_char
        
        # Check if we need to wrap
        if len(original_line) >= (width // 2 - 4):
            # Pad and add the lines
            orig_display = original_line.ljust(width // 2 - 3)
            token_display = token_line.ljust(width // 2 - 3)
            lines.append(f"│ {orig_display}│ {token_display}│")
            original_line = ""
            token_line = ""
    
    # Add remaining content
    if original_line or token_line:
        orig_display = original_line.ljust(width // 2 - 3)
        token_display = token_line.ljust(width // 2 - 3)
        lines.append(f"│ {orig_display}│ {token_display}│")
    
    # Now show the tokenized version with separators
    lines.append("├" + "─" * (width // 2 - 2) + "┼" + "─" * (width // 2 - 2) + "┤")
    
    # Token breakdown
    token_str = ""
    for i, (token, ttype) in enumerate(token_displays):
        if i > 0:
            token_str += "│"
        
        # Format token for display
        if ttype == 'byte':
            display = token
        elif token == '\n':
            display = '↵'
        elif token == '\t':
            display = '→'
        elif token == ' ':
            display = '·'
        else:
            # Show spaces explicitly in tokens
            display = token.replace(' ', '·')
        
        token_str += display
    
    # Wrap token string
    while token_str:
        chunk = token_str[:width // 2 - 4]
        token_str = token_str[width // 2 - 4:]
        lines.append(f"│ {'Full tokenized:'.ljust(width // 2 - 3)}│ {chunk.ljust(width // 2 - 3)}│")
        if token_str:
            lines.append(f"│ {''.ljust(width // 2 - 3)}│ {token_str.ljust(width // 2 - 3)}│")
            break
    
    # Bottom border
    lines.append("└" + "─" * (width // 2 - 2) + "┴" + "─" * (width // 2 - 2) + "┘")
    
    # Add token details
    lines.append("\nToken Breakdown:")
    lines.append("─" * width)
    
    for i, (token, ttype) in enumerate(token_displays):
        if ttype == 'byte':
            # Show what character this byte sequence represents
            try:
                # Extract hex from <bytes:...> or <0x...>
                if token.startswith('<bytes:'):
                    hex_str = token[7:-1]
                    byte_seq = bytes.fromhex(hex_str)
                elif token.startswith('<0x'):
                    hex_str = token[3:-1]
                    byte_seq = bytes.fromhex(hex_str)
                else:
                    byte_seq = b''
                
                char_repr = "?"
                try:
                    # Try to decode the accumulated bytes
                    char_repr = byte_seq.decode('utf-8', errors='replace')
                except:
                    char_repr = "?"
                    
                lines.append(f"  Token {i:2d}: {token} → (part of multi-byte character)")
            except:
                lines.append(f"  Token {i:2d}: {token}")
        else:
            # Regular token
            if token == ' ':
                lines.append(f"  Token {i:2d}: '·' (space)")
            elif token.startswith(' '):
                lines.append(f"  Token {i:2d}: '·{token[1:]}' (space + '{token[1:]}')")
            else:
                lines.append(f"  Token {i:2d}: '{token}'")
    
    return '\n'.join(lines)


def show_tokenizer_comparison(text: str) -> str:
    """Show how different tokenizers handle the same text."""
    output = []
    
    output.append("=" * 80)
    output.append(f"Original text: {repr(text)}")
    output.append("=" * 80)
    
    # Byte-level view
    output.append("\n1. BYTE-LEVEL VIEW (every UTF-8 byte)")
    output.append("-" * 80)
    try:
        byte_tokenizer = ByteLevelTokenizer()
        output.append(create_side_by_side(text, byte_tokenizer))
    except Exception as e:
        output.append(f"Error: {e}")
    
    # GPT-4 view
    output.append("\n\n2. GPT-4 TOKENIZATION (how ChatGPT sees it)")
    output.append("-" * 80)
    try:
        gpt4_tokenizer = GPT4Tokenizer()
        output.append(create_side_by_side(text, gpt4_tokenizer))
    except Exception as e:
        output.append(f"Error: {e}")
    
    return '\n'.join(output)