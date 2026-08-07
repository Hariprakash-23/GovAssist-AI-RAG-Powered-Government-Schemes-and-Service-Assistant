"""
Minimal conversation memory (replaces langchain's
ConversationBufferMemory). Keeps the last N turns per session id.
"""

from collections import defaultdict, deque


class ChatMemory:

    _sessions = defaultdict(lambda: deque(maxlen=6))   # last 6 turns

    @classmethod
    def add_turn(cls, session_id, role, content):
        cls._sessions[session_id].append({"role": role, "content": content})

    @classmethod
    def get_history_text(cls, session_id):
        turns = cls._sessions[session_id]
        if not turns:
            return "(no previous conversation)"

        lines = [f"{t['role'].upper()}: {t['content']}" for t in turns]
        return "\n".join(lines)

    @classmethod
    def reset(cls, session_id):
        cls._sessions[session_id].clear()
