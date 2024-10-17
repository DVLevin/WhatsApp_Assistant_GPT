# OpenAI Assistant API Integration with Flask by https://github.com/DVLevin (TG: @leeevinD)

Welcome to the OpenAI Assistant API integration project! This project provides a simple and user-friendly REST API built using Flask. The API integrates with OpenAI's Assistant to enable you to start conversations, send messages, check statuses, and optionally send responses to WhatsApp.

---

## Features

- **Start conversations** with OpenAI's Assistant API.
- **Send messages** to the assistant and receive responses.
- **Check conversation status** for a specific thread.
- **WhatsApp integration** (optional) for sending assistant responses via `pywhatkit`.

---

## Prerequisites

Before you start, make sure you have the following installed:

1. **Python** (version 3.7 or later)
2. **pip** (Python package manager)

---

## Quick Start Guide

Follow these steps to get started:

### 1. Clone the Repository

First, clone this repository to your local machine:

```bash
git clone https://github.com/yourusername/your-repo.git
cd your-repo
```

### 2. Install the Required Dependencies

Run the following command to install all the necessary packages:

```bash
pip install -r requirements.txt
```

This will install Flask, OpenAI, pywhatkit, and other required packages.

### 3. Set Up Environment Variables

You'll need to set up an `.env` file to store your environment variables, such as the OpenAI API key and Assistant ID. Here’s how to create the `.env` file:

1. Create a file named `.env` in the root directory of the project.
2. Add the following lines:

```bash
# .env file
openai_key=your_openai_api_key_here
```

- You can get your OpenAI API key by signing up on the OpenAI website and navigating to your account settings.
- The **Assistant ID** will be generated automatically when you start the application if it's not provided.

### 4. Running the Flask API

Once everything is set up, run the Flask application using the following command:

```bash
python flask_api.py
```

By default, the API will run on `http://0.0.0.0:8080`. You can interact with it using the API routes described below.

---

## API Endpoints

Here are the available API endpoints to interact with OpenAI's Assistant:

### 1. Start a Conversation

**Endpoint**: `/start`  
**Method**: `GET`  
**Description**: Starts a new conversation by creating a thread with the assistant.

**Request**:
```bash
curl -X GET http://0.0.0.0:8080/start
```

**Response**:
```json
{
  "thread_id": "your_thread_id_here"
}
```

### 2. Send a Message to the Assistant

**Endpoint**: `/chat`  
**Method**: `POST`  
**Description**: Sends a message to the assistant. You need to provide the `thread_id` and the message content.

**Request**:
```bash
curl -X POST http://0.0.0.0:8080/chat -H "Content-Type: application/json" -d '{"thread_id": "your_thread_id_here", "message": "Hello Assistant!"}'
```

**Response**:
```json
{
  "run_id": "your_run_id_here"
}
```

### 3. Check the Status of the Assistant's Response

**Endpoint**: `/check`  
**Method**: `POST`  
**Description**: Checks the status of a message run and retrieves the assistant’s response if completed. Optionally, you can provide a `phone_number` to send the response via WhatsApp.

**Request**:
```bash
curl -X POST http://0.0.0.0:8080/check -H "Content-Type: application/json" -d '{"thread_id": "your_thread_id_here", "run_id": "your_run_id_here", "phone_number": "+123456789"}'
```

**Response**:
```json
{
  "response": "The assistant's response here",
  "status": "completed"
}
```

---

## WhatsApp Integration (Optional)

This project includes optional WhatsApp integration using the `pywhatkit` library. You can send the assistant's response directly to a WhatsApp number by providing the `phone_number` field in the `/check` endpoint.

**How to enable WhatsApp integration**:
1. Ensure you have WhatsApp Web set up on your machine (as `pywhatkit` uses it to send messages).
2. In the `/check` request, include the `phone_number` field in international format (e.g., `+123456789`).

---

## Logging

Logs for each conversation are stored in the `logs/` directory. Each conversation is logged with a unique file name based on the `thread_id`, user metadata, and timestamp. 

Example log filename: `anonymous_user_your_thread_id_20240101_123456.log`

These logs capture:
- Incoming messages
- Assistant responses
- Status updates (such as completed or requires action)

---

## Detailed Steps for Assistant ID Handling

### How the Assistant ID Works:

1. **When the app starts**, it tries to fetch the `assistant_id` from the `.env` file.
2. **If the Assistant ID is not found**, the system will automatically create a new assistant using OpenAI's API.
3. The newly created **Assistant ID** is saved back to the `.env` file, so you don't need to generate a new one manually in the future.

This ensures that the assistant is set up correctly each time without manual intervention.

---

## Project Structure

Here's the structure of the repository:

```
/project-root
│
├── flask_api.py          # Main Flask app with the API routes
├── functions.py          # Utility functions for OpenAI interactions
├── whatsapp_integration.py  # Optional module for WhatsApp integration
├── logs/                 # Directory for conversation logs (auto-generated)
│   └── anonymous_user_your_thread_id_20240101_123456.log
├── requirements.txt      # List of dependencies to install
└── .env                  # Environment variables (created by you)
```

---

## Future Improvements

- **WhatsApp Integration**: You can swap out `pywhatkit` with a more robust service like Twilio's WhatsApp API for production use.
- **Database Integration**: Add support for database-backed conversation storage instead of just logs.
- **Enhanced Error Handling**: Improve error handling for edge cases such as network timeouts or API rate limits.

---

## Contributing

Feel free to contribute to this project! If you find a bug or have an idea for an enhancement, you can create an issue or submit a pull request. Contributions are always welcome.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---