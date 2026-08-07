"""
Plain string prompt templates (no langchain ChatPromptTemplate).
"""

RAG_PROMPT = """You are an AI Government Services Assistant.

Your job is to answer ONLY from the supplied government documents.

If the answer is unavailable in the context, politely reply:
"I couldn't find that information in the available government documents."

Never make up information.

-------------------------
Context:
{context}
-------------------------
Conversation so far:
{history}
-------------------------
Citizen Question:
{question}
-------------------------
Helpful Answer:
"""


# Multi-shot (few-shot) prompt for intent + slot extraction, replacing
# the old keyword-matching IntentClassifier / spaCy SlotExtractor.
# The model must reply with ONLY a JSON object.
INTENT_PROMPT = """Classify the citizen's message into one intent and extract slots.
Reply with ONLY a JSON object like: {{"intent": "...", "scheme": "... or null", "location": "... or null"}}

Valid intents: ELIGIBILITY, DOCUMENTS, APPLICATION, BENEFITS, CSC_LOCATION, SCHEME_INFO, GENERAL_QUERY

Example 1:
Message: "Am I eligible for PM-KISAN if I own 2 acres of land?"
Output: {{"intent": "ELIGIBILITY", "scheme": "pm kisan", "location": null}}

Example 2:
Message: "Where is the nearest CSC center in Chennai?"
Output: {{"intent": "CSC_LOCATION", "scheme": null, "location": "Chennai"}}

Example 3:
Message: "What documents do I need for Ayushman Bharat?"
Output: {{"intent": "DOCUMENTS", "scheme": "ayushman bharat", "location": null}}

Example 4:
Message: "Tell me about PM Vishwakarma scheme."
Output: {{"intent": "SCHEME_INFO", "scheme": "pm vishwakarma", "location": null}}

Now classify this:
Message: "{message}"
Output:"""


# Chain-of-thought explanation for eligibility results — the yes/no
# decision still comes from the deterministic EligibilityService rules
# (never let the LLM invent eligibility), but we use CoT-style
# prompting to turn that verdict into a clear, step-by-step citizen
# explanation.
ELIGIBILITY_EXPLANATION_PROMPT = """A citizen asked about eligibility for the "{scheme}" scheme.
Their answers were: {answers}
The eligibility engine determined: {verdict}

Explain this result to the citizen in simple terms. Let's think step by step:
1. Restate the relevant eligibility rule(s) in plain language.
2. Walk through how their answers map onto each rule.
3. Give the final verdict clearly, and if not eligible, mention what would need to change.

Explanation:"""
