import pytest
from hypothesis import given, strategies as st, example, settings, HealthCheck
from llmvision import (
    SimpleTokenizer,
    WordTokenizer,
    CharTokenizer,
    visualize_tokens,
    tokenize_and_visualize
)


class TestTokenizers:
    @pytest.fixture
    def tokenizers(self):
        return {
            'simple': SimpleTokenizer(),
            'word': WordTokenizer(),
            'char': CharTokenizer()
        }
    
    @given(text=st.text())
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    @example(text="")  # Empty string
    @example(text="Hello, world!")  # Basic ASCII
    @example(text="😀🎉🌍")  # Emojis
    @example(text="你好世界")  # Chinese
    @example(text="مرحبا بالعالم")  # Arabic
    @example(text="Здравствуй мир")  # Cyrillic
    @example(text="🇺🇸🇬🇧🇯🇵")  # Flag emojis
    @example(text="\n\t\r")  # Whitespace
    @example(text="\x00\x01\x02")  # Control characters
    @example(text="\u200b\u200c\u200d")  # Zero-width characters
    @example(text="café")  # Accented characters
    @example(text="🧑‍💻👨‍👩‍👧‍👦")  # Complex emoji sequences
    def test_tokenizer_returns_list(self, text, tokenizers):
        for name, tokenizer in tokenizers.items():
            result = tokenizer.tokenize(text)
            assert isinstance(result, list), f"{name} tokenizer should return a list"
            assert all(isinstance(token, str) for token in result), f"{name} tokenizer should return list of strings"
    
    @given(st.text())
    def test_char_tokenizer_preserves_length(self, text):
        tokenizer = CharTokenizer()
        tokens = tokenizer.tokenize(text)
        assert len(tokens) == len(text)
        assert ''.join(tokens) == text
    
    @given(st.text())
    def test_word_tokenizer_handles_whitespace(self, text):
        tokenizer = WordTokenizer()
        tokens = tokenizer.tokenize(text)
        # Word tokenizer splits on whitespace
        if text.strip():
            assert len(tokens) >= 1
        else:
            assert len(tokens) == 0
    
    @given(st.text(min_size=1))
    def test_visualization_preserves_information(self, text):
        # Test that we can identify token boundaries
        tokenizer = SimpleTokenizer()
        tokens = tokenizer.tokenize(text)
        visualization = visualize_tokens(tokens)
        
        # Check that visualization contains separators
        if len(tokens) > 1:
            assert "│" in visualization
        
        # Ensure no information is completely lost
        assert len(visualization) > 0
    
    @given(st.text())
    def test_tokenize_and_visualize_integration(self, text):
        result = tokenize_and_visualize(text)
        assert isinstance(result, str)
        # Should not raise any exceptions
    
    def test_control_characters(self):
        text = "Hello\x00World\x01Test\x1f"
        result = tokenize_and_visualize(text)
        # Control characters should be escaped
        assert "\\u0000" in result
        assert "\\u0001" in result
        assert "\\u001f" in result
    
    def test_various_unicode_spaces(self):
        # Different Unicode space characters
        spaces = [
            "\u0020",  # Normal space
            "\u00A0",  # Non-breaking space
            "\u2000",  # En quad
            "\u2001",  # Em quad
            "\u2002",  # En space
            "\u2003",  # Em space
            "\u2009",  # Thin space
            "\u200A",  # Hair space
        ]
        
        for space in spaces:
            text = f"Hello{space}World"
            tokens = SimpleTokenizer().tokenize(text)
            assert len(tokens) == 3  # Hello, space, World
            
            # Check visualization
            viz = visualize_tokens(tokens)
            assert "│" in viz
    
    def test_emoji_handling(self):
        emojis = [
            "😀",  # Simple emoji
            "👨‍👩‍👧‍👦",  # Family emoji (ZWJ sequence)
            "🏳️‍🌈",  # Rainbow flag (combining sequence)
            "👋🏾",  # Waving hand with skin tone
        ]
        
        for emoji in emojis:
            # Character tokenizer should handle grapheme clusters
            char_tokens = CharTokenizer().tokenize(emoji)
            simple_tokens = SimpleTokenizer().tokenize(emoji)
            
            # Visualization should handle these without crashing
            viz = tokenize_and_visualize(emoji)
            assert len(viz) > 0
    
    @given(st.lists(st.text(), min_size=1))
    def test_custom_separator(self, tokens):
        # Test with different separators
        separators = ["│", "|", "→", "·", "•"]
        
        for sep in separators:
            result = visualize_tokens(tokens, separator=sep)
            if len(tokens) > 1:
                assert sep in result


class TestRealWorldExamples:
    def test_code_snippet(self):
        code = """def hello_world():
    print("Hello, 世界!")
    return 42"""
        
        result = tokenize_and_visualize(code)
        assert "def" in result
        assert "\n" in result or "\\n" in result  # Newlines should be visible
        assert "世界" in result  # Unicode should be preserved
    
    def test_mixed_scripts(self):
        text = "English العربية 中文 日本語 한국어 עברית"
        result = tokenize_and_visualize(text)
        
        # All scripts should be present
        assert "English" in result
        assert "العربية" in result
        assert "中文" in result
        assert "日本語" in result
        assert "한국어" in result
        assert "עברית" in result
    
    def test_url_tokenization(self):
        url = "https://example.com/path/to/resource?param=value&other=123"
        
        simple = SimpleTokenizer().tokenize(url)
        word = WordTokenizer().tokenize(url)
        
        # Simple tokenizer should split on punctuation
        assert len(simple) > len(word)
        
        # Word tokenizer treats URL as one token
        assert len(word) == 1
    
    def test_mathematical_expressions(self):
        expr = "∑(i=1 to n) x²+2πr = ∞"
        
        result = tokenize_and_visualize(expr)
        # Mathematical symbols should be preserved
        assert "∑" in result
        assert "π" in result
        assert "∞" in result
        assert "²" in result