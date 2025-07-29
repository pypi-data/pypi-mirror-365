"""Main module for the Texventure game engine."""

import argparse
import cmd
import json
import os
import sys

from rich.console import Console

from .engine import GameEngine
from .ui import UIRenderer


class TexventureShell(cmd.Cmd):
    def __init__(
        self,
        story_file=None,
        api_key=None,
        model="gpt-4.1-nano",
        use_llm=True,
        max_tokens=800,
    ):
        super().__init__()
        self.console = Console()
        self.engine = GameEngine(use_llm=use_llm, model=model, max_tokens=max_tokens)
        self.ui = UIRenderer(self.console)
        self.prompt = "(texventure) "

        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key

        if story_file:
            self.load_story(story_file)

    def load_story(self, story_file):
        """Load story data from JSON file."""
        try:
            story_data = self._load_json_file(story_file)
            self.engine.load_story(story_data)
            self.prompt = f"({self.engine.story_data.title}) "

            if story_data.get("is_saved_game", False):
                self._handle_saved_game(story_data)
            else:
                self._handle_new_story()

        except (FileNotFoundError, json.JSONDecodeError) as e:
            error_msg = self._get_file_error_message(e, story_file)
            self.ui.render_error(error_msg)
            sys.exit(1)
        except Exception as e:
            self.ui.render_error(f"Error loading story file: {e}")
            sys.exit(1)

    def _load_json_file(self, story_file):
        """Load and parse JSON file."""
        with open(story_file, "r") as f:
            return json.load(f)

    def _get_file_error_message(self, error, story_file):
        """Get appropriate error message for file loading errors."""
        if isinstance(error, FileNotFoundError):
            return f"Story file '{story_file}' not found."
        elif isinstance(error, json.JSONDecodeError):
            return f"Invalid JSON in story file '{story_file}': {error}"
        return str(error)

    def _handle_saved_game(self, story_data):
        """Handle loading a saved game."""
        self.ui.render_title_screen(self.engine.story_data, "")
        self.console.print("\n[bold green]📁 Loading saved game...[/bold green]")

        event_count = len(self.engine.event_history)
        action_count = len(self.engine.action_log)
        save_point = story_data.get("saved_at", 0)

        self.console.print(
            f"[cyan]Restored {event_count} events and {action_count} actions from save point {save_point}[/cyan]"
        )

        if self.engine.game_state.current_event:
            self.console.print("\n[bold yellow]📍 Resuming from:[/bold yellow]")
            self.ui.render_event(self.engine.game_state.current_event)
        else:
            self.console.print(
                "\n[yellow]No current event found, starting fresh...[/yellow]"
            )
            first_event = self.engine.update_state("begin")
            self.ui.render_event(first_event)

    def _handle_new_story(self):
        """Handle loading a new story."""
        first_scene_desc = self._get_first_scene_description()
        self.ui.render_title_screen(self.engine.story_data, first_scene_desc)

        first_event = self.engine.initial_event()
        self.ui.render_event(first_event)

    def _get_first_scene_description(self):
        """Extract the first scene description for the title screen."""
        if not self.engine.story_data.acts:
            return ""

        first_act = self.engine.story_data.acts[0]
        act_scenes = first_act.get("scenes", [])

        if act_scenes:
            return act_scenes[0].get("description", "")
        return first_act.get("description", "")

    def do_look(self, arg):
        """Look around the current event."""
        current_event = self.engine.game_state.current_event
        if current_event:
            self.ui.render_event(current_event)
        else:
            self.ui.render_error("No current event to display.")

    def do_inventory(self, arg):
        """Show your inventory."""
        items_data = (
            getattr(self.engine.story_data, "items", {})
            if self.engine.story_data
            else {}
        )
        self.ui.render_inventory(self.engine.game_state.inventory, items_data)

    def do_take(self, item_name):
        """Take an item from the current event."""
        if not item_name.strip():
            self.ui.render_error("Please specify an item to take.")
            return

        success, message = self.engine.add_to_inventory(item_name)
        self.ui.render_success(message) if success else self.ui.render_error(message)

    def do_choice(self, choice_num):
        """Make a choice: choice 1."""
        if not choice_num.isdigit():
            self.ui.render_error("Please enter a valid choice number.")
            return

        choice_idx = int(choice_num) - 1
        success, message, new_event = self.engine.make_choice(choice_idx)

        if success:
            # Remove "You chose: " prefix if present
            feedback = message.split(": ", 1)[1] if ": " in message else message
            self.ui.render_choice_feedback(feedback)
            self.ui.render_event(new_event)
        else:
            self.ui.render_error(message)

    def do_save(self, filename):
        """Save the current game state."""
        if not filename.strip():
            title = (
                getattr(self.engine.story_data, "title", "Text Adventure")
                if self.engine.story_data
                else "Text Adventure"
            )
            filename = f"{title}-savegame.json"

        success, message = self.engine.save_game(filename)
        if success:
            self.ui.render_success(message)
            event_count = len(self.engine.event_history)
            action_count = len(self.engine.action_log)
            self.ui.render_info(
                f"Save includes {event_count} events visited and {action_count} actions taken."
            )
        else:
            self.ui.render_error(message)

    def do_history(self, arg):
        """Show the history of events visited and actions taken."""
        self.ui.render_action_history(self.engine.action_log)

    def do_status(self, arg):
        """Show current game status and statistics."""
        self.ui.render_status(
            self.engine.game_state, self.engine.event_history, self.engine.story_data
        )
        self._render_llm_status()

    def _render_llm_status(self):
        """Render LLM configuration status."""
        self.console.print("\n[bold blue]🤖 LLM Configuration[/bold blue]")
        if self.engine.use_llm:
            api_key_status = "✓ Set" if os.getenv("OPENAI_API_KEY") else "✗ Not set"
            self.console.print(f"LLM Enabled: [green]Yes[/green]")
            self.console.print(f"API Key: {api_key_status}")
            self.console.print(f"Model: {self.engine.model}")
            self.console.print(f"Max Tokens: {self.engine.max_tokens}")
        else:
            self.console.print("LLM Enabled: [red]No[/red] (using template events)")

    def default(self, line):
        """Handle numeric input as choices."""
        if line.isdigit():
            self.do_choice(line)
        else:
            self.ui.render_error(f"Unknown command: {line}")
            self.ui.render_info("Type 'help' for available commands.")

    def do_exit(self, arg):
        """Exit the game."""
        self.ui.render_goodbye()
        return True


