"""Timer logic for Thymer."""

import time
from typing import List, Optional
from dataclasses import dataclass, field


@dataclass
class Lap:
    """Represents a lap/split in a timer."""
    duration: float
    timestamp: float


@dataclass
class Timer:
    """Represents a single timer with laps."""
    name: str
    start_time: Optional[float] = None
    elapsed: float = 0.0
    is_running: bool = False
    laps: List[Lap] = field(default_factory=list)
    
    def start(self) -> None:
        """Start or resume the timer."""
        if not self.is_running:
            self.start_time = time.time()
            self.is_running = True
    
    def pause(self) -> None:
        """Pause the timer."""
        if self.is_running and self.start_time is not None:
            self.elapsed += time.time() - self.start_time
            self.start_time = None
            self.is_running = False
    
    def reset(self) -> None:
        """Reset the timer to zero."""
        self.start_time = None
        self.elapsed = 0.0
        self.is_running = False
        self.laps.clear()
    
    def lap(self) -> None:
        """Record a lap/split."""
        current_time = self.get_time()
        last_lap_time = sum(lap.duration for lap in self.laps)
        lap_duration = current_time - last_lap_time
        self.laps.append(Lap(duration=lap_duration, timestamp=current_time))
    
    def get_time(self) -> float:
        """Get the current elapsed time."""
        if self.is_running and self.start_time is not None:
            return self.elapsed + (time.time() - self.start_time)
        return self.elapsed
    
    def toggle(self) -> None:
        """Toggle between running and paused states."""
        if self.is_running:
            self.pause()
        else:
            self.start()


def format_time(seconds: float) -> str:
    """Format seconds into HH:MM:SS.mm format."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:05.2f}"
