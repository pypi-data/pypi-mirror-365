from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from typing import Callable, Awaitable

from rich.console import Console, Group
from rich.panel import Panel
from rich.text import Text
from rich.box import ROUNDED

console = Console()


class RichLoggerMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, get_ocr_logs: Callable[[], list]):
        super().__init__(app)
        self.get_ocr_logs = get_ocr_logs

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable]):
        response = await call_next(request)

        logs = self.get_ocr_logs()
        logs = logs[-15:]  # ostatnie 15 wpisów

        if logs:
            log_texts = []

            for entry in logs:
                level = entry["level"]
                message = entry["message"]
                time = entry["time"]

                style = {
                    "DEBUG": "lightgray",
                    "INFO": "white",
                    "WARNING": "yellow",
                    "ERROR": "bold red"
                }.get(level, "white")

                timestamp = Text(f"[{time}] ", style="lightgray")
                level_text = Text(f"[{level}] ", style=style)
                message_text = Text(message, style=style)

                log_texts.append(Text.assemble(timestamp, level_text, message_text))

            log_group = Group(*log_texts)

            console.print(Panel(
                log_group,
                title="[bold green]OCR Logs",
                border_style="green",
                padding=(1, 2),
                box=ROUNDED
            ))

        return response
