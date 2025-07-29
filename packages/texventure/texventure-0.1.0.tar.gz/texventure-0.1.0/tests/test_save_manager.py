"""Tests for save manager."""

import json
import os
import tempfile
from unittest.mock import mock_open, patch

import pytest

from src.texventure.models import (ActionLogEntry, Choice, Event, GameState,
                                   StoryData)
from src.texventure.save_manager import SaveLoadManager


class TestSaveLoadManager:
    """Test cases for SaveLoadManager."""

    def test_save_game_success(self, save_manager, sample_story_data):
        """Test successful game saving."""
        story_data = StoryData(
            title="Test Game",
            setting="Test World",
            outline="Test outline",
            acts=sample_story_data["acts"],
            npcs=sample_story_data["npcs"],
            items=sample_story_data["items"],
        )

        current_event = Event(
            id="current_event",
            description="Current event description",
            choices=[Choice("Choice 1"), Choice("Choice 2")],
            items=["sword"],
            location="Current location",
            act=0,
            scene=1,
        )

        game_state = GameState(
            current_event=current_event,
            inventory=["potion"],
            act=0,
            scene=1,
            visited_events=["event_0", "current_event"],
            flags={"started": True},
        )

        event_history = [
            Event("event_0", "First event", [Choice("Start")]),
            current_event,
        ]

        action_log = [
            ActionLogEntry(0, "start_game", "Game started"),
            ActionLogEntry(1, "make_choice", "Made choice: Start"),
        ]

        event_counter = 2

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            filename = f.name

        try:
            success, message = save_manager.save_game(
                filename,
                story_data,
                game_state,
                event_history,
                action_log,
                event_counter,
            )

            assert success is True
            assert "Game saved to" in message
            assert filename in message

            # Verify file was created and contains expected data
            assert os.path.exists(filename)

            with open(filename, "r") as f:
                saved_data = json.load(f)

            # Check story data
            assert saved_data["title"] == "Test Game"
            assert saved_data["setting"] == "Test World"
            assert saved_data["outline"] == "Test outline"
            assert saved_data["acts"] == sample_story_data["acts"]
            assert saved_data["npcs"] == sample_story_data["npcs"]
            assert saved_data["items"] == sample_story_data["items"]

            # Check save metadata
            assert saved_data["is_saved_game"] is True
            assert saved_data["saved_at"] == event_counter
            assert saved_data["event_counter"] == event_counter

            # Check current event
            current_event_data = saved_data["current_event"]
            assert current_event_data["id"] == "current_event"
            assert current_event_data["description"] == "Current event description"
            assert len(current_event_data["choices"]) == 2
            assert current_event_data["choices"][0]["text"] == "Choice 1"
            assert current_event_data["items"] == ["sword"]
            assert current_event_data["location"] == "Current location"
            assert current_event_data["act"] == 0
            assert current_event_data["scene"] == 1

            # Check event history
            assert len(saved_data["event_history"]) == 2
            assert saved_data["event_history"][0]["id"] == "event_0"
            assert saved_data["event_history"][1]["id"] == "current_event"

            # Check action log
            assert len(saved_data["action_log"]) == 2
            assert saved_data["action_log"][0]["action_type"] == "start_game"
            assert saved_data["action_log"][1]["action_type"] == "make_choice"

            # Check game state
            game_state_data = saved_data["game_state"]
            assert game_state_data["inventory"] == ["potion"]
            assert game_state_data["act"] == 0
            assert game_state_data["scene"] == 1
            assert game_state_data["visited_events"] == ["event_0", "current_event"]
            assert game_state_data["flags"] == {"started": True}

        finally:
            if os.path.exists(filename):
                os.unlink(filename)

    def test_save_game_no_story_data(self, save_manager):
        """Test saving game with no story data."""
        success, message = save_manager.save_game(
            "test.json", None, GameState(), [], [], 0
        )

        assert success is False
        assert "No story data to save" in message

    def test_save_game_no_current_event(self, save_manager):
        """Test saving game with no current event."""
        story_data = StoryData(title="Test")
        game_state = GameState()  # No current event

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            filename = f.name

        try:
            success, message = save_manager.save_game(
                filename, story_data, game_state, [], [], 0
            )

            assert success is True

            with open(filename, "r") as f:
                saved_data = json.load(f)

            assert saved_data["current_event"] is None

        finally:
            if os.path.exists(filename):
                os.unlink(filename)

    @patch("builtins.open", side_effect=PermissionError("Permission denied"))
    def test_save_game_file_error(self, mock_file, save_manager):
        """Test saving game with file write error."""
        story_data = StoryData(title="Test")

        success, message = save_manager.save_game(
            "test.json", story_data, GameState(), [], [], 0
        )

        assert success is False
        assert "Error saving game" in message
        assert "Permission denied" in message

    def test_load_saved_game_complete(self, save_manager, sample_saved_game_data):
        """Test loading a complete saved game."""
        game_state, event_history, action_log, event_counter = (
            save_manager.load_saved_game(sample_saved_game_data)
        )

        # Check event counter
        assert event_counter == 5

        # Check game state
        assert game_state.inventory == ["potion"]
        assert game_state.act == 0
        assert game_state.scene == 1
        assert game_state.visited_events == ["event_0", "event_1"]
        assert game_state.flags == {"started": True}

        # Check current event (should be set to last event in history)
        assert game_state.current_event is not None
        assert game_state.current_event.id == "event_1"
        assert game_state.current_event.description == "You started the adventure"
        assert len(game_state.current_event.choices) == 2
        assert game_state.current_event.items == ["potion"]
        assert game_state.current_event.location == "Crossroads"

        # Check event history
        assert len(event_history) == 2
        assert event_history[0].id == "event_0"
        assert event_history[0].description == "The beginning"
        assert len(event_history[0].choices) == 2
        assert event_history[0].choices[0].text == "Start"
        assert event_history[0].items == []
        assert event_history[0].location == "Start"
        assert event_history[0].act == 0
        assert event_history[0].scene == 0

        assert event_history[1].id == "event_1"
        assert event_history[1].description == "You started the adventure"

        # Check action log
        assert len(action_log) == 2
        assert action_log[0].timestamp == 0
        assert action_log[0].action_type == "make_choice"
        assert action_log[0].details == "Made choice: Start"

        assert action_log[1].timestamp == 1
        assert action_log[1].action_type == "update_state"
        assert action_log[1].details == "Moved to event: event_1"

    def test_load_saved_game_minimal(self, save_manager):
        """Test loading saved game with minimal data."""
        minimal_save_data = {
            "event_counter": 1,
            "game_state": {},
            "event_history": [],
            "action_log": [],
        }

        game_state, event_history, action_log, event_counter = (
            save_manager.load_saved_game(minimal_save_data)
        )

        assert event_counter == 1
        assert game_state.inventory == []
        assert game_state.act == 0
        assert game_state.scene == 0
        assert game_state.visited_events == []
        assert game_state.flags == {}
        assert game_state.current_event is None
        assert event_history == []
        assert action_log == []

    def test_load_saved_game_no_current_event(self, save_manager):
        """Test loading saved game with empty event history."""
        save_data = {
            "event_counter": 0,
            "game_state": {"inventory": ["item"]},
            "event_history": [],
            "action_log": [],
        }

        game_state, event_history, action_log, event_counter = (
            save_manager.load_saved_game(save_data)
        )

        assert game_state.current_event is None
        assert game_state.inventory == ["item"]
        assert event_history == []

    def test_load_saved_game_choice_formats(self, save_manager):
        """Test loading saved game with different choice formats."""
        save_data = {
            "event_counter": 1,
            "game_state": {},
            "event_history": [
                {
                    "id": "test_event",
                    "description": "Test",
                    "choices": [
                        {"text": "Dict choice"},  # Dict format
                        "String choice",  # String format
                        {"text": ""},  # Empty text
                        {"not_text": "Invalid"},  # Invalid dict
                    ],
                    "items": [],
                    "location": "Test",
                    "act": 0,
                    "scene": 0,
                }
            ],
            "action_log": [],
        }

        game_state, event_history, action_log, event_counter = (
            save_manager.load_saved_game(save_data)
        )

        assert len(event_history) == 1
        event = event_history[0]

        # Should have processed valid choices
        assert len(event.choices) >= 2  # At least the valid ones
        assert any(choice.text == "Dict choice" for choice in event.choices)
        assert any(choice.text == "String choice" for choice in event.choices)

    def test_roundtrip_save_load(self, save_manager, sample_story_data):
        """Test complete save and load roundtrip."""
        # Create original data
        story_data = StoryData(
            title="Roundtrip Test",
            setting="Test World",
            acts=sample_story_data["acts"],
            npcs=sample_story_data["npcs"],
            items=sample_story_data["items"],
        )

        original_event = Event(
            "test_event",
            "Test description",
            [Choice("Test choice 1"), Choice("Test choice 2")],
            ["test_item"],
            "Test location",
            1,
            1,
        )

        original_game_state = GameState(
            current_event=original_event,
            inventory=["item1", "item2"],
            act=1,
            scene=1,
            visited_events=["event_0", "test_event"],
            flags={"test_flag": True, "level": 5},
        )

        original_event_history = [original_event]
        original_action_log = [ActionLogEntry(1, "test_action", "Test details")]
        original_event_counter = 5

        # Save the data
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            filename = f.name

        try:
            success, _ = save_manager.save_game(
                filename,
                story_data,
                original_game_state,
                original_event_history,
                original_action_log,
                original_event_counter,
            )
            assert success is True

            # Load the saved data
            with open(filename, "r") as f:
                saved_data = json.load(f)

            (
                loaded_game_state,
                loaded_event_history,
                loaded_action_log,
                loaded_event_counter,
            ) = save_manager.load_saved_game(saved_data)

            # Verify everything matches
            assert loaded_event_counter == original_event_counter

            assert loaded_game_state.inventory == original_game_state.inventory
            assert loaded_game_state.act == original_game_state.act
            assert loaded_game_state.scene == original_game_state.scene
            assert (
                loaded_game_state.visited_events == original_game_state.visited_events
            )
            assert loaded_game_state.flags == original_game_state.flags

            assert len(loaded_event_history) == len(original_event_history)
            loaded_event = loaded_event_history[0]
            assert loaded_event.id == original_event.id
            assert loaded_event.description == original_event.description
            assert len(loaded_event.choices) == len(original_event.choices)
            assert loaded_event.choices[0].text == original_event.choices[0].text
            assert loaded_event.items == original_event.items
            assert loaded_event.location == original_event.location
            assert loaded_event.act == original_event.act
            assert loaded_event.scene == original_event.scene

            assert len(loaded_action_log) == len(original_action_log)
            loaded_action = loaded_action_log[0]
            assert loaded_action.timestamp == original_action_log[0].timestamp
            assert loaded_action.action_type == original_action_log[0].action_type
            assert loaded_action.details == original_action_log[0].details

        finally:
            if os.path.exists(filename):
                os.unlink(filename)
