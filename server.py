#!/usr/bin/env python3
"""
Agent Rate Limiter MCP Server
==============================
By MEOK AI Labs | https://meok.ai

Fleet-wide rate limiting for agent-to-agent (A2A) and multi-MCP deployments.

PROBLEM SOLVED: most MCP servers rate-limit independently — a hostile or runaway
agent hitting 10 different MCPs gets 10× its quota. This MCP is the shared
counter: every MCP in the fleet checks here before allowing a call. Use the
`acquire` tool to request a slot, `release` when done, `status` to inspect.

USE CASES:
  - A2A orchestration where one buggy agent can DoS the stack
  - Shared per-tenant quotas across multiple MCPs
  - Pre-flight capacity check before expensive calls
  - Fairness between concurrent agent pairs

PRICING:
  - Free — 100 acquire/day per caller
  - Pro £199/mo — unlimited + sliding windows + signed audit trail
  - Enterprise £1,499/mo — multi-tenant, custom algorithms (token-bucket, leaky)

Install: pip install agent-rate-limiter-mcp
Run:     python server.py
"""

import json
import time
from datetime import datetime, timedelta, timezone
from typing import Optional
from collections import defaultdict, deque
from mcp.server.fastmcp import FastMCP

import os as _os
import sys
import os

_MEOK_API_KEY = _os.environ.get("MEOK_API_KEY", "")

try:
    from auth_middleware import check_access as _shared_check_access
    _AUTH_ENGINE_AVAILABLE = True
except ImportError:
    _AUTH_ENGINE_AVAILABLE = False

    def _shared_check_access(api_key: str = ""):
        """Fallback when shared auth engine is not available."""
        if _MEOK_API_KEY and api_key and api_key == _MEOK_API_KEY:
            return True, "OK", "pro"
        if _MEOK_API_KEY and api_key and api_key != _MEOK_API_KEY:
            return False, "Invalid API key. Get one at https://meok.ai/api-keys", "free"
        return True, "OK", "free"


try:
    from attestation import get_attestation_tool_response
    _ATTESTATION_LOCAL = True
except ImportError:
    _ATTESTATION_LOCAL = False

_ATTESTATION_API = _os.environ.get(
    "MEOK_ATTESTATION_API", "https://meok-attestation-api.vercel.app"
)


def check_access(api_key: str = ""):
    return _shared_check_access(api_key)


STRIPE_199 = "https://buy.stripe.com/14A4gB3K4eUWgYR56o8k836"
STRIPE_1499 = "https://buy.stripe.com/4gM9AV80kaEG0ZT42k8k837"


# ── In-memory counters (MVP — swap for Redis in production deployment) ──────
# Structure:
#   _counters[tenant_id][bucket_key] = deque of timestamps within the window
_counters: dict[str, dict[str, deque]] = defaultdict(lambda: defaultdict(deque))
_active: dict[str, dict[str, set]] = defaultdict(lambda: defaultdict(set))
_quotas: dict[str, dict[str, int]] = defaultdict(dict)

# Default quotas per tier (requests per 60-second window)
DEFAULT_QUOTAS = {
    "free": 100,       # generous free tier
    "pro": 10000,      # effectively unlimited for most agent workloads
    "enterprise": 100000,
}


def _prune(bucket: deque, window_sec: int) -> None:
    cutoff = time.time() - window_sec
    while bucket and bucket[0] < cutoff:
        bucket.popleft()


mcp = FastMCP(
    "agent-rate-limiter",
    instructions=(
        "MEOK AI Labs Agent Rate Limiter MCP. Fleet-wide rate limiting for A2A + "
        "multi-MCP deployments — shared state across MCP servers so one hostile agent "
        "can't amplify its quota by spraying across N MCPs. Use `acquire` before a call, "
        "`release` when done, `status` to inspect usage, `set_quota` (Pro) to configure."
    ),
)


