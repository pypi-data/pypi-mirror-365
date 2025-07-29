"""UI rendering components for Texventure."""

from typing import Any, Dict, List, Optional, Union

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .models import ActionLogEntry, Event, GameState, StoryData


class UIRenderer:
    """Handles all UI rendering for the game."""

    def __init__(self, console: Optional[Console] = None) -> None:
        self.console = console or Console()

    def _create_panel(
        self,
        content: str,
        title: str,
        border_style: str = "bright_blue",
        box_style: box.Box = box.SIMPLE,
    ) -> Panel:
        """Create a standardized panel with consistent styling."""
        return Panel(
            content,
            title=title,
            border_style=border_style,
            box=box_style,
        )

    def _create_table(
        self,
        title: str,
        border_style: str = "bright_cyan",
        box_style: box.Box = box.ROUNDED,
    ) -> Table:
        """Create a standardized table with consistent styling."""
        return Table(
            title=title,
            box=box_style,
            border_style=border_style,
        )

    def render_title_screen(
        self, story_data: StoryData, first_scene_desc: str = ""
    ) -> None:
        """Render the title screen when the game starts."""
        content = (
            f"[bold cyan]{story_data.title}[/bold cyan]\n\n"
            f"Welcome to Texventure. Type help or ? to list commands.\n\n"
            f"[italic]{first_scene_desc}[/italic]"
        )
        title_panel = self._create_panel(
            content,
            "[bold yellow]🎮 TEXVENTURE[/bold yellow]",
            border_style="bright_blue",
            box_style=box.DOUBLE,
        )
        self.console.print(title_panel)

    def render_event(self, event: Event) -> None:
        """Render the current event."""
        description_panel = self._create_panel(
            event.description,
            "[bold cyan]🎭 Event[/bold cyan]",
            border_style="cyan",
        )
        self.console.print(description_panel)
        self.render_choices(event.choices)

    def _extract_choice_text(self, choice: Union[Dict[str, Any], Any]) -> str:
        """Extract choice text from various choice formats."""
        if hasattr(choice, "text"):
            return choice.text
        if isinstance(choice, dict):
            return choice.get("text", "Unknown choice")
        return str(choice)

    def render_choices(self, choices: List[Any]) -> None:
        """Render available choices."""
        if not choices:
            no_choices_panel = self._create_panel(
                "[italic red]No choices available - this might be the end of the adventure[/italic red]",
                "",
                border_style="red",
            )
            self.console.print(no_choices_panel)
            return

        choice_table = Table(
            title="[bold bright_cyan]⚡ What do you want to do?[/bold bright_cyan]",
            box=box.SIMPLE_HEAD,
            show_header=False,
            min_width=40,
            border_style="bright_cyan",
        )

        for i, choice in enumerate(choices, 1):
            choice_text = self._extract_choice_text(choice)
            choice_table.add_row(
                f"[bold cyan]{i}.[/bold cyan]", f"[white]{choice_text}[/white]"
            )

        self.console.print(choice_table)

    def render_inventory(
        self, inventory: List[str], items_data: Dict[str, Any]
    ) -> None:
        """Render the player's inventory."""
        if not inventory:
            empty_panel = self._create_panel(
                "[italic bright_black]Your inventory is empty.[/italic bright_black]",
                "[bold yellow]🎒 Inventory[/bold yellow]",
                border_style="yellow",
            )
            self.console.print(empty_panel)
            return

        inv_table = self._create_table(
            "[bold yellow]🎒 Your Inventory[/bold yellow]",
            border_style="yellow",
        )
        inv_table.add_column("Item", style="cyan", no_wrap=True)
        inv_table.add_column("Description", style="white")

        for item_id in inventory:
            item = items_data.get(item_id, {})
            item_name = item.get("name", item_id)
            item_desc = item.get("description", "No description")
            inv_table.add_row(f"✨ {item_name}", item_desc)

        self.console.print(inv_table)

    def render_action_history(
        self, action_log: List[ActionLogEntry], limit: int = 10
    ) -> None:
        """Render recent action history."""
        if not action_log:
            self.console.print("[italic]No history available yet.[/italic]")
            return

        recent_actions = action_log[-limit:]
        action_table = self._create_table(
            "[bold yellow]📝 Recent Actions[/bold yellow]",
            border_style="yellow",
        )
        action_table.add_column("Step", style="yellow", width=8)
        action_table.add_column("Action", style="cyan")
        action_table.add_column("Details", style="white")

        for action in recent_actions:
            action_table.add_row(
                str(action.timestamp),
                action.action_type.replace("_", " ").title(),
                action.details,
            )

        self.console.print(action_table)

        if len(action_log) > limit:
            self.console.print(
                f"[italic]... and {len(action_log) - limit} more actions[/italic]"
            )

    def _render_current_scene(
        self, game_state: GameState, story_data: StoryData
    ) -> None:
        """Render current scene information if available."""
        if not (
            story_data and story_data.acts and game_state.act < len(story_data.acts)
        ):
            return

        current_act = story_data.acts[game_state.act]
        scenes = current_act.get("scenes", [])

        if not (scenes and game_state.scene < len(scenes)):
            return

        current_scene = scenes[game_state.scene]
        scene_description = current_scene.get("description", "")
        scene_name = current_scene.get("name", f"Scene {game_state.scene + 1}")

        if scene_description:
            scene_panel = self._create_panel(
                f"[bold yellow]{scene_name}[/bold yellow]\n\n{scene_description}",
                "[bold green]📍 Current Scene[/bold green]",
                border_style="green",
                box_style=box.ROUNDED,
            )
            self.console.print("\n")
            self.console.print(scene_panel)

    def render_status(
        self,
        game_state: GameState,
        event_history: List[Event],
        story_data: Optional[StoryData] = None,
    ) -> None:
        """Render current game status."""
        status_table = self._create_table(
            "[bold green]🎮 Game Status[/bold green]",
            border_style="green",
        )
        status_table.add_column("Metric", style="cyan", width=20)
        status_table.add_column("Value", style="white")

        current_location = (
            game_state.current_event.location if game_state.current_event else "Unknown"
        )

        status_data = [
            ("Events Visited", str(len(event_history))),
            ("Items in Inventory", str(len(game_state.inventory))),
            ("Current Act", str(game_state.act + 1)),
            ("Current Scene", str(game_state.scene + 1)),
            ("Current Location", current_location),
        ]

        for metric, value in status_data:
            status_table.add_row(metric, value)

        self.console.print(status_table)

        if story_data:
            self._render_current_scene(game_state, story_data)

    def render_choice_feedback(self, choice_text: str) -> None:
        """Render feedback when a choice is made."""
        choice_panel = self._create_panel(
            f"[bold cyan]> {choice_text}[/bold cyan]",
            "",
            border_style="bright_cyan",
        )
        self.console.print(choice_panel)

    def render_message(self, message: str, message_type: str = "info") -> None:
        """Render a message with the specified type (error, success, info)."""
        style_map = {
            "error": ("[bold red]✗", "[/bold red]"),
            "success": ("[bold green]✓", "[/bold green]"),
            "info": ("[cyan]", "[/cyan]"),
        }

        prefix, suffix = style_map.get(message_type, style_map["info"])
        self.console.print(f"{prefix} {message}{suffix}")

    def render_error(self, message: str) -> None:
        """Render an error message."""
        self.render_message(message, "error")

    def render_success(self, message: str) -> None:
        """Render a success message."""
        self.render_message(message, "success")

    def render_info(self, message: str) -> None:
        """Render an info message."""
        self.render_message(message, "info")

    def render_goodbye(self) -> None:
        """Render the goodbye screen."""
        goodbye_panel = self._create_panel(
            "[bold yellow]🌟 Goodbye! 🌟[/bold yellow]\n\n[italic]Thanks for playing Texventure![/italic]",
            "",
            border_style="yellow",
            box_style=box.DOUBLE,
        )
        self.console.print(goodbye_panel)
