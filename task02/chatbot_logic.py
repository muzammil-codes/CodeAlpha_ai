import nltk
import string
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from thefuzz import fuzz

class Chatbot:
    """
    An advanced FAQ Chatbot that uses a hybrid matching approach (TF-IDF and Fuzzy Matching),
    recognizes intents, logs unanswered questions, and provides suggestions.
    This class contains the core logic of the chatbot.
    """
    def __init__(self):
        # --- Confidence Thresholds ---
        self.MAIN_CONFIDENCE_THRESHOLD = 0.65  # Confidence for a direct answer
        self.SUGGESTION_CONFIDENCE_THRESHOLD = 0.45 # Confidence for a suggestion

        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        self.ensure_nltk_data()

        # Expanded Knowledge Base (FAQs)
        self.faqs = {
            # Shipping & Orders
            "What are the shipping options?": "We offer standard shipping (5-7 business days), expedited shipping (2-3 business days), and next-day shipping.",
            "How can I track my order?": "You can track your order status by visiting the 'Track Order' page on our website and entering your order ID and email address.",
            "What is your return policy?": "We accept returns within 30 days of purchase. The item must be unused and in its original packaging. Please visit our 'Returns' page to initiate a return.",
            "How do I change my shipping address?": "You can change your shipping address in the 'My Account' section before your order has been shipped. If it has already shipped, please contact customer support.",
            "Do you ship internationally?": "Currently, we only ship within the country. We are planning to expand to international shipping in the near future.",
            "My order arrived damaged, what do I do?": "We are very sorry to hear that. Please contact our customer support with your order number and a photo of the damaged item, and we will arrange for a replacement or a refund.",

            # Payments
            "What payment methods do you accept?": "We accept all major credit cards (Visa, MasterCard, American Express), PayPal, and direct bank transfers.",
            "Is my payment information secure?": "Yes, absolutely. We use industry-standard SSL encryption to protect your details. Your payment information is securely transmitted directly to our payment processor.",
            "Why was my payment declined?": "Payments can be declined for several reasons. Please ensure your card details are correct, the card has not expired, and you have sufficient funds. If the issue persists, we recommend contacting your bank.",

            # Account Management
            "How do I create an account?": "You can create an account by clicking the 'Sign Up' button on the top right corner of our homepage and filling out the required information.",
            "I forgot my password, what should I do?": "You can reset your password by clicking the 'Forgot Password' link on the login page. You will receive an email with instructions on how to set a new password.",
            "How can I update my account information?": "You can update your personal details, such as your name and contact information, in the 'My Account' section after logging in.",

            # Product Information
            "Are your products eco-friendly?": "Many of our products are made from sustainable and eco-friendly materials. Please check the product description page for specific details on each item.",
            "Where can I find size guides?": "A link to the relevant size guide is available on each product page to help you find the perfect fit.",
            "How can I check if an item is in stock?": "The stock status for each item is displayed on its product page. If an item is out of stock, you can sign up to be notified when it becomes available again."
        }
        
        # Define a list of top FAQs to suggest to the user
        self.top_faqs = [
            "What are the shipping options?",
            "How can I track my order?",
            "What is your return policy?",
            "What payment methods do you accept?"
        ]

        # Intent mapping for better accuracy on common queries
        self.intent_keywords = {
            "reset_password": ["forgot password", "can't log in", "lost my password", "password reset"],
            "track_order": ["track my order", "where is my stuff", "order status", "delivery status"],
            "return_policy": ["return an item", "how to return", "send back"]
        }
        self.intent_to_question = {
            "reset_password": "I forgot my password, what should I do?",
            "track_order": "How can I track my order?",
            "return_policy": "What is your return policy?"
        }

        # Preprocess all FAQ questions
        self.original_questions = list(self.faqs.keys())
        self.processed_questions = [self._preprocess_text(q) for q in self.original_questions]

        # Initialize and fit the TF-IDF Vectorizer
        self.vectorizer = TfidfVectorizer()
        self.faq_vectors = self.vectorizer.fit_transform(self.processed_questions)

    def get_top_faqs(self):
        """Returns the predefined list of top FAQs."""
        return self.top_faqs

    def _preprocess_text(self, text):
        """Preprocesses text for NLP analysis."""
        tokens = nltk.word_tokenize(text.lower())
        lemmatized = [self.lemmatizer.lemmatize(token) for token in tokens if token not in string.punctuation and token not in self.stop_words]
        return " ".join(lemmatized)

    def _get_intent(self, user_question):
        """Checks for specific intents using keywords."""
        for intent, keywords in self.intent_keywords.items():
            for keyword in keywords:
                if keyword in user_question.lower():
                    return self.intent_to_question[intent]
        return None

    def get_response(self, user_question):
        """
        Generates a response to the user's question using a hybrid matching strategy.
        """
        intent_question = self._get_intent(user_question)
        if intent_question:
            return self.faqs[intent_question]

        processed_user_question = self._preprocess_text(user_question)
        user_vector = self.vectorizer.transform([processed_user_question])

        cosine_similarities = cosine_similarity(user_vector, self.faq_vectors).flatten()
        fuzzy_scores = [fuzz.partial_ratio(processed_user_question, q) / 100.0 for q in self.processed_questions]

        combined_scores = 0.7 * cosine_similarities + 0.3 * np.array(fuzzy_scores)

        best_match_index = combined_scores.argmax()
        best_score = combined_scores[best_match_index]

        if best_score >= self.MAIN_CONFIDENCE_THRESHOLD:
            return self.faqs[self.original_questions[best_match_index]]

        elif best_score >= self.SUGGESTION_CONFIDENCE_THRESHOLD:
            suggested_question = self.original_questions[best_match_index]
            return f"I'm not completely sure, but did you mean to ask: '{suggested_question}'?"

        else:
            self._log_unanswered_question(user_question)
            return "I'm sorry, I don't have an answer to that. I've logged your question for our team to review. Could you please try asking in a different way?"

    @staticmethod
    def _log_unanswered_question(question):
        """Logs a question that the bot could not answer."""
        try:
            with open("unanswered_questions.log", "a") as f:
                f.write(f"{question}\n")
        except IOError as e:
            print(f"Error logging unanswered question: {e}")


    @staticmethod
    def ensure_nltk_data():
        """Downloads necessary NLTK data if not found."""
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/stopwords')
            nltk.data.find('corpora/wordnet')
        except LookupError:
            print("--- First-time setup: Downloading NLTK data... ---")
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('wordnet', quiet=True)
            print("--- Download complete. ---")