import pytest

from medtranslate.safety import check_numbers, extract_numbers, normalize_digits


def test_native_digits_are_normalised():
    assert normalize_digits("٥٠٠ ملغ") == "500 ملغ"  # Arabic-Indic
    assert normalize_digits("५०० मिलीग्राम") == "500 मिलीग्राम"  # Devanagari
    assert normalize_digits("۲ گولیاں") == "2 گولیاں"  # Extended Arabic-Indic (Urdu)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Take 500 mg twice, 2.5 ml at 8", ["500", "2.5", "8"]),
        ("1,000 units", ["1000"]),
        ("2,5 ml", ["2.5"]),  # decimal comma
        ("no numbers here", []),
    ],
)
def test_extract_numbers(text, expected):
    assert extract_numbers(text) == expected


def test_matching_numbers_pass_even_if_reordered():
    report = check_numbers("Take 2 tablets every 8 hours", "Cada 8 horas tome 2 tabletas")
    assert report.ok and report.warnings() == []


def test_dropped_dose_is_flagged():
    report = check_numbers("Take 500 mg, 3 times a day", "Tome mg, 3 veces al día")
    assert report.missing_numbers == ["500"]
    assert "500" in report.warnings()[0]


def test_changed_number_is_flagged_both_ways():
    report = check_numbers("Allergic since 2019", "Alérgico desde 2009")
    assert report.missing_numbers == ["2019"] and report.extra_numbers == ["2009"]


def test_duplicate_numbers_are_counted():
    report = check_numbers("5 mg in the morning, 5 mg at night", "5 mg por la mañana")
    assert report.missing_numbers == ["5"]


def test_urdu_translation_with_native_digits_passes():
    assert check_numbers("Take 2 tablets", "۲ گولیاں لیں").ok
