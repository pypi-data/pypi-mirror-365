#!/usr/bin/env python3
"""Test script to verify Claude Code SDK functionality."""

import asyncio

import pytest
from claude_code_sdk import ClaudeCodeOptions, TextBlock, query


@pytest.mark.asyncio
async def test_simple_query():
    """Test a simple query to the Claude Code SDK."""
    print("Testing simple query...")

    options = ClaudeCodeOptions()
    message_count = 0

    try:
        async for message in query(
            prompt="Hello, please respond with just 'Hi there!'", options=options
        ):
            message_count += 1
            print(f"Message {message_count}: {type(message).__name__}")
            print(f"Message attributes: {dir(message)}")

            if hasattr(message, "content") and message.content:
                print(f"Message has {len(message.content)} content blocks")
                for i, block in enumerate(message.content):
                    print(f"Block {i}: {type(block).__name__}")
                    if isinstance(block, TextBlock):
                        print(f"TextBlock content: {block.text}")

            if hasattr(message, "text"):
                print(f"Direct text: {message.text}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()

    print(f"Total messages received: {message_count}")


if __name__ == "__main__":
    asyncio.run(test_simple_query())
