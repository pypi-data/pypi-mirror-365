"""Tests for the story generator module."""

import json
from unittest.mock import Mock, patch

import pytest

from src.texventure.generator import (_fill_fields_individually,
                                      collect_empty_fields, form_bulk_prompt,
                                      format_story, generate_story, llm_call,
                                      set_nested_value)


class TestCollectEmptyFields:
    """Test the collect_empty_fields function."""

    def test_simple_dict(self):
        """Test collecting empty fields from a simple dictionary."""
        data = {"title": "", "setting": "fantasy world", "outline": ""}

        empty_fields = collect_empty_fields(data)
        assert "title" in empty_fields
        assert "outline" in empty_fields
        assert "setting" not in empty_fields
        assert len(empty_fields) == 2

    def test_nested_dict(self):
        """Test collecting empty fields from nested dictionaries."""
        data = {
            "title": "Test Story",
            "acts": {"act1": {"name": "", "description": "First act"}},
            "npcs": {"hero": {"name": "Hero", "description": ""}},
        }

        empty_fields = collect_empty_fields(data)
        assert "acts.act1.name" in empty_fields
        assert "npcs.hero.description" in empty_fields
        assert len(empty_fields) == 2

    def test_list_with_dicts(self):
        """Test collecting empty fields from lists containing dictionaries."""
        data = {
            "acts": [
                {"name": "Act 1", "description": ""},
                {"name": "", "description": "Second act"},
            ]
        }

        empty_fields = collect_empty_fields(data)
        assert "acts[0].description" in empty_fields
        assert "acts[1].name" in empty_fields
        assert len(empty_fields) == 2

    def test_no_empty_fields(self):
        """Test with data that has no empty fields."""
        data = {
            "title": "Complete Story",
            "setting": "Fantasy world",
            "acts": [{"name": "Act 1", "description": "First act"}],
        }

        empty_fields = collect_empty_fields(data)
        assert len(empty_fields) == 0


class TestSetNestedValue:
    """Test the set_nested_value function."""

    def test_simple_path(self):
        """Test setting a value with a simple path."""
        data = {"title": "", "setting": ""}
        set_nested_value(data, "title", "New Title")
        assert data["title"] == "New Title"
        assert data["setting"] == ""

    def test_nested_path(self):
        """Test setting a value with a nested path."""
        data = {"acts": {"act1": {"name": "", "description": ""}}}
        set_nested_value(data, "acts.act1.name", "Chapter One")
        assert data["acts"]["act1"]["name"] == "Chapter One"

    def test_array_path(self):
        """Test setting a value in an array."""
        data = {
            "acts": [{"name": "", "description": ""}, {"name": "", "description": ""}]
        }
        set_nested_value(data, "acts[1].name", "Second Act")
        assert data["acts"][1]["name"] == "Second Act"
        assert data["acts"][0]["name"] == ""


class TestFormBulkPrompt:
    """Test the form_bulk_prompt function."""

    def test_single_field(self):
        """Test prompt formation with a single field."""
        fields = ["title"]
        context = '{"title": "", "setting": "fantasy"}'

        prompt = form_bulk_prompt(fields, context)
        assert "title" in prompt
        assert "JSON object" in prompt
        assert context in prompt

    def test_multiple_fields(self):
        """Test prompt formation with multiple fields."""
        fields = ["title", "setting", "outline"]
        context = '{"title": "", "setting": "", "outline": ""}'

        prompt = form_bulk_prompt(fields, context)
        for field in fields:
            assert field in prompt
        assert "JSON object" in prompt


class TestLLMCall:
    """Test the llm_call function."""

    @patch("src.texventure.generator.requests.post")
    def test_successful_call(self, mock_post):
        """Test a successful LLM API call."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Generated content"}}]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        result = llm_call("test prompt", "test-api-key")
        assert result == "Generated content"

        # Verify the request was made correctly
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert "json" in kwargs
        assert kwargs["json"]["messages"][1]["content"] == "test prompt"

    @patch("src.texventure.generator.requests.post")
    def test_json_mode(self, mock_post):
        """Test LLM call with JSON mode enabled."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": '{"title": "Test"}'}}]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        result = llm_call("test prompt", "test-api-key", force_json=True)
        assert result == '{"title": "Test"}'

        # Verify JSON mode was enabled
        args, kwargs = mock_post.call_args
        assert kwargs["json"]["response_format"] == {"type": "json_object"}
        assert "valid JSON" in kwargs["json"]["messages"][0]["content"]

    @patch("src.texventure.generator.requests.post")
    def test_api_error(self, mock_post):
        """Test handling of API errors."""
        mock_post.side_effect = Exception("API Error")

        result = llm_call("test prompt", "test-api-key")
        assert result is None


