from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "fixtures" / "tiny_repo"


def _load_mathy() -> dict[str, object]:
    ns: dict[str, object] = {}
    exec((ROOT / "pkg" / "mathy.py").read_text(encoding="utf-8"), ns)
    return ns


def test_fixture_has_real_bug_and_passing_regression() -> None:
    ns = _load_mathy()
    add = ns["add"]
    mul = ns["mul"]
    assert add(2, 3) != 5
    assert mul(2, 3) == 6


def test_gold_patch_mentions_addition() -> None:
    patch = (ROOT / "gold.patch").read_text(encoding="utf-8")
    assert "return a + b" in patch
    assert "return a - b" in patch
