"""Main Thymer application with TUI."""

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Label
from textual.containers import Container, VerticalScroll
from textual.binding import Binding
from textual import on
from textual.reactive import reactive
from rich.text import Text
from rich.panel import Panel
from rich.table import Table
from typing import List
import asyncio
from datetime import datetime

from src.timer import Timer, format_time
from src.storage import ThymerStorage, Session
from src.analytics import AnalyticsDisplay


class TimerDisplay(Static):
    """Widget to display a single timer."""
    
    timer: Timer = reactive(None)  # type: ignore
    is_selected: bool = reactive(False)
    
    def __init__(self, timer: Timer, **kwargs) -> None:
        super().__init__(**kwargs)
        self.timer = timer
    
    def render(self) -> Panel:
        """Render the timer display."""
        current_time = self.timer.get_time()
        time_str = format_time(current_time)
        
        # Status indicator
        status = "▶ RUNNING" if self.timer.is_running else "⏸ PAUSED"
        status_color = "green" if self.timer.is_running else "yellow"
        
        # Build the display table
        table = Table.grid(padding=(0, 2))
        table.add_column(style="bold cyan", width=20)
        table.add_column(width=30)
        
        table.add_row("Timer:", self.timer.name)
        table.add_row("Time:", f"[bold white]{time_str}[/]")
        table.add_row("Status:", f"[{status_color}]{status}[/]")
        
        if self.timer.laps:
            table.add_row("", "")
            table.add_row("[bold]Laps:", f"[bold]{len(self.timer.laps)} recorded[/]")
            for idx, lap in enumerate(self.timer.laps[-3:], start=max(1, len(self.timer.laps) - 2)):
                lap_time = format_time(lap.duration)
                table.add_row(f"  Lap {idx}:", lap_time)
        
        # Panel style based on selection
        border_style = "bold blue" if self.is_selected else "dim"
        title_style = "bold" if self.is_selected else ""
        
        return Panel(
            table,
            border_style=border_style,
            title=f"[{title_style}]{'→ ' if self.is_selected else ''}{self.timer.name}[/]",
            subtitle=f"[dim]Laps: {len(self.timer.laps)}[/]" if self.timer.laps else None,
        )


