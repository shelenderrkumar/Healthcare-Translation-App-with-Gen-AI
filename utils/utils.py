import streamlit as st
import openai
from gtts import gTTS
from io import BytesIO


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
