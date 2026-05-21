<div align="center">

> ## 🧱 Part of the MEOK A2A Substrate
>
> This MCP is 1 of 12 agent-to-agent primitives. Run the whole pipeline
> (identity → trust → policy → firewall → rate-limit → handoff → audit
> → governance) as one signed endpoint for **£499/mo** including 100K
> calls — or **£0.0002 per call** pay-as-you-go.
>
> 👉 [meok.ai/a2a](https://meok.ai/a2a) — see the Substrate

# Agent Rate Limiter MCP


> ## Buy Starter — £29/mo
> **Signed attestations + unlimited audits + email support.**
> 👉 **[Subscribe at meok.ai](https://buy.stripe.com/4gMeVfa8sfZ07ohfL28k843)** — instant HMAC signing key + Stripe-managed billing.
>
> Free tier remains MIT-licensed and zero-config. Upgrade only when you need signed compliance artefacts for audit.

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


## Sister MCPs

Part of the MEOK **A2a** pack — designed to work together as a fleet. Install the whole pack with `npx meok-setup --pack a2a`, or pick the ones you need:

- **Prompt Injection Firewall** → `uvx agent-prompt-injection-firewall-mcp` · [PyPI](https://pypi.org/project/agent-prompt-injection-firewall-mcp/) · [GitHub](https://github.com/CSOAI-ORG/agent-prompt-injection-firewall-mcp)
- **Data Residency** → `uvx agent-data-residency-mcp` · [PyPI](https://pypi.org/project/agent-data-residency-mcp/) · [GitHub](https://github.com/CSOAI-ORG/agent-data-residency-mcp)
- **Certified Handoff** → `uvx agent-handoff-certified-mcp` · [PyPI](https://pypi.org/project/agent-handoff-certified-mcp/) · [GitHub](https://github.com/CSOAI-ORG/agent-handoff-certified-mcp)
- **Policy Enforcement** → `uvx agent-policy-enforcement-mcp` · [PyPI](https://pypi.org/project/agent-policy-enforcement-mcp/) · [GitHub](https://github.com/CSOAI-ORG/agent-policy-enforcement-mcp)
- **Audit Logger** → `uvx agent-audit-logger-mcp` · [PyPI](https://pypi.org/project/agent-audit-logger-mcp/) · [GitHub](https://github.com/CSOAI-ORG/agent-audit-logger-mcp)

Full catalogue + Anthropic Registry verify links: [meok.ai/anthropic-registry](https://meok.ai/anthropic-registry)


## Protocol coverage + Universal PAYG

This MCP is part of MEOK's 47-MCP fleet that bridges every active agent-interop protocol
and 30+ regulatory frameworks. See the full coverage matrix at [meok.ai/protocols](https://meok.ai/protocols).

**Agent interop protocols supported (8 live):**

- ✅ **MCP** (Anthropic) — native
- ✅ **A2A** (Google + Linux Foundation, absorbed IBM ACP Sept 2025)
- ✅ **IBM ACP** — covered via A2A merge
- ◐ **Stripe ACP** (Agentic Commerce Protocol) — Q3 bridge via [agent-commerce-protocol-mcp](https://github.com/CSOAI-ORG/agent-commerce-protocol-mcp)
- ◐ **AP2** (Google Agent Payments) — partial via [agent-commerce-payments-mcp](https://github.com/CSOAI-ORG/agent-commerce-payments-mcp)
- ◐ **x402** (Coinbase HTTP 402) — partial via api.meok.ai gateway
- → **OASF / AGNTCY** (Cisco Outshift + Linux Foundation) — Q3 bridge
- 👁 **ANP** (Cisco Agent Network) — watch-list

**Pricing options:**

| Option | Price | Best for |
|---|---|---|
| Self-host (this MCP) | £0 — MIT | Devs |
| This MCP Starter | £29/mo | One-MCP teams |
| This MCP Pro | £79/mo | Production + 24h SLA |
| [Universal PAYG](https://buy.stripe.com/00w3cxcgAaEGcIBcyQ8k90s) | £29/mo + £0.0002/call | Spiky usage across many MCPs |
| Substrate bundle (this category) | £99-£499/mo | A whole pack |
| [MEOK Universe](https://buy.stripe.com/cNi9AV0xS8wy5g9aqI8k90u) | £1,499/mo | All 47 MCPs, 500K calls |

Each tier above the free self-host adds HMAC-signed attestations verifiable at
`verify.meok.ai`. Linux Foundation governance on the A2A spine means EU regulated
buyers can deploy without vendor-lock-in objections.

<!-- mcp-name: io.github.CSOAI-ORG/agent-rate-limiter-mcp -->
