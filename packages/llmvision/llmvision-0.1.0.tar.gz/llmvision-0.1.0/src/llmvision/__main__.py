import sys
from .tokenizer import (
    SimpleTokenizer, 
    WordTokenizer, 
    CharTokenizer,
    GraphemeTokenizer,
    SubwordTokenizer,
    tokenize_and_visualize
)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Visualize text tokenization")
    parser.add_argument("text", nargs="*", help="Text to tokenize (optional)")
    parser.add_argument("-t", "--tokenizer", choices=["simple", "word", "char", "grapheme", "subword"],
                        default="simple", help="Tokenizer to use")
    parser.add_argument("-i", "--indices", action="store_true", help="Show token indices")
    parser.add_argument("-s", "--stats", action="store_true", help="Show tokenization statistics")
    parser.add_argument("-a", "--all", action="store_true", help="Show all tokenizers")
    
    args = parser.parse_args()
    
    # Default test strings if no text provided
    test_strings = [
        "Hello, world!",
        "The quick brown fox jumps over the lazy dog.",
        "LLMs tokenize text differently than humans.",
        "email@example.com",
        "multi-word-hyphenated-text",
        "Line 1\nLine 2\tTabbed text",
        "Numbers: 123, 456.78, -90",
        "Emojis: 😀🎉 Flags: 🇺🇸🇬🇧",
        "Math: ∫₀^∞ e^(-x²) dx = √π/2"
    ]
    
    tokenizers = {
        "Simple (default)": SimpleTokenizer(),
        "Word": WordTokenizer(),
        "Character": CharTokenizer(),
        "Grapheme": GraphemeTokenizer(),
        "Subword": SubwordTokenizer()
    }
    
    if args.text:
        test_strings = [" ".join(args.text)]
    
    for text in test_strings:
        print(f"\nOriginal text: {repr(text)}")
        print("-" * 60)
        
        if args.all:
            # Show all tokenizers
            for name, tokenizer in tokenizers.items():
                result = tokenize_and_visualize(text, tokenizer, 
                                              show_indices=args.indices,
                                              show_stats=args.stats)
                print(f"{name} tokenizer:")
                print(f"  {result}")
        else:
            # Show only selected tokenizer
            tokenizer_map = {
                "simple": SimpleTokenizer(),
                "word": WordTokenizer(),
                "char": CharTokenizer(),
                "grapheme": GraphemeTokenizer(),
                "subword": SubwordTokenizer()
            }
            tokenizer = tokenizer_map[args.tokenizer]
            result = tokenize_and_visualize(text, tokenizer,
                                          show_indices=args.indices,
                                          show_stats=args.stats)
            print(f"{args.tokenizer.title()} tokenizer:")
            print(f"  {result}")
        
        print()


if __name__ == "__main__":
    main()