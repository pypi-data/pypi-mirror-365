"""Tests for main module and shell commands."""

import json
import os
import tempfile
from io import StringIO
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.texventure.main import TexventureShell, main
from src.texventure.models import Choice, Event


class TestTexventureShell:
    """Test cases for TexventureShell."""

    def test_shell_initialization_minimal(self):
        """Test minimal shell initialization."""
        shell = TexventureShell()

        assert shell.console is not None
        assert shell.engine is not None
        assert shell.ui is not None
        assert shell.prompt == "(texventure) "
        assert shell.api_key is None
        assert shell.model == "gpt-3.5-turbo"

    def test_shell_initialization_with_params(self):
        """Test shell initialization with parameters."""
        shell = TexventureShell(api_key="test_key", model="gpt-4", use_llm=False)

        assert shell.api_key == "test_key"
        assert shell.model == "gpt-4"
        assert shell.engine.use_llm is False

    @patch.dict("os.environ", {})
    def test_shell_sets_api_key_env(self):
        """Test that shell sets API key in environment."""
        api_key = "test_api_key"
        shell = TexventureShell(api_key=api_key)

        assert os.environ.get("OPENAI_API_KEY") == api_key

    def test_load_story_new_game(self, sample_story_data):
        """Test loading a new story."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            json.dump(sample_story_data, f)
            filename = f.name

        try:
            shell = TexventureShell()

            with (
                patch.object(shell.ui, "render_title_screen") as mock_title,
                patch.object(shell.ui, "render_event") as mock_event,
                patch.object(shell.engine, "update_state") as mock_update,
            ):

                mock_event_obj = Event("test", "test event")
                mock_update.return_value = mock_event_obj

                shell.load_story(filename)

                assert shell.engine.story_data.title == "Test Adventure"
                assert shell.prompt == "(Test Adventure) "
                mock_title.assert_called_once()
                mock_update.assert_called_once_with("begin")
                mock_event.assert_called_once_with(mock_event_obj)

        finally:
            if os.path.exists(filename):
                os.unlink(filename)

    def test_load_story_saved_game(self, sample_saved_game_data):
        """Test loading a saved game."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            json.dump(sample_saved_game_data, f)
            filename = f.name

        try:
            shell = TexventureShell()

            with (
                patch.object(shell.ui, "render_title_screen") as mock_title,
                patch.object(shell.ui, "render_event") as mock_event,
                patch.object(shell.console, "print") as mock_print,
            ):

                shell.load_story(filename)

                assert shell.engine.story_data.title == "The mysteries of Mr Cat"
                mock_title.assert_called_once()
                mock_event.assert_called_once()

                # Check that saved game messages were printed
                print_calls = [call[0][0] for call in mock_print.call_args_list]
                assert any("Loading saved game" in str(call) for call in print_calls)

        finally:
            if os.path.exists(filename):
                os.unlink(filename)

    def test_load_story_file_not_found(self):
        """Test loading non-existent story file."""
        shell = TexventureShell()

        with (
            patch.object(shell.ui, "render_error") as mock_error,
            patch("sys.exit") as mock_exit,
        ):

            shell.load_story("nonexistent.json")

            mock_error.assert_called_once()
            mock_exit.assert_called_once_with(1)

    def test_load_story_invalid_json(self):
        """Test loading invalid JSON file."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            f.write("Invalid JSON content")
            filename = f.name

        try:
            shell = TexventureShell()

            with (
                patch.object(shell.ui, "render_error") as mock_error,
                patch("sys.exit") as mock_exit,
            ):

                shell.load_story(filename)

                mock_error.assert_called_once()
                error_message = mock_error.call_args[0][0]
                assert "Invalid JSON" in error_message
                mock_exit.assert_called_once_with(1)

        finally:
            if os.path.exists(filename):
                os.unlink(filename)

    def test_do_look_with_current_event(self, sample_story_data):
        """Test look command with current event."""
        shell = TexventureShell()
        shell.engine.load_story(sample_story_data)

        current_event = Event("test", "Test event")
        shell.engine.game_state.current_event = current_event

        with patch.object(shell.ui, "render_event") as mock_render:
            shell.do_look("")
            mock_render.assert_called_once_with(current_event)

    def test_do_look_no_current_event(self):
        """Test look command without current event."""
        shell = TexventureShell()

        with patch.object(shell.ui, "render_error") as mock_error:
            shell.do_look("")
            mock_error.assert_called_once_with("No current event to display.")

    def test_do_inventory(self, sample_story_data):
        """Test inventory command."""
        shell = TexventureShell()
        shell.engine.load_story(sample_story_data)
        shell.engine.game_state.inventory = ["sword", "potion"]

        with patch.object(shell.ui, "render_inventory") as mock_render:
            shell.do_inventory("")

            mock_render.assert_called_once()
            call_args = mock_render.call_args[0]
            assert call_args[0] == ["sword", "potion"]  # inventory
            assert call_args[1] == shell.engine.story_data.items  # items_data

    def test_do_take_success(self, sample_story_data):
        """Test successful take command."""
        shell = TexventureShell()
        shell.engine.load_story(sample_story_data)

        with (
            patch.object(shell.engine, "add_to_inventory") as mock_add,
            patch.object(shell.ui, "render_success") as mock_success,
        ):

            mock_add.return_value = (True, "You take the sword")

            shell.do_take("sword")

            mock_add.assert_called_once_with("sword")
            mock_success.assert_called_once_with("You take the sword")

    def test_do_take_failure(self, sample_story_data):
        """Test failed take command."""
        shell = TexventureShell()
        shell.engine.load_story(sample_story_data)

        with (
            patch.object(shell.engine, "add_to_inventory") as mock_add,
            patch.object(shell.ui, "render_error") as mock_error,
        ):

            mock_add.return_value = (False, "Item not found")

            shell.do_take("nonexistent")

            mock_add.assert_called_once_with("nonexistent")
            mock_error.assert_called_once_with("Item not found")

    def test_do_take_no_item(self):
        """Test take command without item name."""
        shell = TexventureShell()

        with patch.object(shell.ui, "render_error") as mock_error:
            shell.do_take("")
            mock_error.assert_called_once_with("Please specify an item to take.")

    def test_do_choice_success(self, sample_story_data):
        """Test successful choice command."""
        shell = TexventureShell()
        shell.engine.load_story(sample_story_data)

        new_event = Event("new", "New event")

        with (
            patch.object(shell.engine, "make_choice") as mock_choice,
            patch.object(shell.ui, "render_choice_feedback") as mock_feedback,
            patch.object(shell.ui, "render_event") as mock_event,
        ):

            mock_choice.return_value = (True, "You chose: Go north", new_event)

            shell.do_choice("1")

            mock_choice.assert_called_once_with(0)  # 1-indexed to 0-indexed
            mock_feedback.assert_called_once_with("Go north")  # Prefix removed
            mock_event.assert_called_once_with(new_event)

    def test_do_choice_failure(self):
        """Test failed choice command."""
        shell = TexventureShell()

        with (
            patch.object(shell.engine, "make_choice") as mock_choice,
            patch.object(shell.ui, "render_error") as mock_error,
        ):

            mock_choice.return_value = (False, "Invalid choice", None)

            shell.do_choice("10")

            mock_choice.assert_called_once_with(9)  # 1-indexed to 0-indexed
            mock_error.assert_called_once_with("Invalid choice")

    def test_do_choice_invalid_input(self):
        """Test choice command with invalid input."""
        shell = TexventureShell()

        with patch.object(shell.ui, "render_error") as mock_error:
            shell.do_choice("not_a_number")
            mock_error.assert_called_once_with("Please enter a valid choice number.")

    def test_do_save_with_filename(self, sample_story_data):
        """Test save command with filename."""
        shell = TexventureShell()
        shell.engine.load_story(sample_story_data)

        with (
            patch.object(shell.engine, "save_game") as mock_save,
            patch.object(shell.ui, "render_success") as mock_success,
            patch.object(shell.ui, "render_info") as mock_info,
        ):

            mock_save.return_value = (True, "Game saved to test.json")
            shell.engine.event_history = [Event("e1", "Event 1")]
            shell.engine.action_log = [Mock(), Mock()]

            shell.do_save("test.json")

            mock_save.assert_called_once_with("test.json")
            mock_success.assert_called_once_with("Game saved to test.json")
            mock_info.assert_called_once()

    def test_do_save_default_filename(self, sample_story_data):
        """Test save command with default filename."""
        shell = TexventureShell()
        shell.engine.load_story(sample_story_data)

        with patch.object(shell.engine, "save_game") as mock_save:
            mock_save.return_value = (True, "Game saved")

            shell.do_save("")

            expected_filename = "Test Adventure-savegame.json"
            mock_save.assert_called_once_with(expected_filename)

    def test_do_save_failure(self, sample_story_data):
        """Test failed save command."""
        shell = TexventureShell()
        shell.engine.load_story(sample_story_data)

        with (
            patch.object(shell.engine, "save_game") as mock_save,
            patch.object(shell.ui, "render_error") as mock_error,
        ):

            mock_save.return_value = (False, "Save failed")

            shell.do_save("test.json")

            mock_error.assert_called_once_with("Save failed")

    def test_do_history(self):
        """Test history command."""
        shell = TexventureShell()

        with patch.object(shell.ui, "render_action_history") as mock_render:
            shell.do_history("")
            mock_render.assert_called_once_with(shell.engine.action_log)

    def test_do_status(self, sample_story_data):
        """Test status command."""
        shell = TexventureShell()
        shell.engine.load_story(sample_story_data)

        with (
            patch.object(shell.ui, "render_status") as mock_status,
            patch.object(shell.console, "print") as mock_print,
        ):

            shell.do_status("")

            mock_status.assert_called_once_with(
                shell.engine.game_state,
                shell.engine.event_history,
                shell.engine.story_data,
            )

            # Check that LLM status was printed
            print_calls = [call[0][0] for call in mock_print.call_args_list]
            assert any("LLM Configuration" in str(call) for call in print_calls)

    def test_default_numeric_input(self, sample_story_data):
        """Test default handler with numeric input."""
        shell = TexventureShell()
        shell.engine.load_story(sample_story_data)

        with patch.object(shell, "do_choice") as mock_choice:
            shell.default("2")
            mock_choice.assert_called_once_with("2")

    def test_default_invalid_command(self):
        """Test default handler with invalid command."""
        shell = TexventureShell()

        with (
            patch.object(shell.ui, "render_error") as mock_error,
            patch.object(shell.ui, "render_info") as mock_info,
        ):

            shell.default("invalid_command")

            mock_error.assert_called_once()
            mock_info.assert_called_once()

    def test_do_exit(self):
        """Test exit command."""
        shell = TexventureShell()

        with patch.object(shell.ui, "render_goodbye") as mock_goodbye:
            result = shell.do_exit("")

            mock_goodbye.assert_called_once()
            assert result is True  # Should return True to exit


class TestMainFunction:
    """Test cases for main function."""

    @patch("src.texventure.main.TexventureShell")
    @patch("sys.argv", ["texventure", "test.json"])
    def test_main_basic(self, mock_shell_class):
        """Test basic main function execution."""
        mock_shell = Mock()
        mock_shell_class.return_value = mock_shell

        with patch("os.path.exists", return_value=True):
            main()

            mock_shell_class.assert_called_once()
            mock_shell.cmdloop.assert_called_once()

    @patch("sys.argv", ["texventure", "nonexistent.json"])
    @patch("sys.exit")
    def test_main_file_not_found(self, mock_exit):
        """Test main function with non-existent file."""
        with (
            patch("os.path.exists", return_value=False),
            patch("rich.console.Console.print") as mock_print,
        ):

            main()

            mock_exit.assert_called_once_with(1)
            # Check that error was printed
            assert mock_print.called

    @patch("src.texventure.main.TexventureShell")
    @patch(
        "sys.argv",
        ["texventure", "test.json", "--api-key", "test_key", "--model", "gpt-4"],
    )
    def test_main_with_args(self, mock_shell_class):
        """Test main function with command line arguments."""
        mock_shell = Mock()
        mock_shell_class.return_value = mock_shell

        with patch("os.path.exists", return_value=True):
            main()

            # Check that shell was created with correct arguments
            call_args = mock_shell_class.call_args[1]
            assert call_args["api_key"] == "test_key"
            assert call_args["model"] == "gpt-4"
            assert call_args["use_llm"] is True

    @patch("src.texventure.main.TexventureShell")
    @patch("sys.argv", ["texventure", "test.json", "--no-llm"])
    def test_main_no_llm(self, mock_shell_class):
        """Test main function with --no-llm flag."""
        mock_shell = Mock()
        mock_shell_class.return_value = mock_shell

        with patch("os.path.exists", return_value=True):
            main()

            call_args = mock_shell_class.call_args[1]
            assert call_args["use_llm"] is False

    @patch("src.texventure.main.TexventureShell")
    @patch("sys.argv", ["texventure", "test.json"])
    @patch.dict("os.environ", {}, clear=True)
    def test_main_llm_no_api_key_warning(self, mock_shell_class):
        """Test main function with LLM enabled but no API key."""
        mock_shell = Mock()
        mock_shell_class.return_value = mock_shell

        with (
            patch("os.path.exists", return_value=True),
            patch("rich.console.Console.print") as mock_print,
        ):

            main()

            # Check that warning was printed
            print_calls = [call[0][0] for call in mock_print.call_args_list]
            assert any("Warning" in str(call) for call in print_calls)

    @patch("src.texventure.main.TexventureShell")
    @patch("sys.argv", ["texventure", "test.json"])
    def test_main_keyboard_interrupt(self, mock_shell_class):
        """Test main function with keyboard interrupt."""
        mock_shell = Mock()
        mock_shell.cmdloop.side_effect = KeyboardInterrupt()
        mock_shell_class.return_value = mock_shell

        with (
            patch("os.path.exists", return_value=True),
            patch("rich.console.Console.print") as mock_print,
        ):

            main()

            # Check that goodbye was printed
            print_calls = [call[0][0] for call in mock_print.call_args_list]
            assert any("Goodbye" in str(call) for call in print_calls)
