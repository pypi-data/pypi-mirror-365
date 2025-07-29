"""Story generator module for Texventure."""

import argparse
import json
import os
import sys
from typing import List

import requests
import toml
from pydantic import BaseModel, Field


class Scene(BaseModel):
    name: str = ""
    description: str = ""
    location: str = ""
    trigger: str = ""


class Act(BaseModel):
    name: str = ""
    description: str = ""
    scenes: List[Scene] = Field(default_factory=list)


class NPC(BaseModel):
    name: str = ""
    role: str = ""
    description: str = ""
    personality: str = ""


class Story(BaseModel):
    title: str = ""
    setting: str = ""
    outline: str = ""
    style_genre: str = ""
    n_acts: int = 3
    n_scenes: int = 2
    n_npcs: int = 3
    npcs: List[NPC] = Field(default_factory=list)
    acts: List[Act] = Field(default_factory=list)


def llm_call(prompt, api_key, model="gpt-4.1-nano", force_json=False, max_tokens=800):
    """Call the LLM API to generate the story."""
    api_url = "https://api.openai.com/v1/chat/completions"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}

    # Adjust system message based on whether JSON is requested
    if force_json:
        system_content = "You are a creative writing assistant that generates detailed interactive fiction stories. Always respond with valid JSON when requested, using the exact field names provided in the prompt."
    else:
        system_content = "You are a creative writing assistant that generates detailed interactive fiction stories."
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": system_content,
            },
            {"role": "user", "content": prompt},
        ],
        "max_tokens": max_tokens,
        "temperature": 0.8,
    }

    # Add JSON response format if requested
    if force_json:
        payload["response_format"] = {"type": "json_object"}

    try:
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        return content.strip() if content else "No response from LLM"

    except requests.RequestException as e:
        print(f"Error calling LLM API: {e}")
        return None


def form_bulk_prompt(empty_fields, context):
    """Form a prompt to fill multiple empty fields at once."""
    fields_list = "\n".join([f"- {field}" for field in empty_fields])
    return f"""Generate content for the following empty fields in an interactive fiction story. Return your response as a JSON object where each key is the field path and the value is the generated content.

        Each npc is a character in the story, they have a name, role, description, and personality.
        Each act is a major section of the story with a name and description.
        Each scene is a part of an act with a name, description, location, and trigger.
        Descriptions are detailed and should fit the context of the story and describe the narrative.
        Triggers are actions or choices the user makes that lead to the next scene in the story.
        
        All content should match the setting, outline, and style_genre specified in the story context. The style_genre defines the narrative style and genre conventions that should be followed throughout the story.

        Empty fields to fill:
        {fields_list}

        Current story data for context:
        {context}

        Return a JSON object with the field paths as keys and the generated content as values. For example:
        {{"title": "The Mysterious Castle", "setting": "A dark medieval fantasy world", "outline": "A hero must explore a haunted castle to rescue a princess", "style_genre": "Gothic horror adventure"}}"""


def collect_empty_fields(data, path=""):
    """Collect all empty string fields in the data structure."""
    empty_fields = []

    if isinstance(data, dict):
        for key, value in data.items():
            current_path = f"{path}.{key}" if path else key
            if isinstance(value, (dict, list)):
                empty_fields.extend(collect_empty_fields(value, current_path))
            elif value == "":
                empty_fields.append(current_path)
    elif isinstance(data, list):
        for i, item in enumerate(data):
            current_path = f"{path}[{i}]"
            empty_fields.extend(collect_empty_fields(item, current_path))

    return empty_fields


def set_nested_value(data, path, value):
    """Set a value in nested data structure using dot notation path."""
    parts = path.split(".")
    current = data

    for part in parts[:-1]:
        if "[" in part and "]" in part:
            # Handle array notation like "acts[0]"
            key, index_str = part.split("[")
            index = int(index_str.rstrip("]"))
            current = current[key][index]
        else:
            current = current[part]

    final_part = parts[-1]
    if "[" in final_part and "]" in final_part:
        # Handle array notation for final part
        key, index_str = final_part.split("[")
        index = int(index_str.rstrip("]"))
        current[key][index] = value
    else:
        current[final_part] = value


