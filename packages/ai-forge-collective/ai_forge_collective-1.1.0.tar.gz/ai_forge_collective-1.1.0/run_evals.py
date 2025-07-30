"""Automated eval runner that uses the Claude Code Python SDK
instead of the standard Anthropic API.

Each eval task lives under `evals/<task_name>/` with:
    - prompt.txt         : user prompt to send to Claude
    - test_*.py          : pytest file(s) that validate the output

Execution strategy:
1. For every task, create a temporary directory sandbox so no state leaks.
2. Stream Claude's response using `claude_code_sdk.query`. Accumulate the full
   assistant text, then extract the first ```python code block.
3. Write the generated code into the sandbox. Copy the task's test files into
   the same sandbox.
4. Run `pytest` inside the sandbox to validate.
5. Record metrics: success/failure, elapsed seconds, approx token usage.
6. Show a rich table summary.

Run with:
    uv run python run_evals_cc.py
"""

from __future__ import annotations

import logging
import re
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

import anthropic
import anyio
from claude_code_sdk import ClaudeCodeOptions, TextBlock, query
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Configuration ---------------------------------------------------------
EVALS_DIR = Path("evals")
CLAUDE_MD_PATH = Path("output/CLAUDE.md")
TEMP_CODE_FILENAME = "temp_generated_code.py"

# ---------------------------------------------------------------------------


def load_env_file() -> None:
    """Load environment variables from .env file if it exists."""
    load_dotenv()


def extract_python_code(markdown: str) -> str | None:
    """Return the *first* Python code block from a markdown string."""
    # Try to find code in fenced blocks first
    match = re.search(r"```python\n(.*?)\n```", markdown, re.DOTALL)
    if match:
        return match.group(1)

    # Try to find code in generic fenced blocks
    match = re.search(r"```\n(.*?)\n```", markdown, re.DOTALL)
    if match:
        return match.group(1)

    # If no fenced block found, check if the entire response looks like Python code
    # This handles cases where the response is direct Python code without fences
    stripped = markdown.strip()
    if (
        stripped.startswith("def ")
        or stripped.startswith("class ")
        or "def " in stripped
    ):
        return stripped

    return None


def count_tokens(prompt: str, system_prompt: str) -> int:
    """Get accurate token count using Anthropic's count_tokens endpoint."""
    try:
        client = anthropic.Anthropic()
        response = client.messages.count_tokens(
            model="claude-3-5-sonnet-20241022",
            system=system_prompt,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.input_tokens
    except Exception as e:
        logger.warning(f"Token counting failed: {e}")
        return 0  # Fallback if token counting fails


async def collect_response(user_prompt: str, system_prompt: str) -> str:
    """Collect the full response from Claude Code SDK with Anthropic API fallback."""
    # Try Claude Code SDK first
    options = ClaudeCodeOptions()
    full_response = ""
    message_count = 0

    try:
        async for message in query(prompt=user_prompt, options=options):
            message_count += 1
            logger.debug(f"Received message {message_count}: {type(message).__name__}")

            if hasattr(message, "content") and message.content:
                logger.debug(f"Message has {len(message.content)} content blocks")
                for i, block in enumerate(message.content):
                    logger.debug(f"Block {i}: {type(block).__name__}")
                    if isinstance(block, TextBlock):
                        logger.debug(f"TextBlock content length: {len(block.text)}")
                        full_response += block.text
            else:
                logger.debug("Message has no content or empty content")

            # Check if it's a message with text directly
            if hasattr(message, "text"):
                logger.debug(f"Message has direct text: {len(message.text)}")
                full_response += message.text

    except Exception as e:
        logger.error(f"Exception in collect_response: {e}")
        raise

    logger.info(
        f"Total messages: {message_count}, Final response length: {len(full_response)}"
    )

    # If Claude Code SDK didn't return any messages, fallback to Anthropic API
    if message_count == 0:
        logger.warning(
            "Claude Code SDK returned no messages, falling back to Anthropic API"
        )
        try:
            client = anthropic.Anthropic()
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4000,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )
            full_response = response.content[0].text if response.content else ""
            logger.info(f"Fallback API response length: {len(full_response)}")
        except Exception as e:
            logger.error(f"Fallback API also failed: {e}")
            raise

    return full_response


