"""Game engine core logic for Texventure."""

import os
from typing import List, Optional, Tuple

from .event_generators import LLMEventGenerator, TemplateEventGenerator
from .models import ActionLogEntry, Choice, Event, GameState, StoryData
from .save_manager import SaveLoadManager


class GameEngine:
    """Core game engine handling game logic and state management."""

    def __init__(
        self, use_llm: bool = True, model: str = "gpt-4.1-nano", max_tokens=800
    ):
        self.story_data: Optional[StoryData] = None
        self.game_state = GameState()
        self.event_history: List[Event] = []
        self.action_log: List[ActionLogEntry] = []
        self.event_counter = 0
        self.use_llm = use_llm
        self.max_tokens = max_tokens
        self.model = model
        self.save_manager = SaveLoadManager()
        self._setup_event_generator()

    def _setup_event_generator(self) -> None:
        """Setup the appropriate event generator based on configuration."""
        if self.use_llm and (api_key := os.getenv("OPENAI_API_KEY")):
            self.event_generator = LLMEventGenerator(api_key, self.model)
        else:
            self.event_generator = TemplateEventGenerator()

    def load_story(self, story_data: dict) -> None:
        """Load story data into the game engine."""
        self.story_data = StoryData(
            title=story_data.get("title", "Text Adventure"),
            setting=story_data.get("setting", "Unknown"),
            outline=story_data.get("outline", ""),
            acts=story_data.get("acts", []),
            npcs=story_data.get("npcs", []),
            items=story_data.get("items", {}),
        )

        if self._is_saved_game(story_data):
            self._load_saved_game(story_data)
        else:
            self._initialize_game_state()

    def _is_saved_game(self, story_data: dict) -> bool:
        """Check if the data contains a saved game state."""
        return "game_state" in story_data and "event_history" in story_data

    def _load_saved_game(self, save_data: dict) -> None:
        """Load a saved game state."""
        self.game_state, self.event_history, self.action_log, self.event_counter = (
            self.save_manager.load_saved_game(save_data)
        )

    def _initialize_game_state(self) -> None:
        """Initialize the game state."""
        self.game_state = GameState(act=0, scene=0)
        self.event_counter = 0

    def log_action(self, action_type: str, details: str) -> None:
        """Log an action taken by the player."""
        self.action_log.append(
            ActionLogEntry(
                timestamp=self.event_counter, action_type=action_type, details=details
            )
        )

    def generate_event(self, choice_text: str = "begin") -> Event:
        """Generate a new event based on the current game state and choice."""
        if not self.story_data:
            raise ValueError("No story data loaded")

        context = self._build_generation_context()
        event_id = f"event_{self.event_counter}"
        return self.event_generator.generate_event(context, choice_text, event_id)

    def _build_generation_context(self) -> dict:
        """Build context dictionary for event generation."""
        context = {
            "story_data": self.story_data,
            "game_state": self.game_state,
            "current_event": self.game_state.current_event,
        }

        # Add previous event if available
        if len(self.event_history) >= 2:
            context["previous_event"] = self.event_history[-2]

        return context

    def initial_event(self) -> Event:
        """Generate the initial event to start the game."""
        if not self.story_data or not self.story_data.acts:
            raise ValueError("No acts defined in story data")

        # Start with the first act and scene
        self.game_state.act = 0
        self.game_state.scene = 0
        event = self.generate_event("begin")
        self.game_state.current_event = event
        return event

    def update_state(self, choice_idx: int) -> Event:
        """Update the game state based on a choice and return the new event."""
        self.event_counter += 1
        current_event = self.game_state.current_event

        # Check if this is the final trigger before advancing
        is_final_trigger = (choice_idx == current_event.trigger_choice_idx) and (
            self._is_at_final_scene()
        )

        # Handle scene/act progression if choice is a trigger
        if (choice_idx) == current_event.trigger_choice_idx:
            self._advance_scene_and_act()

        # Check if game has ended after triggering the final trigger
        if is_final_trigger:
            # Create final event with no choices
            final_event = Event(
                id=f"event_{self.event_counter}_final",
                description="The adventure comes to an end. Thank you for playing!",
                choices=[],  # No choices - game over
                location=current_event.location if current_event else "Final location",
                act=self.game_state.act,
                scene=self.game_state.scene,
                trigger_choice_idx=-1,
            )
            self._update_game_state_with_event(final_event)
            self.log_action("game_end", "Game completed")
            return final_event

        # Generate new event based on choice
        choice_text = current_event.choices[choice_idx].text
        new_event = self.generate_event(choice_text)
        print(new_event)

        # Update game state
        self._update_game_state_with_event(new_event)
        self.log_action("make_choice", f"Made choice: {choice_text}")

        return new_event

    def _advance_scene_and_act(self) -> None:
        """Advance to the next scene and act if necessary."""
        if not self.story_data or not self.story_data.acts:
            return

        current_act = self.story_data.acts[self.game_state.act]
        scenes = current_act.get("scenes", [])

        if scenes:
            # Check if we're at the last scene of the last act
            is_last_act = self.game_state.act == len(self.story_data.acts) - 1
            is_last_scene = self.game_state.scene == len(scenes) - 1

            if is_last_act and is_last_scene:
                # Don't advance beyond the final scene
                return

            self.game_state.scene = (self.game_state.scene + 1) % len(scenes)
            if self.game_state.scene == 0:
                self.game_state.act = (self.game_state.act + 1) % len(
                    self.story_data.acts
                )

    def _is_at_final_scene(self) -> bool:
        """Check if we're currently at the final scene (before triggering the end)."""
        if not self.story_data or not self.story_data.acts:
            return False

        # Check if we're at the last act and last scene
        last_act_index = len(self.story_data.acts) - 1
        if self.game_state.act < last_act_index:
            return False

        current_act = self.story_data.acts[self.game_state.act]
        scenes = current_act.get("scenes", [])
        if not scenes:
            return False

        last_scene_index = len(scenes) - 1
        return self.game_state.scene >= last_scene_index

    def _update_game_state_with_event(self, event: Event) -> None:
        """Update game state with the new event."""
        self.game_state.current_event = event
        self.event_history.append(event)

        if event.id not in self.game_state.visited_events:
            self.game_state.visited_events.append(event.id)

    def make_choice(self, choice_index: int) -> Tuple[bool, str, Optional[Event]]:
        """Make a choice and return success status, message, and new event."""
        if not self.game_state.current_event:
            return False, "No current event", None

        choices = self.game_state.current_event.choices

        # Check if game has ended (no choices available)
        if len(choices) == 0:
            return False, "The game has ended. No more choices available.", None

        if not self._is_valid_choice_index(choice_index, len(choices)):
            return False, f"Invalid choice. Choose between 1 and {len(choices)}", None

        choice = choices[choice_index]
        new_event = self.update_state(choice_index)
        return True, f"You chose: {choice.text}", new_event

    def _is_valid_choice_index(self, choice_index: int, num_choices: int) -> bool:
        """Check if the choice index is valid."""
        return 0 <= choice_index < num_choices

    def is_game_ended(self) -> bool:
        """Public method to check if the game has ended."""
        # Game has ended if current event has no choices
        current_event = self.game_state.current_event
        return current_event is not None and len(current_event.choices) == 0

    def add_to_inventory(self, item_id: str) -> Tuple[bool, str]:
        """Add an item to inventory."""
        # Validate item availability
        if validation_error := self._validate_item_availability(item_id):
            return False, validation_error

        # Add to inventory and remove from event
        self.game_state.inventory.append(item_id)
        self.game_state.current_event.items.remove(item_id)

        item_name = self.story_data.items[item_id].get("name", item_id)
        self.log_action("take_item", f"Took item: {item_name} ({item_id})")
        return True, f"You take the {item_name}"

    def _validate_item_availability(self, item_id: str) -> Optional[str]:
        """Validate if an item can be taken. Returns error message or None."""
        if not self.story_data or not self.story_data.items:
            return "No items available"

        if item_id not in self.story_data.items:
            return f"Item '{item_id}' not found"

        if item_id in self.game_state.inventory:
            return f"You already have {item_id}"

        current_event = self.game_state.current_event
        if not current_event or item_id not in current_event.items:
            return f"'{item_id}' is not available here"

        return None

    def save_game(self, filename: str) -> Tuple[bool, str]:
        """Save the current game state."""
        success, message = self.save_manager.save_game(
            filename,
            self.story_data,
            self.game_state,
            self.event_history,
            self.action_log,
            self.event_counter,
        )

        if success:
            self.log_action("save_game", f"Game saved to: {filename}")

        return success, message
