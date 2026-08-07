"""
LLM-based intent classification + slot extraction, using few-shot
(multi-shot) prompting against Groq — replaces the old keyword
IntentClassifier + spaCy SlotExtractor (app/nlp/*), removing the
spaCy dependency entirely.
"""

import json
import re

from app.models.groq_client import GroqModel
from app.chatbot.prompts import INTENT_PROMPT

VALID_INTENTS = {
    "ELIGIBILITY", "DOCUMENTS", "APPLICATION",
    "BENEFITS", "CSC_LOCATION", "SCHEME_INFO", "GENERAL_QUERY"
}


class IntentLLM:

    @classmethod
    def classify(cls, message):
        prompt = INTENT_PROMPT.format(message=message)

        raw = GroqModel.chat(prompt, temperature=0, max_tokens=150)

        parsed = cls._safe_parse(raw)

        intent = parsed.get("intent", "GENERAL_QUERY")
        if intent not in VALID_INTENTS:
            intent = "GENERAL_QUERY"

        return {
            "intent": intent,
            "scheme": parsed.get("scheme"),
            "location": parsed.get("location")
        }

    @staticmethod
    def _safe_parse(raw):
        """Groq sometimes wraps JSON in prose/backticks — extract the
        first {...} block defensively before parsing."""
        try:
            return json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            pass

        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass

        return {}
