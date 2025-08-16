
"""
Text-to-Speech functionality for voice output
"""
import streamlit as st
import pyttsx3
import tempfile
import base64
import logging
from pathlib import Path
from typing import Optional, Dict
from gtts import gTTS
import pygame
from config.settings import VOICE_CONFIG

class TextToSpeechProcessor:
    """Handle text-to-speech conversion"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.tts_engine = None
        self._initialize_engine()
        
        # Voice settings
        self.settings = VOICE_CONFIG
    
    def _initialize_engine(self):
        """Initialize TTS engine"""
        try:
            self.tts_engine = pyttsx3.init()
            self._configure_voice()
            self.logger.info("✅ TTS engine initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing TTS engine: {e}")
            self.tts_engine = None
    
    def _configure_voice(self):
        """Configure voice properties"""
        if not self.tts_engine:
            return
        
        try:
            # Get available voices
            voices = self.tts_engine.getProperty('voices')
            
            # Try to find a suitable English voice
            english_voice = None
            for voice in voices:
                if 'english' in voice.name.lower() or 'en' in voice.id.lower():
                    english_voice = voice.id
                    break
            
            if english_voice:
                self.tts_engine.setProperty('voice', english_voice)
            
            # Set rate and volume for spiritual content (slower, calmer)
            self.tts_engine.setProperty('rate', self.settings["tts_rate"])
            self.tts_engine.setProperty('volume', self.settings["tts_volume"])
            
        except Exception as e:
            self.logger.error(f"❌ Error configuring voice: {e}")
    
    def speak_text(
        self, 
        text: str, 
        language: str = "english",
        display_audio: bool = True
    ) -> Optional[str]:
        """
        Convert text to speech and play/display in Streamlit
        
        Args:
            text: Text to speak
            language: Language for TTS
            display_audio: Whether to display audio player in Streamlit
            
        Returns:
            Path to audio file or None
        """
        
        try:
            # Clean text for speech
            clean_text = self._prepare_text_for_speech(text)
            
            if language == "hindi":
                audio_file = self._generate_hindi_speech(clean_text)
            else:
                audio_file = self._generate_english_speech(clean_text)
            
            if audio_file and display_audio:
                self._display_audio_player(audio_file, text)
            
            return audio_file
            
        except Exception as e:
            self.logger.error(f"❌ Error in text-to-speech: {e}")
            st.error(f"Voice output error: {str(e)}")
            return None
    
    def _prepare_text_for_speech(self, text: str) -> str:
        """Prepare text for natural speech"""
        
        # Remove markdown formatting
        import re
        clean_text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Remove bold
        clean_text = re.sub(r'\*(.*?)\*', r'\1', clean_text)  # Remove italic
        clean_text = re.sub(r'`(.*?)`', r'\1', clean_text)   # Remove code
        clean_text = re.sub(r'#{1,6}\s', '', clean_text)     # Remove headers
        
        # Add natural pauses
        clean_text = clean_text.replace('.', '. ')  # Pause after sentences
        clean_text = clean_text.replace(',', ', ')  # Small pause after commas
        clean_text = clean_text.replace(';', '; ')  # Pause after semicolons
        clean_text = clean_text.replace(':', ': ')  # Pause after colons
        
        # Handle verse references
        clean_text = re.sub(r'(\d+)\.(\d+)', r'Chapter \1, Verse \2', clean_text)
        
        # Limit length for better speech quality
        if len(clean_text) > 1000:
            clean_text = clean_text[:1000] + "... The complete response is available in text form."
        
        return clean_text.strip()
    
    def _generate_english_speech(self, text: str) -> Optional[str]:
        """Generate English speech using pyttsx3"""
        
        if not self.tts_engine:
            return self._generate_gtts_speech(text, "en")
        
        try:
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            temp_file.close()
            
            # Generate speech
            self.tts_engine.save_to_file(text, temp_file.name)
            self.tts_engine.runAndWait()
            
            # Check if file was created
            if Path(temp_file.name).exists():
                return temp_file.name
            else:
                # Fallback to gTTS
                return self._generate_gtts_speech(text, "en")
                
        except Exception as e:
            self.logger.error(f"❌ Error generating English speech: {e}")
            return self._generate_gtts_speech(text, "en")
    
    def _generate_hindi_speech(self, text: str) -> Optional[str]:
        """Generate Hindi speech using gTTS"""
        return self._generate_gtts_speech(text, "hi")
    
    def _generate_gtts_speech(self, text: str, lang: str) -> Optional[str]:
        """Generate speech using Google TTS"""
        
        try:
            # Create TTS object
            tts = gTTS(
                text=text, 
                lang=lang, 
                slow=False,  # Normal speed
                tld='com'    # Use .com domain
            )
            
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            temp_file.close()
            
            # Save audio
            tts.save(temp_file.name)
            
            return temp_file.name
            
        except Exception as e:
            self.logger.error(f"❌ Error generating gTTS speech: {e}")
            return None
    
    def _display_audio_player(self, audio_file: str, original_text: str):
        """Display audio player in Streamlit"""
        
        try:
            # Read audio file
            with open(audio_file, 'rb') as audio_bytes:
                audio_data = audio_bytes.read()
            
            # Encode to base64
            audio_b64 = base64.b64encode(audio_data).decode()
            
            # Determine MIME type
            file_ext = Path(audio_file).suffix.lower()
            mime_type = "audio/mpeg" if file_ext == ".mp3" else "audio/wav"
            
            # Create audio HTML
            audio_html = f"""
            <div style="margin: 10px 0;">
                <p style="margin-bottom: 5px;"><strong>🔊 Listen to Response:</strong></p>
                <audio controls style="width: 100%;">
                    <source src="data:{mime_type};base64,{audio_b64}" type="{mime_type}">
                    Your browser does not support the audio element.
                </audio>
            </div>
            """
            
            # Display audio player
            st.markdown(audio_html, unsafe_allow_html=True)
            
            # Show text preview
            with st.expander("📝 View Response Text"):
                st.markdown(original_text)
            
        except Exception as e:
            self.logger.error(f"❌ Error displaying audio player: {e}")
            st.error("Could not display audio player")
    
    def get_available_voices(self) -> Dict:
        """Get information about available voices"""
        
        try:
            if not self.tts_engine:
                return {"status": "error", "error": "TTS engine not available"}
            
            voices = self.tts_engine.getProperty('voices')
            voice_info = []
            
            for voice in voices[:10]:  # Show first 10 voices
                voice_info.append({
                    "id": voice.id,
                    "name": voice.name,
                    "languages": getattr(voice, 'languages', ['Unknown']),
                    "gender": getattr(voice, 'gender', 'Unknown')
                })
            
            return {
                "status": "success",
                "total_voices": len(voices),
                "voices": voice_info,
                "current_settings": {
                    "rate": self.tts_engine.getProperty('rate'),
                    "volume": self.tts_engine.getProperty('volume')
                }
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def test_speech(self, test_text: str = None) -> bool:
        """Test TTS functionality"""
        
        if test_text is None:
            test_text = "Namaste! This is a test of the Bhagavad Gita AI voice system."
        
        try:
            audio_file = self.speak_text(test_text, display_audio=False)
            return audio_file is not None
            
        except Exception as e:
            self.logger.error(f"❌ TTS test failed: {e}")
            return False


# Utility function
def create_tts_processor() -> TextToSpeechProcessor:
    """Create text-to-speech processor"""
    return TextToSpeechProcessor()
