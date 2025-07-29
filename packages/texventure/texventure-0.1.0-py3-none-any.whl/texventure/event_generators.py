"""Event generation strategies for Texventure."""

import json
import random
from abc import ABC, abstractmethod
from typing import List, Tuple

from .generator import llm_call
from .models import Choice, Event


class EventGenerator(ABC):
    """Abstract base class for event generation strategies."""

    @abstractmethod
    def generate_event(self, context: dict, choice_text: str, event_id: str) -> Event:
        """Generate an event based on context and choice."""
        pass


class LLMEventGenerator(EventGenerator):
    """Generates events using LLM."""

    def __init__(self, api_key: str, model: str = "gpt-4.1-nano"):
        self.api_key = api_key
        self.model = model

    def generate_event(self, context: dict, choice_text: str, event_id: str) -> Event:
        """Generate event using LLM."""
        # Note: Don't check for game end here - that's handled in the engine
        # after the final trigger is activated

        context_str = self._build_context_string(context)
        scene_trigger = self._get_current_scene_trigger(context)

        prompt = self._create_continuation_prompt(
            context_str, choice_text, scene_trigger
        )

        try:
            response = llm_call(prompt, self.api_key, force_json=True)
            if response:
                return self._parse_llm_response(response, event_id, context)
        except Exception as e:
            print(f"Error generating event with LLM: {e}")

        return self._create_fallback_event(event_id, choice_text, context)

    def _create_continuation_prompt(
        self, context: str, choice_text: str, scene_trigger: str
    ) -> str:
        """Create prompt for continuation event."""
        trigger_instruction = ""
        if scene_trigger:
            trigger_instruction = f"\nSCENE TRIGGER: {scene_trigger}\nInclude the scene trigger as one of the player choices (rewritten to fit the context)."

        return f"""You are generating the next event in an interactive text adventure game.

STORY CONTEXT:
{context}

PLAYER'S PREVIOUS CHOICE: {choice_text}{trigger_instruction}

Generate the next event. You must respond with valid JSON in this exact format:
{{
    "description": "A vivid description of what happens next (2-3 sentences)",
    "location": "The current location name",
    "choices": [
        {{"text": "First choice option"}},
        {{"text": "Second choice option"}},
        {{"text": "Third choice option"}},
        {{"text": "Fourth choice option"}}
    ],
    "trigger_idx": 3
}}

Requirements:
1. Event logically follows from the player's choice
2. Fits the story's setting and tone
3. Advances the narrative meaningfully
4. Provides impactful choices
5. Includes engaging NPC dialogue when appropriate

Respond only with valid JSON in the specified format."""

    def _build_context_string(self, context: dict) -> str:
        """Build context string for LLM prompt."""
        context_parts = []
        story_data = context.get("story_data")
        game_state = context.get("game_state")

        # Add story basics
        if story_data:
            context_parts.extend(
                [
                    f"Title: {story_data.title}",
                    f"Setting: {story_data.setting}",
                    f"Outline: {story_data.outline}",
                    f"Style/Genre: {story_data.style_genre}",
                ]
            )

        # Add current act/scene info
        if (
            story_data
            and game_state
            and self._is_valid_act_scene(story_data, game_state)
        ):
            current_act = story_data.acts[game_state.act]
            context_parts.extend(
                [
                    f"Current Act: {current_act.get('name', f'Act {game_state.act + 1}')}",
                    f"Act Description: {current_act.get('description', '')}",
                ]
            )

            # Add current scene info
            scenes = current_act.get("scenes", [])
            if scenes and game_state.scene < len(scenes):
                current_scene = scenes[game_state.scene]
                context_parts.extend(
                    [
                        f"Current Scene: {current_scene.get('name', f'Scene {game_state.scene + 1}')}",
                        f"Scene Description: {current_scene.get('description', '')}",
                        f"Location: {current_scene.get('location', '')}",
                    ]
                )

        # Add NPCs context
        if story_data and story_data.npcs:
            context_parts.append("Available NPCs:")
            for npc in story_data.npcs[:3]:  # Limit to first 3 NPCs
                context_parts.append(
                    f"- {npc.get('name', 'Unknown')}: {npc.get('description', '')}"
                )

        # Add event context
        self._add_event_context(context_parts, context)

        # Add inventory
        if game_state and game_state.inventory:
            context_parts.append(f"Player Inventory: {', '.join(game_state.inventory)}")

        return "\n".join(context_parts)

    def _is_valid_act_scene(self, story_data, game_state) -> bool:
        """Check if the current act and scene indices are valid."""
        return (
            hasattr(story_data, "acts")
            and story_data.acts
            and game_state.act < len(story_data.acts)
        )

    def _add_event_context(self, context_parts: List[str], context: dict) -> None:
        """Add current and previous event context to context parts."""
        current_event = context.get("current_event")
        if current_event:
            context_parts.extend(
                [
                    f"Current Event: {current_event.description}",
                    f"Current Location: {current_event.location}",
                ]
            )
            if current_event.items:
                context_parts.append(
                    f"Available Items: {', '.join(current_event.items)}"
                )

        previous_event = context.get("previous_event")
        if previous_event:
            context_parts.extend(
                [
                    f"Previous Event: {previous_event.description}",
                    f"Previous Location: {previous_event.location}",
                ]
            )

    def _get_current_scene_trigger(self, context: dict) -> str:
        """Get the trigger for the current scene."""
        try:
            story_data = context.get("story_data")
            game_state = context.get("game_state")

            if not (
                story_data
                and game_state
                and self._is_valid_act_scene(story_data, game_state)
            ):
                return ""

            current_act = story_data.acts[game_state.act]
            scenes = current_act.get("scenes", [])

            if scenes and game_state.scene < len(scenes):
                return scenes[game_state.scene].get("trigger", "")

            return ""
        except (AttributeError, IndexError, KeyError):
            return ""

    def _shuffle_choices_with_trigger(
        self, choices: List[Choice], trigger_idx: int
    ) -> Tuple[List[Choice], int]:
        """Shuffle choices while maintaining trigger index tracking."""
        if len(choices) <= 1:
            return choices, trigger_idx

        # Create choice-trigger pairs
        choice_items = [(choice, i == trigger_idx) for i, choice in enumerate(choices)]
        random.shuffle(choice_items)

        # Rebuild choices and find new trigger index
        new_choices = []
        new_trigger_idx = -1
        for i, (choice, is_trigger) in enumerate(choice_items):
            new_choices.append(choice)
            if is_trigger:
                new_trigger_idx = i

        return new_choices, new_trigger_idx

    def _ensure_scene_trigger_in_choices(
        self, choices: List[Choice], scene_trigger: str, trigger_idx: int
    ) -> Tuple[List[Choice], int]:
        """Ensure scene trigger is included in choices if it exists."""
        if not scene_trigger or not scene_trigger.strip():
            return choices, trigger_idx

        # Check if trigger already exists in choices
        for i, choice in enumerate(choices):
            if (
                scene_trigger.lower() in choice.text.lower()
                or choice.text.lower() in scene_trigger.lower()
                or trigger_idx == i
            ):
                return choices, i

        # Add or replace with trigger
        if choices:
            choices[-1] = Choice(scene_trigger)
            return choices, len(choices) - 1
        else:
            return [Choice(scene_trigger)], 0

    def _parse_llm_response(
        self, llm_response: str, event_id: str, context: dict
    ) -> Event:
        """Parse LLM response and create Event object."""
        try:
            event_data = json.loads(llm_response.strip())

            # Validate and extract basic fields
            description = event_data.get("description", "")
            if not description:
                raise ValueError("Missing description in LLM response")

            location = event_data.get("location", "Unknown location")
            choices = self._parse_choices(event_data.get("choices", []))

            if not choices:
                raise ValueError("No valid choices in LLM response")

            # Handle scene trigger
            scene_trigger = self._get_current_scene_trigger(context)
            trigger_idx = event_data.get("trigger_idx", -1)
            choices, trigger_idx = self._ensure_scene_trigger_in_choices(
                choices, scene_trigger, trigger_idx
            )

            # Shuffle choices while preserving trigger index
            choices, trigger_idx = self._shuffle_choices_with_trigger(
                choices, trigger_idx
            )

            game_state = context.get("game_state")
            return Event(
                id=event_id,
                description=description,
                choices=choices,
                location=location,
                act=game_state.act if game_state else 0,
                scene=game_state.scene if game_state else 0,
                trigger_choice_idx=trigger_idx,
            )

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Error parsing LLM response: {e}")
            print(f"Raw response: {llm_response}")
            return self._create_fallback_event(event_id, "continue", context)

    def _parse_choices(self, choice_data: list) -> List[Choice]:
        """Parse choices from LLM response data."""
        choices = []
        for choice_item in choice_data:
            choice_text = ""
            if isinstance(choice_item, dict):
                choice_text = choice_item.get("text", "")
            elif isinstance(choice_item, str):
                choice_text = choice_item

            if choice_text:
                choices.append(Choice(choice_text))

        return choices

    def _create_fallback_event(
        self, event_id: str, choice_text: str, context: dict
    ) -> Event:
        """Create a fallback event when LLM fails."""
        game_state = context.get("game_state")

        # Default choices
        choices = [
            Choice("Explore the area"),
            Choice("Look around carefully"),
            Choice("Rest and think"),
            Choice("Move forward"),
        ]

        # Handle scene trigger
        scene_trigger = self._get_current_scene_trigger(context)
        choices, trigger_idx = self._ensure_scene_trigger_in_choices(
            choices, scene_trigger, -1
        )
        choices, trigger_idx = self._shuffle_choices_with_trigger(choices, trigger_idx)

        return Event(
            id=event_id,
            description="The adventure continues as you find yourself in a new situation...",
            choices=choices,
            location="Unknown location",
            act=game_state.act if game_state else 0,
            scene=game_state.scene if game_state else 0,
            trigger_choice_idx=trigger_idx,
        )


