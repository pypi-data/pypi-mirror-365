"""Tests for game engine."""

from unittest.mock import Mock, patch

import pytest

from src.texventure.engine import GameEngine
from src.texventure.event_generators import (LLMEventGenerator,
                                             TemplateEventGenerator)
from src.texventure.models import (ActionLogEntry, Choice, Event, GameState,
                                   StoryData)


class TestGameEngine:
    """Test cases for GameEngine."""

    def test_game_engine_initialization_default(self):
        """Test default game engine initialization."""
        engine = GameEngine()

        assert engine.story_data is None
        assert isinstance(engine.game_state, GameState)
        assert engine.event_history == []
        assert engine.action_log == []
        assert engine.event_counter == 0
        assert engine.use_llm is True
        assert engine.model == "gpt-3.5-turbo"
        assert isinstance(
            engine.event_generator, (LLMEventGenerator, TemplateEventGenerator)
        )

    def test_game_engine_initialization_no_llm(self):
        """Test game engine initialization without LLM."""
        engine = GameEngine(use_llm=False)

        assert engine.use_llm is False
        assert isinstance(engine.event_generator, TemplateEventGenerator)

    def test_game_engine_initialization_custom_model(self):
        """Test game engine initialization with custom model."""
        engine = GameEngine(use_llm=True, model="gpt-4")

        assert engine.model == "gpt-4"

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test_key"})
    def test_game_engine_llm_with_api_key(self):
        """Test game engine with LLM when API key is available."""
        engine = GameEngine(use_llm=True)
        assert isinstance(engine.event_generator, LLMEventGenerator)

    @patch.dict("os.environ", {}, clear=True)
    def test_game_engine_llm_without_api_key(self):
        """Test game engine with LLM when API key is not available."""
        engine = GameEngine(use_llm=True)
        # Should fall back to template generator
        assert isinstance(engine.event_generator, TemplateEventGenerator)

    def test_load_story_new_game(self, sample_story_data):
        """Test loading a new story."""
        engine = GameEngine()
        engine.load_story(sample_story_data)

        assert engine.story_data.title == "Test Adventure"
        assert engine.story_data.setting == "A test world"
        assert engine.story_data.outline == "A simple test story"
        assert len(engine.story_data.acts) == 2
        assert len(engine.story_data.npcs) == 1
        assert len(engine.story_data.items) == 2

        assert engine.game_state.act == 0
        assert engine.game_state.scene == 0
        assert engine.event_counter == 0

    def test_load_story_saved_game(self, sample_saved_game_data):
        """Test loading a saved game."""
        engine = GameEngine()
        engine.load_story(sample_saved_game_data)

        assert engine.story_data.title == "The mysteries of Mr Cat"
        assert engine.event_counter == 5
        assert engine.game_state.act == 0
        assert engine.game_state.scene == 1
        assert engine.game_state.inventory == ["potion"]
        assert len(engine.event_history) == 2
        assert len(engine.action_log) == 2
        assert engine.game_state.current_event is not None

    def test_log_action(self):
        """Test logging actions."""
        engine = GameEngine()
        engine.event_counter = 5

        engine.log_action("test_action", "Test details")

        assert len(engine.action_log) == 1
        action = engine.action_log[0]
        assert action.timestamp == 5
        assert action.action_type == "test_action"
        assert action.details == "Test details"

    def test_generate_event(self, sample_story_data):
        """Test event generation."""
        engine = GameEngine(use_llm=False)  # Use template to avoid LLM calls
        engine.load_story(sample_story_data)

        event = engine.generate_event("begin")

        assert event.id == "event_0"
        assert isinstance(event.description, str)
        assert len(event.description) > 0
        assert len(event.choices) == 4
        assert isinstance(event.location, str)

    def test_generate_event_no_story_data(self):
        """Test event generation without story data."""
        engine = GameEngine()

        with pytest.raises(ValueError, match="No story data loaded"):
            engine.generate_event("begin")

    def test_build_generation_context(self, sample_story_data):
        """Test building generation context."""
        engine = GameEngine()
        engine.load_story(sample_story_data)

        # Add some state
        current_event = Event("current", "Current event")
        engine.game_state.current_event = current_event

        previous_event = Event("previous", "Previous event")
        engine.event_history = [previous_event, current_event]

        context = engine._build_generation_context()

        assert context["story_data"] == engine.story_data
        assert context["game_state"] == engine.game_state
        assert context["current_event"] == current_event
        assert context["previous_event"] == previous_event

    def test_build_generation_context_no_previous(self, sample_story_data):
        """Test building generation context without previous event."""
        engine = GameEngine()
        engine.load_story(sample_story_data)

        current_event = Event("current", "Current event")
        engine.game_state.current_event = current_event
        engine.event_history = [current_event]  # Only one event

        context = engine._build_generation_context()

        assert "previous_event" not in context

    def test_update_state(self, sample_story_data):
        """Test updating game state."""
        engine = GameEngine(use_llm=False)
        engine.load_story(sample_story_data)

        initial_counter = engine.event_counter
        initial_log_count = len(engine.action_log)

        new_event = engine.update_state("test choice")

        assert engine.event_counter == initial_counter + 1
        assert engine.game_state.current_event == new_event
        assert new_event in engine.event_history
        assert new_event.id in engine.game_state.visited_events
        assert len(engine.action_log) == initial_log_count + 2  # choice + update

    def test_make_choice_valid(self, sample_story_data):
        """Test making a valid choice."""
        engine = GameEngine(use_llm=False)
        engine.load_story(sample_story_data)

        # Set up current event
        choices = [Choice("Choice 1"), Choice("Choice 2"), Choice("Choice 3")]
        current_event = Event("current", "Current event", choices=choices)
        engine.game_state.current_event = current_event

        success, message, new_event = engine.make_choice(1)  # Second choice (0-indexed)

        assert success is True
        assert "Choice 2" in message
        assert new_event is not None
        assert new_event != current_event

    def test_make_choice_invalid_index(self, sample_story_data):
        """Test making a choice with invalid index."""
        engine = GameEngine(use_llm=False)
        engine.load_story(sample_story_data)

        choices = [Choice("Choice 1"), Choice("Choice 2")]
        current_event = Event("current", "Current event", choices=choices)
        engine.game_state.current_event = current_event

        success, message, new_event = engine.make_choice(5)  # Invalid index

        assert success is False
        assert "Invalid choice" in message
        assert new_event is None

    def test_make_choice_no_current_event(self):
        """Test making a choice without current event."""
        engine = GameEngine()

        success, message, new_event = engine.make_choice(0)

        assert success is False
        assert "No current event" in message
        assert new_event is None

    def test_add_to_inventory_success(self, sample_story_data):
        """Test successfully adding item to inventory."""
        engine = GameEngine()
        engine.load_story(sample_story_data)

        # Set up current event with item
        current_event = Event("current", "Current event", items=["sword"])
        engine.game_state.current_event = current_event

        success, message = engine.add_to_inventory("sword")

        assert success is True
        assert "Magic Sword" in message  # Item name from story data
        assert "sword" in engine.game_state.inventory
        assert "sword" not in current_event.items

    def test_add_to_inventory_item_not_found(self, sample_story_data):
        """Test adding non-existent item to inventory."""
        engine = GameEngine()
        engine.load_story(sample_story_data)

        current_event = Event("current", "Current event")
        engine.game_state.current_event = current_event

        success, message = engine.add_to_inventory("nonexistent")

        assert success is False
        assert "not found" in message

    def test_add_to_inventory_already_have(self, sample_story_data):
        """Test adding item already in inventory."""
        engine = GameEngine()
        engine.load_story(sample_story_data)

        current_event = Event("current", "Current event", items=["sword"])
        engine.game_state.current_event = current_event
        engine.game_state.inventory = ["sword"]  # Already have it

        success, message = engine.add_to_inventory("sword")

        assert success is False
        assert "already have" in message

    def test_add_to_inventory_not_available_here(self, sample_story_data):
        """Test adding item not available in current event."""
        engine = GameEngine()
        engine.load_story(sample_story_data)

        current_event = Event("current", "Current event", items=[])  # No items
        engine.game_state.current_event = current_event

        success, message = engine.add_to_inventory("sword")

        assert success is False
        assert "not available here" in message

    def test_add_to_inventory_no_items_data(self):
        """Test adding item when no items data available."""
        engine = GameEngine()
        story_data = {"title": "Test", "items": {}}
        engine.load_story(story_data)

        success, message = engine.add_to_inventory("sword")

        assert success is False
        assert "No items available" in message

    def test_save_game(self, sample_story_data):
        """Test saving game."""
        engine = GameEngine()
        engine.load_story(sample_story_data)

        # Add some state
        current_event = Event("current", "Current event")
        engine.game_state.current_event = current_event
        engine.event_history.append(current_event)
        engine.log_action("test", "test action")

        with patch.object(engine.save_manager, "save_game") as mock_save:
            mock_save.return_value = (True, "Saved successfully")

            success, message = engine.save_game("test.json")

            assert success is True
            assert "Saved successfully" in message
            mock_save.assert_called_once_with(
                "test.json",
                engine.story_data,
                engine.game_state,
                engine.event_history,
                engine.action_log,
                engine.event_counter,
            )

            # Check that save action was logged
            assert any(
                action.action_type == "save_game" for action in engine.action_log
            )

    def test_save_game_failure(self, sample_story_data):
        """Test saving game failure."""
        engine = GameEngine()
        engine.load_story(sample_story_data)

        with patch.object(engine.save_manager, "save_game") as mock_save:
            mock_save.return_value = (False, "Save failed")

            success, message = engine.save_game("test.json")

            assert success is False
            assert "Save failed" in message

            # Check that save action was NOT logged on failure
            assert not any(
                action.action_type == "save_game" for action in engine.action_log
            )

    def test_integration_full_game_flow(self, sample_story_data):
        """Test full game flow integration."""
        engine = GameEngine(use_llm=False)

        # Load story
        engine.load_story(sample_story_data)
        assert engine.story_data is not None

        # Generate first event
        first_event = engine.update_state("begin")
        assert first_event.id == "event_1"  # Counter incremented
        assert engine.game_state.current_event == first_event
        assert len(engine.event_history) == 1

        # Make a choice
        success, message, second_event = engine.make_choice(0)
        assert success is True
        assert second_event != first_event
        assert len(engine.event_history) == 2

        # Add item if available
        if first_event.items:
            item_id = first_event.items[0]
            # Put item back for testing
            first_event.items.append(item_id)
            success, message = engine.add_to_inventory(item_id)
            assert success is True
            assert item_id in engine.game_state.inventory

        # Check action log has entries
        assert len(engine.action_log) > 0

        # Verify counters
        assert engine.event_counter == 2

    def test_event_generator_assignment(self):
        """Test that correct event generator is assigned based on configuration."""
        # Test without LLM
        engine_no_llm = GameEngine(use_llm=False)
        assert isinstance(engine_no_llm.event_generator, TemplateEventGenerator)

        # Test with LLM but no API key
        with patch.dict("os.environ", {}, clear=True):
            engine_llm_no_key = GameEngine(use_llm=True)
            assert isinstance(engine_llm_no_key.event_generator, TemplateEventGenerator)

        # Test with LLM and API key
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test_key"}):
            engine_llm_with_key = GameEngine(use_llm=True)
            assert isinstance(engine_llm_with_key.event_generator, LLMEventGenerator)

    def test_event_generation_delegation(self, sample_story_data):
        """Test that event generation is properly delegated to event generator."""
        engine = GameEngine(use_llm=False)
        engine.load_story(sample_story_data)

        # Mock the event generator
        mock_generator = Mock()
        mock_event = Event("mock_event", "Mock description")
        mock_generator.generate_event.return_value = mock_event
        engine.event_generator = mock_generator

        result = engine.generate_event("test choice")

        assert result == mock_event
        mock_generator.generate_event.assert_called_once()

        # Check the context passed to generator
        call_args = mock_generator.generate_event.call_args
        context, choice_text, event_id = call_args[0]

        assert context["story_data"] == engine.story_data
        assert context["game_state"] == engine.game_state
        assert choice_text == "test choice"
        assert event_id == "event_0"
