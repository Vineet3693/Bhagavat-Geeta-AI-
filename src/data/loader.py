
"""
Data loading and preprocessing utilities for Bhagavad Gita AI
"""
import pandas as pd
import json
import pickle
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging
from config.settings import DATA_DIR, DATA_CONFIG

class GitaDataLoader:
    """Load and process Bhagavad Gita data"""
    
    def __init__(self, data_dir: Path = DATA_DIR):
        self.data_dir = Path(data_dir)
        self.logger = logging.getLogger(__name__)
        
        # Initialize data containers
        self.gita_df: Optional[pd.DataFrame] = None
        self.categories: Optional[Dict] = None
        self.sample_questions: Optional[List] = None
        
    def load_gita_data(self, filename: str = "bhagavad_gita.csv") -> pd.DataFrame:
        """
        Load Bhagavad Gita CSV data
        
        Args:
            filename: Name of the CSV file
            
        Returns:
            DataFrame with Gita verses
        """
        try:
            # Try different possible locations
            possible_files = [
                self.data_dir / filename,
                self.data_dir / "processed" / filename,
                self.data_dir / "raw" / filename,
                self.data_dir / "sample_bhagavad_gita.csv"  # Fallback
            ]
            
            file_path = None
            for path in possible_files:
                if path.exists():
                    file_path = path
                    break
            
            if not file_path:
                raise FileNotFoundError(f"Could not find Gita data file. Tried: {possible_files}")
            
            # Load CSV
            self.gita_df = pd.read_csv(file_path)
            
            # Validate required columns
            required_columns = ['chapter', 'verse', 'sanskrit', 'hindi', 'english', 'theme', 'keywords']
            missing_columns = [col for col in required_columns if col not in self.gita_df.columns]
            
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")
            
            # Clean and process data
            self.gita_df = self._clean_data(self.gita_df)
            
            self.logger.info(f"✅ Loaded {len(self.gita_df)} verses from {file_path}")
            return self.gita_df
            
        except Exception as e:
            self.logger.error(f"❌ Error loading Gita data: {e}")
            # Return sample data as fallback
            return self._create_sample_data()
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and preprocess the data"""
        
        # Remove any empty rows
        df = df.dropna(subset=['sanskrit', 'hindi', 'english'])
        
        # Clean text columns
        text_columns = ['sanskrit', 'hindi', 'english', 'theme', 'keywords']
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()
        
        # Create combined text for search
        df['combined_text'] = (
            df['sanskrit'] + ' ' + 
            df['hindi'] + ' ' + 
            df['english'] + ' ' + 
            df['theme'] + ' ' + 
            df['keywords']
        )
        
        # Create verse identifier
        df['verse_id'] = df['chapter'].astype(str) + '.' + df['verse'].astype(str)
        
        # Sort by chapter and verse
        df = df.sort_values(['chapter', 'verse']).reset_index(drop=True)
        
        return df
    
    def _create_sample_data(self) -> pd.DataFrame:
        """Create sample data if main file not found"""
        
        sample_data = [
            {
                'chapter': 1, 'verse': 1,
                'sanskrit': 'धृतराष्ट्र उवाच। धर्मक्षेत्रे कुरुक्षेत्रे समवेता युयुत्सवः।',
                'hindi': 'धृतराष्ट्र बोले- हे संजय! धर्मभूमि कुरुक्षेत्र में युद्ध की इच्छा वाले मेरे और पाण्डु के पुत्र एकत्रित होकर क्या कर रहे हैं?',
                'english': 'Dhritarashtra said: O Sanjaya, what did my sons and the sons of Pandu do when they assembled together on the holy field of Kurukshetra, eager for battle?',
                'theme': 'war,dharma,beginning',
                'keywords': 'dharma,war,kurukshetra,dhritarashtra,pandavas'
            },
            {
                'chapter': 2, 'verse': 47,
                'sanskrit': 'कर्मण्येवाधिकारस्ते मा फलेषु कदाचन। मा कर्मफलहेतुर्भूर्मा ते सङ्गोऽस्त्वकर्मणि॥',
                'hindi': 'तुम्हारा अधिकार केवल कर्म में है, फल में कभी नहीं। इसलिए तुम कर्मफल के हेतु मत बनो और तुम्हारी कर्म न करने में भी आसक्ति न हो।',
                'english': 'You have a right to perform your prescribed duty, but never to the fruits of action. Never consider yourself the cause of the results of your activities, and never be attached to not doing your duty.',
                'theme': 'karma,duty,detachment',
                'keywords': 'karma,duty,action,detachment,right'
            }
        ]
        
        df = pd.DataFrame(sample_data)
        return self._clean_data(df)
    
    def load_categories(self) -> Dict:
        """Load question categories"""
        try:
            categories_file = self.data_dir / "categories.json"
            
            if categories_file.exists():
                with open(categories_file, 'r', encoding='utf-8') as f:
                    self.categories = json.load(f)
            else:
                # Save default categories
                with open(categories_file, 'w', encoding='utf-8') as f:
                    json.dump(self.categories, f, indent=2, ensure_ascii=False)
            
            return self.categories
            
        except Exception as e:
            self.logger.error(f"❌ Error loading categories: {e}")
            return self._create_default_categories()
    
    def _create_default_categories(self) -> Dict:
        """Create default question categories"""
        return {
            "dharma_ethics": {
                "title": "Dharma & Ethics",
                "description": "Questions about righteous duty and moral principles",
                "icon": "⚖️",
                "questions": [
                    "What is dharma according to the Gita?",
                    "How do I know what is right and wrong?",
                    "What should I do when duty conflicts with desire?"
                ]
            },
            "karma_action": {
                "title": "Karma & Action",
                "description": "Understanding action, duty, and selfless service",
                "icon": "🎯",
                "questions": [
                    "What is the meaning of Karma Yoga?",
                    "How can I work without attachment to results?",
                    "What does 'right to action, not results' mean?"
                ]
            },
            "life_purpose": {
                "title": "Life Purpose & Meaning",
                "description": "Finding your path and purpose in life",
                "icon": "🌟",
                "questions": [
                    "What is the purpose of human life?",
                    "How do I find my life's mission?",
                    "What is self-realization?"
                ]
            },
            "relationships": {
                "title": "Relationships & Society",
                "description": "Navigating relationships and social duties",
                "icon": "👥",
                "questions": [
                    "How should I treat difficult people?",
                    "What are my duties to family and society?",
                    "How do I balance personal needs with others' needs?"
                ]
            },
            "spiritual_growth": {
                "title": "Spiritual Growth",
                "description": "Meditation, devotion, and spiritual practices",
                "icon": "🧘",
                "questions": [
                    "How do I practice meditation according to the Gita?",
                    "What is bhakti yoga?",
                    "How can I develop spiritual discipline?"
                ]
            },
            "practical_wisdom": {
                "title": "Practical Wisdom",
                "description": "Applying Gita teachings in daily life",
                "icon": "💡",
                "questions": [
                    "How do I stay calm under pressure?",
                    "What does the Gita say about success and failure?",
                    "How do I overcome fear and anxiety?"
                ]
            }
        }
    
    def load_sample_questions(self) -> List[Dict]:
        """Load sample questions for UI"""
        try:
            questions_file = self.data_dir / "sample_questions.json"
            
            if questions_file.exists():
                with open(questions_file, 'r', encoding='utf-8') as f:
                    self.sample_questions = json.load(f)
            else:
                self.sample_questions = self._create_sample_questions()
                # Save for future use
                with open(questions_file, 'w', encoding='utf-8') as f:
                    json.dump(self.sample_questions, f, indent=2, ensure_ascii=False)
            
            return self.sample_questions
            
        except Exception as e:
            self.logger.error(f"❌ Error loading sample questions: {e}")
            return self._create_sample_questions()
    
    def _create_sample_questions(self) -> List[Dict]:
        """Create sample questions for the UI"""
        return [
            {
                "question": "What is the main message of the Bhagavad Gita?",
                "category": "life_purpose",
                "difficulty": "beginner",
                "tags": ["overview", "philosophy", "purpose"]
            },
            {
                "question": "How can I work without being attached to results?",
                "category": "karma_action", 
                "difficulty": "intermediate",
                "tags": ["karma", "detachment", "work"]
            },
            {
                "question": "What should I do when my duty conflicts with my personal desires?",
                "category": "dharma_ethics",
                "difficulty": "intermediate",
                "tags": ["dharma", "conflict", "duty"]
            },
            {
                "question": "How do I overcome fear and anxiety according to Krishna?",
                "category": "practical_wisdom",
                "difficulty": "beginner",
                "tags": ["fear", "anxiety", "peace"]
            },
            {
                "question": "What is the difference between the soul and the body?",
                "category": "spiritual_growth",
                "difficulty": "intermediate",
                "tags": ["soul", "body", "philosophy"]
            }
        ]
    
    def get_verses_by_theme(self, theme: str) -> pd.DataFrame:
        """Get verses by specific theme"""
        if self.gita_df is None:
            self.load_gita_data()
        
        return self.gita_df[
            self.gita_df['theme'].str.contains(theme, case=False, na=False) |
            self.gita_df['keywords'].str.contains(theme, case=False, na=False)
        ]
    
    def get_verse_by_id(self, chapter: int, verse: int) -> Optional[Dict]:
        """Get specific verse by chapter and verse number"""
        if self.gita_df is None:
            self.load_gita_data()
        
        result = self.gita_df[
            (self.gita_df['chapter'] == chapter) & 
            (self.gita_df['verse'] == verse)
        ]
        
        if not result.empty:
            return result.iloc[0].to_dict()
        return None
    
    def save_processed_data(self, output_dir: Path = None):
        """Save processed data for faster loading"""
        if output_dir is None:
            output_dir = self.data_dir / "processed"
        
        output_dir.mkdir(exist_ok=True)
        
        # Save processed DataFrame
        if self.gita_df is not None:
            self.gita_df.to_csv(output_dir / "bhagavad_gita.csv", index=False)
        
        # Save categories
        if self.categories is not None:
            with open(output_dir / "categories.json", 'w', encoding='utf-8') as f:
                json.dump(self.categories, f, indent=2, ensure_ascii=False)
        
        # Save sample questions
        if self.sample_questions is not None:
            with open(output_dir / "sample_questions.json", 'w', encoding='utf-8') as f:
                json.dump(self.sample_questions, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"✅ Saved processed data to {output_dir}")


# Utility function for easy import
def load_gita_data() -> Tuple[pd.DataFrame, Dict, List[Dict]]:
    """
    Convenience function to load all Gita data
    
    Returns:
        Tuple of (gita_dataframe, categories, sample_questions)
    """
    loader = GitaDataLoader()
    
    gita_df = loader.load_gita_data()
    categories = loader.load_categories() 
    sample_questions = loader.load_sample_questions()
    
    return gita_df, categories, sample_questions
