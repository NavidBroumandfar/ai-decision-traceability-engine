# Configuration

Configuration is loaded from environment variables and optional `.env` files via
Pydantic Settings.

## Core Variables

| Variable | Default | Purpose |
| --- | --- | --- |
| `ENV` | `local` | `local` or `prod`. |
| `LLM_PROVIDER` | `ollama` | `openai`, `ollama`, or `lmstudio`. |
| `LLM_MODEL` | unset | Preferred model variable for local providers. |
| `LLM_BASE_URL` | provider default | Preferred base URL for local providers. |
| `OPENAI_API_KEY` | unset | Required when `LLM_PROVIDER=openai`. |
| `OPENAI_MODEL` | unset | Required when `LLM_PROVIDER=openai`. |
| `OPENAI_BASE_URL` | OpenAI default | Optional OpenAI-compatible base URL. |
| `POLICY_PATH` | `config/reference_policy.md` | Policy text file used by the policy agent. |
| `MAX_REQUEST_SIZE` | `1048576` | FastAPI request body limit in bytes. |
| `LOG_LEVEL` | `INFO` | Python logging level. |

For `ollama` and `lmstudio`, the code prefers `LLM_MODEL` and `LLM_BASE_URL`.
For backward compatibility, it falls back to `OPENAI_MODEL` and
`OPENAI_BASE_URL` when the `LLM_*` values are missing.

## Examples

Ollama:

```env
ENV=local
LLM_PROVIDER=ollama
LLM_MODEL=llama3.2
LLM_BASE_URL=http://localhost:11434/v1
POLICY_PATH=config/reference_policy.md
```

LM Studio:

```env
ENV=local
LLM_PROVIDER=lmstudio
LLM_MODEL=<local-model-name>
LLM_BASE_URL=http://localhost:1234/v1
POLICY_PATH=config/reference_policy.md
```

OpenAI:

```env
ENV=local
LLM_PROVIDER=openai
OPENAI_API_KEY=<OPENAI_API_KEY>
OPENAI_MODEL=gpt-4o-mini
OPENAI_BASE_URL=
POLICY_PATH=config/reference_policy.md
```

## Startup Validation

In `ENV=prod`, required provider fields fail fast on startup:

- OpenAI requires `OPENAI_API_KEY` and `OPENAI_MODEL`.
- Local providers require `LLM_MODEL` and `LLM_BASE_URL`.

In `ENV=local`, missing values are surfaced when the relevant runtime path is
used.

## Policy File

`POLICY_PATH` must point to a non-empty text file. The default sample policy is
public-safe and intentionally generic. Policy versions are not persisted with
decision results.

## Security Notes

- Never commit `.env`.
- Never submit secrets or private payloads to the API/UI; traces store full
  payloads.
- Generated decision, trace, and SQLite artifacts are ignored by git.
- This reference implementation has no authentication, authorization, redaction,
  or encryption at rest.
