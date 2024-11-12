import streamlit as st
import openai
from gtts import gTTS
from io import BytesIO
from audio_recorder_streamlit import audio_recorder

# Set page config
st.set_page_config(
    page_title='Real Time Translation',
    page_icon='🌎',
    layout='centered',
    initial_sidebar_state='collapsed'
)

# Apply custom CSS for a cleaner look
st.markdown("""
    <style>
        .main {background-color: #1f2b38; color: white;}
        .stTextArea, .stSelectbox, .stButton, .stExpander {background-color: #2d3a4b; color: white;}
        .stAudio, .stTextArea, .stSelectbox, .stButton {border-radius: 8px;}
        .stAudio {margin: 10px 0;}
        .title {font-size: 2em; font-weight: bold; text-align: center; color: #00c7ff;}
        .subtitle {font-size: 1.2em; text-align: center; color: #b8c7d8;}
    </style>
""", unsafe_allow_html=True)


# Check for OpenAI API key
from openai import OpenAI
openai.api_key = st.secrets["OPENAI_API_KEY"]
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
        sound_file.seek(0)
        return sound_file
    except Exception as e:
        st.error(f"Text-to-speech error: {str(e)}")
        return None

def main():
    st.markdown('<div class="title">Real Time Translation</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Healthcare Communication Assistant</div>', unsafe_allow_html=True)
    st.divider()

    # Language selection in two columns
    col1, col2 = st.columns(2)
    with col1:
        source_lang = st.selectbox("Source Language", ["English", "Spanish", "Hindi", "Mandarin", "Arabic", "French"], label_visibility="collapsed")
    with col2:
        target_lang = st.selectbox("Target Language", ["Spanish", "English", "Hindi", "Mandarin", "Arabic", "French"], label_visibility="collapsed")

    lang_codes = {
        "English": "en", "Spanish": "es", "Hindi": "hi",
        "Mandarin": "zh-CN", "Arabic": "ar", "French": "fr"
    }

    st.divider()
    
    st.subheader("Record a Voice Message")
    audio_input = st.experimental_audio_input("")
    
    if audio_input:
        audio_bytes = audio_input.read()
        st.audio(audio_bytes, format='audio/wav')

        audio_file = BytesIO(audio_bytes)
        audio_file.name = "voice_message.wav"

        try:
            transcription = client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file
           )
           
            st.text_area(' Original Text:', transcription.text, height=100)
            
            translated_text = translate_text(transcription.text, target_lang)
            if translated_text:
                st.text_area(' Translation:', translated_text, height=100)
                translated_audio = text_to_speech(translated_text, lang_codes[target_lang])
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

if __name__ == '__main__':
    main()





##################################################################
######################################################################
################################################################





# import streamlit as st 
# import openai
# from gtts import gTTS
# from io import BytesIO
# from audio_recorder_streamlit import audio_recorder

# # Simple page config
# st.set_page_config(
#     page_title='Real Time Translation',
#     page_icon='🌎',
#     layout='centered',
#     initial_sidebar_state='collapsed'
# )


# from openai import OpenAI
# if st.secrets["OPENAI_API_KEY"]:
#     print("\nKey found\n")

# openai.api_key = st.secrets["OPENAI_API_KEY"]
# client = OpenAI()

# def translate_text(text, target_lang):
#     """Translate text using OpenAI"""
#     try:
#         completion = client.chat.completions.create(
#             model="gpt-4o-mini",
#             messages=[
#                     {"role": "system", "content": f"Translate the following text to {target_lang}:"},
#                     {"role": "user", "content": text}
#                 ]
#         )

#         return completion.choices[0].message.content

#     except Exception as e:
#         st.error(f"Translation error: {str(e)}")
#         return None

# def text_to_speech(text, lang_code):
#     """Convert text to speech"""
#     try:
#         sound_file = BytesIO()
#         tts = gTTS(text=text, lang=lang_code)
#         tts.write_to_fp(sound_file)
#         sound_file.seek(0)  # Reset file pointer to beginning
#         return sound_file
#     except Exception as e:
#         st.error(f"Text-to-speech error: {str(e)}")
#         return None

# def main():
#     st.title("Real Time Translation")
#     st.subheader("Healthcare Communication Assistant")

#     st.divider()

#     # Language selection in two columns
#     col1, col2 = st.columns(2)
#     with col1:
#         source_lang = st.selectbox(
#             "Source Language",
#             ["English", "Spanish", "Hindi", "Mandarin", "Arabic", "French"],
#             label_visibility="collapsed"
#         )
#     with col2:
#         target_lang = st.selectbox(
#             "Target Language",
#             ["Spanish", "English", "Hindi", "Mandarin", "Arabic", "French"],
#             label_visibility="collapsed"
#         )

#     # Language codes mapping for TTS
#     lang_codes = {
#         "English": "en", "Spanish": "es", "Hindi": "hi",
#         "Mandarin": "zh-CN", "Arabic": "ar", "French": "fr"
#     }

#     st.divider()

#     # Audio input handling
#     audio_input = st.experimental_audio_input("Record a voice message")
    
#     if audio_input is not None:
#         try:
#             # Convert UploadedFile to bytes
#             audio_bytes = audio_input.read()
            
#             # Display original audio
#             st.audio(audio_bytes, format='audio/wav')
            
#             # Create a BytesIO object for Whisper API
#             audio_file = BytesIO(audio_bytes)
#             audio_file.name = "voice_message.wav"
            
#             # Get transcription
#             transcription = client.audio.transcriptions.create(
#                 model="whisper-1", 
#                 file=audio_file
#             )

#             # transcript = openai.Audio.transcribe("whisper-1", audio_file)
            
#             # Display original text
#             st.text_area('Original Text:',transcription.text
# )
#             # st.write("Original Text:")
#             # st.write(transcription.text)
            
#             # Translate text
#             translated_text = translate_text(transcription.text, target_lang)
            
#             if translated_text:
#                 st.text_area('Translation:', translated_text)
#                 # st.write("Translation:")
#                 # st.write(translated_text)
                
#                 # Generate audio for translation
#                 translated_audio = text_to_speech(translated_text, lang_codes[target_lang])
                
#                 if translated_audio:
#                     st.write("Translation Audio:")
#                     st.audio(translated_audio)

#         except Exception as e:
#             st.error(f"Processing error: {str(e)}")

#     # Text to speech section
#     with st.expander("Text to Speech"):
#         text_input = st.text_area("Enter text:")
#         if st.button("Convert to Speech"):
#             if text_input:
#                 audio = text_to_speech(text_input, lang_codes[target_lang])
#                 if audio:
#                     st.audio(audio)

# if __name__ == '__main__':
#     main()

