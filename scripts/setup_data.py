
"""
Script to set up and validate data for Bhagavad Gita AI
Run this script first to ensure all data is properly configured
"""

import pandas as pd
import json
from pathlib import Path
import logging
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.data.loader import GitaDataLoader
from src.data.embedder import GitaEmbedder

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_sample_data():
    """Create sample Gita data if none exists"""
    
    data_dir = project_root / "data"
    data_dir.mkdir(exist_ok=True)
    
    # Sample Bhagavad Gita data
    sample_data = [
        {
            "chapter": 1, "verse": 1,
            "sanskrit": "धृतराष्ट्र उवाच। धर्मक्षेत्रे कुरुक्षेत्रे समवेता युयुत्सवः। मामकाः पाण्डवाश्चैव किमकुर्वत सञ्जय॥",
            "hindi": "धृतराष्ट्र बोले- हे संजय! धर्मभूमि कुरुक्षेत्र में युद्ध की इच्छा वाले मेरे और पाण्डु के पुत्र एकत्रित होकर क्या कर रहे हैं?",
            "english": "Dhritarashtra said: O Sanjaya, what did my sons and the sons of Pandu do when they assembled together on the holy field of Kurukshetra, eager for battle?",
            "theme": "war,dharma,beginning",
            "keywords": "dharma,war,kurukshetra,dhritarashtra,pandavas"
        },
        {
            "chapter": 2, "verse": 47,
            "sanskrit": "कर्मण्येवाधिकारस्ते मा फलेषु कदाचन। मा कर्मफलहेतुर्भूर्मा ते सङ्गोऽस्त्वकर्मणि॥",
            "hindi": "तुम्हारा अधिकार केवल कर्म में है, फल में कभी नहीं। इसलिए तुम कर्मफल के हेतु मत बनो और तुम्हारी कर्म न करने में भी आसक्ति न हो।",
            "english": "You have a right to perform your prescribed duty, but never to the fruits of action. Never consider yourself the cause of the results of your activities, and never be attached to not doing your duty.",
            "theme": "karma,duty,detachment",
            "keywords": "karma,duty,action,detachment,right"
        },
        {
            "chapter": 4, "verse": 7,
            "sanskrit": "यदा यदा हि धर्मस्य ग्लानिर्भवति भारत। अभ्युत्थानमधर्मस्य तदात्मानं सृजाम्यहम्॥",
            "hindi": "हे भारत! जब-जब धर्म की हानि और अधर्म की वृद्धि होती है, तब-तब मैं अपने रूप को रचता हूँ अर्थात् अवतार लेता हूँ।",
            "english": "Whenever there is a decline in righteousness and an increase in unrighteousness, O Arjuna, at that time I manifest myself on earth.",
            "theme": "divine,incarnation,righteousness",
            "keywords": "divine,avatar,dharma,righteousness,krishna"
        },
        {
            "chapter": 18, "verse": 66,
            "sanskrit": "सर्वधर्मान्परित्यज्य मामेकं शरणं व्रज। अहं त्वां सर्वपापेभ्यो मोक्षयिष्यामि मा शुचः॥",
            "hindi": "सब धर्मों को छोड़कर तू केवल मेरी शरण में आ जा। मैं तुझे सम्पूर्ण पापों से मुक्त कर दूँगा, तू शोक मत कर।",
            "english": "Abandon all varieties of dharma and just surrender unto me. I shall deliver you from all sinful reactions. Do not fear.",
            "theme": "surrender,liberation,devotion",
            "keywords": "surrender,moksha,liberation,devotion,fearlessness"
        }
    ]
    
    # Create CSV file
    df = pd.DataFrame(sample_data)
    csv_path = data_dir / "bhagavad_gita.csv"
    df.to_csv(csv_path, index=False)
    
    logger.info(f"✅ Created sample data: {csv_path}")
    return csv_path

def validate_data():
    """Validate the Gita data"""
    
    try:
        loader = GitaDataLoader()
        df = loader.load_gita_data()
        
        logger.info(f"✅ Data validation passed: {len(df)} verses loaded")
        
        # Check required columns
        required_cols = ['chapter', 'verse', 'sanskrit', 'hindi', 'english', 'theme', 'keywords']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            logger.error(f"❌ Missing columns: {missing_cols}")
            return False
        
        logger.info("✅ All required columns present")
        return True
        
    except Exception as e:
        logger.error(f"❌ Data validation failed: {e}")
        return False

def setup_embeddings():
    """Generate embeddings for the data"""
    
    try:
        # Load data
        loader = GitaDataLoader()
        df = loader.load_gita_data()
        
        # Generate embeddings
        embedder = GitaEmbedder()
        embeddings = embedder.generate_embeddings(df, force_regenerate=True)
        
        # Create FAISS index
        embedder.create_faiss_index(embeddings)
        
        logger.info("✅ Embeddings and search index created successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Embedding setup failed: {e}")
        return False

def main():
    """Main setup function"""
    
    logger.info("🚀 Setting up Bhagavad Gita AI...")
    
    # 1. Check/create data directory
    data_dir = project_root / "data"
    if not data_dir.exists():
        data_dir.mkdir()
        logger.info("📁 Created data directory")
    
    # 2. Check for existing data or create sample
    csv_files = list(data_dir.glob("*.csv"))
    if not csv_files:
        logger.info("📊 No CSV data found, creating sample data...")
        setup_sample_data()
    
    # 3. Validate data
    if not validate_data():
        logger.error("❌ Data validation failed. Please check your CSV file.")
        return False
    
    # 4. Setup embeddings
    logger.info("🧠 Setting up embeddings...")
    if not setup_embeddings():
        logger.error("❌ Embedding setup failed.")
        return False
    
    # 5. Create processed directory structure
    processed_dir = data_dir / "processed"
    processed_dir.mkdir(exist_ok=True)
    
    logger.info("✅ Setup completed successfully!")
    logger.info("🚀 You can now run: streamlit run streamlit_app.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
