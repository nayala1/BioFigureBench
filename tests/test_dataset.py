from pathlib import Path

from biofigurebench.dataset import load_cases


def test_dataset_loads_all_final_cases() -> None:
    path = Path(__file__).parents[1] / "data" / "benchmark.jsonl"
    cases = load_cases(path)
    assert len(cases) == 5
    assert [case.case_id for case in cases] == [
        "BFB-001",
        "BFB-002",
        "BFB-003",
        "BFB-004",
        "BFB-005",
    ]
    assert all(case.scoring.field_concepts for case in cases)
    assert all("observations" in case.scoring.field_concepts for case in cases)


def test_bfb002_covers_all_panel_groups() -> None:
    path = Path(__file__).parents[1] / "data" / "benchmark.jsonl"
    case = {case.case_id: case for case in load_cases(path)}["BFB-002"]
    assert "Panels A-C" in case.legend_excerpt
    assert "Panels D-E" in case.legend_excerpt
    assert "Panels F-G" in case.legend_excerpt
    assert "DA/DB" in case.legend_excerpt
