<div align="center">

# Agent Rate Limiter MCP

**MCP server for agent rate limiter mcp operations**

[![PyPI](https://img.shields.io/pypi/v/meok-agent-rate-limiter-mcp)](https://pypi.org/project/meok-agent-rate-limiter-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MEOK AI Labs](https://img.shields.io/badge/MEOK_AI_Labs-MCP_Server-purple)](https://meok.ai)

</div>

## Overview

Agent Rate Limiter MCP provides AI-powered tools via the Model Context Protocol (MCP).

## Tools

| Tool | Description |
|------|-------------|
| `acquire` | Request a rate-limit slot for an agent action. |
| `release` | Release a rate-limit slot. Doesn't refund tokens in the sliding window (those |
| `status` | Inspect usage. If agent_id is empty, returns tenant-wide summary. |
| `set_quota` | Override the default quota for a (tenant, agent, operation) tuple. Pro+ only. |
| `reset_counters` | Clear counters for a tenant (or a specific agent within a tenant). Pro+ only. |
| `sign_rate_limit_attestation` | Emit a cryptographically signed attestation of rate-limit enforcement over a |

## Installation

```bash
pip install meok-agent-rate-limiter-mcp
```

## Usage with Claude Desktop

Add to your Claude Desktop MCP config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "agent-rate-limiter-mcp": {
      "command": "python",
      "args": ["-m", "meok_agent_rate_limiter_mcp.server"]
    }
  }
}
```

## Usage with FastMCP

```python
from mcp.server.fastmcp import FastMCP

# This server exposes 6 tool(s) via MCP
# See server.py for full implementation
```

## License

MIT © [MEOK AI Labs](https://meok.ai)

<!-- mcp-name: io.github.CSOAI-ORG/agent-rate-limiter-mcp -->