class ThymerApp(App):
    """Main Thymer TUI application."""
    
    CSS = """
    Screen {
        background: $surface;
    }
    
    #timers_container {
        height: 100%;
        padding: 1 2;
    }
    
    TimerDisplay {
        margin: 1 0;
        height: auto;
    }
    
    Footer {
        background: $primary;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
        Binding("space", "toggle", "Play/Pause"),
        Binding("l", "lap", "Lap"),
        Binding("r", "reset", "Reset"),
        Binding("n", "new_timer", "New Timer"),
        Binding("up", "prev_timer", "↑ Prev"),
        Binding("down", "next_timer", "↓ Next"),
        Binding("d", "delete_timer", "Delete"),
        Binding("a", "show_analytics", "Analytics"),
        Binding("e", "export_data", "Export"),
        Binding("?", "show_help", "Help"),
    ]
    
    timers: List[Timer] = []
    selected_index: int = 0
    
    def __init__(self):
        super().__init__()
        # Create initial timer
        self.timers = [Timer(name="Timer 1")]
        self.selected_index = 0
        self._update_task = None
        
        # Initialize storage and analytics
        self.storage = ThymerStorage()
        self.analytics = AnalyticsDisplay(self.storage)
    
    def compose(self) -> ComposeResult:
        """Compose the TUI layout."""
        yield Header(show_clock=True)
        with VerticalScroll(id="timers_container"):
            for idx, timer in enumerate(self.timers):
                display = TimerDisplay(timer, id=f"timer_{idx}")
                display.is_selected = (idx == self.selected_index)
                yield display
        yield Footer()
    
    async def on_mount(self) -> None:
        """Set up the app when mounted."""
        self.title = "Thymer - Developer Timer"
        self.sub_title = "Productivity Timer for Developers"
        # Start update loop
        self._update_task = asyncio.create_task(self._update_loop())
    
    async def _update_loop(self) -> None:
        """Continuously update timer displays."""
        while True:
            await asyncio.sleep(0.05)  # Update every 50ms
            for child in self.query(TimerDisplay):
                child.refresh()
    
    def action_toggle(self) -> None:
        """Toggle the selected timer."""
        if self.timers:
            self.timers[self.selected_index].toggle()
            self._update_displays()
    
    def action_lap(self) -> None:
        """Record a lap for the selected timer."""
        if self.timers:
            timer = self.timers[self.selected_index]
            if timer.get_time() > 0:  # Only lap if timer has time
                timer.lap()
                self._update_displays()
    
    def action_reset(self) -> None:
        """Reset the selected timer."""
        if self.timers:
            timer = self.timers[self.selected_index]
            
            # Save session if timer has been used
            if timer.get_time() > 0 and timer.session_start:
                try:
                    session = Session(
                        timer_name=timer.name,
                        start_time=timer.session_start,
                        end_time=datetime.now(),
                        duration=timer.get_time(),
                        laps=[lap.duration for lap in timer.laps]
                    )
                    self.storage.save_session(session)
                except Exception as e:
                    self.notify(f"Failed to save session: {e}", title="Warning", timeout=3)
            
            timer.reset()
            self._update_displays()
    
    def action_new_timer(self) -> None:
        """Create a new timer."""
        timer_num = len(self.timers) + 1
        new_timer = Timer(name=f"Timer {timer_num}")
        self.timers.append(new_timer)
        self.selected_index = len(self.timers) - 1
        self._rebuild_displays()
    
    def action_delete_timer(self) -> None:
        """Delete the selected timer."""
        if len(self.timers) > 1:  # Keep at least one timer
            del self.timers[self.selected_index]
            self.selected_index = min(self.selected_index, len(self.timers) - 1)
            self._rebuild_displays()
    
    def action_prev_timer(self) -> None:
        """Select the previous timer."""
        if self.timers:
            self.selected_index = (self.selected_index - 1) % len(self.timers)
            self._update_selection()
    
    def action_next_timer(self) -> None:
        """Select the next timer."""
        if self.timers:
            self.selected_index = (self.selected_index + 1) % len(self.timers)
            self._update_selection()
    
    def action_show_analytics(self) -> None:
        """Show analytics and habit tracking."""
        try:
            self.analytics.show_full_analytics()
            input("\nPress Enter to return to timer...")
        except Exception as e:
            self.notify(f"Error showing analytics: {e}", title="Error", timeout=5)
    
    def action_export_data(self) -> None:
        """Export analytics data."""
        try:
            filepath = self.analytics.export_data()
            self.notify(f"Data exported to: {filepath}", title="Export Complete", timeout=5)
        except Exception as e:
            self.notify(f"Export failed: {e}", title="Error", timeout=5)
    
    def action_show_help(self) -> None:
        """Show help information."""
        help_text = """
        Thymer - Keyboard Shortcuts
        
        Space : Play/Pause timer
        L     : Record lap/split
        R     : Reset timer
        N     : Create new timer
        D     : Delete timer (min 1)
        ↑/↓   : Navigate timers
        A     : Show analytics
        E     : Export data
        ?     : Show this help
        Q     : Quit application
        """
        self.notify(help_text, title="Help", timeout=10)
    
    def _update_selection(self) -> None:
        """Update which timer is selected."""
        for idx, display in enumerate(self.query(TimerDisplay)):
            display.is_selected = (idx == self.selected_index)
    
    def _update_displays(self) -> None:
        """Refresh all timer displays."""
        for display in self.query(TimerDisplay):
            display.refresh()
    
    def _rebuild_displays(self) -> None:
        """Rebuild all timer displays (for add/delete)."""
        container = self.query_one("#timers_container")
        container.remove_children()
        for idx, timer in enumerate(self.timers):
            display = TimerDisplay(timer, id=f"timer_{idx}")
            display.is_selected = (idx == self.selected_index)
            container.mount(display)


def main() -> None:
    """Entry point for the Thymer application."""
    app = ThymerApp()
    app.run()


if __name__ == "__main__":
    main()
