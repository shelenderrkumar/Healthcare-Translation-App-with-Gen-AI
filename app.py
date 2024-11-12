import os
import streamlit as st 
import openai
from gtts import gTTS
from io import BytesIO
from audio_recorder_streamlit import audio_recorder

# Simple page config
st.set_page_config(
    page_title='Real Time Translation',
    page_icon='🌎',
    layout='centered',
    initial_sidebar_state='collapsed'
)


from openai import OpenAI
if st.secrets["OPENAI_API_KEY"]:
    print("\nKey found\n")

os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
# openai.api_key = st.secrets["OPENAI_API_KEY"]
client = OpenAI()

def translate_text(text, target_lang):
    """Translate text using OpenAI"""
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                    {"role": "system", "content": f"Translate the following text to {target_lang}:"},
                    {"role": "user", "content": text}
                ]
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
        sound_file.seek(0)  # Reset file pointer to beginning
        return sound_file
    except Exception as e:
        st.error(f"Text-to-speech error: {str(e)}")
        return None

def main():
    st.title("Real Time Translation")
    st.subheader("Healthcare Communication Assistant")

    # Language selection in two columns
    col1, col2 = st.columns(2)
    with col1:
        source_lang = st.selectbox(
            "Source Language",
            ["English", "Spanish", "Hindi", "Mandarin", "Arabic", "French"],
            label_visibility="collapsed"
        )
    with col2:
        target_lang = st.selectbox(
            "Target Language",
            ["Spanish", "English", "Hindi", "Mandarin", "Arabic", "French"],
            label_visibility="collapsed"
        )

    # Language codes mapping for TTS
    lang_codes = {
        "English": "en", "Spanish": "es", "Hindi": "hi",
        "Mandarin": "zh-CN", "Arabic": "ar", "French": "fr"
    }

    # Audio input handling
    audio_input = st.experimental_audio_input("Record a voice message")
    
    if audio_input is not None:
        try:
            # Convert UploadedFile to bytes
            audio_bytes = audio_input.read()
            
            # Display original audio
            st.audio(audio_bytes, format='audio/wav')
            
            # Create a BytesIO object for Whisper API
            audio_file = BytesIO(audio_bytes)
            audio_file.name = "voice_message.wav"
            
            # Get transcription
            transcription = client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file
            )

            # transcript = openai.Audio.transcribe("whisper-1", audio_file)
            
            # Display original text
            st.write("Original Text:")
            st.write(transcription.text)
            # st.write(transcript['text'])
            
            # Translate text
            translated_text = translate_text(transcription.text, target_lang)
            
            if translated_text:
                st.write("Translation:")
                st.write(translated_text)
                
                # Generate audio for translation
                translated_audio = text_to_speech(translated_text, lang_codes[target_lang])
                
                if translated_audio:
                    st.write("Translation Audio:")
                    st.audio(translated_audio)

        except Exception as e:
            st.error(f"Processing error: {str(e)}")

    # Text to speech section
    with st.expander("Text to Speech"):
        text_input = st.text_area("Enter text:")
        if st.button("Convert to Speech"):
            if text_input:
                audio = text_to_speech(text_input, lang_codes[target_lang])
                if audio:
                    st.audio(audio)

if __name__ == '__main__':
    main()


# import io
# import openai
# from gtts import gTTS
# import streamlit as st
# from io import BytesIO
# from audio_recorder_streamlit import audio_recorder

# # Set page configuration
# st.set_page_config(
#     page_title='Real Time Translation',
#     page_icon='🌎',
#     layout='centered',
#     initial_sidebar_state='auto'
# )

# # Hide Streamlit footer
# hide_streamlit_style = """
# <style>
#     footer {visibility: hidden;}
# </style>
# """
# st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# def main():
#     st.header('Real Time Translation')
#     st.caption('Written by SK')

#     # Set OpenAI API key
#     openai.api_key = st.secrets["OPENAI_API_KEY"]

#     # Audio input
#     audio_bytes = st.experimental_audio_input("Record a voice message")
#     if audio_bytes:
#         st.audio(audio_bytes)
#         st.session_state.audio_bytes = audio_bytes

#     # Form for real-time translation
#     with st.form('input_form'):
#         submit_button = st.form_submit_button(label='Translate', type='primary')
#         if submit_button and 'audio_bytes' in st.session_state and st.session_state.audio_bytes.size > 0:
#             # Use st.session_state.audio_bytes directly since 
#             # UploadedFile is a subclass of BytesIO
#             audio_file = st.session_state.audio_bytes
#             audio_file.name = "temp_audio_file.wav"
#             audio_file.seek(0)  # Reset file pointer to the beginning
#             transcript = openai.Audio.translate("whisper-1", audio_file)
#             st.markdown("***Translation Transcript***")
#             st.text_area('transcription', transcript['text'], label_visibility='collapsed')
#             if transcript['text']:
#                 # Convert text to speech
#                 sound_file = BytesIO()
#                 tts = gTTS(transcript['text'], lang='en')
#                 tts.write_to_fp(sound_file)
#                 st.markdown("***Synthesized Speech Translation***")
#                 st.audio(sound_file)
#             else:
#                 st.warning('No text to convert to speech.')
#         else:
#             st.warning('No audio recorded, please ensure your audio was recorded correctly.')

#     # Text to speech section
#     with st.expander("Text to speech"):
#         with st.form('text_to_speech'):
#             text_to_speech = st.text_area('Enter text to convert to speech')
#             submit_button = st.form_submit_button(label='Convert')
#             if submit_button and text_to_speech:
#                 # Convert text to speech
#                 sound_file = BytesIO()
#                 tts = gTTS(text_to_speech, lang='en')
#                 tts.write_to_fp(sound_file)
#                 st.audio(sound_file)


# if __name__ == '__main__':
#     main()