class TemplateEventGenerator(EventGenerator):
    """Generates events using predefined templates."""

    def generate_event(self, context: dict, choice_text: str, event_id: str) -> Event:
        """Generate event using templates."""
        story_data = context.get("story_data")
        game_state = context.get("game_state")

        # Note: Don't check for game end here - that's handled in the engine
        # after the final trigger is activated

        if choice_text == "begin" and story_data and story_data.acts:
            description, location = self._get_opening_content(story_data)
        else:
            description = (
                f"You chose: {choice_text}. You find yourself in a new situation."
            )
            location = "Current location"

        choices = [
            Choice("Explore the area"),
            Choice("Look for items"),
            Choice("Rest and recover"),
            Choice("Continue forward"),
        ]

        return Event(
            id=event_id,
            description=description,
            choices=choices,
            location=location,
            act=game_state.act if game_state else 0,
            scene=game_state.scene if game_state else 0,
        )

    def _get_opening_content(self, story_data) -> Tuple[str, str]:
        """Get opening description and location from story data."""
        first_act = story_data.acts[0]
        first_scene = (
            first_act.get("scenes", [{}])[0] if first_act.get("scenes") else {}
        )

        description = (
            first_scene.get("description", "")
            or first_act.get("description", "")
            or "You begin your adventure..."
        )
        location = first_scene.get("location", "Unknown location")

        return description, location
