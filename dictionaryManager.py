"""
Dictionary Manager Module
Handles dictionary storage, word frequency management, and learning mechanisms.
"""

import json
import pickle
from typing import List, Dict, Set, Tuple, Optional
from collections import defaultdict, Counter
from brailleConverter import BrailleConverter

# Constants
FREQUENCY_SCALE = 100
MAX_FREQUENCY_BOOST = 0.5


class DictionaryManager:
    """
    Manages dictionary storage, word frequencies, and learning mechanisms.
    Supports persistent storage and frequency-based ranking.
    """
    
    def __init__(self):
        self.dictionary: Set[str] = set()
        self.word_frequency: Dict[str, int] = defaultdict(int)
        self.user_corrections: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self.converter = BrailleConverter()
        
        # Cache for pattern representations
        self._word_patterns_cache: Dict[str, List[Tuple[int, ...]]] = {}
        
    def add_words(self, words: List[str], frequencies: Optional[List[int]] = None) -> None:
        """
        Add words to the dictionary with optional frequency data.
        
        Args:
            words: List of words to add
            frequencies: Optional list of frequency values for each word
        """
        for i, word in enumerate(words):
            word = word.lower().strip()
            if word and self._is_valid_word(word):
                self.dictionary.add(word)
                
                if frequencies and i < len(frequencies):
                    self.word_frequency[word] = frequencies[i]
                else:
                    self.word_frequency[word] = max(1, self.word_frequency[word])
                
                # Cache the Braille pattern representation
                self._word_patterns_cache[word] = self.converter.text_to_braille_patterns(word)
    
    def remove_word(self, word: str) -> bool:
        """
        Remove a word from the dictionary.
        
        Args:
            word: Word to remove
            
        Returns:
            True if word was removed, False if not found
        """
        word = word.lower().strip()
        if word in self.dictionary:
            self.dictionary.remove(word)
            del self.word_frequency[word]
            if word in self._word_patterns_cache:
                del self._word_patterns_cache[word]
            return True
        return False
    
    def get_word_frequency(self, word: str) -> int:
        """Get the frequency of a specific word."""
        return self.word_frequency.get(word.lower(), 0)
    
    def get_word_patterns(self, word: str) -> List[Tuple[int, ...]]:
        """
        Get cached Braille patterns for a word.
        
        Args:
            word: Word to get patterns for
            
        Returns:
            List of Braille patterns for the word
        """
        word = word.lower()
        if word not in self._word_patterns_cache:
            self._word_patterns_cache[word] = self.converter.text_to_braille_patterns(word)
        return self._word_patterns_cache[word]
    
    def add_user_correction(self, qwerty_input: str, chosen_word: str) -> None:
        """
        Record a user correction for learning purposes.
        
        Args:
            qwerty_input: Original QWERTY input
            chosen_word: Word the user selected/corrected to
        """
        chosen_word = chosen_word.lower().strip()
        if chosen_word in self.dictionary:
            # Increase frequency of the chosen word
            self.word_frequency[chosen_word] += 1
            
            # Record the specific correction pattern
            self.user_corrections[qwerty_input][chosen_word] += 1
            
            # Clear cache to reflect updated frequencies
            self._clear_frequency_cache()
    
    def get_correction_history(self, qwerty_input: str) -> Dict[str, int]:
        """
        Get correction history for a specific input pattern.
        
        Args:
            qwerty_input: QWERTY input pattern
            
        Returns:
            Dictionary of corrections and their frequencies
        """
        return dict(self.user_corrections.get(qwerty_input, {}))
    
    def get_personalized_boost(self, word: str, qwerty_input: str) -> float:
        """
        Calculate personalized boost based on user correction history.
        
        Args:
            word: Word to calculate boost for
            qwerty_input: Original input pattern
            
        Returns:
            Boost factor (0.0 to 1.0)
        """
        corrections = self.user_corrections.get(qwerty_input, {})
        if word in corrections:
            # Boost increases with frequency of this specific correction
            return min(0.2, corrections[word] * 0.05)
        return 0.0
    
    def get_frequency_boost(self, word: str) -> float:
        """
        Calculate frequency-based boost for a word.
        
        Args:
            word: Word to calculate boost for
            
        Returns:
            Frequency boost factor
        """
        frequency = self.word_frequency.get(word, 0)
        return min(MAX_FREQUENCY_BOOST, frequency / FREQUENCY_SCALE)
    
    def get_most_common_words(self, count: int = 100) -> List[Tuple[str, int]]:
        """
        Get the most common words by frequency.
        
        Args:
            count: Number of words to return
            
        Returns:
            List of (word, frequency) tuples, sorted by frequency
        """
        return sorted(self.word_frequency.items(), key=lambda x: x[1], reverse=True)[:count]
    
    def search_by_prefix(self, prefix: str) -> List[str]:
        """
        Find words that start with the given prefix.
        
        Args:
            prefix: Prefix to search for
            
        Returns:
            List of matching words, sorted by frequency
        """
        prefix = prefix.lower()
        matches = [word for word in self.dictionary if word.startswith(prefix)]
        return sorted(matches, key=lambda w: self.word_frequency[w], reverse=True)
    
    def search_by_length(self, length: int) -> List[str]:
        """
        Find words of a specific length.
        
        Args:
            length: Desired word length
            
        Returns:
            List of words of the specified length, sorted by frequency
        """
        matches = [word for word in self.dictionary if len(word) == length]
        return sorted(matches, key=lambda w: self.word_frequency[w], reverse=True)
    
    def get_similar_length_words(self, target_length: int, tolerance: int = 1) -> List[str]:
        """
        Get words with similar length to target.
        
        Args:
            target_length: Target word length
            tolerance: Length tolerance (±tolerance)
            
        Returns:
            List of words within the length range
        """
        min_length = max(1, target_length - tolerance)
        max_length = target_length + tolerance
        
        matches = [word for word in self.dictionary 
                  if min_length <= len(word) <= max_length]
        return sorted(matches, key=lambda w: self.word_frequency[w], reverse=True)
    
    def load_dictionary_from_file(self, filepath: str, format: str = 'text') -> None:
        """
        Load dictionary from file.
        
        Args:
            filepath: Path to dictionary file
            format: File format ('text', 'json', 'csv')
        """
        try:
            if format == 'text':
                with open(filepath, 'r', encoding='utf-8') as f:
                    words = [line.strip() for line in f if line.strip()]
                    self.add_words(words)
            
            elif format == 'json':
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        self.add_words(data)
                    elif isinstance(data, dict):
                        words = list(data.keys())
                        frequencies = list(data.values())
                        self.add_words(words, frequencies)
            
            elif format == 'csv':
                import csv
                with open(filepath, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    words, frequencies = [], []
                    for row in reader:
                        if len(row) >= 1:
                            words.append(row[0])
                            if len(row) >= 2 and row[1].isdigit():
                                frequencies.append(int(row[1]))
                    
                    if frequencies and len(frequencies) == len(words):
                        self.add_words(words, frequencies)
                    else:
                        self.add_words(words)
        
        except Exception as e:
            print(f"Error loading dictionary from {filepath}: {e}")
    
    def save_dictionary_to_file(self, filepath: str, format: str = 'json') -> None:
        """
        Save dictionary to file.
        
        Args:
            filepath: Path to save dictionary
            format: File format ('json', 'csv', 'text')
        """
        try:
            if format == 'json':
                data = {word: freq for word, freq in self.word_frequency.items()}
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            
            elif format == 'csv':
                import csv
                with open(filepath, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Word', 'Frequency'])
                    for word, freq in sorted(self.word_frequency.items()):
                        writer.writerow([word, freq])
            
            elif format == 'text':
                with open(filepath, 'w', encoding='utf-8') as f:
                    for word in sorted(self.dictionary):
                        f.write(f"{word}\n")
        
        except Exception as e:
            print(f"Error saving dictionary to {filepath}: {e}")
    
    def save_user_data(self, filepath: str) -> None:
        """
        Save user corrections and learning data.
        
        Args:
            filepath: Path to save user data
        """
        try:
            user_data = {
                'corrections': dict(self.user_corrections),
                'word_frequency': dict(self.word_frequency)
            }
            
            with open(filepath, 'wb') as f:
                pickle.dump(user_data, f)
        
        except Exception as e:
            print(f"Error saving user data to {filepath}: {e}")
    
    def load_user_data(self, filepath: str) -> None:
        """
        Load user corrections and learning data.
        
        Args:
            filepath: Path to load user data from
        """
        try:
            with open(filepath, 'rb') as f:
                user_data = pickle.load(f)
            
            if 'corrections' in user_data:
                self.user_corrections = defaultdict(lambda: defaultdict(int))
                for input_pattern, corrections in user_data['corrections'].items():
                    for word, count in corrections.items():
                        self.user_corrections[input_pattern][word] = count
            
            if 'word_frequency' in user_data:
                self.word_frequency.update(user_data['word_frequency'])
            
            self._clear_frequency_cache()
        
        except Exception as e:
            print(f"Error loading user data from {filepath}: {e}")
    
    def get_statistics(self) -> Dict:
        """
        Get comprehensive dictionary statistics.
        
        Returns:
            Dictionary containing various statistics
        """
        if not self.dictionary:
            return {
                'total_words': 0,
                'average_word_length': 0,
                'total_corrections': 0,
                'cache_size': 0
            }
        
        word_lengths = [len(word) for word in self.dictionary]
        total_corrections = sum(
            sum(corrections.values()) 
            for corrections in self.user_corrections.values()
        )
        
        return {
            'total_words': len(self.dictionary),
            'average_word_length': sum(word_lengths) / len(word_lengths),
            'min_word_length': min(word_lengths),
            'max_word_length': max(word_lengths),
            'total_frequency': sum(self.word_frequency.values()),
            'total_corrections': total_corrections,
            'unique_input_patterns': len(self.user_corrections),
            'cache_size': len(self._word_patterns_cache),
            'most_common_words': self.get_most_common_words(10)
        }
    
    def optimize_storage(self) -> None:
        """Optimize storage by cleaning up unused cache entries."""
        # Remove cache entries for words no longer in dictionary
        cached_words = set(self._word_patterns_cache.keys())
        for word in cached_words:
            if word not in self.dictionary:
                del self._word_patterns_cache[word]
        
        # Remove corrections for very infrequent patterns
        patterns_to_remove = []
        for pattern, corrections in self.user_corrections.items():
            if sum(corrections.values()) == 1:  # Only corrected once
                patterns_to_remove.append(pattern)
        
        for pattern in patterns_to_remove:
            del self.user_corrections[pattern]
    
    def _is_valid_word(self, word: str) -> bool:
        """
        Check if a word is valid for the dictionary.
        
        Args:
            word: Word to validate
            
        Returns:
            True if word is valid
        """
        if not word or len(word) > 50:  # Reasonable length limit
            return False
        
        # Check if word contains only supported characters
        supported_chars = set(self.converter.char_to_braille.keys())
        return all(char in supported_chars for char in word.lower())
    
    def _clear_frequency_cache(self) -> None:
        """Clear any frequency-based caches."""
        # This method can be extended to clear other caches as needed
        pass


# Example usage and testing
def test_dictionary_manager():
    """Test the DictionaryManager functionality."""
    manager = DictionaryManager()
    
    print("=== Dictionary Manager Tests ===\n")
    
    # Test adding words
    sample_words = ['hello', 'world', 'braille', 'typing', 'test']
    sample_frequencies = [100, 95, 50, 40, 30]
    
    manager.add_words(sample_words, sample_frequencies)
    
    print(f"Added {len(sample_words)} words to dictionary")
    print(f"Dictionary size: {len(manager.dictionary)}")
    
    # Test frequency operations
    print(f"\nFrequency of 'hello': {manager.get_word_frequency('hello')}")
    print(f"Frequency boost for 'hello': {manager.get_frequency_boost('hello'):.3f}")
    
    # Test corrections
    manager.add_user_correction("dwo", "hello")
    manager.add_user_correction("dwo", "hello")  # Same correction again
    
    print(f"\nPersonalized boost for 'hello' with input 'dwo': {manager.get_personalized_boost('hello', 'dwo'):.3f}")
    
    # Test search functions
    print(f"\nWords starting with 'h': {manager.search_by_prefix('h')}")
    print(f"Words of length 5: {manager.search_by_length(5)}")
    
    # Test statistics
    stats = manager.get_statistics()
    print(f"\nDictionary Statistics:")
    for key, value in stats.items():
        if key != 'most_common_words':
            print(f"  {key}: {value}")


if __name__ == "__main__":
    test_dictionary_manager()