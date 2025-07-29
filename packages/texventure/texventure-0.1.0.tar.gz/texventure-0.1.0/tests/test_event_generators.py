"""Tests for event generators."""

import json
from unittest.mock import Mock, patch

import pytest

from src.texventure.event_generators import (EventGenerator, LLMEventGenerator,
                                             TemplateEventGenerator)
from src.texventure.models import Choice, Event, GameState, StoryData


class TestTemplateEventGenerator:
    """Test cases for TemplateEventGenerator."""

    def test_generate_begin_event_with_story(self, template_event_generator):
        """Test generating the begin event with story data."""
        story_data = StoryData(
            title="Test Adventure",
            acts=[
                {
                    "name": "Act 1",
                    "description": "The beginning",
                    "scenes": [
                        {
                            "name": "Scene 1",
                            "description": "Starting scene description",
                            "location": "Starting location",
                        }
                    ],
                }
            ],
        )

        context = {"story_data": story_data, "game_state": GameState()}

        event = template_event_generator.generate_event(context, "begin", "event_0")

        assert event.id == "event_0"
        assert (
            "Starting scene description" in event.description
            or "The beginning" in event.description
        )
        assert event.location in ["Starting location", "Unknown location"]
        assert len(event.choices) == 4
        assert event.act == 0
        assert event.scene == 0

    def test_generate_begin_event_without_story(self, template_event_generator):
        """Test generating the begin event without story data."""
        context = {"story_data": None, "game_state": GameState()}

        event = template_event_generator.generate_event(context, "begin", "event_0")

        assert event.id == "event_0"
        assert "You chose: begin" in event.description
        assert event.location == "Current location"
        assert len(event.choices) == 4

    def test_generate_continuation_event(self, template_event_generator):
        """Test generating a continuation event."""
        context = {"story_data": StoryData(), "game_state": GameState(act=1, scene=2)}

        event = template_event_generator.generate_event(context, "go north", "event_1")

        assert event.id == "event_1"
        assert "You chose: go north" in event.description
        assert event.location == "Current location"
        assert len(event.choices) == 4
        assert event.act == 1
        assert event.scene == 2

    def test_generate_event_choice_types(self, template_event_generator):
        """Test that generated events have correct choice types."""
        context = {"story_data": StoryData(), "game_state": GameState()}

        event = template_event_generator.generate_event(context, "test", "event_0")

        for choice in event.choices:
            assert isinstance(choice, Choice)
            assert isinstance(choice.text, str)
            assert len(choice.text) > 0


