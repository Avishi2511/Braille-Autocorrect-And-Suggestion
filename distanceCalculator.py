"""
Distance Calculator
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
    
    def __init__(self):
        self.error_weights = ERROR_WEIGHTS
    
    def pattern_distance(self, pattern1: Tuple[int, ...], pattern2: Tuple[int, ...]) -> float:
        set1, set2 = set(pattern1), set(pattern2)
  
        missing_dots = set2 - set1
        missing_cost = len(missing_dots) * self.error_weights['missing_dot']
        
        extra_dots = set1 - set2
        extra_cost = len(extra_dots) * self.error_weights['extra_dot']
        
        return missing_cost + extra_cost
    
    def hamming_distance_patterns(self, patterns1: List[Tuple[int, ...]], 
                                 patterns2: List[Tuple[int, ...]]) -> float:
        if len(patterns1) != len(patterns2):
            return float('inf')  # Infinite distance for different lengths
        
        distance = 0
        for p1, p2 in zip(patterns1, patterns2):
            if p1 != p2:
                distance += self.pattern_distance(p1, p2)
        
        return distance
    
    def levenshtein_distance_patterns(self, patterns1: List[Tuple[int, ...]], 
                                    patterns2: List[Tuple[int, ...]]) -> float:
        m, n = len(patterns1), len(patterns2)
      
        dp = [[0.0] * (n + 1) for _ in range(m + 1)]
        
        for i in range(m + 1):
            dp[i][0] = i * self.error_weights['deletion']
        for j in range(n + 1):
            dp[0][j] = j * self.error_weights['insertion']
        
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if patterns1[i-1] == patterns2[j-1]:
                    dp[i][j] = dp[i-1][j-1]  # No cost for exact match
                else:
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
        len1, len2 = len(patterns1), len(patterns2)
        
        if len1 == 0 and len2 == 0:
            return 1.0
        if len1 == 0 or len2 == 0:
            return 0.0
     
        match_window = max(len1, len2) // 2 - 1
        match_window = max(0, match_window)
        
        matches1 = [False] * len1
        matches2 = [False] * len2
        
        matches = 0
        transpositions = 0

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
        
        k = 0
        for i in range(len1):
            if not matches1[i]:
                continue
            while not matches2[k]:
                k += 1
            if patterns1[i] != patterns2[k]:
                transpositions += 1
            k += 1
        
        jaro = (matches/len1 + matches/len2 + (matches - transpositions/2)/matches) / 3.0
        return jaro
    
    def jaro_winkler_similarity(self, patterns1: List[Tuple[int, ...]], 
                               patterns2: List[Tuple[int, ...]], prefix_scale: float = 0.1) -> float:
        jaro = self.jaro_similarity(patterns1, patterns2)
        
        if jaro < 0.7:  
            return jaro
        
        prefix_length = 0
        for i in range(min(4, len(patterns1), len(patterns2))):
            if patterns1[i] == patterns2[i]:
                prefix_length += 1
            else:
                break
        
        return jaro + (prefix_length * prefix_scale * (1 - jaro))
    
    def word_distance(self, word1_patterns: List[Tuple[int, ...]], 
                     word2_patterns: List[Tuple[int, ...]]) -> float:
        len1, len2 = len(word1_patterns), len(word2_patterns)
        
        if len1 == len2:
            return self.hamming_distance_patterns(word1_patterns, word2_patterns)
        else:
            base_distance = self.levenshtein_distance_patterns(word1_patterns, word2_patterns)
            
            length_diff = abs(len1 - len2)
            if length_diff > 2:  
                length_penalty = (length_diff - 2) * 0.5
                return base_distance + length_penalty
            
            return base_distance
    
    def similarity_score(self, word1_patterns: List[Tuple[int, ...]], 
                        word2_patterns: List[Tuple[int, ...]]) -> float:
        distance = self.word_distance(word1_patterns, word2_patterns)
        max_possible_distance = max(len(word1_patterns), len(word2_patterns)) * 3.0
        
        if max_possible_distance == 0:
            return 1.0
        
        similarity = max(0, 1 - distance / max_possible_distance)
        return similarity
    
    def batch_distances(self, input_patterns: List[Tuple[int, ...]], 
                       dictionary_patterns: List[List[Tuple[int, ...]]]) -> List[float]:
        distances = []
        for dict_patterns in dictionary_patterns:
            distance = self.word_distance(input_patterns, dict_patterns)
            distances.append(distance)
        
        return distances
