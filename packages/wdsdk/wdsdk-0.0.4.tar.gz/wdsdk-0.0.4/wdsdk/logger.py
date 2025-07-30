from enum import Enum


class LogLevel(Enum):
    OFF = 0
    INFO = 10


class Logger:
    def __init__(self, logLevel):
        self.logLevel = logLevel

    def info(self, message):
        if self.logLevel == LogLevel.INFO:
            return
        print(f"[INFO] {message}")