class TestGenerateStory:
    """Test the generate_story function."""

    @patch("src.texventure.generator.llm_call")
    def test_no_api_key(self, mock_llm_call):
        """Test behavior when no API key is provided."""
        story_data = {"title": "", "setting": ""}

        generate_story(story_data, None)

        # Should not make any LLM calls
        mock_llm_call.assert_not_called()
        # Data should remain unchanged
        assert story_data["title"] == ""
        assert story_data["setting"] == ""

    @patch("src.texventure.generator.llm_call")
    def test_no_empty_fields(self, mock_llm_call):
        """Test behavior when there are no empty fields."""
        story_data = {"title": "Complete", "setting": "Fantasy"}

        generate_story(story_data, "test-api-key")

        # Should not make any LLM calls
        mock_llm_call.assert_not_called()

    @patch("src.texventure.generator.llm_call")
    def test_successful_generation(self, mock_llm_call):
        """Test successful story generation with JSON response."""
        story_data = {"title": "", "setting": ""}

        # Mock LLM response
        mock_llm_call.return_value = (
            '{"title": "Generated Title", "setting": "Generated Setting"}'
        )

        generate_story(story_data, "test-api-key")

        # Verify LLM was called with JSON mode
        mock_llm_call.assert_called_once()
        args, kwargs = mock_llm_call.call_args
        assert kwargs.get("force_json") is True

        # Verify data was updated
        assert story_data["title"] == "Generated Title"
        assert story_data["setting"] == "Generated Setting"

    @patch("src.texventure.generator.llm_call")
    @patch("src.texventure.generator._fill_fields_individually")
    def test_json_parse_failure_fallback(self, mock_fallback, mock_llm_call):
        """Test fallback to individual filling when JSON parsing fails."""
        story_data = {"title": "", "setting": ""}

        # Mock invalid JSON response
        mock_llm_call.return_value = "Invalid JSON response"

        generate_story(story_data, "test-api-key")

        # Should fall back to individual field filling
        mock_fallback.assert_called_once()

    @patch("src.texventure.generator.llm_call")
    def test_batch_processing(self, mock_llm_call):
        """Test that large numbers of fields are processed in batches."""
        # Create story data with more than 10 empty fields
        story_data = {f"field_{i}": "" for i in range(15)}

        mock_llm_call.return_value = '{"field_0": "content"}'

        generate_story(story_data, "test-api-key")

        # Should make multiple calls due to batching
        assert mock_llm_call.call_count >= 2


class TestFillFieldsIndividually:
    """Test the _fill_fields_individually fallback function."""

    @patch("src.texventure.generator.llm_call")
    def test_individual_filling(self, mock_llm_call):
        """Test filling fields individually."""
        story_data = {"title": "", "setting": ""}
        fields = ["title", "setting"]

        # Mock individual responses
        mock_llm_call.side_effect = ["Generated Title", "Generated Setting"]

        _fill_fields_individually(story_data, fields, "test-api-key", "gpt-3.5-turbo")

        # Should make one call per field
        assert mock_llm_call.call_count == 2

        # Verify data was updated
        assert story_data["title"] == "Generated Title"
        assert story_data["setting"] == "Generated Setting"

    @patch("src.texventure.generator.llm_call")
    def test_empty_response_handling(self, mock_llm_call):
        """Test handling of empty responses."""
        story_data = {"title": ""}
        fields = ["title"]

        # Mock empty response
        mock_llm_call.return_value = ""

        _fill_fields_individually(story_data, fields, "test-api-key", "gpt-3.5-turbo")

        # Data should remain unchanged
        assert story_data["title"] == ""


class TestFormatStory:
    """Test the format_story function."""

    def test_basic_formatting(self):
        """Test basic story formatting."""
        template_data = {
            "title": "Test Story",
            "setting": "Fantasy world",
            "n_acts": 2,
            "n_scenes": 2,
            "n_npcs": 1,
        }

        result = format_story(template_data)

        assert result["title"] == "Test Story"
        assert len(result["acts"]) == 2
        assert len(result["acts"][0]["scenes"]) == 2
        assert len(result["npcs"]) == 1

    def test_creates_missing_acts(self):
        """Test that missing acts are created."""
        template_data = {
            "title": "Test",
            "n_acts": 3,
            "n_scenes": 1,
            "n_npcs": 1,
            "acts": [],
        }

        result = format_story(template_data)

        assert len(result["acts"]) == 3
        assert result["acts"][0]["name"] == "Act 1"
        assert result["acts"][1]["name"] == "Act 2"
        assert result["acts"][2]["name"] == "Act 3"

    def test_creates_missing_scenes(self):
        """Test that missing scenes are created in acts."""
        template_data = {
            "title": "Test",
            "n_acts": 1,
            "n_scenes": 3,
            "n_npcs": 1,
            "acts": [{"name": "Act 1", "description": "", "scenes": []}],
        }

        result = format_story(template_data)

        assert len(result["acts"][0]["scenes"]) == 3
        assert result["acts"][0]["scenes"][0]["name"] == "Scene 1"
        assert result["acts"][0]["scenes"][1]["name"] == "Scene 2"
        assert result["acts"][0]["scenes"][2]["name"] == "Scene 3"

    def test_creates_missing_npcs(self):
        """Test that missing NPCs are created."""
        template_data = {
            "title": "Test",
            "n_acts": 1,
            "n_scenes": 1,
            "n_npcs": 2,
            "npcs": [],
        }

        result = format_story(template_data)

        assert len(result["npcs"]) == 2
        assert result["npcs"][0]["name"] == "Character 1"
        assert result["npcs"][1]["name"] == "Character 2"
