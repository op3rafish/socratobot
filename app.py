from flask import Flask, request, jsonify, render_template, session
from flask_session import Session
from chatbot import get_chatbot_response
import os
from dotenv import load_dotenv
import logging

# Initialize Flask app and session configuration
app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')
Session(app)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Serve the main webpage
@app.route('/')
def index():
    # Initialize chat history only if it doesn't exist
    if 'chat_history' not in session:
        session['chat_history'] = []  # Initialize empty chat history
        welcome_message = (
            "Welcome, I am Socratobot.\n"
            "What do you hold to be true?"
        )
        session['chat_history'].append({"role": "CHATBOT", "message": welcome_message})
        logger.info("Initialized chat history with welcome message")

    return render_template('index.html')

# Static welcome message
@app.route('/welcome', methods=['GET'])
def welcome():
    try:
        chat_history = session.get('chat_history', [])
        response = (
            "Welcome, I am Socratobot.\n"
            "What do you hold to be true?"
        )
        # Only add welcome message if chat history is empty
        if not chat_history:
            chat_history.append({"role": "CHATBOT", "message": response})
            session['chat_history'] = chat_history[-50:]
            logger.info("Generated welcome message")

        # Return the welcome message for display
        return jsonify({'response': response})

    except Exception as e:
        logger.error(f"Welcome message error: {str(e)}")
        return jsonify({'error': 'Failed to generate welcome message'}), 500

# Retrieve full chat history
@app.route('/history', methods=['GET'])
def history():
    try:
        chat_history = session.get('chat_history', [])
        logger.info("Retrieved chat history")
        return jsonify({'history': chat_history})
    except Exception as e:
        logger.error(f"Error retrieving chat history: {str(e)}")
        return jsonify({'error': 'Failed to retrieve chat history'}), 500

# Handle user chat messages sent from the interface
@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_input = request.json.get('message', '')
        if not user_input:
            return jsonify({'error': 'No message provided'}), 400

        chat_history = session.get('chat_history', [])
        response, updated_history = get_chatbot_response(user_input, chat_history)
        session['chat_history'] = updated_history
        return jsonify({'response': response})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Reset chat history
@app.route('/reset', methods=['POST'])
def reset():
    try:
        session['chat_history'] = []  # Clear chat history
        welcome_message = (
            "Welcome, I am Socratobot.\n"
            "What do you hold to be true?"
        )
        session['chat_history'].append({"role": "CHATBOT", "message": welcome_message})
        logger.info("Chat history reset with welcome message")
        return jsonify({'message': 'Chat history reset'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Run the application
if __name__ == '__main__':
    app.run(debug=False)

