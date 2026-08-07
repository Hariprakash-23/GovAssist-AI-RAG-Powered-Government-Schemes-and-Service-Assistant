"""
Thin Groq wrapper (replaces langchain_ollama.ChatOllama). Mirrors the
pattern in the sample scripts (1_groq_connection_test.py etc.) but
loads the key from the environment instead of hardcoding it.
"""

from groq import Groq
from config import Config


class GroqModel:

    _client = None

    @classmethod
    def _get_client(cls):
        if cls._client is None:
            if not Config.GROQ_API_KEY:
                raise RuntimeError(
                    "GROQ_API_KEY is not set. Copy .env.example to .env "
                    "and add your own key — never hardcode it in source."
                )
            cls._client = Groq(api_key=Config.GROQ_API_KEY)
        return cls._client

    @classmethod
    def chat(cls, prompt, temperature=0.2, max_tokens=512, system=None):
        client = cls._get_client()

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response = client.chat.completions.create(
            model=Config.GROQ_MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )

        return response.choices[0].message.content
