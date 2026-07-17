from __future__ import annotations

import argparse
from pathlib import Path
from urllib.parse import urlparse

import httpx

from biofigurebench.dataset import load_cases


def extension_from_url(url: str) -> str:
    path = urlparse(url).path.lower()
    for suffix in (".png", ".jpg", ".jpeg", ".webp", ".gif"):
        if path.endswith(suffix):
            return suffix
    return ".png"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="data/benchmark.jsonl")
    parser.add_argument("--output-dir", default="data/figures")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    cases = load_cases(args.dataset)

    headers = {"User-Agent": "BioFigureBench/0.1 (+research benchmark)"}
    with httpx.Client(follow_redirects=True, timeout=60, headers=headers) as client:
        for case in cases:
            url = str(case.source.image_url)
            target = output_dir / f"{case.case_id}{extension_from_url(url)}"
            try:
                response = client.get(url)
                response.raise_for_status()
                content_type = response.headers.get("content-type", "")
                if "image" not in content_type:
                    raise ValueError(f"Expected image content, received {content_type or 'unknown'}")
                target.write_bytes(response.content)
                print(f"Downloaded {case.case_id} -> {target}")
            except Exception as exc:
                print(f"Could not download {case.case_id}: {exc}")
                print(f"  Figure page: {case.source.figure_page_url}")


if __name__ == "__main__":
    main()
