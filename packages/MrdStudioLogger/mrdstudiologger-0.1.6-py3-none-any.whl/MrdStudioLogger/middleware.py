import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from rich.console import Console
from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text
from collections import deque
from typing import Callable, Awaitable
import time

MAX_LOGS = 15
api_logs = deque(maxlen=MAX_LOGS)
ocr_logs = deque(maxlen=MAX_LOGS)

# Rejestrujemy dwa loggery – jeden dla API, drugi dla OCR
def capture_log(record):
    level = record.levelname
    msg = record.getMessage()
    formatted = f"[{record.asctime if hasattr(record, 'asctime') else time.strftime('%H:%M:%S')}] [{level}] {msg}"

    if '[OCR]' in msg or '[PARSE' in msg or '[XLS]' in msg or '[UPLOAD]' in msg:
        ocr_logs.append((level, formatted))
    else:
        api_logs.append((level, formatted))

class RichLoggerMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.console = Console()

        self._patch_loggers()

    def _patch_loggers(self):
        loggers = [
            logging.getLogger("uvicorn.access"),
            logging.getLogger("uvicorn.error"),
            logging.getLogger("uvicorn"),
            logging.getLogger("fastapi"),
            logging.getLogger(),  # root
        ]
        for logger in loggers:
            if not any(isinstance(h, LogCaptureHandler) for h in logger.handlers):
                logger.addHandler(LogCaptureHandler())

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        response = await call_next(request)

        # Renderujemy panel po każdej odpowiedzi
        self.render_log_panels()

        return response

    def render_log_panels(self):
        api_panel = Panel(
            "\n".join([line for _, line in api_logs]) or "[bold cyan]Brak nowych logów API[/]",
            title="API Logs",
            border_style="green",
        )
        ocr_panel = Panel(
            "\n".join([line for _, line in ocr_logs]) or "[bold cyan]Brak nowych logów OCR[/]",
            title="OCR Logs",
            border_style="green",
        )

        self.console.print(Columns([api_panel, ocr_panel]))

class LogCaptureHandler(logging.Handler):
    def emit(self, record: logging.LogRecord):
        try:
            capture_log(record)
        except Exception:
            pass
