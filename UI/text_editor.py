from typing import Tuple, Optional
import implicit_treap

class TextEditor:
    """
    Stateless Text Editing Module.
    
    This class encapsulates low-level string manipulation logic for text editing operations.
    It is designed to be purely functional and decoupled from any UI framework (e.g., Tkinter).
    
    Architecture Note:
    ------------------
    This module serves as a Python prototype for a planned C++ backend integration.
    Future iterations will likely replace these Python method calls with bindings to a 
    performant C++ text buffer implementation. 
    
    Consequently, methods must remain stateless, accepting the full text context 
    references rather than maintaining internal state.
    """

    @staticmethod
    def type_char(text: str, cursor_index: int, char: str) -> Tuple[str, int]:
        """
        Inserts a single character (or string) at the specified cursor position.
        
        Usage:
            Handles standard typing as well as bulk insertion (e.g., pasting).
            
        Args:
            text (str): The current complete text buffer.
            cursor_index (int): The 0-indexed insertion point.
            char (str): The character(s) to insert.
            
        Returns:
            Tuple[str, int]: A tuple containing the updated text buffer and the new cursor position.
        """
        # Boundary safety checks to prevent out-of-bounds slicing
        if cursor_index < 0:
            cursor_index = 0
        if cursor_index > len(text):
            cursor_index = len(text)
            
        new_text = text[:cursor_index] + char + text[cursor_index:]
        return new_text, cursor_index + len(char)

    @staticmethod
    def range_delete(text: str, start_index: int, end_index: int) -> Tuple[str, int]:
        """
        Removes a segment of text defined by the range [start_index, end_index).
        
        Usage:
            Supports backspace, delete key, and selection deletion.
            
        Args:
            text (str): The current text buffer.
            start_index (int): inclusive start index.
            end_index (int): exclusive end index.
            
        Returns:
            Tuple[str, int]: The updated text and the resulting cursor position (anchored to start).
        """
        # Normalize indices
        if start_index < 0: start_index = 0
        if end_index > len(text): end_index = len(text)
        
        # Valid range check
        if start_index >= end_index:
            return text, start_index

        new_text = text[:start_index] + text[end_index:]
        return new_text, start_index

    @staticmethod
    def copy(text: str, start_index: int, end_index: int) -> str:
        """
        Extracts a substring from the text buffer.
        
        Args:
            text (str): The source text.
            start_index (int): Selection start (inclusive).
            end_index (int): Selection end (exclusive).
            
        Returns:
            str: The extracted substring. Returns empty string if range is invalid.
        """
        if start_index < 0: start_index = 0
        if end_index > len(text): end_index = len(text)
        
        if start_index >= end_index:
            return ""
            
        return text[start_index:end_index]

    @staticmethod
    def cut(text: str, start_index: int, end_index: int) -> Tuple[str, int, str]:
        """
        Performs a 'cut' operation: copies selection to clipboard return value and deletes it.
        
        Args:
            text (str): Text buffer.
            start_index (int): Selection start.
            end_index (int): Selection end.
            
        Returns:
            Tuple[str, int, str]: (updated_text, new_cursor_pos, clipboard_content)
        """
        # Combine Copy and Delete logic
        clipboard = TextEditor.copy(text, start_index, end_index)
        new_text, new_cursor = TextEditor.range_delete(text, start_index, end_index)
        return new_text, new_cursor, clipboard

    @staticmethod
    def paste(text: str, cursor_index: int, clipboard_content: str) -> Tuple[str, int]:
        """
        Inserts clipboard content at the cursor position.
        
        Args:
            text (str): Text buffer.
            cursor_index (int): Insertion position.
            clipboard_content (str): Content to paste.
            
        Returns:
            Tuple[str, int]: Updated text and new cursor position.
        """
        if not clipboard_content:
            return text, cursor_index
            
        # Delegate to type_char which handles insertion logic
        return TextEditor.type_char(text, cursor_index, clipboard_content)

