from flask import Flask, request, jsonify
from flask_cors import CORS
from deep_translator import GoogleTranslator

# to initialize the Flask application
app = Flask(__name__)
# to enable Cross-Origin Resource Sharing (CORS)
CORS(app)

@app.route('/translate', methods=['POST'])
def translate_text():
    """
    Endpoint to translate text.
    Expects a JSON payload with 'text', 'source_lang', and 'target_lang'.
    """
    # to get the data from the incoming request
    data = request.get_json()

    # for basic validation
    if not data or 'text' not in data or 'target_lang' not in data:
        return jsonify({'error': 'Missing required fields: text and target_lang'}), 400

    text_to_translate = data.get('text')
    source_language = data.get('source_lang', 'auto') # Default source to 'auto'
    target_language = data.get('target_lang')

    # to handle empty text input
    if not text_to_translate:
        return jsonify({'translated_text': ''})

    try:
        # to perform the translation
        # note: the library uses short codes e.g., 'en' for English, 'es' for Spanish
        translated_text = GoogleTranslator(source=source_language, target=target_language).translate(text_to_translate)
        
        # to return the result as JSON
        return jsonify({'translated_text': translated_text})

    except Exception as e:
        # to handle potential errors during translation
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # to run the Flask app on port 5000 in debug mode
    app.run(debug=True, port=5000)