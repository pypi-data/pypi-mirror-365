# UI MCP Server

[![CI](https://github.com/ShaojieJiang/ui-mcp-server/actions/workflows/ci.yml/badge.svg?event=push)](https://github.com/ShaojieJiang/ui-mcp-server/actions/workflows/ci.yml?query=branch%3Amain)
[![Coverage](https://coverage-badge.samuelcolvin.workers.dev/ShaojieJiang/ui-mcp-server.svg)](https://coverage-badge.samuelcolvin.workers.dev/redirect/ShaojieJiang/ui-mcp-server)
[![PyPI](https://img.shields.io/pypi/v/ui-mcp-server.svg)](https://pypi.python.org/pypi/ui-mcp-server)

This project initiates at the [Power of Europe Hackathon 2025](https://rewirenow.com/en/resources/blog/power-of-europe-hackathon-building-with-european-ai/).

## Demo

[![Demo Video](https://img.youtube.com/vi/o_kE_zjVRKc/0.jpg)](https://www.youtube.com/watch?v=o_kE_zjVRKc)

https://youtu.be/o_kE_zjVRKc

## Overview

`ui-mcp-server` is an MCP server that generates specifications for a range of UI components, containing only essential data to remain framework-agnostic. Unlike existing solutions, `ui-mcp-server` is data-focused, acquiring and filling data during conversation sessions while leaving rendering entirely to frontend developers (for now).

## Features

- Framework-agnostic UI component specifications
- Data-focused approach with conversation session support
- Full developer freedom for rendering and customization
- Compatible with MCP clients like Cursor, Kilo and Claude Desktop

## Installation

### Claude Desktop

1. Add the server to your Claude Desktop configuration file (`claude_desktop_config.json`):
   ```json
   {
     "mcpServers": {
       "UI MCP Server": {
         "command": "full/path/to/uvx",
         "args": ["ui-mcp-server"]
       },
       // Your existing MCP servers...
     }
   }
   ```

2. Restart Claude Desktop to load the MCP server.

### Kilo

A working configuration looks like below:

```json
{
  "mcpServers": {
    "ui-mcp-server":{
      "command": "full/path/to/ui-mcp-server",
      "args": []
    }
  }
}
```

We might have missed something as the expected version below didn't work:
```json
{
  "mcpServers": {
    "ui-mcp-server":{
      "command": "full/path/to/uvx",
      "args": ["ui-mcp-server"]
    }
  }
}
```

## Core concepts

- UI-as-a-tool: `ui-mcp-server` provides tools that can be used to generate UI components. To this end, frequently used UI components are defined as tools, and the data required for each tool is acquired during the conversation session. The data extraction part is taken care of by AI agents using this MCP server. See our [Streamlit demo](examples/streamlit/) for an example.
- Component standardisation: To be agnostic of frontend frameworks, `ui-mcp-server` defines a standardised component library, which is basically a set of JSON schemas for UI components, with some values are predefined, and others are left to be filled by AI.

## Related Projects

- [Magic MCP](https://github.com/21st-dev/magic-mcp): Generates React components, focusing on development productivity
- [MCP UI](https://github.com/idosal/mcp-ui): Similar concept to this project but with tighter coupling to specific UI implementations. Can't be used as a standalone MCP server.
- [shadcn-ui-mcp-server](https://github.com/Jpisnice/shadcn-ui-mcp-server): Similart to MCP UI, a battery-included solution providing shadcn components as source code.

## Key Differentiators

**Separation of Concerns**: `ui-mcp-server` handles UI types and conversation data exclusively, providing maximum flexibility for developers to customize and render components according to their specific needs and frameworks.

## Future work

- Define standardized component libraries for mainstream frameworks (React, Vue, Svelte, etc.)
- Create templates to streamline frontend development workflow
