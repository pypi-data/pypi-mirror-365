import os
import click
import requests
import json
import shutil
import sys
from typing import List, Optional, Dict, Any

OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
OPENAI_API_URL: str = os.getenv("OPENAI_API_URL", "https://api.openai.com/v1/chat/completions")
FABRIC_MODEL_NAME: str = os.getenv("FABRIC_MODEL_NAME", "gpt-3.5-turbo")

def ensure_config_patterns_exist():
    config_patterns_dir = os.path.expanduser("~/.config/.patterns")
    source_patterns_dir = "patterns"

    if not os.path.exists(config_patterns_dir):
        try:
            os.makedirs(config_patterns_dir)
            click.echo(f"Created directory: {config_patterns_dir}")
        except OSError as e:
            click.echo(f"Error creating directory {config_patterns_dir}: {e}")
            return

    try:
        for filename in os.listdir(source_patterns_dir):
            if filename.endswith(".md"):
                source_file = os.path.join(source_patterns_dir, filename)
                dest_file = os.path.join(config_patterns_dir, filename)
                if not os.path.exists(dest_file):
                    shutil.copy2(source_file, dest_file)
                    click.echo(f"Copied {source_file} to {dest_file}")
    except FileNotFoundError:
        click.echo(f"Warning: Source patterns directory '{source_patterns_dir}' not found. Cannot copy initial patterns.")
    except Exception as e:
        click.echo(f"Error copying pattern files: {e}")

def list_patterns_from_directory(patterns_dir: str = os.path.expanduser("~/.config/.patterns")) -> None:
    available_patterns: List[str] = []
    try:
        if not os.path.isdir(patterns_dir):
            click.echo(f"Error: Directory '{patterns_dir}' not found.")
            return

        for filename in os.listdir(patterns_dir):
            if filename.endswith(".md"):
                pattern_name = os.path.splitext(filename)[0]
                available_patterns.append(pattern_name)
        
        if available_patterns:
            click.echo("Available patterns:")
            for pattern in available_patterns:
                click.echo(f"- {pattern}")
        else:
            click.echo(f"No patterns found in the '{patterns_dir}' directory.")
    except Exception as e:
        click.echo(f"Error listing patterns: {e}")

def get_system_prompt_content(system_prompt_name: str) -> Optional[str]:
    config_patterns_dir = os.path.expanduser("~/.config/.patterns")
    system_prompt_path = os.path.join(config_patterns_dir, f"{system_prompt_name}.md")
    try:
        with open(system_prompt_path, 'r', encoding='utf-8') as f:
            content = f.read()
        click.echo(f"Loaded system prompt from: {system_prompt_path}")
        return content
    except FileNotFoundError:
        click.echo(f"Error: System prompt file not found at {system_prompt_path}")
        return None
    except Exception as e:
        click.echo(f"Error reading system prompt file: {e}")
        return None

@click.command()
@click.argument('user_prompt', required=False, type=str)
@click.option(
        '-p', 
        '--pattern', 
        'system_prompt_name', 
        type=str, 
        help='Name of the system prompt template file in the patterns/ directory.'
    )
@click.option(
        '-l', 
        '--list-patterns', 
        'list_patterns', 
        is_flag=True, 
        help='List all available pattern files in the patterns/ directory.'
    )
def main(user_prompt: Optional[str], system_prompt_name: Optional[str], list_patterns: bool) -> None:
    ensure_config_patterns_exist()

    if list_patterns:
        list_patterns_from_directory()
        return

    # If user_prompt is not provided via command line, check for piped input
    if user_prompt is None and not sys.stdin.isatty():
        user_prompt = sys.stdin.read()

    # If still no user prompt and no system prompt, exit with error
    if not user_prompt and not system_prompt_name:
        click.echo("Error: Please provide a user prompt or specify a system prompt using -p.")
        return

    if not OPENAI_API_KEY:
        click.echo("Error: OPENAI_API_KEY not found in .env file. Please set it.")
        return

    system_prompt_content: Optional[str] = None
    if system_prompt_name:
        system_prompt_content = get_system_prompt_content(system_prompt_name)
        if system_prompt_content is None:
            return

    messages: List[Dict[str, str]] = [{"role": "user", "content": user_prompt}]
    if system_prompt_content:
        messages.insert(0, {"role": "system", "content": system_prompt_content})

    headers: Dict[str, str] = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }

    data: Dict[str, Any] = {
        "model": FABRIC_MODEL_NAME,
        "messages": messages,
        "stream": True, 
    }

    try:
        response = requests.post(OPENAI_API_URL, headers=headers, json=data, stream=True)

        if response.status_code != 200:
            try:
                error_data = response.json()
                click.echo(f"Error: Received status code {response.status_code}")
                click.echo(f"API Response: {json.dumps(error_data, indent=2)}")
            except json.JSONDecodeError:
                click.echo(f"Error: Received status code {response.status_code} with non-JSON response.")
                click.echo(f"Response text: {response.text}")
            return

        full_response_content: str = ""
        for chunk in response.iter_lines():
            if chunk:
                decoded_chunk = chunk.decode('utf-8')
                if decoded_chunk.startswith("data: "):
                    json_data = decoded_chunk[len("data: "):]
                    if json_data == "[DONE]":
                        break
                    try:
                        chunk_data = json.loads(json_data)
                        if "choices" in chunk_data and chunk_data["choices"]:
                            content = chunk_data["choices"][0].get("delta", {}).get("content")
                            if content:
                                click.echo(content, nl=False)
                                full_response_content += content
                    except json.JSONDecodeError:
                        pass
        click.echo()

    except requests.exceptions.RequestException as e:
        click.echo(f"Error making request to OpenAI API: {e}")
    except Exception as e:
        click.echo(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    main()
