# LLM Setup

The agents use an OpenAI-compatible chat completions client. Pick one provider
in `.env`.

## Ollama

```env
ENV=local
LLM_PROVIDER=ollama
LLM_MODEL=llama3.2
LLM_BASE_URL=http://localhost:11434/v1
OPENAI_API_KEY=
POLICY_PATH=config/reference_policy.md
```

Run:

```bash
ollama serve
ollama pull llama3.2
```

## LM Studio

```env
ENV=local
LLM_PROVIDER=lmstudio
LLM_MODEL=<local-model-name>
LLM_BASE_URL=http://localhost:1234/v1
OPENAI_API_KEY=
POLICY_PATH=config/reference_policy.md
```

Start the LM Studio local server before running the API or UI.

## OpenAI

```env
ENV=local
LLM_PROVIDER=openai
OPENAI_API_KEY=<OPENAI_API_KEY>
OPENAI_MODEL=gpt-4o-mini
OPENAI_BASE_URL=
POLICY_PATH=config/reference_policy.md
```

## Troubleshooting

- `LLM_MODEL is required`: set `LLM_MODEL` for `ollama`/`lmstudio`, or
  `OPENAI_MODEL` for `openai`.
- `LLM_BASE_URL is required`: set the local provider URL or rely on the provider
  default.
- Connection refused: start the local provider server.
- Model not found: pull or load the configured model.
- OpenAI authentication failure: check that `OPENAI_API_KEY` is set in the
  environment and not committed to git.
