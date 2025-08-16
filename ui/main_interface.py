
"""
Main Streamlit interface for Bhagavad Gita AI
"""
import streamlit as st
import pandas as pd
from typing import Dict, List, Optional
import logging
from pathlib import Path

# Custom imports
from src.ai.rag_system import GitaRAGSystem
from src.voice.voice_processor import VoiceProcessor
from ui.components.chat_interface import ChatInterface
from ui.components.question_suggestions import QuestionSuggestions
from ui.components.sidebar import AppSidebar
from config.settings import APP_CONFIG, UI_CONFIG

class MainInterface:
    """Main Streamlit application interface"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize session state
        self._init_session_state()
        
        # Load custom CSS
        self._load_custom_styles()
        
        # Initialize components
        self.rag_system = None
        self.voice_processor = None
        self.chat_interface = None
        self.question_suggestions = None
        self.sidebar = None
    
    def _init_session_state(self):
        """Initialize Streamlit session state variables"""
        
        # App state
        if 'initialized' not in st.session_state:
            st.session_state.initialized = False
        
        # Chat history
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        
        # User preferences
        if 'user_preferences' not in st.session_state:
            st.session_state.user_preferences = {
                'response_type': 'general',
                'language': 'english',
                'voice_enabled': True,
                'theme': 'spiritual'
            }
        
        # Current question context
        if 'current_question' not in st.session_state:
            st.session_state.current_question = ""
        
        # Voice interaction state
        if 'voice_active' not in st.session_state:
            st.session_state.voice_active = False
        
        # Error states
        if 'last_error' not in st.session_state:
            st.session_state.last_error = None
    
    def _load_custom_styles(self):
        """Load custom CSS styles"""
        
        try:
            # Custom CSS for spiritual theme
            spiritual_css = """
            <style>
            /* Main theme colors */
            .main {
                background: linear-gradient(135deg, #0f1419 0%, #1a1f2e 100%);
            }
            
            /* Header styling */
            .main-header {
                text-align: center;
                padding: 2rem 0;
                background: linear-gradient(45deg, #ff6b35, #f7931e);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                font-size: 3rem;
                font-weight: bold;
                margin-bottom: 2rem;
                text-shadow: 0 0 20px rgba(255, 107, 53, 0.3);
            }
            
            /* Om symbol animation */
            .om-symbol {
                font-size: 4rem;
                animation: pulse 2s infinite;
                color: #ff6b35;
                text-align: center;
                margin: 1rem 0;
            }
            
            @keyframes pulse {
                0% { opacity: 0.7; transform: scale(1); }
                50% { opacity: 1; transform: scale(1.05); }
                100% { opacity: 0.7; transform: scale(1); }
            }
            
            /* Question cards */
            .question-card {
                background: linear-gradient(135deg, #1e2329 0%, #2d3339 100%);
                border: 1px solid #ff6b35;
                border-radius: 10px;
                padding: 1rem;
                margin: 0.5rem 0;
                transition: all 0.3s ease;
                cursor: pointer;
            }
            
            .question-card:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 20px rgba(255, 107, 53, 0.2);
                border-color: #f7931e;
            }
            
            /* Response styling */
            .gita-response {
                background: linear-gradient(135deg, #1a1f2e 0%, #252a3a 100%);
                border-left: 4px solid #ff6b35;
                padding: 1.5rem;
                border-radius: 0 10px 10px 0;
                margin: 1rem 0;
                font-size: 1.1rem;
                line-height: 1.6;
            }
            
            /* Verse display */
            .verse-container {
                background: linear-gradient(135deg, #2d1b35 0%, #3d2b45 100%);
                border: 1px solid #9b59b6;
                border-radius: 10px;
                padding: 1.5rem;
                margin: 1rem 0;
            }
            
            .sanskrit-text {
                font-family: 'Devanagari', serif;
                font-size: 1.3rem;
                color: #f39c12;
                text-align: center;
                margin-bottom: 1rem;
                line-height: 1.8;
            }
            
            .hindi-text {
                font-size: 1.1rem;
                color: #3498db;
                margin-bottom: 1rem;
                text-align: center;
            }
            
            .english-text {
                font-size: 1rem;
                color: #ecf0f1;
                text-align: center;
                font-style: italic;
            }
            
            /* Voice interface */
            .voice-interface {
                background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
                border-radius: 15px;
                padding: 2rem;
                text-align: center;
                margin: 1rem 0;
                border: 2px solid #3498db;
            }
            
            /* Loading animations */
            .lotus-loader {
                display: inline-block;
                font-size: 2rem;
                animation: rotate 2s linear infinite;
            }
            
            @keyframes rotate {
                from { transform: rotate(0deg); }
                to { transform: rotate(360deg); }
            }
            
            /* Sidebar styling */
            .sidebar-content {
                background: linear-gradient(135deg, #1a1f2e 0%, #252a3a 100%);
                border-radius: 10px;
                padding: 1rem;
                margin: 0.5rem 0;
            }
            
            /* Button styling */
            .stButton > button {
                background: linear-gradient(45deg, #ff6b35, #f7931e);
                color: white;
                border: none;
                border-radius: 25px;
                padding: 0.5rem 1.5rem;
                font-weight: bold;
                transition: all 0.3s ease;
            }
            
            .stButton > button:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 15px rgba(255, 107, 53, 0.4);
            }
            
            /* Input styling */
            .stTextInput > div > div > input {
                background: linear-gradient(135deg, #1e2329 0%, #2d3339 100%);
                border: 2px solid #ff6b35;
                border-radius: 25px;
                color: white;
                padding: 0.75rem 1rem;
            }
            
            /* Hide Streamlit elements */
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            .stDeployButton {display: none;}
            </style>
            """
            
            st.markdown(spiritual_css, unsafe_allow_html=True)
            
        except Exception as e:
            self.logger.error(f"❌ Error loading custom styles: {e}")
    
    def initialize_systems(self):
        """Initialize all systems"""
        
        if st.session_state.initialized:
            return
        
        try:
            with st.spinner("🕉️ Initializing Bhagavad Gita AI..."):
                # Initialize RAG system
                self.rag_system = GitaRAGSystem()
                
                # Initialize voice processor
                self.voice_processor = VoiceProcessor()
                
                # Initialize UI components
                self.chat_interface = ChatInterface(self.rag_system)
                self.question_suggestions = QuestionSuggestions(self.rag_system)
                self.sidebar = AppSidebar()
                
                st.session_state.initialized = True
                
            st.success("✅ System initialized successfully!")
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing systems: {e}")
            st.error(f"Initialization failed: {str(e)}")
            st.session_state.initialized = False
    
    def render_header(self):
        """Render the main header"""
        
        # Om symbol with animation
        st.markdown('<div class="om-symbol">🕉️</div>', unsafe_allow_html=True)
        
        # Main title
        st.markdown(f'<h1 class="main-header">{APP_CONFIG["name"]}</h1>', unsafe_allow_html=True)
        
        # Subtitle
        st.markdown(
            '<p style="text-align: center; font-size: 1.2rem; color: #bdc3c7; margin-bottom: 2rem;">'
            '🌟 Your AI guide to ancient wisdom for modern life 🌟'
            '</p>',
            unsafe_allow_html=True
        )
    
    def render_main_content(self):
        """Render the main content area"""
        
        # Create main layout
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Main chat interface
            self.render_chat_section()
        
        with col2:
            # Question suggestions and voice interface
            self.render_suggestions_section()
    
    def render_chat_section(self):
        """Render the main chat interface section"""
        
        st.markdown("### 💬 Ask Your Question")
        
        # Text input for questions
        question = st.text_input(
            "Enter your question about life, dharma, karma, or any spiritual topic:",
            value=st.session_state.current_question,
            placeholder="e.g., How can I find peace in difficult times?",
            key="question_input"
        )
        
        # Response type selection
        response_type = st.selectbox(
            "Response Style:",
            options=["general", "philosophical", "practical", "beginner"],
            format_func=lambda x: {
                "general": "🧠 General Wisdom",
                "philosophical": "🤔 Deep Philosophy", 
                "practical": "💼 Practical Advice",
                "beginner": "🌱 Beginner Friendly"
            }[x],
            index=0
        )
        
        # Action buttons
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("🚀 Get Wisdom", type="primary"):
                if question.strip():
                    self.process_text_question(question, response_type)
                else:
                    st.warning("Please enter a question first!")
        
        with col2:
            if st.button("🎙️ Voice Mode"):
                self.handle_voice_interaction(response_type)
        
        with col3:
            if st.button("🎲 Random Verse"):
                self.show_random_verse()
        
        # Display chat history
        self.render_chat_history()
    
    def render_suggestions_section(self):
        """Render the suggestions and additional features section"""
        
        st.markdown("### 💡 Suggested Questions")
        
        # Question categories
        categories = self.rag_system.get_categories() if self.rag_system else {}
        
        for category_key, category_info in categories.items():
            with st.expander(f"{category_info['icon']} {category_info['title']}"):
                st.markdown(f"*{category_info['description']}*")
                
                for question in category_info['questions']:
                    if st.button(question, key=f"suggest_{category_key}_{question[:20]}"):
                        st.session_state.current_question = question
                        st.rerun()
        
        # Voice system status
        self.render_voice_status()
        
        # Quick verse lookup
        self.render_verse_lookup()
    
    def render_chat_history(self):
        """Render chat history"""
        
        if not st.session_state.chat_history:
            st.info("💭 Your conversation will appear here...")
            return
        
        st.markdown("### 📚 Conversation History")
        
        # Display conversations in reverse order (newest first)
        for i, conversation in enumerate(reversed(st.session_state.chat_history[-5:])):  # Show last 5
            with st.expander(f"Q: {conversation['question'][:50]}..."):
                # Question
                st.markdown(f"**❓ Question:** {conversation['question']}")
                
                # Response
                if conversation.get('response'):
                    response_data = conversation['response']
                    if response_data['ai_response']['status'] == 'success':
                        main_response = response_data['ai_response']['response']['main_response']
                        st.markdown(f'<div class="gita-response">{main_response}</div>', unsafe_allow_html=True)
                        
                        # Show referenced verses
                        verses = response_data['ai_response']['response'].get('referenced_verses', [])
                        if verses:
                            st.markdown("**📜 Referenced Verses:**")
                            for verse in verses[:2]:  # Show top 2 verses
                                self.render_verse_card(verse)
                
                # Timestamp
                if 'timestamp' in conversation:
                    st.caption(f"🕐 {conversation['timestamp']}")
    
    def render_verse_card(self, verse: Dict):
        """Render a single verse card"""
        
        verse_html = f"""
        <div class="verse-container">
            <div style="text-align: center; margin-bottom: 1rem;">
                <strong style="color: #e74c3c;">Chapter {verse.get('verse_id', 'Unknown')}</strong>
            </div>
            <div class="sanskrit-text">{verse.get('sanskrit', 'N/A')}</div>
            <div class="hindi-text">{verse.get('hindi', 'N/A')}</div>
            <div class="english-text">{verse.get('english', 'N/A')}</div>
        </div>
        """
        st.markdown(verse_html, unsafe_allow_html=True)
    
    def render_voice_status(self):
        """Render voice system status"""
        
        st.markdown("### 🎙️ Voice Features")
        
        if self.voice_processor:
            voice_settings = self.voice_processor.get_voice_settings()
            
            if voice_settings['enabled']:
                st.success("✅ Voice system active")
                
                # Test voice button
                if st.button("🧪 Test Voice System"):
                    self.test_voice_system()
            else:
                st.warning("⚠️ Voice system disabled")
        else:
            st.error("❌ Voice system not initialized")
    
    def render_verse_lookup(self):
        """Render quick verse lookup section"""
        
        st.markdown("### 🔍 Verse Lookup")
        
        col1, col2 = st.columns(2)
        
        with col1:
            chapter = st.number_input("Chapter", min_value=1, max_value=18, value=2)
        
        with col2:
            verse = st.number_input("Verse", min_value=1, max_value=78, value=47)
        
        if st.button("📖 Get Verse"):
            self.show_specific_verse(chapter, verse)
    
    def process_text_question(self, question: str, response_type: str):
        """Process a text question"""
        
        try:
            with st.spinner("🤔 Contemplating your question..."):
                # Process through RAG system
                response_data = self.rag_system.process_question(
                    question=question,
                    response_type=response_type,
                    user_context=st.session_state.user_preferences
                )
                
                # Display response
                self.display_response(response_data)
                
                # Save to chat history
                conversation = {
                    'question': question,
                    'response': response_data,
                    'timestamp': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'response_type': response_type
                }
                st.session_state.chat_history.append(conversation)
                
                # Clear current question
                st.session_state.current_question = ""
                
        except Exception as e:
            self.logger.error(f"❌ Error processing question: {e}")
            st.error(f"Error processing question: {str(e)}")
    
    def handle_voice_interaction(self, response_type: str):
        """Handle voice interaction"""
        
        if not self.voice_processor:
            st.error("Voice system not available")
            return
        
        try:
            # Process voice interaction
            result = self.voice_processor.process_voice_interaction(
                rag_system=self.rag_system,
                response_type=response_type
            )
            
            if result:
                # Save to chat history
                conversation = {
                    'question': result['question'],
                    'response': result,
                    'timestamp': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'response_type': response_type,
                    'voice_interaction': True
                }
                st.session_state.chat_history.append(conversation)
                
        except Exception as e:
            self.logger.error(f"❌ Error in voice interaction: {e}")
            st.error(f"Voice interaction error: {str(e)}")
    
    def show_random_verse(self):
        """Display a random verse"""
        
        try:
            if self.rag_system:
                verse = self.rag_system.get_random_verse()
                if verse:
                    st.markdown("### 🎲 Today's Wisdom")
                    self.render_verse_card(verse)
                else:
                    st.warning("Could not retrieve random verse")
            
        except Exception as e:
            self.logger.error(f"❌ Error getting random verse: {e}")
            st.error(f"Error getting random verse: {str(e)}")
    
    def show_specific_verse(self, chapter: int, verse: int):
        """Display a specific verse"""
        
        try:
            if self.rag_system:
                verse_data = self.rag_system.data_loader.get_verse_by_id(chapter, verse)
                if verse_data:
                    st.markdown(f"### 📖 Chapter {chapter}, Verse {verse}")
                    self.render_verse_card(verse_data)
                else:
                    st.warning(f"Verse {chapter}.{verse} not found")
            
        except Exception as e:
            self.logger.error(f"❌ Error getting specific verse: {e}")
            st.error(f"Error retrieving verse: {str(e)}")
    
    def display_response(self, response_data: Dict):
        """Display AI response"""
        
        if response_data['ai_response']['status'] != 'success':
            st.error("Failed to generate response")
            return
        
        response = response_data['ai_response']['response']
        
        # Main response
        st.markdown("### 🧘‍♀️ Wisdom from the Gita")
        st.markdown(f'<div class="gita-response">{response["main_response"]}</div>', unsafe_allow_html=True)
        
        # Referenced verses
        verses = response.get('referenced_verses', [])
        if verses:
            st.markdown("### 📜 Referenced Verses")
            for verse in verses:
                self.render_verse_card(verse)
        
        # Voice output option
        if st.button("🔊 Listen to Response"):
            if self.voice_processor:
                self.voice_processor.voice_output_only(response["main_response"])
            else:
                st.warning("Voice output not available")
        
        # Metadata
        with st.expander("📊 Response Details"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Words", response.get('response_length', 'N/A'))
            with col2:
                st.metric("Reading Time", f"{response.get('estimated_reading_time', 0):.1f} min")
            with col3:
                st.metric("Verses Used", len(verses))
    
    def test_voice_system(self):
        """Test voice system functionality"""
        
        if self.voice_processor:
            with st.spinner("Testing voice system..."):
                test_results = self.voice_processor.test_voice_system()
                
                if test_results['overall_status'] == 'success':
                    st.success("✅ Voice system working perfectly!")
                elif test_results['overall_status'] == 'partial':
                    st.warning("⚠️ Voice system partially working")
                else:
                    st.error("❌ Voice system has issues")
                
                # Show detailed results
                with st.expander("🔍 Detailed Test Results"):
                    st.json(test_results)
        else:
            st.error("Voice processor not available")
    
    def run(self):
        """Main application entry point"""
        
        try:
            # Configure Streamlit page
            st.set_page_config(
                page_title=APP_CONFIG["name"],
                page_icon="🕉️",
                layout="wide",
                initial_sidebar_state="expanded",
                menu_items={
                    'Get Help': None,
                    'Report a bug': None,
                    'About': f"""
                    # {APP_CONFIG["name"]} v{APP_CONFIG["version"]}
                    
                    {APP_CONFIG["description"]}
                    
                    Created by: {APP_CONFIG["author"]}
                    
                    🙏 May this tool help you find peace and wisdom through the eternal teachings of the Bhagavad Gita.
                    """
                }
            )
            
            # Render header
            self.render_header()
            
            # Initialize systems
            self.initialize_systems()
            
            # Render sidebar (if initialized)
            if self.sidebar:
                self.sidebar.render()
            
            # Main content
            if st.session_state.initialized:
                self.render_main_content()
            else:
                st.error("⚠️ System not properly initialized. Please refresh the page.")
                if st.button("🔄 Retry Initialization"):
                    st.session_state.initialized = False
                    st.rerun()
            
        except Exception as e:
            self.logger.error(f"❌ Critical error in main app: {e}")
            st.error(f"Application error: {str(e)}")
            st.info("Please refresh the page to restart the application.")


# Main application instance
def create_main_interface() -> MainInterface:
    """Create main interface instance"""
    return MainInterface()

