"""Save and load management for Texventure."""

import json
from typing import List, Tuple

from .models import ActionLogEntry, Choice, Event, GameState, StoryData


class SaveLoadManager:
    """Handles saving and loading game states."""

    @staticmethod
    def save_game(
        filename: str,
        story_data: StoryData,
        game_state: GameState,
        event_history: List[Event],
        action_log: List[ActionLogEntry],
        event_counter: int,
    ) -> Tuple[bool, str]:
        """Save the current game state in a format compatible with story loading."""
        if not story_data:
            return False, "No story data to save"

        # Prepare current event data
        current_event_data = None
        if game_state.current_event:
            current_event_data = {
                "id": game_state.current_event.id,
                "description": game_state.current_event.description,
                "choices": [
                    {"text": choice.text} for choice in game_state.current_event.choices
                ],
                "items": game_state.current_event.items,
                "location": game_state.current_event.location,
                "act": game_state.current_event.act,
                "scene": game_state.current_event.scene,
            }

        save_data = {
            # Core story data (compatible with original format)
            "title": story_data.title,
            "setting": story_data.setting,
            "outline": story_data.outline,
            "acts": story_data.acts,
            "npcs": story_data.npcs,
            "items": story_data.items,
            # Save game specific data
            "is_saved_game": True,
            "saved_at": event_counter,
            "current_event": current_event_data,
            "event_history": [
                {
                    "id": event.id,
                    "description": event.description,
                    "choices": [{"text": choice.text} for choice in event.choices],
                    "items": event.items,
                    "location": event.location,
                    "act": event.act,
                    "scene": event.scene,
                }
                for event in event_history
            ],
            "action_log": [
                {
                    "timestamp": entry.timestamp,
                    "action_type": entry.action_type,
                    "details": entry.details,
                }
                for entry in action_log
            ],
            "event_counter": event_counter,
            "game_state": {
                "inventory": game_state.inventory,
                "act": game_state.act,
                "scene": game_state.scene,
                "visited_events": game_state.visited_events,
                "flags": game_state.flags,
            },
        }

        try:
            with open(filename, "w") as f:
                json.dump(save_data, f, indent=2)
            return True, f"Game saved to {filename}"
        except Exception as e:
            return False, f"Error saving game: {e}"

    @staticmethod
    def load_saved_game(
        save_data: dict,
    ) -> Tuple[GameState, List[Event], List[ActionLogEntry], int]:
        """Load a saved game state and return components."""
        # Restore basic counters
        event_counter = save_data.get("event_counter", 0)

        # Restore game state
        saved_state = save_data.get("game_state", {})
        game_state = GameState(
            inventory=saved_state.get("inventory", []),
            act=saved_state.get("act", 0),
            scene=saved_state.get("scene", 0),
            visited_events=saved_state.get("visited_events", []),
            flags=saved_state.get("flags", {}),
        )

        # Restore event history
        event_history_data = save_data.get("event_history", [])
        event_history = []
        for event_data in event_history_data:
            choices = []
            for choice_data in event_data.get("choices", []):
                choice_text = (
                    choice_data.get("text", "")
                    if isinstance(choice_data, dict)
                    else choice_data
                )
                choices.append(Choice(choice_text))

            event = Event(
                id=event_data.get("id", ""),
                description=event_data.get("description", ""),
                choices=choices,
                items=event_data.get("items", []),
                location=event_data.get("location", ""),
                act=event_data.get("act", 0),
                scene=event_data.get("scene", 0),
            )
            event_history.append(event)

        # Set current event to the last one in history
        if event_history:
            game_state.current_event = event_history[-1]

        # Restore action log
        action_log_data = save_data.get("action_log", [])
        action_log = []
        for action_data in action_log_data:
            entry = ActionLogEntry(
                timestamp=action_data.get("timestamp", 0),
                action_type=action_data.get("action_type", ""),
                details=action_data.get("details", ""),
            )
            action_log.append(entry)

        return game_state, event_history, action_log, event_counter
