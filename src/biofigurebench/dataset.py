from __future__ import annotations

import json
from pathlib import Path

from .models import BenchmarkCase, ModelResponse


def load_cases(path: str | Path) -> list[BenchmarkCase]:
    cases: list[BenchmarkCase] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                cases.append(BenchmarkCase.model_validate_json(line))
            except Exception as exc:
                raise ValueError(f"Invalid benchmark record at line {line_number}: {exc}") from exc
    ids = [case.case_id for case in cases]
    if len(ids) != len(set(ids)):
        raise ValueError("Benchmark contains duplicate case IDs")
    return cases


def load_responses(path: str | Path) -> list[ModelResponse]:
    responses: list[ModelResponse] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                responses.append(ModelResponse.model_validate_json(line))
            except Exception as exc:
                raise ValueError(f"Invalid response at line {line_number}: {exc}") from exc
    return responses


def write_jsonl(path: str | Path, records: list[dict]) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def append_jsonl(path: str | Path, record: dict) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")
