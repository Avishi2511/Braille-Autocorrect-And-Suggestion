"""
Dictionary Manager
Handles dictionary storage and provides closest word suggestion based on Braille pattern.
"""

from typing import List, Dict, Set, Tuple
from brailleConverter import BrailleConverter

class DictionaryManager:
    def __init__(self):
        self.dictionary: Set[str] = set()
        self.converter = BrailleConverter()
        self._word_patterns_cache: Dict[str, List[Tuple[int, ...]]] = {}

    def add_words(self, words: List[str]) -> None:
        for word in words:
            word = word.lower().strip()
            if word:
                self.dictionary.add(word)
                self._word_patterns_cache[word] = self.converter.text_to_braille_patterns(word)

    def get_word_patterns(self, word: str) -> List[Tuple[int, ...]]:
        word = word.lower()
        if word not in self._word_patterns_cache:
            self._word_patterns_cache[word] = self.converter.text_to_braille_patterns(word)
        return self._word_patterns_cache[word]

    def suggest_closest_words(self, input_pattern: List[Tuple[int, ...]]) -> list:
        from distanceCalculator import DistanceCalculator
        distance_calc = DistanceCalculator()
        candidates = sorted(self.dictionary)  # Sort alphabetically for consistency
        candidate_patterns = [self.get_word_patterns(word) for word in candidates]
        distances = distance_calc.batch_distances(input_pattern, candidate_patterns)
        min_distance = min(distances)
        best_indices = [i for i, d in enumerate(distances) if d == min_distance]
        return [candidates[i] for i in best_indices]


# Example usage and testing
def test_dictionary_manager():
    manager = DictionaryManager()

    print("=== Dictionary Manager Tests ===\n")

    with open("dictionary.txt", "r", encoding="utf-8") as f:
        sample_words = [line.strip() for line in f if line.strip()]
    manager.add_words(sample_words)

    print(f"Added {len(sample_words)} words to dictionary")
    print(f"Dictionary size: {len(manager.dictionary)}")
    
    for word in sample_words:
        patterns = manager.get_word_patterns(word)
        print(f"Braille patterns for '{word}': {patterns}")

if __name__ == "__main__":
    test_dictionary_manager()