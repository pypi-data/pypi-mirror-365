"""Integration tests for Texventure."""

import json
import os
import tempfile
from unittest.mock import patch

import pytest

from src.texventure.engine import GameEngine
from src.texventure.main import TexventureShell
from src.texventure.models import Choice, Event


class TestIntegration:
    """Integration tests for the complete Texventure system."""

    def test_complete_game_flow(self, sample_story_data):
        """Test a complete game flow from start to finish."""
        # Create a temporary story file
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            json.dump(sample_story_data, f)
            story_file = f.name

        try:
            # Initialize shell
            shell = TexventureShell(use_llm=False)  # Use template to avoid LLM calls

            # Load story
            with (
                patch.object(shell.ui, "render_title_screen"),
                patch.object(shell.ui, "render_event"),
            ):
                shell.load_story(story_file)

            # Verify story loaded
            assert shell.engine.story_data.title == "Test Adventure"
            assert shell.engine.game_state.current_event is not None
            assert len(shell.engine.event_history) == 1

            # Make a choice
            with (
                patch.object(shell.ui, "render_choice_feedback"),
                patch.object(shell.ui, "render_event"),
            ):
                shell.do_choice("1")

            # Verify choice was made
            assert len(shell.engine.event_history) == 2
            assert len(shell.engine.action_log) >= 2

            # Check inventory initially empty
            with patch.object(shell.ui, "render_inventory"):
                shell.do_inventory("")

            # Try to take an item (if available)
            current_event = shell.engine.game_state.current_event
            if current_event and current_event.items:
                item_to_take = current_event.items[0]
                with patch.object(shell.ui, "render_success"):
                    shell.do_take(item_to_take)

                # Verify item was taken
                assert item_to_take in shell.engine.game_state.inventory
                assert item_to_take not in current_event.items

            # Save game
            save_file = f"test-save-{os.getpid()}.json"
            try:
                with (
                    patch.object(shell.ui, "render_success"),
                    patch.object(shell.ui, "render_info"),
                ):
                    shell.do_save(save_file)

                # Verify save file was created
                assert os.path.exists(save_file)

                # Load the saved game in a new shell
                shell2 = TexventureShell(use_llm=False)
                with (
                    patch.object(shell2.ui, "render_title_screen"),
                    patch.object(shell2.ui, "render_event"),
                    patch.object(shell2.console, "print"),
                ):
                    shell2.load_story(save_file)

                # Verify save was loaded correctly
                assert shell2.engine.event_counter == shell.engine.event_counter
                assert len(shell2.engine.event_history) == len(
                    shell.engine.event_history
                )
                assert (
                    shell2.engine.game_state.inventory
                    == shell.engine.game_state.inventory
                )

            finally:
                if os.path.exists(save_file):
                    os.unlink(save_file)

            # Check status
            with (
                patch.object(shell.ui, "render_status"),
                patch.object(shell.console, "print"),
            ):
                shell.do_status("")

            # Check history
            with patch.object(shell.ui, "render_action_history"):
                shell.do_history("")

            # Look around
            with patch.object(shell.ui, "render_event"):
                shell.do_look("")

        finally:
            if os.path.exists(story_file):
                os.unlink(story_file)

    def test_error_handling_integration(self):
        """Test error handling in integrated scenarios."""
        shell = TexventureShell(use_llm=False)

        # Try commands without loading story
        with patch.object(shell.ui, "render_error"):
            shell.do_take("sword")  # Should handle gracefully

        with patch.object(shell.ui, "render_error"):
            shell.do_choice("1")  # Should handle gracefully

        # Load invalid story file
        with patch.object(shell.ui, "render_error"), patch("sys.exit"):
            shell.load_story("nonexistent.json")

    def test_llm_fallback_integration(self, sample_story_data):
        """Test LLM fallback behavior in integration."""
        # Create story file
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            json.dump(sample_story_data, f)
            story_file = f.name

        try:
            # Test with LLM enabled but no API key
            with patch.dict("os.environ", {}, clear=True):
                shell = TexventureShell(use_llm=True)

                with (
                    patch.object(shell.ui, "render_title_screen"),
                    patch.object(shell.ui, "render_event"),
                ):
                    shell.load_story(story_file)

                # Should fall back to template generator
                from src.texventure.event_generators import \
                    TemplateEventGenerator

                assert isinstance(shell.engine.event_generator, TemplateEventGenerator)

                # Make choices should still work
                with (
                    patch.object(shell.ui, "render_choice_feedback"),
                    patch.object(shell.ui, "render_event"),
                ):
                    shell.do_choice("1")

                assert len(shell.engine.event_history) == 2

        finally:
            if os.path.exists(story_file):
                os.unlink(story_file)

    def test_save_load_roundtrip_integration(self, sample_story_data):
        """Test complete save/load roundtrip with complex state."""
        # Create story file
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            json.dump(sample_story_data, f)
            story_file = f.name

        try:
            # Create initial game state
            shell1 = TexventureShell(use_llm=False)

            with (
                patch.object(shell1.ui, "render_title_screen"),
                patch.object(shell1.ui, "render_event"),
            ):
                shell1.load_story(story_file)

            # Build up some game state
            for i in range(3):
                with (
                    patch.object(shell1.ui, "render_choice_feedback"),
                    patch.object(shell1.ui, "render_event"),
                ):
                    shell1.do_choice("1")

            # Take items if available
            for event in shell1.engine.event_history:
                if event.items:
                    for item in event.items[
                        :
                    ]:  # Copy to avoid modification during iteration
                        shell1.engine.game_state.current_event = event
                        with patch.object(shell1.ui, "render_success"):
                            shell1.do_take(item)

            # Save the complex state
            save_file = f"complex-save-{os.getpid()}.json"
            try:
                with (
                    patch.object(shell1.ui, "render_success"),
                    patch.object(shell1.ui, "render_info"),
                ):
                    shell1.do_save(save_file)

                # Load in new shell
                shell2 = TexventureShell(use_llm=False)
                with (
                    patch.object(shell2.ui, "render_title_screen"),
                    patch.object(shell2.ui, "render_event"),
                    patch.object(shell2.console, "print"),
                ):
                    shell2.load_story(save_file)

                # Verify all state was preserved
                assert shell2.engine.event_counter == shell1.engine.event_counter
                assert len(shell2.engine.event_history) == len(
                    shell1.engine.event_history
                )
                assert len(shell2.engine.action_log) == len(shell1.engine.action_log)
                assert (
                    shell2.engine.game_state.inventory
                    == shell1.engine.game_state.inventory
                )
                assert (
                    shell2.engine.game_state.visited_events
                    == shell1.engine.game_state.visited_events
                )

                # Continue playing from loaded state
                with (
                    patch.object(shell2.ui, "render_choice_feedback"),
                    patch.object(shell2.ui, "render_event"),
                ):
                    shell2.do_choice("2")

                # Verify game continues normally
                assert (
                    len(shell2.engine.event_history)
                    == len(shell1.engine.event_history) + 1
                )

            finally:
                if os.path.exists(save_file):
                    os.unlink(save_file)

        finally:
            if os.path.exists(story_file):
                os.unlink(story_file)

    def test_engine_event_generator_integration(self, sample_story_data):
        """Test integration between engine and event generators."""
        engine = GameEngine(use_llm=False)
        engine.load_story(sample_story_data)

        # Test event generation
        event = engine.generate_event("begin")
        assert isinstance(event, Event)
        assert event.id == "event_0"
        assert len(event.choices) == 4

        # Test state update
        new_event = engine.update_state("test choice")
        assert new_event != event
        assert new_event.id == "event_1"
        assert engine.game_state.current_event == new_event
        assert new_event in engine.event_history

        # Test choice making
        success, message, next_event = engine.make_choice(0)
        assert success is True
        assert next_event is not None
        assert len(engine.event_history) == 3  # begin + test choice + choice 0

    def test_ui_engine_integration(self, sample_story_data):
        """Test integration between UI and engine components."""
        shell = TexventureShell(use_llm=False)

        # Create story file
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            json.dump(sample_story_data, f)
            story_file = f.name

        try:
            # Load story and capture UI calls
            ui_calls = []

            def track_ui_call(method_name):
                def wrapper(*args, **kwargs):
                    ui_calls.append(method_name)
                    return None

                return wrapper

            # Patch UI methods to track calls
            with (
                patch.object(shell.ui, "render_title_screen", track_ui_call("title")),
                patch.object(shell.ui, "render_event", track_ui_call("event")),
                patch.object(
                    shell.ui, "render_choice_feedback", track_ui_call("choice_feedback")
                ),
                patch.object(shell.ui, "render_success", track_ui_call("success")),
                patch.object(shell.ui, "render_error", track_ui_call("error")),
                patch.object(shell.ui, "render_inventory", track_ui_call("inventory")),
                patch.object(shell.ui, "render_status", track_ui_call("status")),
                patch.object(
                    shell.ui, "render_action_history", track_ui_call("history")
                ),
                patch.object(shell.console, "print"),
            ):

                # Load story
                shell.load_story(story_file)
                assert "title" in ui_calls
                assert "event" in ui_calls

                # Make choice
                ui_calls.clear()
                shell.do_choice("1")
                assert "choice_feedback" in ui_calls
                assert "event" in ui_calls

                # Show inventory
                ui_calls.clear()
                shell.do_inventory("")
                assert "inventory" in ui_calls

                # Show status
                ui_calls.clear()
                shell.do_status("")
                assert "status" in ui_calls

                # Show history
                ui_calls.clear()
                shell.do_history("")
                assert "history" in ui_calls

                # Invalid choice
                ui_calls.clear()
                shell.do_choice("invalid")
                assert "error" in ui_calls

        finally:
            if os.path.exists(story_file):
                os.unlink(story_file)

    def test_cross_component_data_flow(self, sample_story_data):
        """Test data flow across all components."""
        engine = GameEngine(use_llm=False)
        engine.load_story(sample_story_data)

        # Trace data flow from story -> engine -> events -> choices -> state

        # 1. Story data flows to engine
        assert engine.story_data.title == sample_story_data["title"]
        assert len(engine.story_data.acts) == len(sample_story_data["acts"])

        # 2. Engine generates event using story context
        event = engine.generate_event("begin")
        assert event.description is not None
        assert len(event.choices) > 0

        # 3. Event updates engine state
        old_counter = engine.event_counter
        new_event = engine.update_state("test")
        assert engine.event_counter == old_counter + 1
        assert engine.game_state.current_event == new_event

        # 4. Choice affects state and generates new event
        choice_count = len(engine.event_history)
        action_count = len(engine.action_log)

        success, message, next_event = engine.make_choice(0)
        assert success is True
        assert len(engine.event_history) == choice_count + 1
        assert len(engine.action_log) > action_count

        # 5. Save captures all state
        save_data = {
            "title": engine.story_data.title,
            "setting": engine.story_data.setting,
            "acts": engine.story_data.acts,
            "npcs": engine.story_data.npcs,
            "items": engine.story_data.items,
            "is_saved_game": True,
            "event_counter": engine.event_counter,
            "game_state": {
                "inventory": engine.game_state.inventory,
                "act": engine.game_state.act,
                "scene": engine.game_state.scene,
                "visited_events": engine.game_state.visited_events,
                "flags": engine.game_state.flags,
            },
            "event_history": [
                {
                    "id": e.id,
                    "description": e.description,
                    "choices": [{"text": c.text} for c in e.choices],
                    "items": e.items,
                    "location": e.location,
                    "act": e.act,
                    "scene": e.scene,
                }
                for e in engine.event_history
            ],
            "action_log": [
                {
                    "timestamp": a.timestamp,
                    "action_type": a.action_type,
                    "details": a.details,
                }
                for a in engine.action_log
            ],
        }

        # 6. Load restores all state
        new_engine = GameEngine(use_llm=False)
        new_engine.load_story(save_data)

        assert new_engine.event_counter == engine.event_counter
        assert len(new_engine.event_history) == len(engine.event_history)
        assert len(new_engine.action_log) == len(engine.action_log)
        assert new_engine.game_state.inventory == engine.game_state.inventory
