---
hide:
  - toc
---

<div class="plyra-hero">
  <h1>plyra-memory-server</h1>
  <p class="tagline">Self-hosted memory infrastructure for agentic AI.<br>
  Multi-tenant. API key auth. Workspace isolation.</p>
</div>

<div class="plyra-grid">
  <div class="plyra-card">
    <h3>Three commands</h3>
    <p>Clone, configure, docker compose up. Server running on :7700.</p>
  </div>
  <div class="plyra-card">
    <h3>API key auth</h3>
    <p>plm_live_... keys. SHA-256 hashed. Create and revoke via admin API.</p>
  </div>
  <div class="plyra-card">
    <h3>Workspace isolation</h3>
    <p>workspace → user → agent. No cross-tenant memory access.</p>
  </div>
  <div class="plyra-card">
    <h3>Zero client changes</h3>
    <p>Set two env vars. plyra-memory routes to server automatically.</p>
  </div>
</div>

## What this is

plyra-memory-server is the server component of the plyra-memory stack.

```
Agent A (LangGraph)   ─┐
Agent B (AutoGen)     ──┤── plyra-memory-server ── persistent storage
Agent C (plain Python) ─┘         ↑
                             plm_live_abc123
                           Authorization: Bearer
```

The library ([plyra-memory](https://plyraai.github.io/plyra-memory)) handles
local mode. The server handles multi-agent, multi-tenant production.

## When to use this

Use plyra-memory-server when:

- More than one agent process needs to share memory
- Memory must survive container restarts and deployments
- You need per-workspace isolation between different teams or customers
- You want a single memory endpoint across multiple machines

For single-agent development, use
[plyra-memory locally](https://plyraai.github.io/plyra-memory) — zero setup.

## Start here

<div class="plyra-grid">
  <div class="plyra-card">
    <h3><a href="quickstart/">Quickstart</a></h3>
    <p>Server running in 3 commands.</p>
  </div>
  <div class="plyra-card">
    <h3><a href="deploy/azure/">Azure</a></h3>
    <p>Production deploy on Azure Container Apps.</p>
  </div>
  <div class="plyra-card">
    <h3><a href="api/">API reference</a></h3>
    <p>All routes, request/response schemas.</p>
  </div>
  <div class="plyra-card">
    <h3><a href="guides/isolation/">Isolation model</a></h3>
    <p>How workspace → user → agent works.</p>
  </div>
</div>

---

Part of the [Plyra](https://plyraai.github.io) open-source stack.  
Also see [plyra-memory](https://plyraai.github.io/plyra-memory) (library) and
[plyra-guard](https://plyraai.github.io/plyra-guard) (action middleware).
