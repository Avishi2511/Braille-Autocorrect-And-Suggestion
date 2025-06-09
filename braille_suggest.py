from brailleConverter import BrailleConverter
from dictionaryManager import DictionaryManager
from distanceCalculator import DistanceCalculator

converter = BrailleConverter()
dictionary = DictionaryManager()
distance_calc = DistanceCalculator()

with open("dictionary.txt", "r", encoding="utf-8") as f:
    sample_words = [line.strip() for line in f if line.strip()]
dictionary.add_words(sample_words)

print("Braille QWERTY Auto-correct & Suggestion System")
print("Type your Braille QWERTY input (e.g., 'dk ok'), or 'exit' to quit.")

while True:
    user_input = input("Enter Braille QWERTY sequence: ").strip()
    if user_input.lower() == 'exit':
        break
    if not converter.validate_qwerty_input(user_input):
        print("Invalid input: Only Braille QWERTY keys (d, w, q, k, o, p) and spaces allowed.")
        continue
    input_patterns = converter.qwerty_to_braille_pattern(user_input)
    candidates = list(dictionary.dictionary)
    candidate_patterns = [dictionary.get_word_patterns(word) for word in candidates]
    distances = distance_calc.batch_distances(input_patterns, candidate_patterns)
    
    min_distance = min(distances)
    best_indices = [i for i, d in enumerate(distances) if d == min_distance]
    suggestions = [candidates[i] for i in best_indices]
    print(f"Suggestion(s): {', '.join(suggestions)} (distance: {min_distance})\n")
