"""Analytics and habit tracking for Thymer."""

from typing import Dict, List, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.columns import Columns
from datetime import datetime, timedelta
from src.storage import ThymerStorage
from src.timer import format_time


class AnalyticsDisplay:
    """Displays analytics and habit tracking information."""
    
    def __init__(self, storage: ThymerStorage):
        self.storage = storage
        self.console = Console()
    
    def show_daily_summary(self) -> Panel:
        """Show today's summary."""
        today = datetime.now().date().isoformat()
        daily_stats = self.storage.get_daily_stats(1)
        
        if not daily_stats or daily_stats[0].date != today:
            return Panel(
                Text("No activity today", style="dim"),
                title="Today's Summary",
                border_style="blue"
            )
        
        stat = daily_stats[0]
        streak_data = self.storage.get_streak_data()
        
        content = f"""
📊 Sessions: {stat.session_count}
⏱️  Total Time: {format_time(stat.total_time)}
🎯 Timers Used: {', '.join(stat.timer_names)}
🔥 Streak: {streak_data['current_streak']} days
        """.strip()
        
        return Panel(
            content,
            title="Today's Summary",
            border_style="green" if stat.total_time > 0 else "blue"
        )
    
    def show_weekly_summary(self) -> Panel:
        """Show this week's summary."""
        weekly_stats = self.storage.get_daily_stats(7)
        
        if not weekly_stats:
            return Panel(
                Text("No activity this week", style="dim"),
                title="This Week",
                border_style="blue"
            )
        
        total_time = sum(stat.total_time for stat in weekly_stats)
        total_sessions = sum(stat.session_count for stat in weekly_stats)
        active_days = len([s for s in weekly_stats if s.total_time > 0])
        
        content = f"""
📅 Active Days: {active_days}/7
⏱️  Total Time: {format_time(total_time)}
📊 Sessions: {total_sessions}
📈 Avg/Day: {format_time(total_time / 7)}
        """.strip()
        
        return Panel(
            content,
            title="This Week",
            border_style="green" if active_days >= 5 else "yellow"
        )
    
    def show_timer_stats(self) -> Table:
        """Show statistics for all timers."""
        table = Table(title="Timer Statistics (Last 30 Days)")
        table.add_column("Timer", style="cyan")
        table.add_column("Sessions", justify="right")
        table.add_column("Total Time", justify="right")
        table.add_column("Avg Duration", justify="right")
        table.add_column("Active Days", justify="right")
        
        # Get unique timer names from recent sessions
        recent_sessions = self.storage.get_recent_sessions(1000)
        timer_names = list(set(session.timer_name for session in recent_sessions))
        
        for timer_name in sorted(timer_names):
            stats = self.storage.get_timer_stats(timer_name, 30)
            if stats:
                table.add_row(
                    timer_name,
                    str(stats['total_sessions']),
                    format_time(stats['total_time']),
                    format_time(stats['average_duration']),
                    str(stats['active_days'])
                )
        
        return table
    
    def show_habit_streak(self) -> Panel:
        """Show habit streak information."""
        streak_data = self.storage.get_streak_data()
        
        content = f"""
🔥 Current Streak: {streak_data['current_streak']} days
🏆 Longest Streak: {streak_data['longest_streak']} days
📅 Total Active Days: {streak_data['total_days']} days
        """.strip()
        
        # Determine streak status
        if streak_data['current_streak'] >= 7:
            border_style = "green"
            emoji = "🔥"
        elif streak_data['current_streak'] >= 3:
            border_style = "yellow"
            emoji = "⚡"
        else:
            border_style = "red"
            emoji = "💪"
        
        return Panel(
            content,
            title=f"{emoji} Habit Streak",
            border_style=border_style
        )
    
    def show_recent_activity(self) -> Table:
        """Show recent timer sessions."""
        table = Table(title="Recent Activity")
        table.add_column("Time", style="dim")
        table.add_column("Timer", style="cyan")
        table.add_column("Duration", justify="right")
        table.add_column("Laps", justify="right")
        
        recent_sessions = self.storage.get_recent_sessions(10)
        
        for session in recent_sessions:
            time_str = session.start_time.strftime("%H:%M")
            duration_str = format_time(session.duration)
            laps_count = len(session.laps)
            
            table.add_row(
                time_str,
                session.timer_name,
                duration_str,
                str(laps_count)
            )
        
        return table
    
    def show_full_analytics(self):
        """Display comprehensive analytics."""
        self.console.clear()
        
        # Create columns layout
        left_column = [
            self.show_daily_summary(),
            self.show_weekly_summary(),
            self.show_habit_streak()
        ]
        
        right_column = [
            self.show_timer_stats(),
            self.show_recent_activity()
        ]
        
        # Display in columns
        self.console.print(Columns(left_column, equal=True))
        self.console.print()
        self.console.print(Columns(right_column, equal=True))
    
    def export_data(self, filepath: str = None):
        """Export analytics data."""
        if filepath is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"thymer_export_{timestamp}.json"
        
        self.storage.export_data(filepath)
        return filepath
