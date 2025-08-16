
"""
Test voice system setup
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import logging
from src.voice.voice_processor import VoiceProcessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_voice_system():
    """Test the complete voice system"""
    
    logger.info("🎙️ Testing voice system...")
    
    try:
        # Create voice processor
        processor = VoiceProcessor()
        
        # Run system test
        results = processor.test_voice_system()
        
        print("\n" + "="*50)
        print("🎙️ VOICE SYSTEM TEST RESULTS")
        print("="*50)
        
        print(f"Voice Enabled: {'✅' if results['voice_enabled'] else '❌'}")
        print(f"Overall Status: {results['overall_status'].upper()}")
        
        # STT Test Results
        print(f"\n🎤 Speech-to-Text:")
        if results['stt_test']:
            stt = results['stt_test']
            print(f"  Status: {'✅' if stt.get('status') == 'success' else '❌'}")
            print(f"  Microphones: {stt.get('microphones_available', 'N/A')}")
        
        # TTS Test Results
        print(f"\n🔊 Text-to-Speech:")
        if results['tts_test']:
            tts = results['tts_test']
            print(f"  Status: {'✅' if tts.get('status') == 'success' else '❌'}")
        
        # Voice Settings
        settings = processor.get_voice_settings()
        print(f"\n⚙️ Voice Settings:")
        print(f"  Supported Languages: {', '.join(settings['supported_languages'])}")
        print(f"  TTS Rate: {settings['tts_settings']['rate']}")
        print(f"  TTS Volume: {settings['tts_settings']['volume']}")
        
        print("="*50)
        
        if results['overall_status'] == 'success':
            print("🎉 Voice system is ready to use!")
        else:
            print("⚠️ Voice system has issues. Check the details above.")
        
        return results['overall_status'] == 'success'
        
    except Exception as e:
        logger.error(f"❌ Voice test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_voice_system()
    sys.exit(0 if success else 1)
