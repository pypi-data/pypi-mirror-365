# Texventure

A text-based adventure game. It allows you to create and play interactive stories using a command-line interface.

## Installation

Clone the repository and install with `pip install .` from within the repo 

## Requirements

texventure relies on openai for dynamic event generation, so you need to have an OpenAI API key. You can set it as an environment variable:

```bash
export OPENAI_API_KEY="your_api_key_here"
```
You can optionally choose the model to use for dynamic event generation by passing the `--model` argument when running the game. The default model is `gpt-4.1-nano`, but you can change it to any other OpenAI model that suits your needs.

## Creating a story

To create a story, you need to write a TOML file that defines the structure of your adventure. The file should include the following sections:

- `title`: The title of your story.
- `setting`: A description of the world where the story takes place.
- `outline`: A brief overview of the main plot points.
- `n_acts`: The number of acts in your story.
- `n_scenes`: The number of scenes in each act.
- `n_npcs`: The number of non-player characters (NPCs) in your story.

You can optionall also provide the acts and scenes in the TOML file, or you can let the game generate them dynamically based on your outline.

With a template complete, generate a story file with the following command:

```bash
texventure-generate your_story_template.toml -o your_story_file.json
```
See `template.toml` as an example.

## Playing a texventure game
To play a game, run the following command:

```bash
texventure-play your_story_file.json
```
## Commands

Within the game, you are presented with events in the narrative, and you must make choices to progress the story. Additionally, you can use the following commands:
- `look`: Look around the current scene.
- `history`: View the history of your actions.
- `inventory`: Check your inventory for items you have collected.
- `save`: Save your current game state.
- `status`: Check your current status, scene, and other relevant information.
- `choice <choice_number>`: Make a choice based on the available options presented in the current scene.
- `exit`: Exit the game.

The save command will produce a `your_story_file-savegame.json`. To continue your progress where you left off, run the play command with the save file:

```bash
texventure your_story_file-savegame.json
```