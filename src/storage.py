"""Persistent storage system for Thymer analytics and habit tracking."""

import json
import os
from datetime import datetime, date
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import sqlite3


@dataclass
class Session:
    """Represents a timer session."""
    timer_name: str
    start_time: datetime
    end_time: Optional[datetime]
    duration: float
    laps: List[float]
    notes: Optional[str] = None


@dataclass
class DailyStats:
    """Daily statistics for habit tracking."""
    date: str
    total_time: float
    session_count: int
    timer_names: List[str]
    average_session_duration: float


class ThymerStorage:
    """Handles persistent storage for Thymer data."""
    
    def __init__(self):
        self.app_dir = self._get_app_directory()
        self.db_path = self.app_dir / "thymer.db"
        self._ensure_app_directory()
        self._init_database()
    
    def _get_app_directory(self) -> Path:
        """Get the application data directory."""
        home = Path.home()
        
        # Platform-specific paths
        if os.name == 'nt':  # Windows
            app_dir = home / "AppData" / "Local" / "Thymer"
        elif os.name == 'posix':  # macOS/Linux
            if os.uname().sysname == "Darwin":  # macOS
                app_dir = home / "Library" / "Application Support" / "Thymer"
            else:  # Linux
                app_dir = home / ".local" / "share" / "thymer"
        else:
            app_dir = home / ".thymer"
        
        return app_dir
    
    def _ensure_app_directory(self):
        """Create app directory if it doesn't exist."""
        self.app_dir.mkdir(parents=True, exist_ok=True)
    
    def _init_database(self):
        """Initialize SQLite database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timer_name TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    duration REAL NOT NULL,
                    laps TEXT NOT NULL,
                    notes TEXT,
                    created_at TEXT NOT NULL
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS daily_stats (
                    date TEXT PRIMARY KEY,
                    total_time REAL NOT NULL,
                    session_count INTEGER NOT NULL,
                    timer_names TEXT NOT NULL,
                    average_session_duration REAL NOT NULL
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS timer_preferences (
                    timer_name TEXT PRIMARY KEY,
                    color TEXT,
                    default_duration REAL,
                    notes TEXT
                )
            """)
    
    def save_session(self, session: Session):
        """Save a timer session."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO sessions 
                (timer_name, start_time, end_time, duration, laps, notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                session.timer_name,
                session.start_time.isoformat(),
                session.end_time.isoformat() if session.end_time else None,
                session.duration,
                json.dumps(session.laps),
                session.notes,
                datetime.now().isoformat()
            ))
    
    def get_recent_sessions(self, limit: int = 50) -> List[Session]:
        """Get recent timer sessions."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT timer_name, start_time, end_time, duration, laps, notes
                FROM sessions
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,))
            
            sessions = []
            for row in cursor.fetchall():
                sessions.append(Session(
                    timer_name=row[0],
                    start_time=datetime.fromisoformat(row[1]),
                    end_time=datetime.fromisoformat(row[2]) if row[2] else None,
                    duration=row[3],
                    laps=json.loads(row[4]),
                    notes=row[5]
                ))
            
            return sessions
    
    def get_daily_stats(self, days: int = 30) -> List[DailyStats]:
        """Get daily statistics for the last N days."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT 
                    DATE(start_time) as date,
                    SUM(duration) as total_time,
                    COUNT(*) as session_count,
                    GROUP_CONCAT(DISTINCT timer_name) as timer_names,
                    AVG(duration) as avg_duration
                FROM sessions
                WHERE DATE(start_time) >= DATE('now', '-{} days')
                GROUP BY DATE(start_time)
                ORDER BY date DESC
            """.format(days))
            
            stats = []
            for row in cursor.fetchall():
                stats.append(DailyStats(
                    date=row[0],
                    total_time=row[1] or 0,
                    session_count=row[2] or 0,
                    timer_names=row[3].split(',') if row[3] else [],
                    average_session_duration=row[4] or 0
                ))
            
            return stats
    
    def get_timer_stats(self, timer_name: str, days: int = 30) -> Dict[str, Any]:
        """Get statistics for a specific timer."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT 
                    COUNT(*) as total_sessions,
                    SUM(duration) as total_time,
                    AVG(duration) as avg_duration,
                    MIN(duration) as min_duration,
                    MAX(duration) as max_duration,
                    COUNT(DISTINCT DATE(start_time)) as active_days
                FROM sessions
                WHERE timer_name = ? AND DATE(start_time) >= DATE('now', '-{} days')
            """.format(days), (timer_name,))
            
            row = cursor.fetchone()
            if not row:
                return {}
            
            return {
                'total_sessions': row[0],
                'total_time': row[1] or 0,
                'average_duration': row[2] or 0,
                'min_duration': row[3] or 0,
                'max_duration': row[4] or 0,
                'active_days': row[5]
            }
    
    def export_data(self, filepath: str):
        """Export all data to JSON file."""
        data = {
            'sessions': [asdict(session) for session in self.get_recent_sessions(1000)],
            'daily_stats': [asdict(stat) for stat in self.get_daily_stats(365)],
            'export_date': datetime.now().isoformat()
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def get_streak_data(self) -> Dict[str, Any]:
        """Calculate habit streaks."""
        daily_stats = self.get_daily_stats(365)
        
        if not daily_stats:
            return {'current_streak': 0, 'longest_streak': 0, 'total_days': 0}
        
        # Calculate current streak
        current_streak = 0
        today = date.today()
        
        for stat in daily_stats:
            stat_date = datetime.fromisoformat(stat.date).date()
            if stat_date == today or stat_date == today.replace(day=today.day-1):
                current_streak += 1
            else:
                break
        
        # Calculate longest streak
        longest_streak = 0
        temp_streak = 0
        
        for stat in daily_stats:
            if stat.total_time > 0:
                temp_streak += 1
                longest_streak = max(longest_streak, temp_streak)
            else:
                temp_streak = 0
        
        return {
            'current_streak': current_streak,
            'longest_streak': longest_streak,
            'total_days': len([s for s in daily_stats if s.total_time > 0])
        }
