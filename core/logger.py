import logging
import sys
from core.config import settings


def setup_logger():
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("logs/bot.log", encoding="utf-8"),
        ],
    )


logger = logging.getLogger("tgbot")
