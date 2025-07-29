# MCP Ableton Live Server

A Model Context Protocol (MCP) server for Ableton Live integration.

## Features

- Connect to Ableton Live via Live API
- Control playback, recording, and transport
- Access track and device parameters
- Manage clips and scenes

## Installation

```bash
pip install mcp-ableton-live
```

## Usage

Add to your MCP configuration:

```json
{
  "mcpServers": {
    "ableton-live": {
      "command": "uvx",
      "args": ["mcp-ableton-live"],
      "disabled": false
    }
  }
}
```

## Requirements

- Ableton Live 11 or later
- Python 3.8+
- Live API enabled in Ableton Live preferences

## License

MIT