async def run_single_eval(
    task_name: str, system_prompt: str
) -> dict[str, str | int | float]:
    """Run one eval task and return a result dict suitable for tabulation."""
    task_dir = EVALS_DIR / task_name
    prompt_path = task_dir / "prompt.txt"
    test_files = list(task_dir.glob("test_*.py"))

    if not prompt_path.exists():
        logger.error(f"Missing prompt file for task {task_name}")
        return {"status": "FAIL", "reason": "Missing prompt.txt file."}

    if not test_files:
        logger.error(f"No test files found for task {task_name}")
        return {"status": "FAIL", "reason": "No test_*.py files found."}

    try:
        user_prompt = prompt_path.read_text()
    except Exception as e:
        logger.error(f"Failed to read prompt file for task {task_name}: {e}")
        return {"status": "FAIL", "reason": f"Failed to read prompt: {e}"}

    # Get token count for the input
    input_tokens = count_tokens(user_prompt, system_prompt)

    # Track files before SDK call to clean up any created files
    root_dir = Path.cwd()
    files_before = set(f.name for f in root_dir.glob("*.py") if f.is_file())

    start = time.perf_counter()
    try:
        assistant_md = await collect_response(user_prompt, system_prompt)
    except Exception as e:
        logger.error(f"SDK error for task {task_name}: {e}")
        return {
            "status": "FAIL",
            "reason": f"SDK error: {e}",
            "duration": 0,
            "tokens": input_tokens,
        }
    finally:
        # Clean up any .py files created by SDK in root directory
        files_after = set(f.name for f in root_dir.glob("*.py") if f.is_file())
        new_files = files_after - files_before
        for filename in new_files:
            file_path = root_dir / filename
            if file_path.exists():
                logger.info(f"Cleaning up SDK-created file: {filename}")
                file_path.unlink()

    duration = time.perf_counter() - start

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)

            generated_code = extract_python_code(assistant_md)
            if not generated_code:
                logger.warning(f"No Python code found in response for task {task_name}")
                return {
                    "status": "FAIL",
                    "reason": (
                        f"No python code fence found in response. "
                        f"Response length: {len(assistant_md)} chars. "
                        f"Response: '{assistant_md[:200]}'"
                    ),
                    "duration": duration,
                    "tokens": input_tokens,
                }

            code_file = tmp_path / TEMP_CODE_FILENAME
            code_file.write_text(generated_code)

            for tf in test_files:
                shutil.copy(tf, tmp_path / tf.name)

            result = subprocess.run(
                ["pytest", "-q"], cwd=tmp_path, capture_output=True, text=True
            )

            status = "SUCCESS" if result.returncode == 0 else "FAIL"
            reason = (
                "Tests passed" if status == "SUCCESS" else result.stdout + result.stderr
            )

    except Exception as e:
        logger.error(f"Error running eval for task {task_name}: {e}")
        return {
            "status": "FAIL",
            "reason": f"Eval execution error: {e}",
            "duration": 0,
            "tokens": input_tokens,
        }

    return {
        "status": status,
        "reason": reason,
        "duration": duration,
        "tokens": input_tokens,
    }


def get_valid_tasks() -> list[str]:
    """Get list of valid task directories with both prompt.txt and test files."""
    tasks = []
    for d in EVALS_DIR.iterdir():
        if d.is_dir():
            prompt_file = d / "prompt.txt"
            test_files = list(d.glob("test_*.py"))
            if prompt_file.exists() and test_files:
                tasks.append(d.name)
    return sorted(tasks)


async def amain() -> None:
    """Main async function to run all evaluations."""
    # Load environment variables from .env file if it exists
    load_env_file()

    console = Console()

    if not CLAUDE_MD_PATH.exists():
        console.print(
            f"[bold red]Error: {CLAUDE_MD_PATH} not found. Run build first.[/bold red]"
        )
        return

    try:
        system_prompt = CLAUDE_MD_PATH.read_text()
    except Exception as e:
        console.print(f"[bold red]Error reading system prompt: {e}[/bold red]")
        return

    table = Table(title="AI-Forge Evaluation Results (Claude Code)")
    table.add_column("Task", style="cyan")
    table.add_column("Completion", style="magenta")
    table.add_column("Approx Tokens", style="green")
    table.add_column("Duration (s)", style="yellow")

    tasks = get_valid_tasks()

    if not tasks:
        console.print("[yellow]No valid evaluation tasks found.[/yellow]")
        return

    logger.info(f"Found {len(tasks)} valid evaluation tasks")

    for task in tasks:
        with console.status(f"[bold green]Running eval for {task}...[/bold green]"):
            res = await run_single_eval(task, system_prompt)
        emoji = "✅" if res["status"] == "SUCCESS" else "❌"

        # Print failure reason for debugging
        if res["status"] == "FAIL":
            console.print(
                f"[red]Task {task} failed: {res.get('reason', 'Unknown reason')}[/red]"
            )

        table.add_row(
            task,
            f"{emoji} {res['status']}",
            str(res.get("tokens", "N/A")),
            f"{res.get('duration', 0):.2f}",
        )

    console.print(table)


def main() -> None:
    anyio.run(amain)


if __name__ == "__main__":
    main()
