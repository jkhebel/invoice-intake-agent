from rich.console import Console
from rich.theme import Theme


THEME = Theme(
    {
        "orch": "bold blue",
        "invoice": "bold green",
        "guardrail": "bold red",
        "error": "bold red",
        "sys": "yellow",
        "dim": "dim",
        "notify": "bold green",
    }
)

console = Console(theme=THEME)
