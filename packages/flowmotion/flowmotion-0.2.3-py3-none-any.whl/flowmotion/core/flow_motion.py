from datetime import datetime
from enum import Enum


class FlowMotion:
    """
    Base class for flowmotion objects providing action types and logging.
    """

    class FlowAction(Enum):
        ADD = "ADD"
        PLAY = "PLAY"
        SKIP = "SKIP"
        REMOVE = "REMOVE"

    _log_file_path = "flowmotion.log"

    @classmethod
    def log(cls, message: str):
        """
        Log a message with timestamp and class name to the flowmotion log file.

        Args:
            message (str): The message to log.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] [{cls.__name__}] {message}"

        with open(cls._log_file_path, "a") as f:
            f.write(log_line + "\n")
