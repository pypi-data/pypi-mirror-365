#!/usr/bin/env python3
"""MCP server for Ableton Live integration."""

import asyncio
import logging
from typing import Any, Sequence

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-ableton-live")

# Create server instance
server = Server("mcp-ableton-live")


@server.list_tools()
async def handle_list_tools() -> ListToolsResult:
    """List available Ableton Live tools."""
    return ListToolsResult(
        tools=[
            Tool(
                name="play",
                description="Start playback in Ableton Live",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            ),
            Tool(
                name="stop",
                description="Stop playback in Ableton Live",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            ),
            Tool(
                name="record",
                description="Start/stop recording in Ableton Live",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "enable": {
                            "type": "boolean",
                            "description": "Enable or disable recording",
                            "default": True,
                        }
                    },
                    "required": [],
                },
            ),
            Tool(
                name="get_tempo",
                description="Get current tempo from Ableton Live",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            ),
            Tool(
                name="set_tempo",
                description="Set tempo in Ableton Live",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "bpm": {
                            "type": "number",
                            "description": "Tempo in beats per minute",
                            "minimum": 20,
                            "maximum": 999,
                        }
                    },
                    "required": ["bpm"],
                },
            ),
        ]
    )


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict[str, Any] | None
) -> CallToolResult:
    """Handle tool calls for Ableton Live operations."""
    if arguments is None:
        arguments = {}

    try:
        if name == "play":
            # In a real implementation, this would connect to Ableton Live
            # For now, return a placeholder response
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text="Playback started in Ableton Live (placeholder - requires Live API connection)",
                    )
                ]
            )

        elif name == "stop":
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text="Playback stopped in Ableton Live (placeholder - requires Live API connection)",
                    )
                ]
            )

        elif name == "record":
            enable = arguments.get("enable", True)
            action = "started" if enable else "stopped"
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Recording {action} in Ableton Live (placeholder - requires Live API connection)",
                    )
                ]
            )

        elif name == "get_tempo":
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text="Current tempo: 120 BPM (placeholder - requires Live API connection)",
                    )
                ]
            )

        elif name == "set_tempo":
            bpm = arguments.get("bpm")
            if bpm is None:
                raise ValueError("BPM is required")
            
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Tempo set to {bpm} BPM in Ableton Live (placeholder - requires Live API connection)",
                    )
                ]
            )

        else:
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        logger.error(f"Error in tool {name}: {e}")
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"Error: {str(e)}",
                )
            ],
            isError=True,
        )


async def main():
    """Main entry point for the server."""
    # Run the server using stdin/stdout streams
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="mcp-ableton-live",
                server_version="0.1.0",
                capabilities=server.get_capabilities(),
            ),
        )


def cli_main():
    """CLI entry point."""
    asyncio.run(main())


if __name__ == "__main__":
    cli_main()