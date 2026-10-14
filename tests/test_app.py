"""Headless UI tests with Streamlit's AppTest; model calls are stubbed out."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from medtranslate.pipeline import GTTSSynthesizer, TranslationPipeline

APP = str(Path(__file__).resolve().parent.parent / "app.py")


def test_missing_key_shows_setup_message(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    at = AppTest.from_file(APP).run()
    assert not at.exception
    assert "OPENAI_API_KEY" in at.error[0].value


@pytest.fixture
def stubbed(monkeypatch):
    calls = []

    def fake_translate(self, text, source, target):
        calls.append((text, source.name, target.name))
        return {"Spanish": "Tome 500 mg.", "English": "Take 500 mg."}[target.name]

    monkeypatch.setattr(TranslationPipeline, "translate", fake_translate)
    monkeypatch.setattr(GTTSSynthesizer, "synthesize", lambda self, text, lang: b"mp3")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    return calls


def test_typed_message_is_translated_and_round_tripped(stubbed):
    at = AppTest.from_file(APP).run()
    at.text_input(key="typed_clinician").input("Take 500 mg.")
    at.button[0].click().run()  # first form submit button: clinician panel
    assert not at.exception
    assert stubbed == [
        ("Take 500 mg.", "English", "Spanish"),
        ("Tome 500 mg.", "Spanish", "English"),  # round-trip check
    ]
    assert len(at.session_state.history) == 1
    turn = at.session_state.history[0]
    assert turn["result"].translation == "Tome 500 mg." and turn["speech"] == b"mp3"
    assert len(at.warning) == 0  # numbers preserved, no safety warning
