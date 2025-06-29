from flask import Flask, render_template, request, jsonify
from chatbot_logic import Chatbot  # Import your chatbot logic

# Initialize the Flask app
app = Flask(__name__)

# Instantiate your chatbot
# This will be created once when the server starts
chatbot = Chatbot()

# Define the route for the main page
@app.route("/")
def index():
    """Serves the main HTML page."""
    return render_template("index.html")

# Define the new endpoint to serve the top FAQs
@app.route("/get_top_faqs")
def get_top_faqs():
    """Provides the list of top FAQ questions as JSON."""
    top_faqs = chatbot.get_top_faqs()
    return jsonify({"top_faqs": top_faqs})

# Define the route for handling chat messages
@app.route("/chat", methods=["POST"])
def chat():
    """
    Handles POST requests from the JavaScript frontend.
    Receives a user's message, gets a response from the chatbot,
    and returns it as JSON.
    """
    user_message = request.json.get("message")
    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    response = chatbot.get_response(user_message)
    return jsonify({"response": response})

if __name__ == "__main__":
    # Runs the Flask server
    app.run(debug=True)