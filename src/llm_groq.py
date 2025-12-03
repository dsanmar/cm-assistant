# llm_groq.py

import os
import requests

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


class GroqClientError(Exception):
    """Custom exception for Groq client errors."""
    pass


def _check_api_key():
    if not GROQ_API_KEY:
        raise GroqClientError(
            "GROQ_API_KEY environment variable is not set. "
            "Export it in your shell or put it in a .env file."
        )


def call_groq_chat(messages, model="llama-3.1-8b-instant", temperature=0.2):
    """
    Call Groq's chat completion API and return the assistant's message text.
    """
    _check_api_key()

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }

    response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=60)
    try:
        response.raise_for_status()
    except requests.HTTPError as e:
        raise GroqClientError(f"Groq API error: {e} - {response.text}") from e

    data = response.json()
    return data["choices"][0]["message"]["content"]


