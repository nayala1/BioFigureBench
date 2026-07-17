from __future__ import annotations

import base64
import time

import anthropic
import httpx

from ..models import BenchmarkCase, ModelAnswer, ModelResponse
from ..prompts import SYSTEM_PROMPT, render_prompt
from .base import ModelAdapter


SUPPORTED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}


def _detect_image_type(data: bytes, content_type: str | None) -> str:
    normalized = (content_type or "").split(";", 1)[0].strip().lower()
    if normalized in SUPPORTED_IMAGE_TYPES:
        return normalized
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if data.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if data.startswith((b"GIF87a", b"GIF89a")):
        return "image/gif"
    if data.startswith(b"RIFF") and data[8:12] == b"WEBP":
        return "image/webp"
    raise ValueError(
        "Figure URL did not return a supported image. "
        f"Received Content-Type: {content_type!r}."
    )


def _download_image(url: str) -> tuple[str, str]:
    response = httpx.get(url, follow_redirects=True, timeout=30.0)
    response.raise_for_status()
    media_type = _detect_image_type(response.content, response.headers.get("content-type"))
    encoded = base64.b64encode(response.content).decode("ascii")
    return media_type, encoded


class AnthropicAdapter(ModelAdapter):
    def __init__(self, model: str = "claude-sonnet-5", max_tokens: int = 1800) -> None:
        self.model = model
        self.max_tokens = max_tokens
        self.client = anthropic.Anthropic()

    def run_case(self, case: BenchmarkCase) -> ModelResponse:
        started = time.perf_counter()
        media_type, image_data = _download_image(str(case.source.image_url))

        try:
            message = self.client.messages.parse(
                model=self.model,
                max_tokens=self.max_tokens,
                system=SYSTEM_PROMPT,
                output_format=ModelAnswer,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": image_data,
                                },
                            },
                            {"type": "text", "text": render_prompt(case)},
                        ],
                    }
                ],
            )
        except anthropic.BadRequestError as exc:
            detail = getattr(exc, "body", None)
            raise RuntimeError(
                f"Anthropic rejected the benchmark request: {detail or str(exc)}"
            ) from exc

        answer = message.parsed_output
        if answer is None:
            raise RuntimeError(
                f"Claude returned no parsed output (stop_reason={message.stop_reason!r})."
            )

        text = "".join(
            block.text for block in message.content if block.type == "text"
        ).strip()
        return ModelResponse(
            case_id=case.case_id,
            model=self.model,
            answer=answer,
            raw_text=text,
            latency_seconds=round(time.perf_counter() - started, 3),
        )
