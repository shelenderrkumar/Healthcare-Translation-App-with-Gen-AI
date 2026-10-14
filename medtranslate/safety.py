"""Deterministic checks that catch the most dangerous translation errors.

LLM translations are fluent but can silently drop or alter a dose, a number or a negation.
These checks don't need a model: they compare the numbers in the source and the translation
(after normalising Arabic-Indic, Devanagari and other native digits) and surface any mismatch
for the clinician to confirm.
"""

import re
import unicodedata
from dataclasses import dataclass

_NUMBER = re.compile(r"\d+(?:[.,]\d+)?")


def normalize_digits(text: str) -> str:
    """Map every Unicode decimal digit (e.g. '٥', '५', '۵') to ASCII."""
    return "".join(
        str(unicodedata.digit(ch)) if ch.isdigit() and not ch.isascii() else ch for ch in text
    )


def extract_numbers(text: str) -> list[str]:
    """Numbers in reading order, with ',' decimal separators and thousands commas unified."""
    numbers = []
    for raw in _NUMBER.findall(normalize_digits(text)):
        # "1,000" (thousands) -> "1000"; "2,5" (decimal) -> "2.5"
        if re.fullmatch(r"\d{1,3}(,\d{3})+", raw):
            raw = raw.replace(",", "")
        numbers.append(raw.replace(",", "."))
    return numbers


@dataclass
class SafetyReport:
    missing_numbers: list[str]
    extra_numbers: list[str]

    @property
    def ok(self) -> bool:
        return not (self.missing_numbers or self.extra_numbers)

    def warnings(self) -> list[str]:
        out = []
        if self.missing_numbers:
            out.append(
                "Numbers in the original that are missing from the translation: "
                + ", ".join(self.missing_numbers)
            )
        if self.extra_numbers:
            out.append(
                "Numbers in the translation that were not in the original: "
                + ", ".join(self.extra_numbers)
            )
        return out


def check_numbers(source: str, translation: str) -> SafetyReport:
    """Compare numbers as multisets: order may change between languages, counts may not."""
    remaining = extract_numbers(translation)
    missing = []
    for number in extract_numbers(source):
        if number in remaining:
            remaining.remove(number)
        else:
            missing.append(number)
    return SafetyReport(missing_numbers=missing, extra_numbers=remaining)
