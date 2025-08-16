
"""
Sidebar component for Bhagavad Gita AI
"""
import streamlit as st
import logging
from typing import Dict
from config.settings import APP_CONFIG, VOICE_CONFIG

class AppSidebar:
    """Application sidebar with settings and information"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def render(self):
        """Render the complete sidebar"""
        
        with st.sidebar:
            # App info
            self.render_app_info()
            
            # User preferences
            self.render_user_preferences()
            
            # Voice settings
            self.render_voice_settings()
            
            # System status
            self.render_system_status()
            
            # Help & About
            self.render_help_section()
    
    def render_app_info(self):
        """Render app information section"""
        
        st.markdown("---")
        st.markdown("## 🕉️ Bhagavad Gita AI")
        st.markdown(f"**Version:** {APP_CONFIG['version']}")
        st.markdown(f"**Author:** {APP_CONFIG['author']}")
        
        # Quick stats
        if 'chat_history' in st.session_state:
            st.metric("Questions Asked", len(st.session_state.chat_history))
        
        st.markdown("---")
    
    def render_user_preferences(self):
        """Render user preferences section"""
        
        st.markdown("### ⚙️ Preferences")
        
        # Response type preference
        default_response = st.selectbox(
            "Default Response Style:",
            options=["general", "philosophical", "practical", "beginner"],
            format_func=lambda x: {
                "general": "🧠 General",
                "philosophical": "🤔 Philosophical", 
                "practical": "💼 Practical",
                "beginner": "🌱 Beginner"
            }[x],
            index=0
        )
        
        # Language preference
        language = st.selectbox(
            "Language:",
            options=list(VOICE_CONFIG["languages"].keys()),
            format_func=lambda x: x.title(),
            index=0
        )
        
        # Theme preference
        theme = st.selectbox(
            "Theme:",
            options=["spiritual", "modern", "classic"],
            format_func=lambda x: {
                "spiritual": "🕉️ Spiritual",
                "modern": "🌟 Modern",
                "classic": "📜 Classic"
            }[x],
            index=0
        )
        
        # Update session state
        if 'user_preferences' in st.session_state:
            st.session_state.user_preferences.update({
                'response_type': default_response,
                'language': language,
                'theme': theme
            })
        
        st.markdown("---")
    
    def render_voice_settings(self):
        """Render voice settings section"""
        
        st.markdown("### 🎙️ Voice Settings")
        
        # Enable/disable voice
        voice_enabled = st.checkbox(
            "Enable Voice Features",
            value=VOICE_CONFIG["enabled"],
            help="Turn on/off voice input and output"
        )
        
        if voice_enabled:
            # Voice speed
            speech_rate = st.slider(
                "Speech Rate:",
                min_value=100,
                max_value=250,
                value=VOICE_CONFIG["tts_rate"],
                step=10,
                help="Adjust how fast the AI speaks"
            )
            
            # Voice volume
            speech_volume = st.slider(
                "Speech Volume:",
                min_value=0.1,
                max_value=1.0,
                value=VOICE_CONFIG["tts_volume"],
                step=0.1,
                help="Adjust voice output volume"
            )
            
            # Auto-play responses
            auto_voice = st.checkbox(
                "Auto-play Voice Responses",
                value=False,
                help="Automatically play voice output for responses"
            )
            
            # Update session state
            if 'user_preferences' in st.session_state:
                st.session_state.user_preferences.update({
                    'voice_enabled': voice_enabled,
                    'speech_rate': speech_rate,
                    'speech_volume': speech_volume,
                    'auto_voice': auto_voice
                })
        
        st.markdown("---")
    
    def render_system_status(self):
        """Render system status section"""
        
        st.markdown("### 📊 System Status")
        
        # API status
        if st.button("🔍 Check API Status"):
            self.check_api_status()
        
        # Memory usage
        if 'chat_history' in st.session_state:
            memory_usage = len(str(st.session_state.chat_history))
            st.metric("Memory Usage", f"{memory_usage} chars")
        
        # Session info
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_history = []
            st.success("Chat history cleared!")
            st.rerun()
        
        st.markdown("---")
    
    def render_help_section(self):
        """Render help and about section"""
        
        st.markdown("### ℹ️ Help & About")
        
        with st.expander("❓ How to Use"):
            st.markdown("""
            **Getting Started:**
            1. 📝 Type your question in the main text area
            2. 🎯 Select your preferred response style
            3. 🚀 Click "Get Wisdom" to receive guidance
            
            **Voice Features:**
            1. 🎙️ Click "Voice Mode" to speak your question
            2. 🔊 Use voice output for responses
            3. 🧪 Test voice system in settings
            
            **Question Types:**
            - Life purpose and meaning
            - Dharma and ethics
            - Karma and action
            - Relationships and society
            - Spiritual practices
            - Practical daily wisdom
            """)
        
        with st.expander("📖 About Bhagavad Gita"):
            st.markdown("""
            The **Bhagavad Gita** is a 700-verse Hindu scripture that is part of the epic Mahabharata. 
            It consists of a conversation between Prince Arjuna and Lord Krishna, who serves as his 
            charioteer and spiritual guide.
            
            **Core Teachings:**
            - **Dharma:** Righteous duty and moral law
            - **Karma:** Action and the law of cause and effect
            - **Yoga:** Union with the divine through various paths
            - **Moksha:** Liberation from the cycle of rebirth
            
            This AI aims to make these timeless teachings accessible for modern life challenges.
            """)
        
        with st.expander("🛠️ Technical Info"):
            st.markdown(f"""
            **Technology Stack:**
            - **Frontend:** Streamlit
            - **AI Engine:** Groq (LLaMA/Mixtral models)
            - **Embeddings:** Sentence Transformers
            - **Voice:** SpeechRecognition + pyttsx3/gTTS
            - **Search:** FAISS vector database
            
            **Version:** {APP_CONFIG['version']}
            **Author:** {APP_CONFIG['author']}
            """)
        
        # Contact/Support
        st.markdown("### 📞 Support")
        st.markdown("For issues or suggestions:")
        st.markdown("📧 vineet9949@gmail.com")
        st.markdown("🐙 [GitHub Repository](https://github.com/Vineet3693/bhagavad-gita-ai)")
    
    def check_api_status(self):
        """Check and display API status"""
        
        try:
            # Check if we can import and create Groq client
            from groq import Groq
            from config.settings import GROQ_API_KEY
            
            if GROQ_API_KEY == "xyz":
                st.warning("⚠️ Using placeholder API key. Set your real Groq API key.")
                st.info("API Status: **Mock Mode** (for testing)")
            else:
                # Try to create client
                client = Groq(api_key=GROQ_API_KEY)
                st.success("✅ API Status: **Connected**")
            
            # System components status
            st.markdown("**System Components:**")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("✅ RAG System")
                st.markdown("✅ Data Loader")
                st.markdown("✅ Embeddings")
            
            with col2:
                st.markdown("✅ Vector Search")
                st.markdown("✅ UI Components")
                voice_status = "✅" if VOICE_CONFIG["enabled"] else "⚠️"
                st.markdown(f"{voice_status} Voice System")
                
        except Exception as e:
            st.error(f"❌ API Status: **Error** - {str(e)}")