def generate_story(story_data, api_key, model="gpt-4.1-nano", max_tokens=800):
    """Generate story content using JSON responses to fill multiple fields at once."""

    if not api_key:
        print("No API key provided, skipping LLM generation")
        return

    # Collect all empty fields
    empty_fields = collect_empty_fields(story_data)

    if not empty_fields:
        print("No empty fields to fill")
        return

    print(f"Found {len(empty_fields)} empty fields to fill")

    # Process fields in batches to avoid token limits
    batch_size = 10  # Adjust based on token limits and field complexity

    for i in range(0, len(empty_fields), batch_size):
        batch_fields = empty_fields[i : i + batch_size]
        print(f"Filling batch {i//batch_size + 1}: {len(batch_fields)} fields")

        # Create prompt for this batch
        context = json.dumps(story_data, indent=2)
        prompt = form_bulk_prompt(batch_fields, context)

        # Get JSON response from LLM
        llm_response = llm_call(
            prompt, api_key, model, force_json=True, max_tokens=max_tokens
        )

        if llm_response:
            try:
                # Parse JSON response
                generated_content = json.loads(llm_response)

                # Apply generated content to story data
                for field_path, content in generated_content.items():
                    if field_path in batch_fields and content.strip():
                        set_nested_value(story_data, field_path, content.strip())
                        print(f"  Filled: {field_path}")

            except json.JSONDecodeError as e:
                print(f"Failed to parse JSON response: {e}")
                print(f"Raw response: {llm_response}")
                # Fallback to single-field approach for this batch
                _fill_fields_individually(
                    story_data, batch_fields, api_key, model, max_tokens
                )
        else:
            print(f"No response from LLM for batch {i//batch_size + 1}")


def _fill_fields_individually(story_data, fields, api_key, model, max_tokens=800):
    """Fallback method to fill fields one by one if JSON parsing fails."""
    print("Falling back to individual field filling...")

    for field_path in fields:
        prompt = f"Generate content for the '{field_path}' field of an interactive fiction story. Ensure the content matches the setting, outline, and style_genre specified in the story context. The current story data is: {json.dumps(story_data, indent=2)}"
        llm_response = llm_call(prompt, api_key, model, max_tokens=max_tokens)

        if llm_response and llm_response.strip():
            set_nested_value(story_data, field_path, llm_response.strip())
            print(f"  Filled: {field_path}")


def format_story(template_data):
    story = Story.model_validate(template_data)
    story_data = story.model_dump()
    # Ensure we have the required number of acts
    while len(story_data["acts"]) < story_data["n_acts"]:
        act_number = len(story_data["acts"]) + 1
        new_act = Act(name="", description="", scenes=[])
        story_data["acts"].append(new_act.model_dump())

    # Ensure each act has the required number of scenes
    for act in story_data["acts"]:
        while len(act["scenes"]) < story_data["n_scenes"]:
            scene_number = len(act["scenes"]) + 1
            new_scene = Scene(name="", description="", location="", trigger="")
            act["scenes"].append(new_scene.model_dump())

    # Ensure we have the required number of NPCs
    while len(story_data["npcs"]) < story_data["n_npcs"]:
        npc_number = len(story_data["npcs"]) + 1
        new_npc = NPC(name="", role="", description="", personality="")
        story_data["npcs"].append(new_npc.model_dump())
    return story_data


def main():
    """Main entry point for the texventure-generate command."""
    parser = argparse.ArgumentParser(
        description="Generate a story file from a TOML template"
    )
    parser.add_argument("toml_file", help="Path to the TOML template file")
    parser.add_argument(
        "-o",
        "--output",
        help="Output JSON file path (default: story.json)",
        default="story.json",
    )
    parser.add_argument(
        "--api-key", help="OpenAI API key (or set OPENAI_API_KEY environment variable)"
    )
    parser.add_argument("--model", help="LLM model to use", default="gpt-4.1-nano")
    parser.add_argument(
        "--max-tokens",
        type=int,
        help="Maximum number of tokens for LLM responses (default: 800)",
        default=800,
    )
    parser.add_argument(
        "--no-llm", action="store_true", help="Generate basic story without LLM"
    )
    args = parser.parse_args()

    # Read TOML template file
    try:
        with open(args.toml_file, "r") as f:
            template_data = toml.load(f)

    except FileNotFoundError:
        print(f"Error: Template file {args.toml_file} not found")
        return 1

    print(f"Generating story from template: {args.toml_file}")

    story_data = format_story(template_data)

    if not args.no_llm:
        # Get API key
        api_key = args.api_key or os.getenv("OPENAI_API_KEY")

        if api_key:
            print("Calling LLM to generate detailed story...")
            generate_story(story_data, api_key, args.model, args.max_tokens)

        else:
            print(
                "Warning: No API key provided. Use --api-key or set OPENAI_API_KEY environment variable."
            )
    else:
        print("Generating basic outline without LLM...")

    # Write story to output file
    try:
        with open(args.output, "w") as f:
            json.dump(story_data, f)
        print(f"Story generated successfully: {args.output}")
        print(f"Run the game with: texventure {args.output}")
        return 0
    except IOError as e:
        print(f"Error writing output file {args.output}: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
