"""
Eligibility verdicts stay 100% rule-based/deterministic — we never
let the LLM decide eligibility. Gen AI (Groq, chain-of-thought style
prompting) is only used afterwards, to turn the verdict into a
clear, step-by-step explanation for the citizen.
"""

from app.models.groq_client import GroqModel
from app.chatbot.prompts import ELIGIBILITY_EXPLANATION_PROMPT


class EligibilityService:

    def pm_kisan(self, answers):
        if answers["land_owner"] == "yes" and answers["income_tax"] == "no":
            return {
                "eligible": True,
                "message": "Based on the provided information, you appear eligible for PM-KISAN."
            }

        return {
            "eligible": False,
            "message": "Based on the provided information, you may not be eligible for PM-KISAN."
        }

    def evaluate(self, scheme, answers, explain=False):
        scheme_key = scheme.lower()

        if scheme_key == "pm kisan":
            result = self.pm_kisan(answers)
        else:
            result = {
                "eligible": False,
                "message": "Eligibility rules are not available."
            }

        if explain:
            result["explanation"] = self._explain(scheme, answers, result)

        return result

    def _explain(self, scheme, answers, result):
        prompt = ELIGIBILITY_EXPLANATION_PROMPT.format(
            scheme=scheme,
            answers=answers,
            verdict="ELIGIBLE" if result["eligible"] else "NOT ELIGIBLE"
        )
        return GroqModel.chat(prompt, temperature=0.3, max_tokens=300)