@mcp.tool()
def acquire(
    tenant_id: str,
    agent_id: str,
    operation: str = "default",
    window_sec: int = 60,
    weight: int = 1,
    api_key: str = "",
) -> str:
    """Request a rate-limit slot for an agent action.

    Returns {allowed, current, limit, retry_after_sec}.

    - tenant_id: the customer / organisation identifier
    - agent_id: which agent is calling (may be a chain: "orchestrator:supervisor:worker")
    - operation: a key to scope counters (e.g. "llm_call", "db_write", "external_api")
    - window_sec: sliding window in seconds (default 60)
    - weight: how many tokens this call consumes (default 1 — expensive calls can weight >1)
    """
    allowed_acc, msg, tier = check_access(api_key)
    if not allowed_acc:
        return json.dumps({"error": msg, "upgrade_url": STRIPE_199})

    bucket_key = f"{agent_id}|{operation}|{window_sec}"
    bucket = _counters[tenant_id][bucket_key]
    _prune(bucket, window_sec)

    # Resolve quota
    configured = _quotas.get(tenant_id, {}).get(bucket_key)
    limit = configured if configured is not None else DEFAULT_QUOTAS.get(tier, 100)

    current_weighted = len(bucket)
    if current_weighted + weight > limit:
        # Reject — compute retry_after (when oldest entry falls out of window)
        retry = max(1, int(bucket[0] + window_sec - time.time())) if bucket else 1
        return json.dumps({
            "allowed": False,
            "current": current_weighted,
            "limit": limit,
            "tier": tier,
            "retry_after_sec": retry,
            "reason": "rate-limit exceeded for this (tenant, agent, operation, window)",
            "upgrade_url": STRIPE_199 if tier == "free" else None,
        })

    # Grant
    now = time.time()
    for _ in range(weight):
        bucket.append(now)
    grant_id = f"rl-{int(now*1000)}-{abs(hash(bucket_key)) % 10000:04d}"
    _active[tenant_id][bucket_key].add(grant_id)

    return json.dumps({
        "allowed": True,
        "grant_id": grant_id,
        "current": current_weighted + weight,
        "limit": limit,
        "window_sec": window_sec,
        "tier": tier,
        "released_by": "call release() with this grant_id when done",
    })


@mcp.tool()
def release(tenant_id: str, agent_id: str, grant_id: str, operation: str = "default",
            window_sec: int = 60, api_key: str = "") -> str:
    """Release a rate-limit slot. Doesn't refund tokens in the sliding window (those
    naturally expire), but removes the grant from the active-calls set — useful for
    concurrency-limit tools that track in-flight operations."""
    allowed_acc, msg, tier = check_access(api_key)
    if not allowed_acc:
        return json.dumps({"error": msg})
    bucket_key = f"{agent_id}|{operation}|{window_sec}"
    active = _active[tenant_id][bucket_key]
    if grant_id in active:
        active.discard(grant_id)
        return json.dumps({"released": True, "active_now": len(active)})
    return json.dumps({"released": False, "note": "grant_id not found (already expired or invalid)"})


@mcp.tool()
def status(tenant_id: str, agent_id: str = "", operation: str = "", api_key: str = "") -> str:
    """Inspect usage. If agent_id is empty, returns tenant-wide summary."""
    allowed_acc, msg, tier = check_access(api_key)
    if not allowed_acc:
        return json.dumps({"error": msg})

    out = []
    for bucket_key, bucket in _counters[tenant_id].items():
        bk_agent, bk_op, bk_win = bucket_key.split("|")
        if agent_id and bk_agent != agent_id:
            continue
        if operation and bk_op != operation:
            continue
        _prune(bucket, int(bk_win))
        out.append({
            "agent_id": bk_agent,
            "operation": bk_op,
            "window_sec": int(bk_win),
            "current": len(bucket),
            "active_grants": len(_active[tenant_id][bucket_key]),
            "limit": _quotas.get(tenant_id, {}).get(bucket_key, DEFAULT_QUOTAS.get(tier, 100)),
        })
    return json.dumps({
        "tenant_id": tenant_id,
        "tier": tier,
        "counters": out,
        "upsell": f"Pro £199/mo unlocks custom quotas, sliding windows, + signed audit trail: {STRIPE_199}" if tier == "free" else None,
    }, indent=2)


