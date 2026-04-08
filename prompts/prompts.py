import os
from config.config import Config


def read_prompt_file(filename: str) -> str:
    filepath = os.path.join(Config.PROMPTS_DIR, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

class Prompts:
    SEARCH_TOPICS_SYSTEM_PROMPT = read_prompt_file("search_topics_prompt.txt")
    FINAL_ANSWER_SYSTEM_PROMPT = read_prompt_file("system_prompt.txt")
    FINAL_ANSWER_USER_PROMPT = read_prompt_file("user_promt.txt")
    LINK_SELECTION_PROMPT = read_prompt_file("link_prompt.txt")
__all__ = [
    "Prompts"
]
