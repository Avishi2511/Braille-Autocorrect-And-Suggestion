from typing import List, Tuple, Dict

class BrailleConverter:
    """
    Handles conversion between QWERTY input, Braille patterns, and text.
    """
    
    def __init__(self):
        # QWERTY to Braille dot mapping
        self.key_to_dot = {
            'd': 1, 'w': 2, 'q': 3,  # Left column: dots 1,2,3
            'k': 4, 'o': 5, 'p': 6   # Right column: dots 4,5,6
        }
        
        # Braille patterns to characters (basic alphabet)
        self.braille_to_char = {
            (1,): 'a', (1,2): 'b', (1,4): 'c', (1,4,5): 'd', (1,5): 'e',
            (1,2,4): 'f', (1,2,4,5): 'g', (1,2,5): 'h', (2,4): 'i', (2,4,5): 'j',
            (1,3): 'k', (1,2,3): 'l', (1,3,4): 'm', (1,3,4,5): 'n', (1,3,5): 'o',
            (1,2,3,4): 'p', (1,2,3,4,5): 'q', (1,2,3,5): 'r', (2,3,4): 's', (2,3,4,5): 't',
            (1,3,6): 'u', (1,2,3,6): 'v', (2,4,5,6): 'w', (1,3,4,6): 'x', (1,3,4,5,6): 'y',
            (1,3,5,6): 'z', (): ' '
        }
        
        # Reverse mapping for encoding
        self.char_to_braille = {v: k for k, v in self.braille_to_char.items()}
    
    def qwerty_to_braille_pattern(self, qwerty_input: str) -> List[Tuple[int, ...]]:
        """
        Convert QWERTY input to Braille dot patterns.
        Input: String of simultaneous key presses separated by spaces
        Example: "dk ok" -> [(1,4), (5,4)] for letters 'c' and something
        """
        if not qwerty_input.strip():
            return []
            
        patterns = []
        # Split by spaces to get individual character inputs
        char_inputs = qwerty_input.lower().split()
        
        for char_input in char_inputs:
            dots = []
            for key in char_input:
                if key in self.key_to_dot:
                    dots.append(self.key_to_dot[key])
            
            # Sort dots and convert to tuple
            pattern = tuple(sorted(dots)) if dots else ()
            patterns.append(pattern)
        
        return patterns
    
    def braille_patterns_to_text(self, patterns: List[Tuple[int, ...]]) -> str:
        """Convert Braille patterns to readable text."""
        text = ""
        for pattern in patterns:
            char = self.braille_to_char.get(pattern, '?')
            text += char
        return text
    
    def text_to_braille_patterns(self, text: str) -> List[Tuple[int, ...]]:
        """Convert text to Braille patterns."""
        patterns = []
        for char in text.lower():
            pattern = self.char_to_braille.get(char, ())
            patterns.append(pattern)
        return patterns
    
    def validate_qwerty_input(self, qwerty_input: str) -> bool:
        """Validate if QWERTY input contains only valid Braille keys."""
        valid_keys = set(self.key_to_dot.keys()) | {' '}
        return all(char in valid_keys for char in qwerty_input.lower())

