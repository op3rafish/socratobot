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
    session['chat_history'] = []  # Initialize empty chat history
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
        # Add welcome message to chat history
        chat_history.append({"role": "CHATBOT", "message": response})

        # Chat history limited to only 50 messages (list slicing)
        session['chat_history'] = chat_history[-50:]

        # Logs message showing the welcome message was created successfully
        logger.info("Generated welcome message")

        # Welcome message is converted to JSON, to be sent to the frontend
        return jsonify({'response': response})

    # Catch errors and store as `e`
    except Exception as e:
        # Log error with details
        logger.error(f"Welcome message error: {str(e)}")

        # Send JSON error message to the brower; HTTP status code 500
        # Inform frontend of failure so error can be displayed
        return jsonify({'error': 'Failed to generate welcome message'}), 500

# Handle user chat messages sent from the interface
# Logic for handling user input and generating bot responses
@app.route('/chat', methods=['POST'])
def chat():
    # Ensure an error doesn't crash the app
    try:
        # Extract user input
        user_input = request.json.get('message', '')

        # What if user input is empty? Send error message 400 (bad request)
        # Prevent empty messages
        if not user_input:
            return jsonify({'error': 'No message provided'}), 400

        # Retrieve chat history; empty if none exists
        chat_history = session.get('chat_history', [])

        # Call get_chatbot_response function, pass in user input + chat history
        # Get Socratic response from Cohere API
        response, updated_history = get_chatbot_response(user_input, chat_history)

        # Update new chat history
        session['chat_history'] = updated_history

        # Send bot response as a JSON string to the frontend
        return jsonify({'response': response})

    # Handle common errors (Exception as parent class)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Reset chat history
@app.route('/reset', methods=['POST'])
# POST because user has to hit the 'reset' button

# Define logic for clearing the convo
def reset():
    try:
        # Set chat history to empty list
        session['chat_history'] = []  # Clear chat history

        # Send message to the frontend that the reset was successful
        return jsonify({'message': 'Chat history reset'})

    # Send JSON error message 500; inform of any issues during reset
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Run the application
# Ensure script is being run directly, not imported as a module
if __name__ == '__main__':

    # Production mode: False = no auto reloading or detailed error pages
    app.run(debug=False)
