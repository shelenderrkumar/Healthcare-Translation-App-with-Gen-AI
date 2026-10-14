"""Streamlit UI: a two-way, spoken conversation between a clinician and a patient."""

import os

import streamlit as st

from medtranslate.languages import LANGUAGES, get_language
from medtranslate.pipeline import TranslationPipeline, audio_fingerprint

st.set_page_config(page_title="Medical Interpreter", page_icon="🩺", layout="wide")

ROLES = {"clinician": ("🩺", "Clinician"), "patient": ("🧑", "Patient")}


def api_key() -> str | None:
    try:
        return st.secrets["OPENAI_API_KEY"]
    except (KeyError, FileNotFoundError, st.errors.StreamlitSecretNotFoundError):
        return os.getenv("OPENAI_API_KEY")


@st.cache_resource
def get_pipeline(key: str) -> TranslationPipeline:
    from openai import OpenAI

    return TranslationPipeline(
        OpenAI(api_key=key), chat_model=os.getenv("CHAT_MODEL", "gpt-4o-mini")
    )


def process(pipeline, role, other, text=None, audio=None):
    speaker, listener = st.session_state.lang[role], st.session_state.lang[other]
    with st.spinner("Translating..."):
        if audio is not None:
            text = pipeline.transcribe(audio, speaker)
        if not text:
            st.toast("No speech detected. Please try again.")
            return
        result = pipeline.run(text, speaker, listener, back_translate=st.session_state.verify)
        speech = pipeline.speak(result.translation, listener) if st.session_state.speak else None
    st.session_state.history.append({"role": role, "result": result, "speech": speech})


def render_turn(turn):
    icon, label = ROLES[turn["role"]]
    result = turn["result"]
    with st.chat_message(turn["role"], avatar=icon):
        st.caption(f"{label} · {result.source.name} → {result.target.name}")
        st.markdown(f"**{result.translation}**")
        st.markdown(f":gray[{result.source_text}]")
        for warning in result.warnings:
            st.warning(warning, icon="⚠️")
        if result.back_translation:
            with st.expander(f"Round-trip check (back into {result.source.name})"):
                st.write(result.back_translation)
        if turn["speech"]:
            st.audio(turn["speech"], format="audio/mp3")


def speaker_panel(pipeline, role, other):
    icon, label = ROLES[role]
    st.subheader(f"{icon} {label} speaks {st.session_state.lang[role].name}")
    audio = st.audio_input(f"Record the {label.lower()}", key=f"audio_{role}")
    if audio is not None:
        data = audio.getvalue()
        fingerprint = audio_fingerprint(data)
        if fingerprint not in st.session_state.processed:  # never re-bill on UI re-runs
            st.session_state.processed.add(fingerprint)
            process(pipeline, role, other, audio=data)
    with st.form(f"text_{role}", clear_on_submit=True, border=False):
        typed = st.text_input("…or type", key=f"typed_{role}", placeholder="Type instead")
        if st.form_submit_button("Translate") and typed.strip():
            process(pipeline, role, other, text=typed.strip())


def main():
    st.session_state.setdefault("history", [])
    st.session_state.setdefault("processed", set())

    with st.sidebar:
        st.header("Settings")
        names = list(LANGUAGES)
        clinician = st.selectbox("Clinician language", names, index=names.index("English"))
        patient = st.selectbox("Patient language", names, index=names.index("Spanish"))
        st.session_state.lang = {
            "clinician": get_language(clinician),
            "patient": get_language(patient),
        }
        st.session_state.verify = st.toggle("Round-trip check", value=True)
        st.session_state.speak = st.toggle("Speak translations aloud", value=True)
        if st.button("Clear conversation", use_container_width=True):
            st.session_state.history.clear()
        st.caption(
            "Audio and text are sent to OpenAI for processing. Do not use with real patient "
            "data unless your organisation has an appropriate agreement in place."
        )

    st.title("🩺 Medical Interpreter")
    st.info(
        "Assistive tool, not a certified medical interpreter. Always confirm doses, "
        "allergies and consent with a qualified interpreter.",
        icon="ℹ️",
    )

    key = api_key()
    if not key:
        st.error("Set `OPENAI_API_KEY` in `.streamlit/secrets.toml` or the environment.")
        st.stop()
    pipeline = get_pipeline(key)

    left, right = st.columns(2)
    with left:
        speaker_panel(pipeline, "clinician", "patient")
    with right:
        speaker_panel(pipeline, "patient", "clinician")

    st.divider()
    st.subheader("Conversation")
    if not st.session_state.history:
        st.caption("Translations will appear here.")
    for turn in reversed(st.session_state.history):
        render_turn(turn)


main()
