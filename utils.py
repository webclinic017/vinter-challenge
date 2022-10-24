import logging
import sys
from datetime import datetime
from os import path
from pathlib import Path
from typing import Optional

from config import LOG_TO_FILE, LOGGING_LEVEL


def logging_setup(log_file_prefix: str = "") -> Optional[str]:
    """
    Logging setting. Only console or console + time.log file.

    :param log_file_prefix: String prefix for the log file.
    :return: If LOG_TO_FILE -> returns name of the log file.
    """
    if LOG_TO_FILE:
        destination: Path = Path("./logs")
        Path(destination).mkdir(parents=True, exist_ok=True)

        # Check if it has .gitignore file. If not -> create it.
        if not path.isfile(destination / ".gitignore"):
            with open(destination / ".gitignore", "w") as gitignore_file:
                gitignore_file.write("*\n* /\n!.gitignore\n")

        log_prefix: str = f"{log_file_prefix}-" if log_file_prefix else ""
        log_file_name: str = (
            f"{log_prefix}{str(datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))}.log"
        )
        logging.basicConfig(
            level=LOGGING_LEVEL,
            format="%(asctime)s | %(levelname)-7s | %(filename)s:%(lineno)d | %(message)s",
            handlers=[
                logging.FileHandler(destination / log_file_name),
                logging.StreamHandler(sys.stdout),
            ],
            force=True,
        )
        return log_file_name
    else:
        logging.basicConfig(
            level=LOGGING_LEVEL,
            format="%(asctime)s | %(levelname)-7s | %(filename)s:%(lineno)d | %(message)s",
            handlers=[logging.StreamHandler(sys.stdout)],
            force=True,
        )
        return None
