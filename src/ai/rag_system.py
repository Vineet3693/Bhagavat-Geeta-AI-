
"""
RAG (Retrieval-Augmented Generation) system for Bhagavad Gita AI
"""
import pandas as pd
from typing import Dict, List, Tuple, Optional
import logging
from src.data.loader import GitaDataLoader
from src.data.embedder import GitaEmbedder
from src.ai.groq_engine import GitaGroqEngine
from config.settings import DATA_CONFIG

class GitaRAGSystem:
    """Complete RAG system combining retrieval and generation"""
    
    def __init__(self, api_key: str = None):
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.data_loader = GitaDataLoader()
        self.embedder = GitaEmbedder()
        self.ai_engine = GitaGroqEngine(api_key)
        
        # Data containers
        self.gita_df: Optional[pd.DataFrame] = None
        self.categories: Optional[Dict] = None
        self.sample_questions: Optional[List] = None
        
        # Initialize system
        self._initialize_system()
    
    def _initialize_system(self):
        """Initialize the RAG system"""
        try:
            self.logger.info("🚀 Initializing Bhagavad Gita RAG System...")
            
            # Load data
            self.gita_df = self.data_loader.load_gita_data()
            self.categories = self.data_loader.load_categories()
            self.sample_questions = self.data_loader.load_sample_questions()
            
            # Setup embeddings
            self.embedder.generate_embeddings(self.gita_df)
            
            # Try to load existing FAISS index
            try:
                self.embedder.load_faiss_index()
            except:
                # Create new index if not found
                self.embedder.create_faiss_index()
            
            self.logger.info("✅ RAG System initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing RAG system: {e}")
            raise
    
    def process_question(
        self, 
        question: str,
        response_type: str = "general",
        num_verses: int = None,
        user_context: Dict = None,
        voice_mode: bool = False
    ) -> Dict:
        """
        Main function to process a question through the RAG pipeline
        
        Args:
            question: User's question
            response_type: Type of response (philosophical, practical, etc.)
            num_verses: Number of verses to retrieve
            user_context: Additional user context
            voice_mode: Whether to optimize for voice output
            
        Returns:
            Complete response with metadata
        """
        
        if num_verses is None:
            num_verses = DATA_CONFIG["max_search_results"]
        
        try:
            self.logger.info(f"Processing question: {question[:50]}...")
            
            # Step 1: Retrieve relevant verses
            relevant_verses = self.retrieve_relevant_verses(question, num_verses)
            
            # Step 2: Generate AI response
            ai_response = self.ai_engine.generate_response(
                question=question,
                relevant_verses=relevant_verses,
                response_type=response_type,
                user_context=user_context,
                voice_mode=voice_mode
            )
            
            # Step 3: Combine results
            complete_response = {
                "question": question,
                "retrieval_results": {
                    "verses_found": len(relevant_verses),
                    "relevant_verses": relevant_verses
                },
                "ai_response": ai_response,
                "metadata": {
                    "response_type": response_type,
                    "voice_mode": voice_mode,
                    "timestamp": pd.Timestamp.now().isoformat(),
                    "system_version": "1.0.0"
                }
            }
            
            self.logger.info("✅ Question processed successfully")
            return complete_response
            
        except Exception as e:
            self.logger.error(f"❌ Error processing question: {e}")
            return self._get_error_response(question, str(e))
    
    def retrieve_relevant_verses(self, question: str, k: int = 5) -> List[Dict]:
        """
        Retrieve relevant verses using semantic search
        
        Args:
            question: User's question
            k: Number of verses to retrieve
            
        Returns:
            List of relevant verses with metadata
        """
        
        try:
            # Use embedder for semantic search
            search_results = self.embedder.search_similar(question, k)
            
            # Convert search results to verse data
            relevant_verses = []
            for text, similarity_score in search_results:
                # Extract verse information from the combined text
                verse_info = self._extract_verse_info_from_text(text, similarity_score)
                if verse_info:
                    relevant_verses.append(verse_info)
            
            # If no good matches found, get some default verses
            if len(relevant_verses) == 0 or all(v["similarity_score"] < DATA_CONFIG["similarity_threshold"] for v in relevant_verses):
                relevant_verses.extend(self._get_default_verses(question))
            
            return relevant_verses[:k]
            
        except Exception as e:
            self.logger.error(f"❌ Error retrieving verses: {e}")
            return self._get_default_verses(question)
    
    def _extract_verse_info_from_text(self, text: str, similarity_score: float) -> Optional[Dict]:
        """Extract verse information from search result text"""
        
        try:
            # Parse the combined text to extract verse information
            lines = text.strip().split('\n')
            verse_info = {"similarity_score": similarity_score}
            
            for line in lines:
                line = line.strip()
                if line.startswith('Chapter ') and ', Verse ' in line:
                    parts = line.replace('Chapter ', '').replace(', Verse ', '.').split('.')
                    if len(parts) >= 2:
                        verse_info['chapter'] = int(parts[0])
                        verse_info['verse'] = int(parts[1])
                elif line.startswith('Sanskrit: '):
                    verse_info['sanskrit'] = line.replace('Sanskrit: ', '')
                elif line.startswith('Hindi: '):
                    verse_info['hindi'] = line.replace('Hindi: ', '')
                elif line.startswith('English: '):
                    verse_info['english'] = line.replace('English: ', '')
                elif line.startswith('Theme: '):
                    verse_info['theme'] = line.replace('Theme: ', '')
                elif line.startswith('Keywords: '):
                    verse_info['keywords'] = line.replace('Keywords: ', '')
            
            # Validate that we have minimum required info
            if 'chapter' in verse_info and 'verse' in verse_info:
                return verse_info
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Error extracting verse info: {e}")
            return None
    
    def _get_default_verses(self, question: str) -> List[Dict]:
        """Get default verses when search doesn't return good results"""
        
        # Some universally relevant verses
        default_verses = [
            {"chapter": 2, "verse": 47},  # Karma Yoga
            {"chapter": 18, "verse": 66}, # Surrender
            {"chapter": 4, "verse": 7},   # Divine incarnation
            {"chapter": 7, "verse": 1}    # Knowledge
        ]
        
        result_verses = []
        for verse_ref in default_verses:
            verse_data = self.data_loader.get_verse_by_id(
                verse_ref["chapter"], verse_ref["verse"]
            )
            if verse_data:
                verse_data["similarity_score"] = 0.5  # Default similarity
                result_verses.append(verse_data)
        
        return result_verses
    
    def _get_error_response(self, question: str, error: str) -> Dict:
        """Generate error response"""
        return {
            "question": question,
            "retrieval_results": {"verses_found": 0, "relevant_verses": []},
            "ai_response": {
                "status": "error",
                "response": {
                    "main_response": f"I apologize, but I encountered an error while processing your question: '{question}'. Please try again with a simpler question or check the system configuration.",
                    "referenced_verses": [],
                    "response_type": "error"
                },
                "error": error
            },
            "metadata": {
                "response_type": "error",
                "timestamp": pd.Timestamp.now().isoformat(),
                "error": error
            }
        }
    
    def get_verses_by_category(self, category: str, limit: int = 10) -> List[Dict]:
        """Get verses by category/theme"""
        try:
            verses_df = self.data_loader.get_verses_by_theme(category)
            return verses_df.head(limit).to_dict('records')
        except Exception as e:
            self.logger.error(f"❌ Error getting verses by category: {e}")
            return []
    
    def get_random_verse(self) -> Dict:
        """Get a random verse for daily wisdom"""
        try:
            if self.gita_df is not None and not self.gita_df.empty:
                random_verse = self.gita_df.sample(1).iloc[0].to_dict()
                return random_verse
            return {}
        except Exception as e:
            self.logger.error(f"❌ Error getting random verse: {e}")
            return {}
    
    def get_suggested_questions(self, category: str = None) -> List[Dict]:
        """Get suggested questions, optionally filtered by category"""
        if category:
            return [q for q in self.sample_questions if q.get("category") == category]
        return self.sample_questions
    
    def get_categories(self) -> Dict:
        """Get available question categories"""
        return self.categories
    
    def search_verses(self, query: str, search_field: str = "all") -> List[Dict]:
        """
        Search verses by text content
        
        Args:
            query: Search query
            search_field: Field to search in (all, sanskrit, hindi, english, theme)
            
        Returns:
            List of matching verses
        """
        try:
            if self.gita_df is None:
                return []
            
            query_lower = query.lower()
            
            if search_field == "all":
                mask = (
                    self.gita_df['sanskrit'].str.lower().str.contains(query_lower, na=False) |
                    self.gita_df['hindi'].str.lower().str.contains(query_lower, na=False) |
                    self.gita_df['english'].str.lower().str.contains(query_lower, na=False) |
                    self.gita_df['theme'].str.lower().str.contains(query_lower, na=False) |
                    self.gita_df['keywords'].str.lower().str.contains(query_lower, na=False)
                )
            else:
                if search_field in self.gita_df.columns:
                    mask = self.gita_df[search_field].str.lower().str.contains(query_lower, na=False)
                else:
                    return []
            
            results = self.gita_df[mask].to_dict('records')
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Error searching verses: {e}")
            return []


# Utility function for easy import
def create_rag_system(api_key: str = None) -> GitaRAGSystem:
    """
    Create and initialize RAG system
    
    Args:
        api_key: Groq API key
        
    Returns:
        Initialized GitaRAGSystem
    """
    return GitaRAGSystem(api_key)
