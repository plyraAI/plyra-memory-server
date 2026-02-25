# LLM Extraction with Groq

The server uses Groq for background fact extraction when `GROQ_API_KEY` is set.

## Why Groq?

- Free tier: 14,400 requests/day on `llama-3.1-8b-instant`
- Fast: ~800 tokens/second — extraction completes in <200ms
- OpenAI-compatible API — no special client needed

## Setup

```bash
# Get key at console.groq.com (no card required)
# Set as Azure secret:
az containerapp secret set \
  --name plyra-memory-server \
  --resource-group plyra-rg \
  --secrets groq-key="gsk_..."

az containerapp update \
  --name plyra-memory-server \
  --resource-group plyra-rg \
  --set-env-vars GROQ_API_KEY=secretref:groq-key
```

## Verify it's working

```bash
# Check server logs for startup message
az containerapp logs show \
  --name plyra-memory-server \
  --resource-group plyra-rg \
  --tail 30 | grep -i "groq\|extraction"
# Should show: "LLM extraction: Groq llama-3.1-8b-instant"

# Check stats after remember() — semantic count should increase
curl -H "Authorization: Bearer $YOUR_KEY" \
  $SERVER_URL/v1/stats
# {"working": 1, "episodic": 0, "semantic": 1}
#                                          ↑ Groq extracted a fact
```

## Fallback behaviour

If `GROQ_API_KEY` is not set, the server falls back to `RegexExtractor`.
Regex catches ~60% of explicit facts ("my name is X", "I prefer Y").
LLM extraction catches implicit facts and context.

Priority order: `GROQ_API_KEY` → `ANTHROPIC_API_KEY` → `OPENAI_API_KEY` → regex

## Alternative providers

For Anthropic:
```bash
# .env
ANTHROPIC_API_KEY=sk-ant-...
```

For OpenAI:
```bash
OPENAI_API_KEY=sk-...
```

## Client vs server extraction

| | Client-side | Server-side |
|---|---|---|
| Config | `Memory.with_groq(api_key=...)` | `GROQ_API_KEY` on server |
| Applies to | that agent only | all agents on this server |
| API key | in agent environment | in server environment only |

Server-side is simpler for multi-agent setups — one API key to manage.

→ [LLM extraction docs](https://plyraai.github.io/plyra-memory/extraction/llm/)

---

← [API key lifecycle](api-keys.md) · [Production checklist →](production.md)
