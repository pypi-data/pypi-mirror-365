from datetime import datetime
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from rich.console import Console
from rich.table import Table
from rich.text import Text

from logger import _ocr_logs_buffer_ctx  # WAŻNE

class RichLoggerMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, get_ocr_logs: Callable[[], list]):
        super().__init__(app)
        self.console = Console()
        self.get_ocr_logs = get_ocr_logs

    async def dispatch(self, request: Request, call_next) -> Response:
        _ocr_logs_buffer_ctx.set([])  # inicjalizacja kontekstu per request
        start_time = datetime.now()
        response: Response = await call_next(request)
        end_time = datetime.now()

        # === Access log
        status_code = response.status_code
        path = request.url.path
        time_str = end_time.strftime("%d-%m-%Y %H:%M:%S")

        code_style = (
            "green" if 200 <= status_code < 300
            else "yellow" if 400 <= status_code < 500
            else "red"
        )
        access_log = Text(f"[{time_str}] [", style="white")
        access_log.append(str(status_code), style=code_style)
        access_log.append(f"] {path}", style="white")

        # === OCR logs
        ocr_logs = self.get_ocr_logs()
        ocr_texts = []
        for level, msg in ocr_logs:
            level_style = {
                "INFO": "cyan",
                "WARNING": "yellow",
                "ERROR": "bold red"
            }.get(level, "white")
            ocr_msg = Text(f"[{time_str}] [", style="white")
            ocr_msg.append(level, style=level_style)
            ocr_msg.append(f"] {msg}", style="white")
            ocr_texts.append(ocr_msg)

        # === Output table
        table = Table.grid(expand=True)
        table.add_column(justify="left", ratio=1)
        table.add_column(justify="left", ratio=1)

        max_len = max(len(ocr_texts), 1)
        for i in range(max_len):
            left = access_log if i == 0 else ""
            right = ocr_texts[i] if i < len(ocr_texts) else ""
            table.add_row(left, right)

        self.console.print(table)
        return response
