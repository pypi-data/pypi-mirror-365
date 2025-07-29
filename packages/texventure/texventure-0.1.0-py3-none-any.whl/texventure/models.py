"""Data models for Texventure game engine."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Choice:
    """Represents a choice in an event."""

    text: str
    consequences: Dict[str, Any] = field(default_factory=dict)
    requirements: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Event:
    """Represents a game event."""

    id: str
    description: str
    choices: List[Choice] = field(default_factory=list)
    items: List[str] = field(default_factory=list)
    location: str = ""
    act: int = 0
    scene: int = 0
    trigger_choice_idx: int = -1


@dataclass
class GameState:
    """Represents the current game state."""

    current_event: Optional[Event] = None
    inventory: List[str] = field(default_factory=list)
    act: int = 0
    scene: int = 0
    visited_events: List[str] = field(default_factory=list)
    flags: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ActionLogEntry:
    """Represents an action log entry."""

    timestamp: int
    action_type: str
    details: str


@dataclass
class StoryData:
    """Represents the loaded story data."""

    title: str = "Text Adventure"
    setting: str = "Unknown"
    outline: str = ""
    style_genre: str = ""
    acts: List[Dict[str, Any]] = field(default_factory=list)
    npcs: List[Dict[str, Any]] = field(default_factory=list)
    items: Dict[str, Dict[str, Any]] = field(default_factory=dict)
