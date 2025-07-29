# LLMVision

> See the world through the eyes of language models

LLMVision is a Python library for visualizing how Large Language Models (LLMs) tokenize text. It reveals the hidden world of tokens that LLMs actually see, including the often surprising ways they split words, handle Unicode, and represent emojis.

## Why LLMVision?

Ever wondered why your LLM usage costs more for emoji-heavy text? Or why certain prompts seem to work better than others? LLMVision helps you understand by showing exactly how text is tokenized.

```python
from llmvision import tokenize_and_visualize, GPT4Tokenizer

text = "Hello world! 👋🌍"
print(tokenize_and_visualize(text, GPT4Tokenizer()))
# Output: Hello│ world│!│<bytes:20f09f>│<bytes:91>│<bytes:8b>│<bytes:f09f>│<bytes:8c>│<bytes:8d>
```

That friendly wave emoji? It's actually 3 tokens! The Earth emoji? Another 3 tokens. That's why emoji-rich text can be expensive.

## Features

- 🔍 **Multiple Tokenizers**: GPT-2, GPT-4, byte-level, character-level, and more
- 👁️ **Visual Representation**: See token boundaries with clear separators
- 📊 **Token Statistics**: Analyze token counts, categories, and patterns
- 🌍 **Unicode Handling**: Properly handles emojis, multi-language text, and special characters
- 🎯 **LLM-Faithful**: Shows actual tokenization used by real language models

## Installation

```bash
pip install llmvision
```

## Quick Start

### Command Line

```bash
# Basic usage
llmvision "Hello world!"

# Show all tokenizers
llmvision "Hello world!" --all

# Show token indices
llmvision "Hello world!" --indices

# Show statistics
llmvision "Hello world!" --stats
```

### Python API

```python
from llmvision import tokenize_and_visualize, GPT4Tokenizer, SimpleTokenizer

# Quick visualization
text = "The tokenization process is fascinating!"
print(tokenize_and_visualize(text))

# Use specific tokenizer
gpt4 = GPT4Tokenizer()
print(tokenize_and_visualize(text, gpt4))

# Show token indices
print(tokenize_and_visualize(text, gpt4, show_indices=True))
```

## Examples

### See How LLMs Really See Text

```python
from llmvision import show_tokenizer_comparison

# Compare different tokenizer views
show_tokenizer_comparison("Hello 世界! 🌍")
```

### Understand Token Boundaries

```python
from llmvision import GPT4Tokenizer

tokenizer = GPT4Tokenizer()
tokens = tokenizer.tokenize("Hello world!")
print(tokens)
# ['Hello', ' world', '!']
# Note: the space is part of 'world' token!
```

### Analyze Token Usage

```python
from llmvision import analyze_tokens, SimpleTokenizer

text = "The quick brown fox jumps over the lazy dog."
tokenizer = SimpleTokenizer()
tokens = tokenizer.tokenize(text)
stats = analyze_tokens(tokens)

print(f"Total tokens: {stats['total_tokens']}")
print(f"Unique tokens: {stats['unique_tokens']}")
print(f"Average token length: {stats['avg_token_length']:.2f}")
```

## Available Tokenizers

- **SimpleTokenizer**: Basic word/punctuation/space tokenization
- **WordTokenizer**: Whitespace-based tokenization
- **CharTokenizer**: Character-level tokenization
- **GraphemeTokenizer**: Unicode grapheme clusters (user-perceived characters)
- **ByteLevelTokenizer**: Raw UTF-8 byte representation
- **GPT2Tokenizer**: Actual GPT-2 tokenization (via tiktoken)
- **GPT4Tokenizer**: Actual GPT-4 tokenization (via tiktoken)
- **SubwordTokenizer**: Simple subword tokenization
- **LLMStyleTokenizer**: Simulates common LLM tokenization patterns
- **SentencePieceStyleTokenizer**: Simulates SentencePiece-style tokenization

## Understanding Token Costs

Different tokenizers can result in vastly different token counts:

```python
from llmvision import GPT4Tokenizer, tokenize_and_visualize

examples = [
    "Hello world!",          # 3 tokens
    "Hello 世界!",           # 5 tokens (Chinese costs more!)
    "Hello 👋🌍!",           # 8 tokens (emojis are expensive!)
    "👨‍👩‍👧‍👦",                    # 18 tokens (!!)
]

tokenizer = GPT4Tokenizer()
for text in examples:
    tokens = tokenizer.tokenize(text)
    print(f"{text:20} → {len(tokens)} tokens")
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details.

## Acknowledgments

Built with [tiktoken](https://github.com/openai/tiktoken) for accurate GPT tokenization.