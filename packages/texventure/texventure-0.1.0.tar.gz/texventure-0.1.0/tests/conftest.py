"""Fixtures and utilities for testing."""

import json
from unittest.mock import Mock

import pytest

from src.texventure.engine import GameEngine
from src.texventure.event_generators import (LLMEventGenerator,
                                             TemplateEventGenerator)
from src.texventure.models import (ActionLogEntry, Choice, Event, GameState,
                                   StoryData)
from src.texventure.save_manager import SaveLoadManager


@pytest.fixture
def sample_story_data():
    """Sample story data for testing."""
    return {
        "title": "Test Adventure",
        "setting": "A test world",
        "outline": "A simple test story",
        "acts": [
            {
                "name": "Act 1",
                "description": "The beginning",
                "scenes": [
                    {
                        "name": "Scene 1",
                        "description": "The starting scene",
                        "location": "Starting location",
                    },
                    {
                        "name": "Scene 2",
                        "description": "The second scene",
                        "location": "Second location",
                    },
                ],
            },
            {
                "name": "Act 2",
                "description": "The middle",
                "scenes": [
                    {
                        "name": "Scene 3",
                        "description": "The third scene",
                        "location": "Third location",
                    }
                ],
            },
        ],
        "npcs": [
            {"name": "Test NPC", "description": "A test character", "role": "helper"}
        ],
        "items": {
            "sword": {"name": "Magic Sword", "description": "A gleaming sword"},
            "potion": {"name": "Health Potion", "description": "Restores health"},
        },
    }


@pytest.fixture
def sample_saved_game_data(sample_story_data):
    """Sample saved game data for testing."""
    saved_data = sample_story_data.copy()
    saved_data.update(
        {
            "is_saved_game": True,
            "saved_at": 5,
            "event_counter": 5,
            "current_event": {
                "id": "event_4",
                "description": "You are in a saved location",
                "choices": [
                    {"text": "Continue forward"},
                    {"text": "Look around"},
                    {"text": "Rest"},
                    {"text": "Check inventory"},
                ],
                "items": ["sword"],
                "location": "Saved location",
                "act": 0,
                "scene": 1,
            },
            "event_history": [
                {
                    "id": "event_0",
                    "description": "The beginning",
                    "choices": [{"text": "Start"}, {"text": "Wait"}],
                    "items": [],
                    "location": "Start",
                    "act": 0,
                    "scene": 0,
                },
                {
                    "id": "event_1",
                    "description": "You started the adventure",
                    "choices": [{"text": "Go north"}, {"text": "Go south"}],
                    "items": ["potion"],
                    "location": "Crossroads",
                    "act": 0,
                    "scene": 0,
                },
            ],
            "action_log": [
                {
                    "timestamp": 0,
                    "action_type": "make_choice",
                    "details": "Made choice: Start",
                },
                {
                    "timestamp": 1,
                    "action_type": "update_state",
                    "details": "Moved to event: event_1",
                },
            ],
            "game_state": {
                "inventory": ["potion"],
                "act": 0,
                "scene": 1,
                "visited_events": ["event_0", "event_1"],
                "flags": {"started": True},
            },
        }
    )
    return saved_data


@pytest.fixture
def sample_choice():
    """Sample choice for testing."""
    return Choice("Test choice")


@pytest.fixture
def sample_event():
    """Sample event for testing."""
    choices = [
        Choice("Option 1"),
        Choice("Option 2"),
        Choice("Option 3"),
        Choice("Option 4"),
    ]
    return Event(
        id="test_event",
        description="A test event",
        choices=choices,
        items=["sword"],
        location="Test location",
        act=0,
        scene=0,
    )


@pytest.fixture
def sample_game_state():
    """Sample game state for testing."""
    return GameState(
        inventory=["potion"],
        act=0,
        scene=0,
        visited_events=["event_0"],
        flags={"test": True},
    )


@pytest.fixture
def sample_action_log_entry():
    """Sample action log entry for testing."""
    return ActionLogEntry(
        timestamp=1, action_type="test_action", details="Test action details"
    )


@pytest.fixture
def mock_llm_response():
    """Mock LLM response for testing."""
    return json.dumps(
        {
            "description": "A mysterious forest path winds before you, shrouded in mist.",
            "location": "Misty Forest Path",
            "choices": [
                {"text": "Follow the path deeper into the forest"},
                {"text": "Examine the strange markings on nearby trees"},
                {"text": "Call out to see if anyone responds"},
                {"text": "Turn back to safety"},
            ],
        }
    )


@pytest.fixture
def game_engine():
    """Game engine instance for testing."""
    return GameEngine(use_llm=False)


@pytest.fixture
def game_engine_with_llm():
    """Game engine instance with LLM enabled for testing."""
    return GameEngine(use_llm=True)


@pytest.fixture
def template_event_generator():
    """Template event generator for testing."""
    return TemplateEventGenerator()


@pytest.fixture
def mock_llm_event_generator():
    """Mock LLM event generator for testing."""
    generator = Mock(spec=LLMEventGenerator)
    return generator


@pytest.fixture
def save_manager():
    """Save manager instance for testing."""
    return SaveLoadManager()
