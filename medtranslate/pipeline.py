"""Speech -> text -> translation -> verification -> speech."""

import hashlib
import logging
from dataclasses import dataclass, field
from io import BytesIO
from typing import Protocol

from medtranslate.languages import Language
from medtranslate.prompts import TRANSLATE
from medtranslate.safety import SafetyReport, check_numbers

logger = logging.getLogger(__name__)


class SpeechSynthesizer(Protocol):
    def synthesize(self, text: str, language: Language) -> bytes: ...


class GTTSSynthesizer:
    def synthesize(self, text: str, language: Language) -> bytes:
        from gtts import gTTS

        buffer = BytesIO()
        gTTS(text=text, lang=language.tts).write_to_fp(buffer)
        return buffer.getvalue()


@dataclass
class TranslationResult:
    source_text: str
    translation: str
    back_translation: str | None
    safety: SafetyReport
    source: Language
    target: Language
    warnings: list[str] = field(default_factory=list)


class TranslationPipeline:
    """Wraps an OpenAI-compatible client; every step is individually testable."""

    def __init__(
        self,
        client,
        chat_model: str = "gpt-4o-mini",
        stt_model: str = "whisper-1",
        synthesizer: SpeechSynthesizer | None = None,
    ):
        self.client = client
        self.chat_model = chat_model
        self.stt_model = stt_model
        self.synthesizer = synthesizer or GTTSSynthesizer()

    def transcribe(self, audio: bytes, language: Language, filename: str = "speech.wav") -> str:
        file = BytesIO(audio)
        file.name = filename
        # The language hint improves accuracy and stops Whisper from guessing wrongly on
        # short clips (e.g. Urdu transcribed as Hindi script).
        result = self.client.audio.transcriptions.create(
            model=self.stt_model, file=file, language=language.whisper
        )
        return result.text.strip()

    def translate(self, text: str, source: Language, target: Language) -> str:
        if source == target:
            return text
        completion = self.client.chat.completions.create(
            model=self.chat_model,
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": TRANSLATE.format(source=source.name, target=target.name),
                },
                {"role": "user", "content": f"<source>\n{text}\n</source>"},
            ],
        )
        return completion.choices[0].message.content.strip()

    def run(
        self, text: str, source: Language, target: Language, back_translate: bool = True
    ) -> TranslationResult:
        translation = self.translate(text, source, target)
        back = None
        if back_translate and source != target:
            # Round-trip check: the clinician reads, in their own language, what the
            # patient will actually hear.
            back = self.translate(translation, target, source)
        safety = check_numbers(text, translation)
        return TranslationResult(
            source_text=text,
            translation=translation,
            back_translation=back,
            safety=safety,
            source=source,
            target=target,
            warnings=safety.warnings(),
        )

    def speak(self, text: str, language: Language) -> bytes | None:
        try:
            return self.synthesizer.synthesize(text, language)
        except Exception:
            logger.exception("Text-to-speech failed for %s", language.name)
            return None


def audio_fingerprint(audio: bytes) -> str:
    """Stable key so a recording is processed once, not on every UI re-run."""
    return hashlib.sha256(audio).hexdigest()
