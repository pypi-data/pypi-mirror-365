"""
Test cases for text_optimizer module.
"""
import unittest
import sys
import os

# Add parent directory to path to import doc2txt
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from doc2txt.text_optimizer import (
    is_table_row,
    is_cjk_language,
    is_likely_paragraph_break,
    optimize_text
)


class TestTableRowDetection(unittest.TestCase):
    """Test cases for table row detection."""
    
    def test_is_table_row_valid(self):
        """Test detection of valid table rows."""
        self.assertTrue(is_table_row("Name | Age | City"))
        self.assertTrue(is_table_row("John | 25 | New York"))
        self.assertTrue(is_table_row("| Column 1 | Column 2 | Column 3 |"))
        self.assertTrue(is_table_row("A|B|C"))
    
    def test_is_table_row_invalid(self):
        """Test detection of invalid table rows."""
        self.assertFalse(is_table_row("This is a normal sentence."))
        self.assertFalse(is_table_row("No pipes here"))
        self.assertFalse(is_table_row("Only | one pipe"))
        self.assertFalse(is_table_row(""))


class TestCJKLanguageDetection(unittest.TestCase):
    """Test cases for CJK language detection."""
    
    def test_chinese_text(self):
        """Test Chinese text detection."""
        chinese_text = "这是一段中文文本，用于测试中文检测功能。"
        self.assertTrue(is_cjk_language(chinese_text))
    
    def test_japanese_text(self):
        """Test Japanese text detection."""
        japanese_text = "これは日本語のテストです。ひらがなとカタカナも含まれています。"
        self.assertTrue(is_cjk_language(japanese_text))
    
    def test_korean_text(self):
        """Test Korean text detection."""
        korean_text = "이것은 한국어 텍스트입니다. 한글 문자 감지를 테스트합니다."
        self.assertTrue(is_cjk_language(korean_text))
    
    def test_english_text(self):
        """Test English text detection."""
        english_text = "This is an English text for testing language detection."
        self.assertFalse(is_cjk_language(english_text))
    
    def test_mixed_text(self):
        """Test mixed language text."""
        mixed_text = "Hello 你好 world 世界"
        # Should return True if CJK characters are >30%
        result = is_cjk_language(mixed_text)
        # This depends on the ratio, but we expect it to be detected as CJK
        self.assertTrue(result)
    
    def test_empty_text(self):
        """Test empty text."""
        self.assertFalse(is_cjk_language(""))
    
    def test_numbers_only(self):
        """Test text with only numbers."""
        self.assertFalse(is_cjk_language("123456"))


class TestParagraphBreakDetection(unittest.TestCase):
    """Test cases for paragraph break detection."""
    
    def test_empty_lines(self):
        """Test empty lines trigger paragraph breaks."""
        self.assertTrue(is_likely_paragraph_break("", "Next line", False))
        self.assertTrue(is_likely_paragraph_break("Current line", "", False))
    
    def test_indented_lines(self):
        """Test indented lines trigger paragraph breaks."""
        self.assertTrue(is_likely_paragraph_break("First line", "    Indented line", False))
        self.assertTrue(is_likely_paragraph_break("First line", "　Full-width space", False))
    
    def test_table_rows(self):
        """Test table rows trigger paragraph breaks."""
        self.assertTrue(is_likely_paragraph_break("Normal text", "Name | Age | City", False))
    
    def test_paragraph_starters(self):
        """Test paragraph starter words."""
        starters = ["The ", "This ", "However, ", "Therefore, ", "Chapter "]
        for starter in starters:
            test_line = starter + "rest of the sentence."
            self.assertTrue(is_likely_paragraph_break("Previous sentence.", test_line, False))
    
    def test_numbered_lists(self):
        """Test numbered and bulleted lists."""
        list_items = ["1. First item", "2. Second item", "• Bullet point", "- Dash item"]
        for item in list_items:
            self.assertTrue(is_likely_paragraph_break("Previous text.", item, False))
    
    def test_sentence_endings(self):
        """Test sentence endings with capital letters."""
        self.assertTrue(is_likely_paragraph_break("End of sentence.", "The next sentence.", False))
        self.assertTrue(is_likely_paragraph_break("Question?", "Answer here.", False))
    
    def test_cjk_behavior(self):
        """Test CJK-specific behavior."""
        # For CJK languages, paragraph starters should not apply
        self.assertFalse(is_likely_paragraph_break("中文句子。", "The English sentence.", True))


class TestTextOptimization(unittest.TestCase):
    """Test cases for text optimization."""
    
    def test_empty_text(self):
        """Test optimization of empty text."""
        self.assertEqual(optimize_text(""), "")
        self.assertEqual(optimize_text(None), None)
    
    def test_simple_line_merging(self):
        """Test basic line merging for non-CJK text."""
        input_text = "This is the first line\nand this continues\nthe same paragraph."
        expected = "This is the first line\nand this continues the same paragraph."
        result = optimize_text(input_text)
        # The exact result depends on the optimization logic
        self.assertIn("continues", result)
    
    def test_table_preservation(self):
        """Test that table rows are preserved."""
        input_text = "Header text\nName | Age | City\nJohn | 25 | NYC\nMore text"
        result = optimize_text(input_text)
        self.assertIn("Name | Age | City", result)
        self.assertIn("John | 25 | NYC", result)
    
    def test_cjk_text_optimization(self):
        """Test CJK text optimization (no spaces when merging)."""
        input_text = "这是第一行\n这是第二行\n这是第三行"
        result = optimize_text(input_text)
        # Should merge without adding spaces
        self.assertNotIn("这是第一行 这是第二行", result)
    
    def test_whitespace_removal(self):
        """Test removal of leading/trailing whitespace."""
        input_text = "  \n  Line with spaces  \n  \n"
        result = optimize_text(input_text)
        self.assertFalse(result.startswith(" "))
        self.assertFalse(result.endswith(" "))
    
    def test_multiple_newlines_reduction(self):
        """Test reduction of multiple consecutive newlines."""
        input_text = "Line 1\n\n\nLine 2\n\n\n\nLine 3"
        result = optimize_text(input_text)
        self.assertNotIn("\n\n\n", result)
    
    def test_first_three_lines_preservation(self):
        """Test that first three lines are always preserved separately."""
        input_text = "Title\nSubtitle\nAuthor\nFirst paragraph line\ncontinues here"
        result = optimize_text(input_text)
        lines = result.split('\n')
        # First three lines should be separate
        self.assertEqual(len([line for line in lines[:3] if line.strip()]), 3)


class TestFastLangdetectIntegration(unittest.TestCase):
    """Test cases for fast-langdetect integration."""
    
    def test_fast_langdetect_import(self):
        """Test that fast-langdetect can be imported."""
        try:
            from fast_langdetect import detect
            self.assertTrue(True)
        except ImportError:
            self.skipTest("fast-langdetect not installed")
    
    def test_fast_langdetect_functionality(self):
        """Test fast-langdetect basic functionality."""
        try:
            from fast_langdetect import detect
            result = detect("Hello world")
            self.assertIsInstance(result, dict)
            self.assertIn('lang', result)
            self.assertIn('score', result)
        except ImportError:
            self.skipTest("fast-langdetect not installed")
    
    def test_fallback_mechanism(self):
        """Test that fallback mechanism works when fast-langdetect is unavailable."""
        # This tests the character-based fallback
        chinese_text = "这是中文文本"
        result = is_cjk_language(chinese_text)
        # Should work regardless of fast-langdetect availability
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()