# LLMVision

Visualize how LLMs tokenize text.

```python
from llmvision import tokenize_and_visualize, GPT4Tokenizer

text = "Hello world! 👋🌍"
print(tokenize_and_visualize(text, GPT4Tokenizer()))
# Output: Hello│ world│!│<bytes:20f09f>│<bytes:91>│<bytes:8b>│<bytes:f09f>│<bytes:8c>│<bytes:8d>
```

## Features

- Multiple tokenizers: GPT-2, GPT-4, byte-level, character-level
- Visual token boundaries  
- Unicode/emoji handling
- Actual tokenization used by OpenAI models

## Installation

```bash
pip install llmvision
```

## Usage

```bash
llmvision "Hello world!"
llmvision "Hello world!" --tokenizer gpt4
llmvision "Hello world!" --indices
```

```python
from llmvision import tokenize_and_visualize, GPT4Tokenizer

# Default tokenizer
print(tokenize_and_visualize("Hello world!"))

# Specific tokenizer
print(tokenize_and_visualize("Hello world!", GPT4Tokenizer()))
```

## Examples

```python
from llmvision import GPT4Tokenizer

tokenizer = GPT4Tokenizer()
tokens = tokenizer.tokenize("Hello world!")
print(tokens)  # ['Hello', ' world', '!']
```

## Tokenizers

- `SimpleTokenizer` - word/punctuation/space
- `WordTokenizer` - whitespace-based
- `CharTokenizer` - character-level
- `GraphemeTokenizer` - Unicode grapheme clusters
- `ByteLevelTokenizer` - UTF-8 bytes
- `GPT2Tokenizer` - GPT-2 (via tiktoken)
- `GPT4Tokenizer` - GPT-4 (via tiktoken)
- `SubwordTokenizer` - basic subword splitting

## Token Costs

```python
tokenizer = GPT4Tokenizer()
examples = [
    "Hello world!",    # 3 tokens
    "Hello 世界!",     # 5 tokens  
    "Hello 👋🌍!",     # 8 tokens
    "👨‍👩‍👧‍👦",            # 18 tokens
]
for text in examples:
    print(f"{text:15} → {len(tokenizer.tokenize(text))} tokens")
```

## License

MIT