class TestLLMEventGenerator:
    """Test cases for LLMEventGenerator."""

    def test_llm_generator_initialization(self):
        """Test LLM generator initialization."""
        api_key = "test_key"
        model = "gpt-4"
        generator = LLMEventGenerator(api_key, model)

        assert generator.api_key == api_key
        assert generator.model == model

    def test_llm_generator_default_model(self):
        """Test LLM generator with default model."""
        generator = LLMEventGenerator("test_key")
        assert generator.model == "gpt-3.5-turbo"

    @patch("src.texventure.event_generators.llm_call")
    def test_generate_begin_event_success(self, mock_llm_call, mock_llm_response):
        """Test successful begin event generation with LLM."""
        mock_llm_call.return_value = mock_llm_response

        generator = LLMEventGenerator("test_key")
        context = {
            "story_data": StoryData(title="Test", setting="Test world"),
            "game_state": GameState(),
        }

        event = generator.generate_event(context, "begin", "event_0")

        assert event.id == "event_0"
        assert "mysterious forest path" in event.description.lower()
        assert event.location == "Misty Forest Path"
        assert len(event.choices) == 4
        mock_llm_call.assert_called_once()

        # Check that force_json=True was passed
        call_args = mock_llm_call.call_args
        assert call_args[1]["force_json"] is True

    @patch("src.texventure.event_generators.llm_call")
    def test_generate_continuation_event_success(
        self, mock_llm_call, mock_llm_response
    ):
        """Test successful continuation event generation with LLM."""
        mock_llm_call.return_value = mock_llm_response

        generator = LLMEventGenerator("test_key")
        context = {
            "story_data": StoryData(title="Test", setting="Test world"),
            "game_state": GameState(),
            "current_event": Event("prev_event", "Previous event"),
            "previous_event": Event("prev_prev_event", "Previous previous event"),
        }

        event = generator.generate_event(context, "go north", "event_1")

        assert event.id == "event_1"
        assert len(event.choices) == 4
        mock_llm_call.assert_called_once()

    @patch("src.texventure.event_generators.llm_call")
    def test_generate_event_llm_failure(self, mock_llm_call):
        """Test event generation when LLM call fails."""
        mock_llm_call.side_effect = Exception("API Error")

        generator = LLMEventGenerator("test_key")
        context = {"story_data": StoryData(), "game_state": GameState()}

        event = generator.generate_event(context, "test", "event_0")

        # Should fall back to template event
        assert event.id == "event_0"
        assert "adventure continues" in event.description.lower()
        assert len(event.choices) == 4

    @patch("src.texventure.event_generators.llm_call")
    def test_generate_event_invalid_json(self, mock_llm_call):
        """Test event generation with invalid JSON response."""
        mock_llm_call.return_value = "Invalid JSON response"

        generator = LLMEventGenerator("test_key")
        context = {"story_data": StoryData(), "game_state": GameState()}

        event = generator.generate_event(context, "test", "event_0")

        # Should fall back to template event
        assert event.id == "event_0"
        assert len(event.choices) == 4

    def test_build_context_string_comprehensive(self):
        """Test building comprehensive context string."""
        generator = LLMEventGenerator("test_key")

        story_data = StoryData(
            title="Test Adventure",
            setting="Fantasy realm",
            outline="Epic quest",
            acts=[
                {
                    "name": "Act 1",
                    "description": "The beginning",
                    "scenes": [
                        {
                            "name": "Scene 1",
                            "description": "Starting area",
                            "location": "Village",
                        }
                    ],
                }
            ],
            npcs=[{"name": "Wizard", "description": "Wise old wizard"}],
        )

        game_state = GameState(inventory=["sword", "potion"], act=0, scene=0)

        current_event = Event(
            "current_id",
            "Current event description",
            location="Current location",
            items=["treasure"],
        )

        previous_event = Event(
            "prev_id", "Previous event description", location="Previous location"
        )

        context = {
            "story_data": story_data,
            "game_state": game_state,
            "current_event": current_event,
            "previous_event": previous_event,
        }

        context_str = generator._build_context_string(context)

        assert "Test Adventure" in context_str
        assert "Fantasy realm" in context_str
        assert "Epic quest" in context_str
        assert "Act 1" in context_str
        assert "The beginning" in context_str
        assert "Scene 1" in context_str
        assert "Starting area" in context_str
        assert "Village" in context_str
        assert "Wizard" in context_str
        assert "Wise old wizard" in context_str
        assert "Current event description" in context_str
        assert "Current location" in context_str
        assert "treasure" in context_str
        assert "Previous event description" in context_str
        assert "Previous location" in context_str
        assert "sword, potion" in context_str

    def test_build_context_string_minimal(self):
        """Test building context string with minimal data."""
        generator = LLMEventGenerator("test_key")

        context = {}
        context_str = generator._build_context_string(context)

        # Should not crash and return empty or minimal string
        assert isinstance(context_str, str)

    def test_parse_llm_response_valid(self):
        """Test parsing valid LLM response."""
        generator = LLMEventGenerator("test_key")

        response = json.dumps(
            {
                "description": "Test description",
                "location": "Test location",
                "choices": [
                    {"text": "Choice 1"},
                    {"text": "Choice 2"},
                    {"text": "Choice 3"},
                    {"text": "Choice 4"},
                ],
            }
        )

        context = {"game_state": GameState(act=1, scene=2)}
        event = generator._parse_llm_response(response, "test_id", context)

        assert event.id == "test_id"
        assert event.description == "Test description"
        assert event.location == "Test location"
        assert len(event.choices) == 4
        assert event.choices[0].text == "Choice 1"
        assert event.act == 1
        assert event.scene == 2

    def test_parse_llm_response_missing_description(self):
        """Test parsing LLM response with missing description."""
        generator = LLMEventGenerator("test_key")

        response = json.dumps(
            {"location": "Test location", "choices": [{"text": "Choice 1"}]}
        )

        context = {"game_state": GameState()}
        event = generator._parse_llm_response(response, "test_id", context)

        # Should fall back to default event
        assert event.id == "test_id"
        assert "adventure continues" in event.description.lower()
        assert len(event.choices) == 4

    def test_parse_llm_response_empty_choices(self):
        """Test parsing LLM response with empty choices."""
        generator = LLMEventGenerator("test_key")

        response = json.dumps(
            {
                "description": "Test description",
                "location": "Test location",
                "choices": [],
            }
        )

        context = {"game_state": GameState()}
        event = generator._parse_llm_response(response, "test_id", context)

        assert event.description == "Test description"
        assert event.location == "Test location"
        # Should have default choices
        assert len(event.choices) == 4

    def test_create_fallback_event(self):
        """Test creating fallback event."""
        generator = LLMEventGenerator("test_key")

        context = {"game_state": GameState(act=2, scene=1)}
        event = generator._create_fallback_event("fallback_id", "test_choice", context)

        assert event.id == "fallback_id"
        assert "adventure continues" in event.description.lower()
        assert event.location == "Unknown location"
        assert len(event.choices) == 4
        assert event.act == 2
        assert event.scene == 1

    def test_prompt_generation_begin(self):
        """Test that begin prompts are generated correctly."""
        generator = LLMEventGenerator("test_key")

        context_str = "Test context"
        prompt = generator._create_opening_prompt(context_str)

        assert "opening event" in prompt.lower()
        assert "interactive text adventure" in prompt.lower()
        assert context_str in prompt
        assert "valid JSON" in prompt

    def test_prompt_generation_continuation(self):
        """Test that continuation prompts are generated correctly."""
        generator = LLMEventGenerator("test_key")

        context_str = "Test context"
        choice_text = "go north"
        prompt = generator._create_continuation_prompt(context_str, choice_text)

        assert "next event" in prompt.lower()
        assert "interactive text adventure" in prompt.lower()
        assert context_str in prompt
        assert choice_text in prompt
        assert "valid JSON" in prompt
