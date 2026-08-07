from app.chatbot.intent_llm import IntentLLM

from app.services.scheme_service import SchemeService
from app.services.csc_locator import CSCLocator

from app.api.schemas import ChatResponse


class ChatController:

    def __init__(self):
        self.scheme_service = SchemeService()
        self.csc = CSCLocator()

    def chat(self, question, session_id="default"):

        classification = IntentLLM.classify(question)
        intent = classification["intent"]

        # --------------------------
        # Scheme Information (RAG)
        # --------------------------
        if intent == "SCHEME_INFO":
            answer = self.scheme_service.get_scheme_information(question, session_id)
            return ChatResponse(
                success=True,
                intent=intent,
                answer=answer,
                scheme=classification.get("scheme")
            ).to_dict()

        # --------------------------
        # CSC
        # --------------------------
        if intent == "CSC_LOCATION":
            city = classification.get("location")

            if city is None:
                return ChatResponse(
                    success=False,
                    intent=intent,
                    answer="Please provide your city."
                ).to_dict()

            centers = self.csc.search(city)

            if len(centers) == 0:
                return ChatResponse(
                    success=False,
                    intent=intent,
                    answer="No CSC found.",
                    location=city
                ).to_dict()

            center = centers[0]
            answer = f"""
CSC Name : {center['name']}
Address : {center['address']}
Phone : {center['phone']}
"""
            return ChatResponse(
                success=True,
                intent=intent,
                answer=answer,
                location=city
            ).to_dict()

        # --------------------------
        # Default -> fall back to RAG over the scheme knowledge base
        # (covers ELIGIBILITY / DOCUMENTS / APPLICATION / BENEFITS /
        # GENERAL_QUERY — the vector store context usually answers these)
        # --------------------------
        answer = self.scheme_service.get_scheme_information(question, session_id)

        return ChatResponse(
            success=True,
            intent=intent,
            answer=answer,
            scheme=classification.get("scheme")
        ).to_dict()
