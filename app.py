import streamlit as st
import openai
from gtts import gTTS
from io import BytesIO
from audio_recorder_streamlit import audio_recorder

st.set_page_config(
    page_title="Real Time Translation",
    page_icon="🌎",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
        .main {background-color: #1f2b38; color: white;}
        .stTextArea, .stSelectbox, .stButton, .stExpander {background-color: #2d3a4b; color: white;}
        .stAudio, .stTextArea, .stSelectbox, .stButton {border-radius: 8px;}
        .stAudio {margin: 10px 0;}
        .title {font-size: 2em; font-weight: bold; text-align: center; color: #00c7ff;}
        .subtitle {font-size: 1.2em; text-align: center; color: #b8c7d8;}
    </style>
""",
    unsafe_allow_html=True,
)


from openai import OpenAI

openai.api_key = st.secrets["OPENAI_API_KEY"]
client = OpenAI()


def translate_text(text, target_lang):
    """Translate text using OpenAI"""
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": f"Translate the following text to {target_lang}:",
                },
                {"role": "user", "content": text},
            ],
        )

        return completion.choices[0].message.content

    except Exception as e:
        st.error(f"Translation error: {str(e)}")
        return None


def text_to_speech(text, lang_code):
    """Convert text to speech"""
    try:
        sound_file = BytesIO()
        tts = gTTS(text=text, lang=lang_code)
        tts.write_to_fp(sound_file)
        sound_file.seek(0)
        return sound_file
    except Exception as e:
        st.error(f"Text-to-speech error: {str(e)}")
        return None


def main():
    st.markdown(
        '<div class="title">Real Time Translation</div>', unsafe_allow_html=True
    )
    st.markdown(
        '<div class="subtitle">Healthcare Communication Assistant</div>',
        unsafe_allow_html=True,
    )
    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        source_lang = st.selectbox(
            "Source Language",
            ["English", "Spanish", "Hindi", "Mandarin", "Arabic", "French"],
            label_visibility="collapsed",
        )
    with col2:
        target_lang = st.selectbox(
            "Target Language",
            ["Spanish", "English", "Hindi", "Mandarin", "Arabic", "French"],
            label_visibility="collapsed",
        )

    lang_codes = {
        "English": "en",
        "Spanish": "es",
        "Hindi": "hi",
        "Mandarin": "zh-CN",
        "Arabic": "ar",
        "French": "fr",
    }

    st.divider()

    st.subheader("Record a Voice Message")
    audio_input = st.experimental_audio_input("")

    if audio_input:
        audio_bytes = audio_input.read()
        st.audio(audio_bytes, format="audio/wav")

        audio_file = BytesIO(audio_bytes)
        audio_file.name = "voice_message.wav"

        try:
            transcription = client.audio.transcriptions.create(
                model="whisper-1", file=audio_file
            )

            st.text_area(" Original Text:", transcription.text, height=100)

            translated_text = translate_text(transcription.text, target_lang)
            if translated_text:
                st.text_area(" Translation:", translated_text, height=100)
                translated_audio = text_to_speech(
                    translated_text, lang_codes[target_lang]
                )
                if translated_audio:
                    st.subheader("Translation Audio")
                    st.audio(translated_audio)

        except Exception as e:
            st.error(f"Processing error: {str(e)}")

    with st.expander("Text to Speech"):
        text_input = st.text_area("Enter text:")
        if st.button("Convert to Speech"):
            if text_input:
                audio = text_to_speech(text_input, lang_codes[target_lang])
                if audio:
                    st.audio(audio)


if __name__ == "__main__":
    main()
