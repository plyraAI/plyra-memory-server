# Workspace Isolation

How plyra-memory-server separates memory between tenants.

## The hierarchy

```
workspace_id          ← derived from API key (server-enforced)
  └── user_id         ← passed by client (optional)
        └── agent_id  ← passed by client (optional)
```

Every API key belongs to exactly one workspace.
`workspace_id` is never passed by the client — the server derives it
from the API key. A client cannot access another workspace's memory
even if it knows the `workspace_id`.

## Storage namespacing

Internally, memory is stored under a compound key:

```
ws_{workspace_id}:u_{user_id}:a_{agent_id}
```

For example:
- `ws_acme:u_user123:a_support-agent`
- `ws_acme:u_user456:a_support-agent`   ← same agent, different user
- `ws_acme`                             ← workspace-level (no user/agent)

These are completely separate memory namespaces. No cross-contamination.

## Workspace isolation guarantee

Two clients with different API keys cannot access each other's memory,
even if they use the same `user_id` and `agent_id` values:

```python
# Key A (workspace "acme")
await memory_a.remember("acme secret data")

# Key B (workspace "other")
ctx = await memory_b.context_for("acme secret")
# → empty. Server enforces isolation.
```

This is verified by the `test_workspace_isolation` test in the test suite.

## Multi-agent within a workspace

Multiple agents in the same workspace can share memory
by omitting `agent_id` or by using a shared namespace:

```python
# Agent A and Agent B both read/write workspace-level memory
await memory.remember(content, metadata={"user_id": "user_xyz"})
# No agent_id → stored at workspace/user level, visible to all agents
```

Or give each agent its own namespace:
```python
# Agent-specific memory (not shared)
await memory.remember(content,
    metadata={"user_id": "user_xyz", "agent_id": "agent-a"})
```

→ [Multi-agent guide](https://plyraai.github.io/plyra-memory/guides/multi-agent/)

---

← [Admin keys](../api/admin.md) · [API key management →](api-keys.md)
