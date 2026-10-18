"""Generate synthetic MT564 corporate action messages (cash dividends).

Scope for v0.1: CAEV//DVCA (cash dividend), message function NEWM only.
All data is fake: invented company names, randomly built ISINs and
placeholder BIC codes. The same seed always gives the same output.
"""

from __future__ import annotations

import argparse
import random
import string
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

SENDER_BIC = "TESTBEBBAXXX"  # placeholder, not a real bank
RECEIVER_BIC = "TESTDEFFXXXX"  # placeholder, not a real bank
ISIN_COUNTRY = "SE"
CURRENCIES = ("SEK", "EUR", "DKK", "NOK", "USD")
COMPANY_NAMES = (
    "Nordvik Industrier AB",
    "Solberg Energi AB",
    "Kestrel Logistik AB",
    "Aurelia Medtech AB",
    "Brightwater Foods AB",
    "Velmora Telecom AB",
    "Halvard Fastigheter AB",
    "Crestline Retail AB",
)
FIRST_EX_DATE = date(2026, 1, 1)
EX_DATE_WINDOW_DAYS = 330


@dataclass(frozen=True)
class DividendEvent:
    """One cash dividend announcement, with dates already in order."""

    reference: str
    isin: str
    company_name: str
    currency: str
    gross_rate: float
    prep_date: date
    ex_date: date
    record_date: date
    payment_date: date


def isin_check_digit(body: str) -> int:
    """Return the check digit for the first 11 characters of an ISIN.

    Letters become numbers (A=10 ... Z=35), then a Luhn mod-10 check
    runs over every digit.
    """
    expanded = "".join(str(int(char, 36)) for char in body)
    total = 0
    for position, char in enumerate(reversed(expanded)):
        digit = int(char)
        if position % 2 == 0:
            digit *= 2
            if digit > 9:
                digit -= 9
        total += digit
    return (10 - total % 10) % 10


def make_isin(rng: random.Random) -> str:
    """Build a fake 12-character ISIN with a valid check digit."""
    alphabet = string.digits + string.ascii_uppercase
    nsin = "".join(rng.choices(alphabet, k=9))
    body = ISIN_COUNTRY + nsin
    return body + str(isin_check_digit(body))


def make_event(rng: random.Random, index: int) -> DividendEvent:
    """Create one dividend event with ex-date < record date < payment date."""
    ex_date = FIRST_EX_DATE + timedelta(days=rng.randint(0, EX_DATE_WINDOW_DAYS))
    record_date = ex_date + timedelta(days=rng.randint(1, 3))
    payment_date = record_date + timedelta(days=rng.randint(5, 30))
    return DividendEvent(
        reference=f"CA{index:08d}",
        isin=make_isin(rng),
        company_name=rng.choice(COMPANY_NAMES),
        currency=rng.choice(CURRENCIES),
        gross_rate=round(rng.uniform(0.10, 5.00), 2),
        prep_date=ex_date - timedelta(days=2),
        ex_date=ex_date,
        record_date=record_date,
        payment_date=payment_date,
    )


def generate_events(count: int, seed: int) -> list[DividendEvent]:
    """Return `count` events. The same seed always returns the same list."""
    rng = random.Random(seed)
    return [make_event(rng, index) for index in range(1, count + 1)]


def _mt_date(value: date) -> str:
    """Format a date the way SWIFT expects: YYYYMMDD."""
    return value.strftime("%Y%m%d")


def _mt_rate(value: float) -> str:
    """SWIFT uses a decimal comma, so 2.5 becomes 2,50."""
    return f"{value:.2f}".replace(".", ",")


def render_mt564(event: DividendEvent, message_number: int) -> str:
    """Return the full text of one MT564 message."""
    lines = [
        f"{{1:F01{SENDER_BIC}0000000000}}{{2:I564{RECEIVER_BIC}N}}{{4:",
        ":16R:GENL",
        f":20C::SEME//MSG{message_number:05d}",
        ":23G:NEWM",
        ":22F::CAEV//DVCA",
        f":98A::PREP//{_mt_date(event.prep_date)}",
        f":20C::CORP//{event.reference}",
        ":16S:GENL",
        ":16R:USECU",
        f":35B:ISIN {event.isin}",
        event.company_name,
        ":16S:USECU",
        ":16R:CADETL",
        f":98A::EXDT//{_mt_date(event.ex_date)}",
        f":98A::RDTE//{_mt_date(event.record_date)}",
        f":98A::PAYD//{_mt_date(event.payment_date)}",
        f":92A::GRSS//{_mt_rate(event.gross_rate)}",
        ":16S:CADETL",
        ":16R:CAOPTN",
        ":13A::CAON//001",
        ":22F::CAOP//CASH",
        ":17B::DFLT//Y",
        f":11A::OPTN//{event.currency}",
        ":16S:CAOPTN",
        "-}",
    ]
    return "\n".join(lines) + "\n"


def write_messages(events: list[DividendEvent], output_dir: Path) -> list[Path]:
    """Write one .txt file per event and return the file paths."""
    output_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for number, event in enumerate(events, start=1):
        path = output_dir / f"mt564_{number:04d}.txt"
        path.write_text(render_mt564(event, number), encoding="utf-8")
        paths.append(path)
    return paths


def main(argv: list[str] | None = None) -> None:
    """Command-line entry point."""
    parser = argparse.ArgumentParser(
        description="Generate synthetic MT564 cash dividend messages."
    )
    parser.add_argument("--count", type=int, default=10, help="number of messages")
    parser.add_argument("--seed", type=int, default=42, help="random seed")
    parser.add_argument(
        "--output", type=Path, default=Path("sample_data"), help="output folder"
    )
    args = parser.parse_args(argv)
    if args.count < 1:
        parser.error("--count must be at least 1")

    events = generate_events(args.count, args.seed)
    paths = write_messages(events, args.output)
    print(f"Wrote {len(paths)} messages to {args.output}")


if __name__ == "__main__":
    main()