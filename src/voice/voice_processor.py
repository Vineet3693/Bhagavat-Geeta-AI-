"""
Main voice processing coordinator
"""
import streamlit as st
import logging
from typing import Optional, Dict, Tuple
from src.voice.speech_to_text import SpeechToTextProcessor
from src.voice.text_to_speech import TextToSpeechProcessor
from config.settings import VOICE_CONFIG

class VoiceProcessor:
    """Main voice processing coordinator"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize processors
        self.stt_processor = SpeechToTextProcessor()
        self.tts_processor = TextToSpeechProcessor()
        
        # Voice settings
        self.enabled = VOICE_CONFIG["enabled"]
        self.default_language = "english"
    
    def process_voice_interaction(
        self, 
        rag_system,
        language: str = None,
        response_type: str = "general"
    ) -> Optional[Dict]:
        """
        Complete voice interaction: speech input -> AI processing -> speech output
        
        Args:
            rag_system: RAG system for processing questions
            language: Language for voice processing
            response_type: Type of response to generate
            
        Returns:
            Complete interaction result or None
        """
        
        if not self.enabled:
            st.warning("🔇 Voice features are disabled in configuration")
            return None
        
        if language is None:
            language = self.default_language
        
        try:
            # Step 1: Voice Input
            st.markdown("### 🎙️ Voice Interaction")
            
            # Get speech input
            question = self.stt_processor.record_audio_streamlit(language)
            
            if not question:
                return None
            
            # Step 2: Process question through RAG system
            with st.spinner("🤔 Processing your question..."):
                response_data = rag_system.process_question(
                    question=question,
                    response_type=response_type,
                    voice_mode=True  # Optimize for voice output
                )
            
            # Step 3: Voice Output
            if response_data["ai_response"]["status"] == "success":
                response_text = response_data["ai_response"]["response"]["main_response"]
                
                # Generate speech output
                with st.spinner("🗣️ Generating voice response..."):
                    self.tts_processor.speak_text(
                        text=response_text,
                        language=language,
                        display_audio=True
                    )
            
            return response_data
            
        except Exception as e:
            self.logger.error(f"❌ Error in voice interaction: {e}")
            st.error(f"Voice interaction error: {str(e)}")
            return None
    
    def voice_input_only(self, language: str = None) -> Optional[str]:
        """Get voice input only (no AI processing)"""
        
        if language is None:
            language = self.default_language
        
        return self.stt_processor.record_audio_streamlit(language)
    
    def voice_output_only(self, text: str, language: str = None) -> Optional[str]:
        """Generate voice output only (no input processing)"""
        
        if language is None:
            language = self.default_language
        
        return self.tts_processor.speak_text(text, language)
    
    def test_voice_system(self) -> Dict:
        """Test complete voice system functionality"""
        
        test_results = {
            "voice_enabled": self.enabled,
            "stt_test": None,
            "tts_test": None,
            "overall_status": "unknown"
        }
        
        try:
            # Test STT
            stt_test = self.stt_processor.test_microphone()
            test_results["stt_test"] = stt_test
            
            # Test TTS
            tts_test = self.tts_processor.test_speech()
            test_results["tts_test"] = {"status": "success" if tts_test else "failed"}
            
            # Overall status
            stt_ok = stt_test.get("status") == "success"
            tts_ok = tts_test
            
            if stt_ok and tts_ok:
                test_results["overall_status"] = "success"
            elif stt_ok or tts_ok:
                test_results["overall_status"] = "partial"
            else:
                test_results["overall_status"] = "failed"
            
            return test_results
            
        except Exception as e:
            test_results["overall_status"] = "error"
            test_results["error"] = str(e)
            return test_results
    
    def get_voice_settings(self) -> Dict:
        """Get current voice settings"""
        
        return {
            "enabled": self.enabled,
            "default_language": self.default_language,
            "supported_languages": list(VOICE_CONFIG["languages"].keys()),
            "tts_settings": {
                "rate": VOICE_CONFIG["tts_rate"],
                "volume": VOICE_CONFIG["tts_volume"]
            },
            "available_voices": self.tts_processor.get_available_voices()
        }


# Utility function
def create_voice_processor() -> VoiceProcessor:
    """Create voice processor"""
    return VoiceProcessor()
