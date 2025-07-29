"""Text optimization utilities for document text extraction."""
import re

try:
    from fast_langdetect import detect
    FAST_LANGDETECT_AVAILABLE = True
except ImportError:
    FAST_LANGDETECT_AVAILABLE = False


def is_table_row(line):
    """Check if a line appears to be a table row with | separators."""
    return '|' in line and line.count('|') >= 2


def is_cjk_language(text):
    """
    Detect if text is primarily in CJK (Chinese, Japanese, Korean) languages.
    
    Args:
        text (str): Text to analyze
        
    Returns:
        bool: True if text is detected as CJK language, False otherwise
    """
    if not FAST_LANGDETECT_AVAILABLE:
        # Fallback: simple character-based detection for CJK
        cjk_chars = 0
        total_chars = 0
        
        for char in text:
            if char.isalpha():
                total_chars += 1
                # Check if character is in CJK unicode ranges
                if (0x4e00 <= ord(char) <= 0x9fff or    # Chinese
                    0x3400 <= ord(char) <= 0x4dbf or    # Chinese Extension A
                    0x3040 <= ord(char) <= 0x309f or    # Hiragana
                    0x30a0 <= ord(char) <= 0x30ff or    # Katakana
                    0xac00 <= ord(char) <= 0xd7af):     # Hangul
                    cjk_chars += 1
        
        return total_chars > 0 and cjk_chars / total_chars > 0.3
    
    try:
        # Use fast-langdetect for more accurate detection
        # Take first 100 characters for better performance and accuracy
        clean_text = text.replace('\n', ' ').strip()
        if len(clean_text) < 3:
            # Too short for reliable detection, use fallback
            raise Exception("Text too short")
        
        # Use first 100 characters to avoid "text too long" warning
        # fast-langdetect works best with shorter text samples
        sample_text = clean_text[:100]
        result = detect(sample_text)
        detected_lang = result['lang'] if isinstance(result, dict) else result
        return detected_lang in ['zh', 'ja', 'ko']
    except:
        # Fallback to character-based detection if fast-langdetect fails
        cjk_chars = 0
        total_chars = 0
        
        for char in text:
            if char.isalpha():
                total_chars += 1
                # Check if character is in CJK unicode ranges
                if (0x4e00 <= ord(char) <= 0x9fff or    # Chinese
                    0x3400 <= ord(char) <= 0x4dbf or    # Chinese Extension A
                    0x3040 <= ord(char) <= 0x309f or    # Hiragana
                    0x30a0 <= ord(char) <= 0x30ff or    # Katakana
                    0xac00 <= ord(char) <= 0xd7af):     # Hangul
                    cjk_chars += 1
        
        return total_chars > 0 and cjk_chars / total_chars > 0.3


def is_likely_paragraph_break(current_line, next_line, is_cjk):
    """
    Determine if there should be a paragraph break between current and next line.
    
    Args:
        current_line (str): Current line text
        next_line (str): Next line text
        is_cjk (bool): Whether text is CJK language
        
    Returns:
        bool: True if there should be a paragraph break
    """
    if not current_line.strip() or not next_line.strip():
        return True
    
    # If next line starts with space/indent, it's likely a new paragraph
    if next_line.startswith(' ') or next_line.startswith('\u2000'):
        return True
    
    # Table rows should be separate
    if is_table_row(next_line):
        return True
    
    # For Latin languages, use additional heuristics
    if not is_cjk:
        current_stripped = current_line.strip()
        next_stripped = next_line.strip()
        
        # Check if current line ends with sentence-ending punctuation
        if current_stripped.endswith(('.', '!', '?', ':', ';')):
            # If next line starts with capital letter, likely new paragraph
            if next_stripped and next_stripped[0].isupper():
                return True
        
        # Check if next line starts with typical paragraph indicators
        paragraph_starters = ['The ', 'This ', 'In ', 'For ', 'However, ', 'Therefore, ', 'Chapter ', 'Article ',
                             'Moreover, ', 'Furthermore, ', 'Additionally, ', 'Nevertheless, ',
                             'Consequently, ', 'Similarly, ', 'Meanwhile, ', 'Finally, ',
                             'First, ', 'Second, ', 'Third, ', 'Last, ', 'Next, ']
        
        if any(next_stripped.startswith(starter) for starter in paragraph_starters):
            return True
            
        # Check for numbered/bulleted lists
        if (next_stripped.startswith(('1. ', '2. ', '3. ', '4. ', '5. ')) or 
            next_stripped.startswith(('• ', '- ', '* '))):
            return True
    
    return False


def optimize_text(text):
    """
    Optimize text formatting by merging lines without leading spaces to the previous line.

    This fixes the issue where doc files are rendered with visual line breaks.
    Special handling for table rows that contain | characters.
    Language-aware merging: CJK languages merge without spaces, Latin languages add spaces.
    Smart paragraph detection to avoid merging distinct paragraphs.

    Args:
        text (str): Raw text extracted from document

    Returns:
        str: Optimized text with merged lines
    """
    if not text:
        return text

    # Detect if text is primarily CJK language
    is_cjk = is_cjk_language(text)
    
    lines = text.split('\n')
    optimized_lines = []

    for i, line in enumerate(lines):
        if i < 3:
            # First 3 lines always get added separately (title and initial content)
            optimized_lines.append(line)
        else:
            # Check if this should be a separate line/paragraph
            should_separate = is_likely_paragraph_break(
                lines[i-1] if i > 0 else '', 
                line, 
                is_cjk
            )
            
            if should_separate:
                # Keep as separate line
                optimized_lines.append(line)
            else:
                # Merge with previous line
                if optimized_lines and optimized_lines[-1].strip() != '':
                    if is_cjk:
                        # CJK languages: merge directly without adding space
                        optimized_lines[-1] += line
                    else:
                        # Latin languages: add space when merging
                        optimized_lines[-1] += ' ' + line
                else:
                    # Previous line was empty, start new line
                    optimized_lines.append(line)

    # Final step: remove leading spaces from each line (except table rows)
    final_lines = []
    for line in optimized_lines:
        # Remove spaces and full-width spaces from lines
        final_lines.append(line.strip(' \u2000'))

    result = '\n'.join(final_lines)
    
    # Replace multiple consecutive newlines with single newline

    result = re.sub(r'\n{2,}', '\n', result)
    
    # Remove leading and trailing whitespace from the entire text
    result = result.strip()
    
    return result