import logging

logger = logging.getLogger("chat_logger")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler("/app/logs/chat.log", mode="a", encoding="utf-8")
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)
