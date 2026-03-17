
"""
Groq AI engine for Bhagavad Gita responses
"""
import os
import asyncio
from typing import Dict, List, Optional, Tuple
import logging
from groq import Groq
from config.settings import GROQ_CONFIG, GROQ_API_KEY
import yaml
from pathlib import Path

class GitaGroqEngine:
    """Main AI engine using Groq for generating responses"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or GROQ_API_KEY
        self.client = None
        self.logger = logging.getLogger(__name__)
        self.prompts = self._load_prompts()
        
        # Initialize Groq client
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Groq client"""
        try:
            if self.api_key == "xyz":
                self.logger.warning("⚠️  Using placeholder API key 'api key'. Please set your real Groq API key.")
                # For development/testing, we'll create a mock client
                self.client = MockGroqClient()
            else:
                self.client = Groq(api_key=self.api_key)
            
            self.logger.info("✅ Groq client initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing Groq client: {e}")
            # Fallback to mock client for testing
            self.client = MockGroqClient()
    
    def _load_prompts(self) -> Dict:
        """Load system prompts from YAML file"""
        try:
            prompts_file = Path("config/prompts/system_prompts.yaml")
            if prompts_file.exists():
                with open(prompts_file, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
            else:
                return self._get_default_prompts()
                
        except Exception as e:
            self.logger.error(f"❌ Error loading prompts: {e}")
            return self._get_default_prompts()
    
    def _get_default_prompts(self) -> Dict:
        """Default system prompts"""
        return {
            "base_system_prompt": """You are a wise and compassionate Bhagavad Gita AI assistant. You have deep knowledge of the Bhagavad Gita, its teachings, and their practical applications in modern life.

Guidelines:
- Always be respectful and spiritual in your responses
- Reference specific verses when relevant  
- Provide practical applications of the teachings
- Maintain authenticity to the original philosophy
- Be accessible to both beginners and advanced seekers""",
            
            "philosophical_prompt": """You are a profound philosophical guide specializing in Bhagavad Gita wisdom. 
Provide deep, contemplative responses that explore the metaphysical and philosophical aspects of Krishna's teachings.
Reference classical commentaries when appropriate and connect concepts to broader Vedantic philosophy.""",
            
            "practical_prompt": """You are a practical spiritual counselor using Bhagavad Gita wisdom for modern life guidance.
Focus on actionable advice and real-world applications of the teachings.
Help users apply Krishna's wisdom to their daily challenges, relationships, and personal growth.""",
            
            "voice_optimized_prompt": """You are providing voice responses for a Bhagavad Gita AI. 
Keep responses conversational, well-paced for speech, and include natural pauses.
Avoid complex formatting and focus on clear, spoken delivery."""
        }
    
    def select_model(self, question_type: str = "general", user_preference: str = "balanced") -> str:
        """
        Select appropriate Groq model based on question type and user preference
        
        Args:
            question_type: Type of question (philosophical, practical, beginner, etc.)
            user_preference: User's preference (fast, balanced, creative)
            
        Returns:
            Model name to use
        """
        
        model_selection = {
            "philosophical": GROQ_CONFIG["default_model"],  # Use balanced model for philosophy
            "practical": "llama3-8b-8192",  # Fast model for practical advice
            "beginner": "llama3-8b-8192",  # Fast model for simple questions
            "creative": "mixtral-8x7b-32768",  # Creative model for interpretative answers
            "voice": "llama3-8b-8192"  # Fast model for voice responses
        }
        
        if user_preference == "fast":
            return "llama3-8b-8192"
        elif user_preference == "creative":
            return "mixtral-8x7b-32768"
        else:
            return model_selection.get(question_type, GROQ_CONFIG["default_model"])
    
    def generate_response(
        self, 
        question: str, 
        relevant_verses: List[Dict], 
        response_type: str = "general",
        user_context: Dict = None,
        voice_mode: bool = False
    ) -> Dict:
        """
        Generate AI response using Groq
        
        Args:
            question: User's question
            relevant_verses: List of relevant Gita verses
            response_type: Type of response (philosophical, practical, etc.)
            user_context: Additional user context
            voice_mode: Whether to optimize for voice output
            
        Returns:
            Dictionary containing the response and metadata
        """
        
        try:
            # Select appropriate model and prompt
            model = self.select_model(
                response_type if not voice_mode else "voice",
                user_context.get("preference", "balanced") if user_context else "balanced"
            )
            
            prompt_key = "voice_optimized_prompt" if voice_mode else f"{response_type}_prompt"
            system_prompt = self.prompts.get(prompt_key, self.prompts["base_system_prompt"])
            
            # Format relevant verses
            verses_context = self._format_verses_for_context(relevant_verses)
            
            # Create user message
            user_message = self._create_user_message(question, verses_context, voice_mode)
            
            # Generate response
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=GROQ_CONFIG["temperature"],
                max_tokens=GROQ_CONFIG["max_tokens"],
                top_p=0.9,
                stream=False
            )
            
            # Extract and process response
            ai_response = response.choices[0].message.content
            
            # Format response
            formatted_response = self._format_response(
                ai_response, relevant_verses, response_type, voice_mode
            )
            
            return {
                "status": "success",
                "response": formatted_response,
                "model_used": model,
                "verses_referenced": len(relevant_verses),
                "response_type": response_type,
                "voice_optimized": voice_mode
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error generating response: {e}")
            return {
                "status": "error",
                "response": self._get_fallback_response(question),
                "error": str(e)
            }
    
    def _format_verses_for_context(self, verses: List[Dict]) -> str:
        """Format verses for inclusion in the prompt"""
        if not verses:
            return "No specific verses found, please provide general guidance from Bhagavad Gita wisdom."
        
        formatted_verses = []
        for verse in verses[:3]:  # Use top 3 most relevant verses
            formatted_verse = f"""
Verse {verse.get('chapter', 'Unknown')}.{verse.get('verse', 'Unknown')}:
Sanskrit: {verse.get('sanskrit', 'N/A')}
Hindi: {verse.get('hindi', 'N/A')}
English: {verse.get('english', 'N/A')}
Theme: {verse.get('theme', 'N/A')}
"""
            formatted_verses.append(formatted_verse.strip())
        
        return "\n\n".join(formatted_verses)
    
    def _create_user_message(self, question: str, verses_context: str, voice_mode: bool) -> str:
        """Create the user message for the AI"""
        
        base_message = f"""
Question: {question}

Relevant Verses from Bhagavad Gita:
{verses_context}

Please provide a comprehensive answer that:
1. Directly addresses the question
2. References the relevant verses appropriately
3. Explains the philosophical context
4. Provides practical applications for modern life
5. Maintains spiritual authenticity
"""
        
        if voice_mode:
            base_message += "\n6. Format the response for natural speech delivery with appropriate pauses"
        
        return base_message.strip()
    
    def _format_response(
        self, 
        ai_response: str, 
        verses: List[Dict], 
        response_type: str, 
        voice_mode: bool
    ) -> Dict:
        """Format the AI response with additional metadata"""
        
        return {
            "main_response": ai_response,
            "referenced_verses": [
                {
                    "verse_id": f"{v.get('chapter', 'Unknown')}.{v.get('verse', 'Unknown')}",
                    "sanskrit": v.get('sanskrit', ''),
                    "english": v.get('english', ''),
                    "hindi": v.get('hindi', '')
                }
                for v in verses[:3]
            ],
            "response_length": len(ai_response.split()),
            "estimated_reading_time": len(ai_response.split()) / 200,  # ~200 words per minute
            "response_type": response_type,
            "voice_optimized": voice_mode
        }
    
    def _get_fallback_response(self, question: str) -> Dict:
        """Provide fallback response when AI fails"""
        return {
            "main_response": f"""I apologize, but I'm currently unable to provide a detailed response to your question: "{question}". 

However, I can share this fundamental wisdom from the Bhagavad Gita: 

The essence of Krishna's teaching is to perform our duties with dedication while remaining detached from the results. As stated in verse 2.47: "You have a right to perform your prescribed duty, but never to the fruits of action."

This principle can be applied to most life situations - focus on doing your best in whatever role you have, whether as a student, professional, parent, or friend, while accepting whatever outcome arises with equanimity.

Please try asking your question again, or explore our suggested questions for more guidance.""",
            "referenced_verses": [
                {
                    "verse_id": "2.47",
                    "sanskrit": "कर्मण्येवाधिकारस्ते मा फलेषु कदाचन।",
                    "english": "You have a right to perform your prescribed duty, but never to the fruits of action.",
                    "hindi": "तुम्हारा अधिकार केवल कर्म में है, फल में कभी नहीं।"
                }
            ],
            "response_type": "fallback",
            "voice_optimized": False
        }
    
    async def generate_response_async(self, *args, **kwargs) -> Dict:
        """Async version of generate_response"""
        return await asyncio.get_event_loop().run_in_executor(
            None, self.generate_response, *args, **kwargs
        )


class MockGroqClient:
    """Mock Groq client for testing when API key is 'xyz'"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    @property
    def chat(self):
        return self
    
    @property  
    def completions(self):
        return self
        
    def create(self, **kwargs):
        """Mock response creation"""
        question = kwargs.get("messages", [{}])[-1].get("content", "")
        
        # Simple mock response based on keywords
        mock_response = self._generate_mock_response(question)
        
        # Return mock response object
        return MockResponse(mock_response)
    
    def _generate_mock_response(self, question: str) -> str:
        """Generate simple mock responses based on question keywords"""
        question_lower = question.lower()
        
        if "karma" in question_lower:
            return """According to the Bhagavad Gita, karma means action performed with awareness and without attachment to results. Krishna teaches Arjuna in verse 2.47 that we have the right to perform our duties, but not to the fruits of our actions.

This principle helps us:
1. Focus on the process rather than outcomes
2. Reduce anxiety about results
3. Perform actions with dedication and excellence
4. Develop equanimity in success and failure

In practical terms, whether you're studying, working, or serving others, give your best effort while accepting whatever results come with grace and learning."""
        
        elif "dharma" in question_lower:
            return """Dharma in the Bhagavad Gita refers to righteous duty and the path of moral and spiritual righteousness. It's the cosmic order that maintains harmony in the universe and our individual duty that aligns with this greater good.

Krishna explains that dharma is not just following rules, but understanding our role in the larger scheme of life and acting accordingly. This includes:
1. Our duties based on our stage of life (ashrama)
2. Our duties based on our nature and skills (varna)
3. Universal duties like truthfulness, non-violence, and compassion

When we align our actions with dharma, we contribute to universal harmony while growing spiritually."""
        
        else:
            return """The Bhagavad Gita offers timeless wisdom for navigating life's challenges. Krishna's teachings emphasize performing our duties with dedication while maintaining inner detachment from results.

Key principles include:
1. **Karma Yoga** - The path of selfless action
2. **Bhakti Yoga** - The path of devotion and love
3. **Jnana Yoga** - The path of knowledge and wisdom
4. **Dharma** - Living in harmony with cosmic order

These teachings help us find purpose, peace, and spiritual growth regardless of our external circumstances. The essence is to act with awareness, compassion, and surrender to the divine will."""
        
        # Add note about mock response
        mock_note = "\n\n*Note: This is a mock response for testing. Please set your Groq API key to get AI-powered responses.*"
        return mock_response + mock_note


class MockResponse:
    """Mock response object"""
    def __init__(self, content: str):
        self.choices = [MockChoice(content)]


class MockChoice:
    """Mock choice object"""
    def __init__(self, content: str):
        self.message = MockMessage(content)


class MockMessage:
    """Mock message object"""
    def __init__(self, content: str):
        self.content = content


# Utility function for easy import
def create_groq_engine(api_key: str = None) -> GitaGroqEngine:
    """
    Create and initialize Groq engine
    
    Args:
        api_key: Groq API key (defaults to environment variable)
        
    Returns:
        Initialized GitaGroqEngine
    """
    return GitaGroqEngine(api_key)
