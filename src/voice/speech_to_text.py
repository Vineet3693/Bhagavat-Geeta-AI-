
"""
Speech-to-Text functionality for voice input
"""
import streamlit as st
import speech_recognition as sr
from audio_recorder_streamlit import audio_recorder
import io
import logging
from typing import Optional, Dict
from config.settings import VOICE_CONFIG

class SpeechToTextProcessor:
    """Handle speech-to-text conversion"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.logger = logging.getLogger(__name__)
        
        # Configure recognizer
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        
        # Supported languages
        self.languages = VOICE_CONFIG["languages"]
    
    def record_audio_streamlit(self, language: str = "english") -> Optional[str]:
        """
        Record audio using Streamlit audio recorder
        
        Args:
            language: Language for recognition
            
        Returns:
            Transcribed text or None
        """
        
        try:
            # Display voice input interface
            st.markdown("### 🎙️ Voice Input")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col2:
                # Audio recorder component
                audio_bytes = audio_recorder(
                    text="🎙️ Click to ask your Gita question",
                    recording_color="#ff6b35",
                    neutral_color="#333333", 
                    icon_name="microphone",
                    icon_size="2x",
                    pause_threshold=2.0,
                    sample_rate=41_000
                )
            
            if audio_bytes:
                # Show processing message
                with st.spinner("🔄 Converting speech to text..."):
                    # Convert bytes to audio file
                    audio_file = io.BytesIO(audio_bytes)
                    
                    # Perform speech recognition
                    text = self._recognize_speech(audio_file, language)
                    
                    if text:
                        st.success("✅ Speech recognized successfully!")
                        st.markdown(f"**You said:** *{text}*")
                        return text
                    else:
                        st.error("❌ Could not understand the audio. Please try again.")
                        return None
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Error in audio recording: {e}")
            st.error(f"Voice input error: {str(e)}")
            return None
    
    def _recognize_speech(self, audio_file: io.BytesIO, language: str) -> Optional[str]:
        """
        Recognize speech from audio file
        
        Args:
            audio_file: Audio file as BytesIO
            language: Language code for recognition
            
        Returns:
            Recognized text or None
        """
        
        try:
            # Get language code
            lang_code = self.languages.get(language, "en-US")
            
            # Convert BytesIO to AudioFile
            with sr.AudioFile(audio_file) as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                # Record the audio
                audio_data = self.recognizer.record(source)
            
            # Perform recognition
            try:
                # Try Google Speech Recognition (free)
                text = self.recognizer.recognize_google(
                    audio_data, 
                    language=lang_code,
                    show_all=False
                )
                
                self.logger.info(f"✅ Speech recognized: {text[:50]}...")
                return text
                
            except sr.UnknownValueError:
                self.logger.warning("Could not understand audio")
                return None
                
            except sr.RequestError as e:
                self.logger.error(f"Speech recognition service error: {e}")
                # Fallback to offline recognition if available
                return self._offline_recognition_fallback(audio_data)
                
        except Exception as e:
            self.logger.error(f"❌ Error in speech recognition: {e}")
            return None
    
    def _offline_recognition_fallback(self, audio_data) -> Optional[str]:
        """Fallback to offline recognition if available"""
        try:
            # Try offline recognition (if available)
            text = self.recognizer.recognize_sphinx(audio_data)
            self.logger.info("✅ Used offline recognition")
            return text
        except:
            return None
    
    def test_microphone(self) -> Dict:
        """Test microphone functionality"""
        try:
            # List available microphones
            mic_list = sr.Microphone.list_microphone_names()
            
            return {
                "status": "success",
                "microphones_available": len(mic_list),
                "microphone_names": mic_list[:5],  # Show first 5
                "recognizer_ready": True
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "recognizer_ready": False
            }


# Utility functions
def create_speech_processor() -> SpeechToTextProcessor:
    """Create speech-to-text processor"""
    return SpeechToTextProcessor()
