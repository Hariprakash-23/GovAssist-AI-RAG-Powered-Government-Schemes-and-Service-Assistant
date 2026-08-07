from app.chatbot.rag import GovernmentRAG


class SchemeService:

    def __init__(self):
        self.chatbot = GovernmentRAG()

    def get_scheme_information(self, question, session_id="default"):
        result = self.chatbot.ask(question, session_id=session_id)
        return result["answer"]
