"""
Distance Calculator Module
Implements various distance and similarity algorithms for Braille pattern matching.
"""

from typing import List, Tuple

ERROR_WEIGHTS = {
    'missing_dot': 1.0,
    'extra_dot': 1.0,
    'deletion': 2.0,
    'insertion': 2.0,
    'substitution': 1.5
}


class DistanceCalculator:
    """
    Calculates distances and similarities between Braille patterns and words.
    Supports multiple algorithms optimized for Braille input characteristics.
    """
    
    def __init__(self):
        self.error_weights = ERROR_WEIGHTS
    
    def pattern_distance(self, pattern1: Tuple[int, ...], pattern2: Tuple[int, ...]) -> float:
        """
        Calculate distance between two Braille patterns.
        
        This method considers the unique characteristics of Braille input:
        - Missing dots (user didn't press a required key)
        - Extra dots (user accidentally pressed additional keys)
        - Different weights for different error types
        
        Args:
            pattern1: First Braille pattern (typically user input)
            pattern2: Second Braille pattern (typically dictionary word)
        
        Returns:
            Distance score (lower = more similar)
        """
        set1, set2 = set(pattern1), set(pattern2)
        
        # Missing dots (in target but not in input)
        missing_dots = set2 - set1
        missing_cost = len(missing_dots) * self.error_weights['missing_dot']
        
        # Extra dots (in input but not in target)
        extra_dots = set1 - set2
        extra_cost = len(extra_dots) * self.error_weights['extra_dot']
        
        return missing_cost + extra_cost
    
    def hamming_distance_patterns(self, patterns1: List[Tuple[int, ...]], 
                                 patterns2: List[Tuple[int, ...]]) -> float:
        """
        Calculate Hamming distance between two equal-length pattern sequences.
        
        Args:
            patterns1: First sequence of Braille patterns
            patterns2: Second sequence of Braille patterns
        
        Returns:
            Hamming distance (number of differing positions)
        """
        if len(patterns1) != len(patterns2):
            return float('inf')  # Infinite distance for different lengths
        
        distance = 0
        for p1, p2 in zip(patterns1, patterns2):
            if p1 != p2:
                distance += self.pattern_distance(p1, p2)
        
        return distance
    
    def levenshtein_distance_patterns(self, patterns1: List[Tuple[int, ...]], 
                                    patterns2: List[Tuple[int, ...]]) -> float:
        """
        Calculate Levenshtein (edit) distance for Braille patterns with custom costs.
        
        This implementation uses dynamic programming and considers:
        - Character insertion/deletion costs
        - Substitution costs based on pattern similarity
        - Optimized for Braille-specific error patterns
        
        Args:
            patterns1: First sequence of Braille patterns
            patterns2: Second sequence of Braille patterns
        
        Returns:
            Edit distance with custom costs
        """
        m, n = len(patterns1), len(patterns2)
        
        # Create DP table
        dp = [[0.0] * (n + 1) for _ in range(m + 1)]
        
        # Initialize base cases
        for i in range(m + 1):
            dp[i][0] = i * self.error_weights['deletion']
        for j in range(n + 1):
            dp[0][j] = j * self.error_weights['insertion']
        
        # Fill DP table
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if patterns1[i-1] == patterns2[j-1]:
                    dp[i][j] = dp[i-1][j-1]  # No cost for exact match
                else:
                    # Calculate substitution cost based on pattern similarity
                    substitute_cost = self.pattern_distance(patterns1[i-1], patterns2[j-1])
                    if substitute_cost == 0:
                        substitute_cost = self.error_weights['substitution']
                    
                    dp[i][j] = min(
                        dp[i-1][j] + self.error_weights['deletion'],      # Deletion
                        dp[i][j-1] + self.error_weights['insertion'],     # Insertion
                        dp[i-1][j-1] + substitute_cost                    # Substitution
                    )
        
        return dp[m][n]
    
    def jaro_similarity(self, patterns1: List[Tuple[int, ...]], 
                       patterns2: List[Tuple[int, ...]]) -> float:
        """
        Calculate Jaro similarity for Braille patterns.
        Good for detecting similar sequences with transpositions.
        
        Args:
            patterns1: First sequence of Braille patterns
            patterns2: Second sequence of Braille patterns
        
        Returns:
            Jaro similarity score (0-1, higher = more similar)
        """
        len1, len2 = len(patterns1), len(patterns2)
        
        if len1 == 0 and len2 == 0:
            return 1.0
        if len1 == 0 or len2 == 0:
            return 0.0
        
        # Calculate matching window
        match_window = max(len1, len2) // 2 - 1
        match_window = max(0, match_window)
        
        # Track matches
        matches1 = [False] * len1
        matches2 = [False] * len2
        
        matches = 0
        transpositions = 0
        
        # Find matches
        for i in range(len1):
            start = max(0, i - match_window)
            end = min(i + match_window + 1, len2)
            
            for j in range(start, end):
                if matches2[j] or patterns1[i] != patterns2[j]:
                    continue
                matches1[i] = matches2[j] = True
                matches += 1
                break
        
        if matches == 0:
            return 0.0
        
        # Count transpositions
        k = 0
        for i in range(len1):
            if not matches1[i]:
                continue
            while not matches2[k]:
                k += 1
            if patterns1[i] != patterns2[k]:
                transpositions += 1
            k += 1
        
        # Calculate Jaro similarity
        jaro = (matches/len1 + matches/len2 + (matches - transpositions/2)/matches) / 3.0
        return jaro
    
    def jaro_winkler_similarity(self, patterns1: List[Tuple[int, ...]], 
                               patterns2: List[Tuple[int, ...]], prefix_scale: float = 0.1) -> float:
        """
        Calculate Jaro-Winkler similarity (enhanced Jaro with prefix bonus).
        
        Args:
            patterns1: First sequence of Braille patterns
            patterns2: Second sequence of Braille patterns
            prefix_scale: Scaling factor for common prefix bonus
        
        Returns:
            Jaro-Winkler similarity score (0-1, higher = more similar)
        """
        jaro = self.jaro_similarity(patterns1, patterns2)
        
        if jaro < 0.7:  # Only apply prefix bonus for reasonably similar strings
            return jaro
        
        # Calculate common prefix length (up to 4 characters)
        prefix_length = 0
        for i in range(min(4, len(patterns1), len(patterns2))):
            if patterns1[i] == patterns2[i]:
                prefix_length += 1
            else:
                break
        
        return jaro + (prefix_length * prefix_scale * (1 - jaro))
    
    def word_distance(self, word1_patterns: List[Tuple[int, ...]], 
                     word2_patterns: List[Tuple[int, ...]]) -> float:
        """
        Calculate comprehensive distance between two words represented as Braille patterns.
        
        Uses the most appropriate algorithm based on word characteristics:
        - Hamming distance for same-length words
        - Levenshtein distance for different-length words
        - Additional penalties for significant length differences
        
        Args:
            word1_patterns: First word as Braille patterns
            word2_patterns: Second word as Braille patterns
        
        Returns:
            Comprehensive distance score
        """
        len1, len2 = len(word1_patterns), len(word2_patterns)
        
        if len1 == len2:
            # Same length - use Hamming distance (faster)
            return self.hamming_distance_patterns(word1_patterns, word2_patterns)
        else:
            # Different lengths - use Levenshtein distance
            base_distance = self.levenshtein_distance_patterns(word1_patterns, word2_patterns)
            
            # Add length penalty for very different lengths
            length_diff = abs(len1 - len2)
            if length_diff > 2:  # Significant length difference
                length_penalty = (length_diff - 2) * 0.5
                return base_distance + length_penalty
            
            return base_distance
    
    def similarity_score(self, word1_patterns: List[Tuple[int, ...]], 
                        word2_patterns: List[Tuple[int, ...]]) -> float:
        """
        Calculate similarity score (inverse of distance, normalized to 0-1 range).
        
        Args:
            word1_patterns: First word as Braille patterns
            word2_patterns: Second word as Braille patterns
        
        Returns:
            Similarity score (0-1, higher = more similar)
        """
        distance = self.word_distance(word1_patterns, word2_patterns)
        max_possible_distance = max(len(word1_patterns), len(word2_patterns)) * 3.0
        
        if max_possible_distance == 0:
            return 1.0
        
        # Convert distance to similarity (0-1 scale)
        similarity = max(0, 1 - distance / max_possible_distance)
        return similarity
    
    def batch_distances(self, input_patterns: List[Tuple[int, ...]], 
                       dictionary_patterns: List[List[Tuple[int, ...]]]) -> List[float]:
        """
        Calculate distances between input and multiple dictionary entries efficiently.
        
        Args:
            input_patterns: Input word as Braille patterns
            dictionary_patterns: List of dictionary words as Braille patterns
        
        Returns:
            List of distance scores
        """
        distances = []
        for dict_patterns in dictionary_patterns:
            distance = self.word_distance(input_patterns, dict_patterns)
            distances.append(distance)
        
        return distances


