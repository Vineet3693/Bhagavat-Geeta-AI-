
"""
Main Streamlit application for Bhagavad Gita AI
Entry point for the web application
"""

import os
import sys
import logging
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('gita_ai.log')
    ]
)

logger = logging.getLogger(__name__)

# Import main interface
try:
    from ui.main_interface import MainInterface
    
    def main():
        """Main application function"""
        
        try:
            # Create and run main interface
            app = MainInterface()
            app.run()
            
        except Exception as e:
            logger.error(f"❌ Critical application error: {e}")
            import streamlit as st
            st.error("🚨 Application Error")
            st.error(f"Error: {str(e)}")
            st.info("Please check your configuration and try refreshing the page.")
            
            # Show debug info in expander
            with st.expander("🐛 Debug Information"):
                st.code(f"Error: {str(e)}")
                st.code(f"Type: {type(e).__name__}")
                
                # Show traceback
                import traceback
                st.code(traceback.format_exc())
    
    # Run the application
    if __name__ == "__main__":
        main()

except ImportError as e:
    # Fallback if imports fail
    import streamlit as st
    
    st.error("🚨 Import Error")
    st.error(f"Failed to import required modules: {str(e)}")
    
    st.markdown("""
    ### 🔧 Setup Instructions
    
    It looks like the application is not properly set up. Please follow these steps:
    
    1. **Install Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```
    
    2. **Set up Environment Variables:**

    ```bash
    cp .env.example .env
    # Edit .env file with your Groq API key
    ```
    
    3. **Add Sample Data:**

    ```bash
    # Place your bhagavad_gita.csv file in the data/ folder
    ```
    
    4. **Run the Application:**

    ```bash
    streamlit run streamlit_app.py
    ```
    
    ### 📋 Required Files:
    - `requirements.txt` - Python dependencies
    - `data/bhagavad_gita.csv` - Gita verses dataset
    - `.env` - Environment variables (Groq API key)
    
    ### 🆘 Need Help?
    - Check the GitHub repository README
    - Ensure all files are in the correct structure
    - Verify your Python environment
    """)
