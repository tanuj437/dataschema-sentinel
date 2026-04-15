"""Terminal output alerter using Rich."""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from sentinel.alerts.base import BaseAlerter
from sentinel.detector.drift import DriftEvent, DriftSeverity
from sentinel.store.models import SchemaSnapshot


SEVERITY_STYLE = {
    DriftSeverity.BREAKING: ("bold red", "BREAKING"),
    DriftSeverity.WARNING: ("yellow", "WARNING"),
    DriftSeverity.INFO: ("dim", "INFO"),
}


class TerminalAlerter(BaseAlerter):
    """Alert renderer for terminal output using Rich."""

    def __init__(self, console: Console | None = None):
        """Initialize terminal alerter.

        Args:
            console: Rich Console instance (creates new if None)
        """
        self.console = console or Console()

    def alert(
        self,
        name: str,
        old_snapshot: SchemaSnapshot,
        new_snapshot: SchemaSnapshot,
        events: list[DriftEvent],
    ) -> None:
        """Render drift report to terminal.

        Args:
            name: Schema name
            old_snapshot: Previous snapshot
            new_snapshot: Current snapshot
            events: List of drift events
        """
        if not events:
            self.console.print(
                f"\n[green]✓[/green] No schema drift detected in [bold]{name}[/bold]\n"
            )
            return

        table = Table(box=box.ROUNDED, show_header=True, header_style="bold", expand=True)
        table.add_column("Severity", width=10)
        table.add_column("Column", width=22)
        table.add_column("Rule", width=22)
        table.add_column("Change")

        for event in events:
            style, label = SEVERITY_STYLE[event.severity]
            col_display = event.column or "(table)"
            change = (
                f"{event.old_value} → {event.new_value}"
                if event.old_value or event.new_value
                else event.message
            )
            table.add_row(f"[{style}]{label}[/]", col_display, event.rule, change)

        breaking = sum(1 for e in events if e.severity == DriftSeverity.BREAKING)
        warnings = sum(1 for e in events if e.severity == DriftSeverity.WARNING)
        infos = sum(1 for e in events if e.severity == DriftSeverity.INFO)

        title = (
            f"[bold]Schema drift detected: {name}[/bold]  "
            f"v{old_snapshot.version} → v{new_snapshot.version}"
        )
        self.console.print(Panel(table, title=title))

        parts = []
        if breaking:
            parts.append(f"[bold red]{breaking} BREAKING[/]")
        if warnings:
            parts.append(f"[yellow]{warnings} WARNING[/]")
        if infos:
            parts.append(f"[dim]{infos} INFO[/]")
        self.console.print("  " + " · ".join(parts) + "\n")