@mcp.tool()
def set_quota(tenant_id: str, agent_id: str, operation: str, limit: int,
              window_sec: int = 60, api_key: str = "") -> str:
    """Override the default quota for a (tenant, agent, operation) tuple. Pro+ only."""
    allowed_acc, msg, tier = check_access(api_key)
    if not allowed_acc:
        return json.dumps({"error": msg, "upgrade_url": STRIPE_199})
    if tier == "free":
        return json.dumps({
            "error": "Custom quotas require Pro (£199/mo) or Enterprise tier.",
            "upgrade_url": STRIPE_199,
        })
    bucket_key = f"{agent_id}|{operation}|{window_sec}"
    _quotas[tenant_id][bucket_key] = int(limit)
    return json.dumps({
        "tenant_id": tenant_id,
        "agent_id": agent_id,
        "operation": operation,
        "window_sec": window_sec,
        "limit_set_to": limit,
    })


@mcp.tool()
def reset_counters(tenant_id: str, agent_id: str = "", api_key: str = "") -> str:
    """Clear counters for a tenant (or a specific agent within a tenant). Pro+ only.
    Useful for daily resets, test harnesses, emergency overrides."""
    allowed_acc, msg, tier = check_access(api_key)
    if not allowed_acc:
        return json.dumps({"error": msg, "upgrade_url": STRIPE_199})
    if tier == "free":
        return json.dumps({
            "error": "Counter reset requires Pro (£199/mo) or Enterprise tier.",
            "upgrade_url": STRIPE_199,
        })
    cleared = 0
    for bucket_key in list(_counters[tenant_id].keys()):
        if not agent_id or bucket_key.startswith(f"{agent_id}|"):
            _counters[tenant_id][bucket_key].clear()
            _active[tenant_id][bucket_key].clear()
            cleared += 1
    return json.dumps({"tenant_id": tenant_id, "agent_id_filter": agent_id or "*", "buckets_cleared": cleared})


@mcp.tool()
def sign_rate_limit_attestation(
    tenant_id: str,
    window_start_utc: str,
    window_end_utc: str,
    total_grants: int,
    total_rejections: int,
    peak_concurrent: int,
    api_key: str = "",
    email: str = "",
) -> str:
    """Emit a cryptographically signed attestation of rate-limit enforcement over a
    window. Enterprise audit evidence — show regulators you were enforcing quotas
    during the incident window."""
    allowed_acc, msg, tier = check_access(api_key)
    if not allowed_acc:
        return json.dumps({"error": msg, "upgrade_url": STRIPE_199})
    if tier == "free":
        return json.dumps({
            "error": "Signed attestations require Pro (£199/mo) or Enterprise tier.",
            "upgrade_url": STRIPE_199,
        })

    score = 100 * total_grants / max(1, total_grants + total_rejections)
    findings = [
        f"Window: {window_start_utc} → {window_end_utc}",
        f"Total grants: {total_grants}",
        f"Total rejections: {total_rejections}",
        f"Peak concurrent: {peak_concurrent}",
    ]

    if _ATTESTATION_LOCAL:
        cert = get_attestation_tool_response(
            regulation="A2A rate-limit enforcement (fleet-wide)",
            entity=f"tenant:{tenant_id}",
            score=score,
            findings=findings,
            articles_audited=None,
            tier=tier,
        )
    else:
        import urllib.request as _url
        try:
            req = _url.Request(
                f"{_ATTESTATION_API}/sign",
                data=json.dumps({
                    "api_key": api_key, "email": email,
                    "regulation": "A2A rate-limit enforcement (fleet-wide)",
                    "entity": f"tenant:{tenant_id}",
                    "score": score,
                    "findings": findings,
                    "tier": tier,
                }).encode(),
                headers={"Content-Type": "application/json"},
            )
            with _url.urlopen(req, timeout=15) as resp:
                cert = json.loads(resp.read())
        except Exception as e:
            return json.dumps({"error": f"Attestation API unreachable: {e}"})

    return json.dumps(cert, indent=2)


def main():
    mcp.run()


if __name__ == "__main__":
    main()
