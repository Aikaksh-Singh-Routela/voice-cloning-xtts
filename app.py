import streamlit as st
import os
import tempfile
import soundfile as sf
import numpy as np
import io
from TTS.api import TTS

# Page config
st.set_page_config(
    page_title="Voice Cloning Studio",
    page_icon="🎤",
    layout="wide"
)

st.title("🎤 Voice Cloning Studio")
st.markdown("*Clone voices and generate speech from text using Coqui XTTS-v2*")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    st.markdown("""
    **License Notice:**
    Coqui XTTS-v2 is licensed under the Coqui Public Model License (CPML).
    This project is for **non-commercial use only**.
    """)
    
    st.markdown("---")
    
    # Language selection
    language = st.selectbox(
        "Language",
        ["en", "es", "fr", "de", "hi", "ja", "zh-cn", "it", "pt", "ru"]
    )
    
    st.markdown("---")
    st.markdown("### 🎙️ Upload Voice Sample")
    
    uploaded_file = st.file_uploader(
        "Upload a WAV file (3-10 seconds)",
        type=['wav']
    )
    
    st.markdown("---")
    st.markdown("### 📝 Text Input")
    
    text_to_speak = st.text_area(
        "Enter text to speak",
        "Hello, this is a voice cloned from your sample!",
        height=100
    )

# Load TTS model
@st.cache_resource
def load_tts_model():
    try:
        tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=False)
        return tts
    except Exception as e:
        st.error(f"Error loading model: {str(e)}")
        return None

# Main app logic
if st.button("🎤 Generate Speech"):
    if not text_to_speak:
        st.warning("Please enter some text to speak.")
    else:
        with st.spinner("Loading XTTS model and generating speech..."):
            tts = load_tts_model()
            
            if tts is None:
                st.stop()
            
            voice_audio_path = None
            
            # Save uploaded file temporarily
            if uploaded_file is not None:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    voice_audio_path = tmp_file.name
                
                # Play uploaded audio
                st.sidebar.audio(uploaded_file.getvalue(), format='audio/wav')
                st.sidebar.success("✅ Voice sample uploaded!")
            
            # Generate speech
            with st.spinner("Generating speech..."):
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as output_file:
                        output_path = output_file.name
                    
                    # Generate speech using XTTS
                    if voice_audio_path:
                        tts.tts_to_file(
                            text=text_to_speak,
                            file_path=output_path,
                            speaker_wav=voice_audio_path,
                            language=language
                        )
                    else:
                        st.warning("Please upload a voice sample for cloning!")
                        st.stop()
                    
                    # Read generated audio
                    audio_data, sample_rate = sf.read(output_path)
                    
                    # Convert to bytes for playback
                    audio_bytes = io.BytesIO()
                    sf.write(audio_bytes, audio_data, sample_rate, format='wav')
                    audio_bytes.seek(0)
                    
                    # Display audio player
                    st.audio(audio_bytes, format='audio/wav')
                    
                    # Download button
                    st.download_button(
                        "⬇️ Download Generated Audio",
                        audio_bytes,
                        file_name="cloned_voice.wav",
                        mime="audio/wav"
                    )
                    
                    st.success("✅ Speech generated successfully!")
                    
                    # Clean up
                    os.unlink(output_path)
                    if voice_audio_path:
                        os.unlink(voice_audio_path)
                    
                except Exception as e:
                    st.error(f"Error generating speech: {str(e)}")

# Footer
st.markdown("---")
st.caption("🎤 Voice Cloning Studio - Powered by Coqui XTTS-v2 | Non-commercial use only")