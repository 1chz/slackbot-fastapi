import logging

from config.environment import CHATGPT_EMAIL, CHATGPT_PASSWORD
from revChatGPT.V1 import Chatbot

login = True
chatbot = None

try:
    chatbot = Chatbot(
        config={
            "email": CHATGPT_EMAIL,
            "password": CHATGPT_PASSWORD,
        }
    )

except Exception as e:
    logging.error(f"[{'login chatgpt':<30}] : {e}")
    login = False
