from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from logger import get_ocr_logs
import logging

console = Console()

class RichLoggerMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        self.render_logs()
        return response

    def render_logs(self):
        ocr_logs = get_ocr_logs()

        # Prawa kolumna: OCR Logs
        ocr_table = Table(show_header=False, expand=True, box=None)
        for entry in ocr_logs:
            level = entry["level"]
            color = "lightgray" if level == "DEBUG" else "cyan" if level == "INFO" else "red"
            line = f"[{color}][{entry['time']}] [{level}] {entry['message']}[/{color}]"
            ocr_table.add_row(line)

        ocr_panel = Panel(ocr_table, title="OCR Logs", border_style="green", expand=True)

        # Lewa kolumna: API Logs placeholder
        api_table = Table(show_header=False, expand=True, box=None)
        api_table.add_row("[cyan]Brak nowych logów API[/cyan]")  # Tu można rozbudować
        api_panel = Panel(api_table, title="API Logs", border_style="green", expand=True)

        # Wyświetlenie jako 2 kolumny
        console.print(Columns([api_panel, ocr_panel], expand=True))
