# Codex instructions

Work within this repository and use `.venv/bin/...` executables because Codex may run with a restricted PATH.

Security:
- Never print, log, hash, or write `ANTHROPIC_API_KEY`.
- Use the environment variable only.
- Request network approval only for figure retrieval and Anthropic API calls.

Final MVP scope:
- Preserve exactly five benchmark cases unless explicitly instructed otherwise.
- Prefer small, tested fixes over new architecture.
- The canonical end-to-end command is:

```bash
.venv/bin/biofigurebench pipeline --dataset data/benchmark.jsonl --model claude-sonnet-5 --output-dir results/claude-sonnet-5-final
```

Before a paid run:
1. Run `.venv/bin/pytest`.
2. Run `.venv/bin/biofigurebench validate --dataset data/benchmark.jsonl`.
3. Confirm the API key exists using a boolean/prefix/length check only.
4. Confirm `client.models.list()` succeeds.

After a run:
- Confirm BFB-001 through BFB-005 are present in `responses.jsonl`.
- Open `report.html` and inspect missing concepts and triggered contradictions.
