from flask import Flask, render_template, request, jsonify
from brailleConverter import BrailleConverter
from dictionaryManager import DictionaryManager
from distanceCalculator import DistanceCalculator

app = Flask(__name__)

# Initialize components
converter = BrailleConverter()
dictionary = DictionaryManager()
distance_calc = DistanceCalculator()

# Load a sample dictionary (customize as needed)
sample_words = ['hello', 'world', 'braille', 'typing', 'test', 'help', 'word', 'python', 'code', 'dot']
dictionary.add_words(sample_words)

@app.route('/', methods=['GET', 'POST'])
def index():
    suggestion = None
    min_distance = None
    user_input = ''
    if request.method == 'POST':
        user_input = request.form.get('braille_input', '').strip()
        if not converter.validate_qwerty_input(user_input):
            suggestion = 'Invalid input: Only Braille QWERTY keys (d, w, q, k, o, p) and spaces allowed.'
        else:
            input_patterns = converter.qwerty_to_braille_pattern(user_input)
            candidates = list(dictionary.dictionary)
            candidate_patterns = [dictionary.get_word_patterns(word) for word in candidates]
            distances = distance_calc.batch_distances(input_patterns, candidate_patterns)
            min_distance = min(distances)
            best_indices = [i for i, d in enumerate(distances) if d == min_distance]
            suggestions = [candidates[i] for i in best_indices]
            suggestion = f"Suggestion(s): {', '.join(suggestions)} (distance: {min_distance})"
    return render_template('index.html', suggestion=suggestion, user_input=user_input)

@app.route('/suggest', methods=['POST'])
def suggest():
    data = request.get_json()
    user_input = data.get('braille_input', '').strip()
    if not converter.validate_qwerty_input(user_input):
        return jsonify({'error': 'Invalid input: Only Braille QWERTY keys (d, w, q, k, o, p) and spaces allowed.'})
    input_patterns = converter.qwerty_to_braille_pattern(user_input)
    candidates = list(dictionary.dictionary)
    candidate_patterns = [dictionary.get_word_patterns(word) for word in candidates]
    distances = distance_calc.batch_distances(input_patterns, candidate_patterns)
    min_distance = min(distances)
    best_indices = [i for i, d in enumerate(distances) if d == min_distance]
    suggestions = [candidates[i] for i in best_indices]
    return jsonify({'suggestions': suggestions, 'distance': min_distance})

if __name__ == '__main__':
    app.run(debug=True)
