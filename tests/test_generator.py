"""Tests for the synthetic MT564 generator."""

import re
from datetime import datetime

import pytest

from mt564lens.generator import (
    generate_events,
    isin_check_digit,
    main,
    render_mt564,
)

MANDATORY_TAGS = (
    ":16R:GENL",
    ":20C::SEME//",
    ":23G:NEWM",
    ":22F::CAEV//DVCA",
    ":20C::CORP//",
    ":35B:ISIN ",
    ":98A::EXDT//",
    ":98A::RDTE//",
    ":98A::PAYD//",
    ":92A::GRSS//",
    ":13A::CAON//001",
    ":22F::CAOP//CASH",
)


@pytest.fixture
def messages() -> list[str]:
    events = generate_events(20, seed=1)
    return [render_mt564(event, number) for number, event in enumerate(events, 1)]


def _read_date(text: str, qualifier: str) -> datetime:
    match = re.search(rf":98A::{qualifier}//(\d{{8}})", text)
    assert match, f"missing {qualifier} date"
    return datetime.strptime(match.group(1), "%Y%m%d")


def test_generates_requested_number_of_messages(tmp_path):
    assert len(generate_events(20, seed=1)) == 20

    main(["--count", "20", "--seed", "1", "--output", str(tmp_path)])
    assert len(list(tmp_path.glob("*.txt"))) == 20


def test_mandatory_tags_present(messages):
    for text in messages:
        for tag in MANDATORY_TAGS:
            assert tag in text, f"{tag} missing"


def test_dates_are_in_order(messages):
    for text in messages:
        ex_date = _read_date(text, "EXDT")
        record_date = _read_date(text, "RDTE")
        payment_date = _read_date(text, "PAYD")
        assert ex_date < record_date < payment_date


def test_isin_check_digit_is_valid(messages):
    for text in messages:
        match = re.search(r":35B:ISIN ([A-Z0-9]{12})", text)
        assert match, "no ISIN found"
        isin = match.group(1)
        assert isin_check_digit(isin[:11]) == int(isin[11])


def test_known_isin_check_digit():
    # Textbook example from ISIN documentation, used to check the algorithm.
    assert isin_check_digit("AU0000XVGZA") == 3


def test_same_seed_gives_same_output():
    first = [render_mt564(e, n) for n, e in enumerate(generate_events(10, 7), 1)]
    second = [render_mt564(e, n) for n, e in enumerate(generate_events(10, 7), 1)]
    assert first == second


def test_different_seed_gives_different_output():
    assert generate_events(10, seed=7) != generate_events(10, seed=8)


def test_cli_output_is_reproducible(tmp_path):
    run_a = tmp_path / "a"
    run_b = tmp_path / "b"
    main(["--count", "5", "--seed", "1", "--output", str(run_a)])
    main(["--count", "5", "--seed", "1", "--output", str(run_b)])

    for file_a in sorted(run_a.glob("*.txt")):
        assert file_a.read_text(encoding="utf-8") == (run_b / file_a.name).read_text(
            encoding="utf-8"
        )