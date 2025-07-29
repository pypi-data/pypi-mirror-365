"""Tests for data models."""

from dataclasses import FrozenInstanceError

import pytest

from src.texventure.models import (ActionLogEntry, Choice, Event, GameState,
                                   StoryData)


class TestChoice:
    """Test cases for Choice model."""

    def test_choice_creation(self):
        """Test basic choice creation."""
        choice = Choice("Test choice")
        assert choice.text == "Test choice"
        assert choice.consequences == {}
        assert choice.requirements == {}

    def test_choice_with_consequences(self):
        """Test choice with consequences."""
        consequences = {"health": -10, "experience": 5}
        choice = Choice("Dangerous choice", consequences=consequences)
        assert choice.text == "Dangerous choice"
        assert choice.consequences == consequences

    def test_choice_with_requirements(self):
        """Test choice with requirements."""
        requirements = {"level": 5, "item": "sword"}
        choice = Choice("Advanced choice", requirements=requirements)
        assert choice.text == "Advanced choice"
        assert choice.requirements == requirements

    def test_choice_equality(self):
        """Test choice equality."""
        choice1 = Choice("Same text")
        choice2 = Choice("Same text")
        choice3 = Choice("Different text")

        assert choice1 == choice2
        assert choice1 != choice3


class TestEvent:
    """Test cases for Event model."""

    def test_event_creation_minimal(self):
        """Test minimal event creation."""
        event = Event(id="test", description="Test event")
        assert event.id == "test"
        assert event.description == "Test event"
        assert event.choices == []
        assert event.items == []
        assert event.location == ""
        assert event.act == 0
        assert event.scene == 0

    def test_event_creation_full(self, sample_choice):
        """Test full event creation."""
        choices = [sample_choice]
        items = ["sword", "potion"]
        event = Event(
            id="full_event",
            description="Full test event",
            choices=choices,
            items=items,
            location="Test location",
            act=1,
            scene=2,
        )

        assert event.id == "full_event"
        assert event.description == "Full test event"
        assert event.choices == choices
        assert event.items == items
        assert event.location == "Test location"
        assert event.act == 1
        assert event.scene == 2

    def test_event_choices_modification(self):
        """Test that event choices can be modified."""
        event = Event(id="test", description="Test")
        choice = Choice("New choice")
        event.choices.append(choice)
        assert len(event.choices) == 1
        assert event.choices[0] == choice


class TestGameState:
    """Test cases for GameState model."""

    def test_game_state_creation_default(self):
        """Test default game state creation."""
        state = GameState()
        assert state.current_event is None
        assert state.inventory == []
        assert state.act == 0
        assert state.scene == 0
        assert state.visited_events == []
        assert state.flags == {}

    def test_game_state_creation_with_values(self, sample_event):
        """Test game state creation with values."""
        inventory = ["sword", "potion"]
        visited = ["event_1", "event_2"]
        flags = {"started": True, "level": 5}

        state = GameState(
            current_event=sample_event,
            inventory=inventory,
            act=2,
            scene=3,
            visited_events=visited,
            flags=flags,
        )

        assert state.current_event == sample_event
        assert state.inventory == inventory
        assert state.act == 2
        assert state.scene == 3
        assert state.visited_events == visited
        assert state.flags == flags

    def test_game_state_modification(self):
        """Test that game state can be modified."""
        state = GameState()
        state.inventory.append("new_item")
        state.flags["new_flag"] = True

        assert "new_item" in state.inventory
        assert state.flags["new_flag"] is True


class TestActionLogEntry:
    """Test cases for ActionLogEntry model."""

    def test_action_log_entry_creation(self):
        """Test action log entry creation."""
        entry = ActionLogEntry(
            timestamp=123, action_type="test_action", details="Test details"
        )

        assert entry.timestamp == 123
        assert entry.action_type == "test_action"
        assert entry.details == "Test details"

    def test_action_log_entry_equality(self):
        """Test action log entry equality."""
        entry1 = ActionLogEntry(1, "action", "details")
        entry2 = ActionLogEntry(1, "action", "details")
        entry3 = ActionLogEntry(2, "action", "details")

        assert entry1 == entry2
        assert entry1 != entry3


class TestStoryData:
    """Test cases for StoryData model."""

    def test_story_data_creation_default(self):
        """Test default story data creation."""
        story = StoryData()
        assert story.title == "Text Adventure"
        assert story.setting == "Unknown"
        assert story.outline == ""
        assert story.acts == []
        assert story.npcs == []
        assert story.items == {}

    def test_story_data_creation_with_values(self):
        """Test story data creation with values."""
        acts = [{"name": "Act 1", "description": "First act"}]
        npcs = [{"name": "Hero", "description": "Main character"}]
        items = {"sword": {"name": "Sword", "description": "Sharp blade"}}

        story = StoryData(
            title="Test Story",
            setting="Fantasy World",
            outline="Epic adventure",
            acts=acts,
            npcs=npcs,
            items=items,
        )

        assert story.title == "Test Story"
        assert story.setting == "Fantasy World"
        assert story.outline == "Epic adventure"
        assert story.acts == acts
        assert story.npcs == npcs
        assert story.items == items

    def test_story_data_modification(self):
        """Test that story data can be modified."""
        story = StoryData()
        story.acts.append({"name": "New Act"})
        story.npcs.append({"name": "New NPC"})
        story.items["new_item"] = {"name": "New Item"}

        assert len(story.acts) == 1
        assert len(story.npcs) == 1
        assert "new_item" in story.items
