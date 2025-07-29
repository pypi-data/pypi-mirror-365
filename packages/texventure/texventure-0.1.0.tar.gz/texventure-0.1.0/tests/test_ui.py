"""Tests for UI renderer."""

from io import StringIO

import pytest
from rich.console import Console

from src.texventure.models import (ActionLogEntry, Choice, Event, GameState,
                                   StoryData)
from src.texventure.ui import UIRenderer


class TestUIRenderer:
    """Test cases for UIRenderer."""

    def test_ui_renderer_initialization_default(self):
        """Test default UI renderer initialization."""
        ui = UIRenderer()
        assert ui.console is not None
        assert isinstance(ui.console, Console)

    def test_ui_renderer_initialization_custom_console(self):
        """Test UI renderer initialization with custom console."""
        custom_console = Console(file=StringIO())
        ui = UIRenderer(custom_console)
        assert ui.console == custom_console

    def test_render_title_screen(self):
        """Test rendering title screen."""
        output = StringIO()
        console = Console(file=output, force_terminal=False, width=80)
        ui = UIRenderer(console)

        story_data = StoryData(title="Test Adventure")
        ui.render_title_screen(story_data, "A mysterious beginning...")

        rendered = output.getvalue()
        assert "Test Adventure" in rendered
        assert "TEXVENTURE" in rendered
        assert "A mysterious beginning..." in rendered

    def test_render_event(self, sample_event):
        """Test rendering an event."""
        output = StringIO()
        console = Console(file=output, force_terminal=False, width=80)
        ui = UIRenderer(console)

        ui.render_event(sample_event)

        rendered = output.getvalue()
        assert sample_event.description in rendered
        assert "Event" in rendered
        assert "What do you want to do?" in rendered

        # Check that choices are rendered
        for i, choice in enumerate(sample_event.choices, 1):
            assert f"{i}." in rendered
            assert choice.text in rendered

    def test_render_choices_with_choices(self):
        """Test rendering choices when choices are available."""
        output = StringIO()
        console = Console(file=output, force_terminal=False, width=80)
        ui = UIRenderer(console)

        choices = [
            Choice("Go north"),
            Choice("Go south"),
            Choice("Rest"),
            Choice("Check inventory"),
        ]

        ui.render_choices(choices)

        rendered = output.getvalue()
        assert "What do you want to do?" in rendered
        assert "1." in rendered
        assert "Go north" in rendered
        assert "2." in rendered
        assert "Go south" in rendered
        assert "3." in rendered
        assert "Rest" in rendered
        assert "4." in rendered
        assert "Check inventory" in rendered

    def test_render_choices_empty(self):
        """Test rendering when no choices are available."""
        output = StringIO()
        console = Console(file=output, force_terminal=False, width=80)
        ui = UIRenderer(console)

        ui.render_choices([])

        rendered = output.getvalue()
        assert "No choices available" in rendered
        assert "end of the adventure" in rendered

    def test_render_choices_dict_format(self):
        """Test rendering choices in dict format."""
        output = StringIO()
        console = Console(file=output, force_terminal=False, width=80)
        ui = UIRenderer(console)

        # Test with dict-style choices (for backward compatibility)
        choices = [{"text": "Dict choice 1"}, {"text": "Dict choice 2"}]

        ui.render_choices(choices)

        rendered = output.getvalue()
        assert "Dict choice 1" in rendered
        assert "Dict choice 2" in rendered

    def test_render_inventory_with_items(self):
        """Test rendering inventory with items."""
        output = StringIO()
        console = Console(file=output, force_terminal=False, width=80)
        ui = UIRenderer(console)

        inventory = ["sword", "potion"]
        items_data = {
            "sword": {"name": "Magic Sword", "description": "A gleaming blade"},
            "potion": {"name": "Health Potion", "description": "Restores health"},
        }

        ui.render_inventory(inventory, items_data)

        rendered = output.getvalue()
        assert "Inventory" in rendered
        assert "Magic Sword" in rendered
        assert "A gleaming blade" in rendered
        assert "Health Potion" in rendered
        assert "Restores health" in rendered

    def test_render_inventory_empty(self):
        """Test rendering empty inventory."""
        output = StringIO()
        console = Console(file=output, force_terminal=False, width=80)
        ui = UIRenderer(console)

        ui.render_inventory([], {})

        rendered = output.getvalue()
        assert "Inventory" in rendered
        assert "empty" in rendered

    def test_render_inventory_missing_item_data(self):
        """Test rendering inventory with missing item data."""
        output = StringIO()
        console = Console(file=output, force_terminal=False, width=80)
        ui = UIRenderer(console)

        inventory = ["unknown_item"]
        items_data = {}

        ui.render_inventory(inventory, items_data)

        rendered = output.getvalue()
        assert "unknown_item" in rendered
        assert "No description" in rendered

    def test_render_action_history_with_actions(self):
        """Test rendering action history with actions."""
        output = StringIO()
        console = Console(file=output, force_terminal=False, width=80)
        ui = UIRenderer(console)

        action_log = [
            ActionLogEntry(1, "make_choice", "Made choice: Go north"),
            ActionLogEntry(2, "update_state", "Moved to new location"),
            ActionLogEntry(3, "take_item", "Took sword"),
        ]

        ui.render_action_history(action_log)

        rendered = output.getvalue()
        assert "Recent Actions" in rendered
        assert "Make Choice" in rendered  # Should be title-cased
        assert "Made choice: Go north" in rendered
        assert "Update State" in rendered
        assert "Take Item" in rendered

    def test_render_action_history_empty(self):
        """Test rendering empty action history."""
        output = StringIO()
        console = Console(file=output, force_terminal=False, width=80)
        ui = UIRenderer(console)

        ui.render_action_history([])

        rendered = output.getvalue()
        assert "No history available" in rendered

    def test_render_action_history_with_limit(self):
        """Test rendering action history with limit."""
        output = StringIO()
        console = Console(file=output, force_terminal=False, width=80)
        ui = UIRenderer(console)

        # Create more actions than limit
        action_log = [
            ActionLogEntry(i, f"action_{i}", f"Action {i}") for i in range(15)
        ]

        ui.render_action_history(action_log, limit=5)

        rendered = output.getvalue()
        # Should only show last 5 actions
        assert "Action 14" in rendered  # Last action
        assert "Action 10" in rendered  # 5th from last
        assert "Action 9" not in rendered  # 6th from last should not be shown
        assert "more actions" in rendered  # Should indicate there are more

    def test_render_status_basic(self):
        """Test rendering basic status."""
        output = StringIO()
        console = Console(file=output, force_terminal=False, width=80)
        ui = UIRenderer(console)

        current_event = Event("current", "Current event", location="Test Location")
        game_state = GameState(
            current_event=current_event, inventory=["item1", "item2"], act=1, scene=2
        )
        event_history = [Event("event1", "Event 1"), current_event]

        ui.render_status(game_state, event_history)

        rendered = output.getvalue()
        assert "Game Status" in rendered
        assert "Events Visited" in rendered
        assert "2" in rendered  # 2 events
        assert "Items in Inventory" in rendered
        assert "2" in rendered  # 2 items
        assert "Current Act" in rendered
        assert "2" in rendered  # Act 2 (1-indexed)
        assert "Current Scene" in rendered
        assert "3" in rendered  # Scene 3 (1-indexed)
        assert "Test Location" in rendered

    def test_render_status_with_story_data(self):
        """Test rendering status with story data for scene description."""
        output = StringIO()
        console = Console(file=output, force_terminal=False, width=80)
        ui = UIRenderer(console)

        game_state = GameState(act=0, scene=0)
        event_history = []
        story_data = StoryData(
            acts=[
                {
                    "name": "Act 1",
                    "description": "The beginning",
                    "scenes": [
                        {
                            "name": "Opening Scene",
                            "description": "A detailed scene description",
                            "location": "Starting location",
                        }
                    ],
                }
            ]
        )

        ui.render_status(game_state, event_history, story_data)

        rendered = output.getvalue()
        assert "Current Scene" in rendered
        assert "Opening Scene" in rendered
        assert "A detailed scene description" in rendered

    def test_render_choice_feedback(self):
        """Test rendering choice feedback."""
        output = StringIO()
        console = Console(file=output, force_terminal=False, width=80)
        ui = UIRenderer(console)

        ui.render_choice_feedback("Go north")

        rendered = output.getvalue()
        assert "> Go north" in rendered

    def test_render_error(self):
        """Test rendering error message."""
        output = StringIO()
        console = Console(file=output, force_terminal=False, width=80)
        ui = UIRenderer(console)

        ui.render_error("Test error message")

        rendered = output.getvalue()
        assert "✗ Test error message" in rendered

    def test_render_success(self):
        """Test rendering success message."""
        output = StringIO()
        console = Console(file=output, force_terminal=False, width=80)
        ui = UIRenderer(console)

        ui.render_success("Test success message")

        rendered = output.getvalue()
        assert "✓ Test success message" in rendered

    def test_render_info(self):
        """Test rendering info message."""
        output = StringIO()
        console = Console(file=output, force_terminal=False, width=80)
        ui = UIRenderer(console)

        ui.render_info("Test info message")

        rendered = output.getvalue()
        assert "Test info message" in rendered

    def test_render_goodbye(self):
        """Test rendering goodbye message."""
        output = StringIO()
        console = Console(file=output, force_terminal=False, width=80)
        ui = UIRenderer(console)

        ui.render_goodbye()

        rendered = output.getvalue()
        assert "Goodbye!" in rendered
        assert "Thanks for playing" in rendered

    def test_render_status_no_current_event(self):
        """Test rendering status without current event."""
        output = StringIO()
        console = Console(file=output, force_terminal=False, width=80)
        ui = UIRenderer(console)

        game_state = GameState()  # No current event
        event_history = []

        ui.render_status(game_state, event_history)

        rendered = output.getvalue()
        assert "Game Status" in rendered
        assert "Unknown" in rendered  # Current location should be Unknown

    def test_render_status_missing_scene_data(self):
        """Test rendering status with missing scene data."""
        output = StringIO()
        console = Console(file=output, force_terminal=False, width=80)
        ui = UIRenderer(console)

        game_state = GameState(act=0, scene=1)  # Scene 1 but only scene 0 exists
        event_history = []
        story_data = StoryData(
            acts=[
                {
                    "name": "Act 1",
                    "scenes": [{"name": "Scene 0", "description": "Only scene"}],
                }
            ]
        )

        ui.render_status(game_state, event_history, story_data)

        rendered = output.getvalue()
        # Should not crash, just not show scene description
        assert "Game Status" in rendered