def main():
    """Main entry point for the texventure command."""
    args = _parse_arguments()
    console = Console()

    # Validate story file exists
    if not os.path.exists(args.story_file):
        _print_file_not_found_error(console, args.story_file)
        sys.exit(1)

    # Configure LLM settings
    api_key = args.api_key or os.getenv("OPENAI_API_KEY")
    use_llm = not args.no_llm

    # Warn about missing API key
    if use_llm and not api_key:
        _print_api_key_warning(console)

    # Create and run the game
    game = TexventureShell(
        story_file=args.story_file,
        api_key=api_key,
        model=args.model,
        use_llm=use_llm,
        max_tokens=args.max_tokens,
    )

    try:
        game.cmdloop()
    except KeyboardInterrupt:
        console.print("\n[yellow]Goodbye![/yellow]")


def _parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run a text-based adventure game from a story JSON file"
    )
    parser.add_argument("story_file", help="Path to the story JSON file")
    parser.add_argument(
        "--api-key", help="OpenAI API key (or set OPENAI_API_KEY environment variable)"
    )
    parser.add_argument(
        "--model",
        help="LLM model to use for dynamic event generation",
        default="gpt-4.1-nano",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        help="Maximum number of tokens for LLM responses (default: 800)",
        default=800,
    )
    parser.add_argument(
        "--no-llm",
        action="store_true",
        help="Disable LLM-powered dynamic event generation",
    )
    return parser.parse_args()


def _print_file_not_found_error(console, story_file):
    """Print error message when story file is not found."""
    console.print(
        f"[bold red]Error:[/bold red] Story file '[cyan]{story_file}[/cyan]' not found."
    )
    console.print("[yellow]Usage:[/yellow] [cyan]texventure <story_file.json>[/cyan]")


def _print_api_key_warning(console):
    """Print warning when LLM is enabled but no API key is provided."""
    console.print(
        "[yellow]Warning:[/yellow] LLM is enabled but no API key provided. "
        "Dynamic event generation will fall back to basic templates."
    )
    console.print(
        "[italic]Set OPENAI_API_KEY environment variable or use --api-key flag for full LLM features.[/italic]"
    )


if __name__ == "__main__":
    main()