# Performance testing and example usage
def test_distance_calculator():
    """Test the DistanceCalculator functionality."""
    calculator = DistanceCalculator()
    
    print("=== Distance Calculator Tests ===\n")
    
    # Test pattern distance
    pattern1 = (1, 2)      # 'b'
    pattern2 = (1, 2, 4)   # 'f'
    pattern3 = (1,)        # 'a'
    
    print("Pattern Distance Tests:")
    print(f"Pattern {pattern1} vs {pattern2}: {calculator.pattern_distance(pattern1, pattern2)}")
    print(f"Pattern {pattern1} vs {pattern3}: {calculator.pattern_distance(pattern1, pattern3)}")
    print(f"Pattern {pattern2} vs {pattern3}: {calculator.pattern_distance(pattern2, pattern3)}")
    print()
    
    # Test word distances
    word1 = [(1,), (1,2)]           # "ab"
    word2 = [(1,), (1,2,4)]         # "af"
    word3 = [(1,), (1,2), (1,4)]    # "abc"
    
    print("Word Distance Tests:")
    print(f"'ab' vs 'af': {calculator.word_distance(word1, word2)}")
    print(f"'ab' vs 'abc': {calculator.word_distance(word1, word3)}")
    print(f"'af' vs 'abc': {calculator.word_distance(word2, word3)}")
    print()
    
    # Test similarity scores
    print("Similarity Score Tests:")
    print(f"'ab' vs 'af': {calculator.similarity_score(word1, word2):.3f}")
    print(f"'ab' vs 'abc': {calculator.similarity_score(word1, word3):.3f}")
    print(f"'af' vs 'abc': {calculator.similarity_score(word2, word3):.3f}")
    print()
    
    # Test Jaro-Winkler similarity
    print("Jaro-Winkler Similarity Tests:")
    print(f"'ab' vs 'af': {calculator.jaro_winkler_similarity(word1, word2):.3f}")
    print(f"'ab' vs 'abc': {calculator.jaro_winkler_similarity(word1, word3):.3f}")


if __name__ == "__main__":
    test_distance_calculator()