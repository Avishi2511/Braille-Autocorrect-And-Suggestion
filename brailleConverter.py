from typing import List, Tuple, Dict

class BrailleConverter:
    """
    Handles conversion between QWERTY input, Braille patterns, and text.
    """
    
    def __init__(self):
        self.key_to_dot = {
            'd': 1, 'w': 2, 'q': 3,  
            'k': 4, 'o': 5, 'p': 6  
        }
        
        self.braille_to_char = {
            (1,): 'a', (1,2): 'b', (1,4): 'c', (1,4,5): 'd', (1,5): 'e',
            (1,2,4): 'f', (1,2,4,5): 'g', (1,2,5): 'h', (2,4): 'i', (2,4,5): 'j',
            (1,3): 'k', (1,2,3): 'l', (1,3,4): 'm', (1,3,4,5): 'n', (1,3,5): 'o',
            (1,2,3,4): 'p', (1,2,3,4,5): 'q', (1,2,3,5): 'r', (2,3,4): 's', (2,3,4,5): 't',
            (1,3,6): 'u', (1,2,3,6): 'v', (2,4,5,6): 'w', (1,3,4,6): 'x', (1,3,4,5,6): 'y',
            (1,3,5,6): 'z', (): ' '
        }
        
        self.char_to_braille = {v: k for k, v in self.braille_to_char.items()}
    
    def qwerty_to_braille_pattern(self, qwerty_input: str) -> List[Tuple[int, ...]]:
        if not qwerty_input.strip():
            return []
            
        patterns = []
        char_inputs = qwerty_input.lower().split()
        
        for char_input in char_inputs:
            dots = []
            for key in char_input:
                if key in self.key_to_dot:
                    dots.append(self.key_to_dot[key])
            
            pattern = tuple(sorted(dots)) if dots else ()
            patterns.append(pattern)
        
        return patterns
    
    def braille_patterns_to_text(self, patterns: List[Tuple[int, ...]]) -> str:
        text = ""
        for pattern in patterns:
            char = self.braille_to_char.get(pattern, '?')
            text += char
        return text
    
    def text_to_braille_patterns(self, text: str) -> List[Tuple[int, ...]]:
        patterns = []
        for char in text.lower():
            pattern = self.char_to_braille.get(char, ())
            patterns.append(pattern)
        return patterns
    
    def validate_qwerty_input(self, qwerty_input: str) -> bool:
        valid_keys = set(self.key_to_dot.keys()) | {' '}
        return all(char in valid_keys for char in qwerty_input.lower())

