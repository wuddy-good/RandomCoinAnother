import logging

# Установка уровня логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s (%(asctime)s) (Line: %(lineno)d) [%(filename)s] : %(message)s ",
    datefmt="%d/%m/%Y %I:%M:%S",
    encoding="utf-8",
    filemode="w",
)

# Создание логгера
logger = logging.getLogger(__name__)
file_handler = logging.FileHandler(
    "bot_logs.log",
    encoding="utf-8",
)

file_formatter = logging.Formatter(
    "%(levelname)s (%(asctime)s): %(message)s (Line: %(lineno)d) [%(filename)s]"
)
file_handler.setFormatter(file_formatter)

logger.addHandler(file_handler)
#
# console_handler = logging.StreamHandler()
# console_handler.setLevel(logging.INFO)
# logger.addHandler(console_handler)
