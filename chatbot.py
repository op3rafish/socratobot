import cohere
import os
from dotenv import load_dotenv
import logging

# Set up logging for debugging and monitoring
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Initialize Cohere client with API key
API_KEY = os.getenv("COHERE_API_KEY")

# Check if API key is empty; if it is stop program with error message
if not API_KEY:
    raise ValueError("COHERE_API_KEY environment variable not set")

# Catch errors when initialising Cohere client
try:
    co = cohere.Client(API_KEY)
except Exception as e:
    raise ValueError(f"Failed to initialize Cohere client: {str(e)}")

def get_chatbot_response(user_input, chat_history=None):
    # If no chat history set to an empty list
    if chat_history is None:
        chat_history = []

    # Validate user input
    if not user_input or len(user_input.strip()) == 0:
        return "Please provide a valid input.", chat_history

    # Size limit to avoid overwhelming the API
    if len(user_input) > 2000:
        return "Input is too long. Please shorten it.", chat_history

    # Log first 50 chars of user input
    logger.info(f"Received user input: {user_input[:50]}...")

    # Define chatbot's conversational style and instructions
    preamble = """
    You are a concise guide, engaging in Socratic dialogue with a refined tone.
    You speak like Socrates and your aim is solely to help people forge a deeper understanding of themselves.
    Prompt the user to defend their reasoning with questions, avoiding lengthy discourse.
    Use a line at the start of the response to respond to the user's thoughts. Make it sound like you are a contemplative philosopher and add character where possible.
    If the user asks a question directly, use an additional line to answer it.
    Start each new idea or new thought on a new line.
    Each response should be short and succinct, only around 2 lines long (you may use more if necessary).
    In standard responses, end with a maximum of two questions to help the user deepen their thought.
    Your questions should follow the phases of a Socratic dialogue: clarifying the issue, exploring evidence, examining consequences, and potentially finding alternative perspectives.
    NO QUESTIONS IN YOUR FEEDBACK.
    """

    # Count user messages to determine rounds
    user_messages = sum(1 for entry in chat_history if entry["role"] == "USER")
    is_fifth_round = user_messages % 5 == 0 and user_messages > 0

    # Standard Socratic response
    try:
        stream = co.chat_stream(
            message=user_input,
            chat_history=chat_history,
            model="command-r-plus",
            temperature=0.05,
            max_tokens=700,
            preamble=preamble
        )
    except cohere.CohereError as e:
        logger.error(f"Cohere API error: {str(e)}")
        raise ValueError(f"Cohere API error: {str(e)}")

    # Collect streamed response
    full_response = ""
    for event in stream:
        if event.event_type == "text-generation":
            full_response += event.text

    if len(full_response.strip()) == 0:
        full_response = "Please clarify your statement."

    # Update chat history with user input
    chat_history.append({"role": "USER", "message": user_input})

    # If fifth round, assess reasoning and provide score + feedback
    if is_fifth_round:
        feedback_preamble = """
        You are a wise but strict philosopher, assessing a student's reasoning skills after five rounds of Socratic dialogue.
        Based on the chat history, evaluate the strength of their reasoning on a scale of 1 to 10. Be strict in your assessment.
        Consider clarity, coherence, depth, and consistency in their arguments.
        Short responses in the chat history should be marked down and commented on.
        Deliver clear, firm, actionable advice in a thoughtful, Socratic tone to deepen understanding.
        Ensure every line is a complete statement, ending with a period. No questions.
        Format your response strictly as follows:

        DON'T ASK MULTIPLE QUESTIONS HERE.

        - "Based on your responses, I score your reasoning a [score]/10."

        - "[pointer 1]"

        - "[pointer 2]"

        - "[pointer 3, if applicable]"

        - "Continue this dialogue by sharing further thoughts below, or reset to begin anew."

        - Sign off as "-- Socratobot"
        """
        try:
            feedback_stream = co.chat_stream(
                message="Please assess my reasoning skills based on our dialogue.",
                chat_history=chat_history,
                model="command-r-plus",
                temperature=0.0,
                max_tokens=700,
                preamble=feedback_preamble
            )
            feedback_response = ""
            for event in feedback_stream:
                if event.event_type == "text-generation":
                    feedback_response += event.text
            if len(feedback_response.strip()) == 0:
                feedback_response = "My friend, I score your reasoning a 5/10.\nConsider this: Clarify your initial claims.\nReflect here: Seek consistency in your reasoning."
            full_response += "\n\n" + feedback_response
        except cohere.CohereError as e:
            logger.error(f"Cohere API error in feedback: {str(e)}")
            full_response += "\n\nMy friend, I score your reasoning a 5/10.\nConsider this: Clarify your initial claims.\nReflect here: Seek consistency in your reasoning."

    # Update chat history with chatbot response
    chat_history.append({"role": "CHATBOT", "message": full_response})
    chat_history = chat_history[-50:]

    # Log response
    logger.info(f"Generated response: {full_response[:50]}...")

    return full_response, chat_history
