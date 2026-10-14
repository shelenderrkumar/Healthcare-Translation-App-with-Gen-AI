from dataclasses import dataclass


@dataclass(frozen=True)
class Language:
    name: str
    whisper: str  # ISO-639-1 code passed to Whisper as a transcription hint
    tts: str  # gTTS language code


LANGUAGES: dict[str, Language] = {
    lang.name: lang
    for lang in [
        Language("English", "en", "en"),
        Language("Spanish", "es", "es"),
        Language("Urdu", "ur", "ur"),
        Language("Hindi", "hi", "hi"),
        Language("Arabic", "ar", "ar"),
        Language("Mandarin Chinese", "zh", "zh-CN"),
        Language("French", "fr", "fr"),
        Language("Portuguese", "pt", "pt"),
        Language("Bengali", "bn", "bn"),
        Language("Vietnamese", "vi", "vi"),
    ]
}


def get_language(name: str) -> Language:
    try:
        return LANGUAGES[name]
    except KeyError:
        raise ValueError(f"Unsupported language: {name}") from None
