import os
import json
import time
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from dotenv import load_dotenv, set_key
import openai
from openai import OpenAI
from packaging import version
import functions

# Load environment variables from .env
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Set required version for OpenAI API
required_version = version.parse("1.1.1")
current_version = version.parse(openai.__version__)

# Version check for OpenAI API
if current_version < required_version:
    raise ValueError(f"OpenAI version {openai.__version__} is less than required version 1.1.1")
else:
    print("OpenAI version is compatible.")

# Initialize OpenAI client with API key
client = OpenAI(api_key=functions.get_env('openai_key'))

# Get the assistant ID from the .env file, or generate it if not present
def get_or_create_assistant(client):
    """Fetches the Assistant ID from .env or creates a new assistant if not present.
    
    The newly created Assistant ID is then written back to the .env file.

    Args:
        client: The OpenAI API client.

    Returns:
        str: The ID of the assistant.
    """
    assistant_id = os.getenv('assistant_id')

    # Check if assistant ID exists in the environment variables
    if assistant_id:
        print(f"Assistant ID found in .env: {assistant_id}")
        return assistant_id
    else:
        # If no assistant ID is found, create a new one
        print("No Assistant ID found. Creating a new assistant...")
        assistant_id = functions.create_assistant(client)

        # Update the .env file with the new Assistant ID
        env_file = '.env'
        set_key(env_file, 'assistant_id', assistant_id)

        print(f"New Assistant created with ID: {assistant_id} and saved in .env")
        return assistant_id

# Load or create assistant ID
assistant_id = get_or_create_assistant(client)

# Create logs directory if not present
LOG_DIR = 'logs'
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Initialize logger for each user thread
def initialize_logger(thread_id, metadata):
    """Initializes a logger for each user based on their thread ID and metadata.

    Args:
        thread_id (str): The ID of the thread.
        metadata (str): Metadata associated with the user (could be name, ID, etc.).

    Returns:
        Logger object specific to this user's thread.
    """
    log_filename = f"{metadata}_{thread_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    log_path = os.path.join(LOG_DIR, log_filename)
    logger = logging.getLogger(thread_id)
    logger.setLevel(logging.INFO)
    
    # Create file handler for logs
    file_handler = logging.FileHandler(log_path)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

# Route to start a new conversation
@app.route('/start', methods=['GET'])
def start_conversation():
    """Starts a new conversation with the assistant by creating a thread."""
    thread = client.beta.threads.create()
    logger = initialize_logger(thread.id, "anonymous_user")  # Assume anonymous if metadata unavailable
    logger.info(f"New conversation started with thread ID: {thread.id}")
    return jsonify({"thread_id": thread.id})

# Route to send a message to the assistant
@app.route('/chat', methods=['POST'])
def chat():
    """Handles user input and passes it to the assistant for a response.

    Expects a POST request with `thread_id` and `message`.

    Returns:
        JSON: Response containing the run ID or error message.
    """
    data = request.json
    thread_id = data.get('thread_id')
    user_input = data.get('message', '')

    if not thread_id:
        return jsonify({"error": "Missing thread_id"}), 400
    
    logger = initialize_logger(thread_id, "anonymous_user")
    logger.info(f"Received message for thread ID {thread_id}: {user_input}")
    
    # Send user message to OpenAI
    client.beta.threads.messages.create(thread_id=thread_id, role="user", content=user_input)
    run = client.beta.threads.runs.create(thread_id=thread_id, assistant_id=assistant_id)

    logger.info(f"Run started with ID {run.id}")
    return jsonify({"run_id": run.id})

# Route to check the status of the assistant's run
@app.route('/check', methods=['POST'])
def check_run_status():
    """Checks the status of a message run and retrieves the assistant's response if completed.

    Expects a POST request with `thread_id` and `run_id`.

    Returns:
        JSON: Response containing the assistant's message or status.
    """
    data = request.json
    thread_id = data.get('thread_id')
    run_id = data.get('run_id')
    
    if not thread_id or not run_id:
        return jsonify({"response": "error"}), 400

    logger = initialize_logger(thread_id, "anonymous_user")
    logger.info(f"Checking run status for thread ID {thread_id} and run ID {run_id}")
    
    start_time = time.time()
    while time.time() - start_time < 8:  # Limit check duration to 8 seconds to avoid timeout
        run_status = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)

        if run_status.status == 'completed':
            messages = client.beta.threads.messages.list(thread_id=thread_id)
            message_content = messages.data[0].content[0].text

            # Remove annotations (if any)
            annotations = message_content.annotations
            for annotation in annotations:
                message_content.value = message_content.value.replace(annotation.text, '')

            logger.info(f"Run completed. Response: {message_content.value}")
            return jsonify({"response": message_content.value, "status": "completed"})

        if run_status.status == 'requires_action':
            logger.info(f"Run requires action for thread ID {thread_id}.")
            handle_required_actions(run_status, thread_id, run_id)

        time.sleep(1)  # Short delay to avoid hammering the API

    logger.warning("Run timed out.")
    return jsonify({"response": "timeout"})

def handle_required_actions(run_status, thread_id, run_id):
    """Handles the required actions if the run is waiting for a function call (e.g., lead creation).

    Args:
        run_status: The current status of the run.
        thread_id (str): The thread ID.
        run_id (str): The run ID.
    """
    logger = initialize_logger(thread_id, "anonymous_user")
    
    for tool_call in run_status.required_action.submit_tool_outputs.tool_calls:
        if tool_call.function.name == "create_lead":
            # Process lead creation
            arguments = json.loads(tool_call.function.arguments)
            output = functions.create_lead(**arguments)
            client.beta.threads.runs.submit_tool_outputs(
                thread_id=thread_id,
                run_id=run_id,
                tool_outputs=[{"tool_call_id": tool_call.id, "output": json.dumps(output)}]
            )
            logger.info(f"Lead created for thread ID {thread_id}.")

        if tool_call.function.name == "time_schedule":
            # Process getting time schedule
            arguments = json.loads(tool_call.function.arguments)
            output = functions.get_time_schedule(**arguments)
            client.beta.threads.runs.submit_tool_outputs(
                thread_id=thread_id,
                run_id=run_id,
                tool_outputs=[{"tool_call_id": tool_call.id, "output": json.dumps(output)}]
            )
            logger.info(f"Time schedule processed for thread ID {thread_id}.")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
