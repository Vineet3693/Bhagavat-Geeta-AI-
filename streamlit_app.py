
import streamlit as st
import os
from typing import Dict, List

# Configure page
st.set_page_config(
    page_title="🕉️ Bhagavad Gita AI",
    page_icon="🕉️",
    layout="wide"
)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Get API key
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "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")

# Mock Gita data (no external files needed)
GITA_VERSES = {
    "2.47": {
        "sanskrit": "कर्मण्येवाधिकारस्ते मा फलेषु कदाचन। मा कर्मफलहेतुर्भूर्मा ते सङ्गोऽस्त्वकर्मणि॥",
        "english": "You have a right to perform your prescribed duty, but never to the fruits of action. Never consider yourself the cause of the results of your activities, and never be attached to not doing your duty.",
        "hindi": "तुम्हारा अधिकार केवल कर्म में है, फल में कभी नहीं। इसलिए तुम कर्मफल के हेतु मत बनो और तुम्हारी कर्म न करने में भी आसक्ति न हो।",
        "theme": "Karma Yoga",
        "chapter": 2,
        "verse": 47
    },
    "4.7": {
        "sanskrit": "यदा यदा हि धर्मस्य ग्लानिर्भवति भारत। अभ्युत्थानमधर्मस्य तदात्मानं सृजाम्यहम्॥",
        "english": "Whenever there is a decline in righteousness and an increase in unrighteousness, O Arjuna, at that time I manifest myself on earth.",
        "hindi": "हे भारत! जब-जब धर्म की हानि और अधर्म की वृद्धि होती है, तब-तब मैं अपने रूप को रचता हूँ।",
        "theme": "Divine Incarnation",
        "chapter": 4,
        "verse": 7
    },
    "18.66": {
        "sanskrit": "सर्वधर्मान्परित्यज्य मामेकं शरणं व्रज। अहं त्वां सर्वपापेभ्यो मोक्षयिष्यामि मा शुचः॥",
        "english": "Abandon all varieties of dharma and just surrender unto me. I shall deliver you from all sinful reactions. Do not fear.",
        "hindi": "सब धर्मों को छोड़कर तू केवल मेरी शरण में आ जा। मैं तुझे सम्पूर्ण पापों से मुक्त कर दूँगा, तू शोक मत कर।",
        "theme": "Surrender",
        "chapter": 18,
        "verse": 66
    },
    "2.20": {
        "sanskrit": "न जायते म्रियते वा कदाचिन्नायं भूत्वा भविता वा न भूयः। अजो नित्यः शाश्वतोऽयं पुराणो न हन्यते हन्यमाने शरीरे॥",
        "english": "For the soul there is neither birth nor death. It is not slain when the body is slain.",
        "hindi": "आत्मा का न तो जन्म होता है और न मृत्यु। शरीर के नष्ट होने पर आत्मा नष्ट नहीं होती।",
        "theme": "Soul",
        "chapter": 2,
        "verse": 20
    },
    "3.21": {
        "sanskrit": "यद्यदाचरति श्रेष्ठस्तत्तदेवेतरो जनः। स यत्प्रमाणं कुरुते लोकस्तदनुवर्तते॥",
        "english": "Whatever action a great man performs, common men follow. And whatever standards he sets by exemplary acts, all the world pursues.",
        "hindi": "श्रेष्ठ पुरुष जो कुछ आचरण करता है, अन्य मनुष्य भी वैसा ही आचरण करते हैं।",
        "theme": "Leadership",
        "chapter": 3,
        "verse": 21
    }
}

# Simple AI response function
def get_ai_response(question: str, relevant_verse: Dict) -> str:
    """Generate AI response using Groq API or mock response"""
    
    if GROQ_API_KEY == "xyz":
        # Mock response for testing
        return f"""Based on your question about "{question}", the Bhagavad Gita teaches us through Chapter {relevant_verse['chapter']}, Verse {relevant_verse['verse']}:

**Key Teaching:** {relevant_verse['theme']}

{relevant_verse['english']}

**Practical Application:** 
This verse guides us to understand that {relevant_verse['theme'].lower()} is essential for spiritual growth. In your daily life, you can apply this wisdom by focusing on righteous action without attachment to results.

**Reflection:** 
The eternal wisdom of the Gita reminds us that true peace comes from understanding our dharma (righteous duty) and performing it with devotion and detachment."""
    
    try:
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)
        
        prompt = f"""You are a wise spiritual guide well-versed in the Bhagavad Gita. A seeker has asked: "{question}"

Here's a relevant verse from the Gita:
Chapter {relevant_verse['chapter']}, Verse {relevant_verse['verse']}
Sanskrit: {relevant_verse['sanskrit']}
English: {relevant_verse['english']}
Theme: {relevant_verse['theme']}

Provide a compassionate, wise response that:
1. Addresses their question directly
2. Explains how this verse applies to their situation
3. Offers practical guidance for daily life
4. Maintains the spiritual depth of the original teachings

Keep the response warm, accessible, and around 200-300 words."""

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        # Fallback to mock response
        return f"""I understand your question about "{question}". The Bhagavad Gita offers timeless wisdom through Chapter {relevant_verse['chapter']}, Verse {relevant_verse['verse']}:

"{relevant_verse['english']}"

This teaches us about {relevant_verse['theme'].lower()}. In practical terms, this means approaching life's challenges with wisdom, performing our duties with dedication while remaining detached from outcomes.

The Gita's message is always relevant - whether dealing with personal struggles, relationships, or finding purpose, these teachings provide a foundation for righteous living and inner peace."""

# Function to find relevant verse based on question
def find_relevant_verse(question: str) -> Dict:
    """Find the most relevant verse based on the question"""
    question_lower = question.lower()
    
    # Simple keyword matching
    if any(word in question_lower for word in ['work', 'job', 'duty', 'action', 'result']):
        return GITA_VERSES["2.47"]
    elif any(word in question_lower for word in ['god', 'divine', 'incarnation', 'avatar']):
        return GITA_VERSES["4.7"]
    elif any(word in question_lower for word in ['surrender', 'devotion', 'faith', 'trust']):
        return GITA_VERSES["18.66"]
    elif any(word in question_lower for word in ['soul', 'death', 'life', 'eternal', 'birth']):
        return GITA_VERSES["2.20"]
    elif any(word in question_lower for word in ['leadership', 'example', 'influence', 'guide']):
        return GITA_VERSES["3.21"]
    else:
        # Default to karma yoga verse
        return GITA_VERSES["2.47"]

# Custom CSS
st.markdown("""
<style>
.main {
    background: linear-gradient(135deg, #0f1419 0%, #1a1f2e 100%);
}
.stTitle {
    color: #ff6b35;
    text-align: center;
    font-size: 3rem;
    margin-bottom: 2rem;
}
.verse-container {
    background: linear-gradient(135deg, #2d1b35 0%, #3d2b45 100%);
    border: 1px solid #9b59b6;
    border-radius: 10px;
    padding: 1.5rem;
    margin: 1rem 0;
}
.sanskrit-text {
    color: #f39c12;
    font-size: 1.2rem;
    text-align: center;
    margin-bottom: 1rem;
    font-weight: bold;
}
.english-text {
    color: #ecf0f1;
    font-size: 1rem;
    text-align: center;
    font-style: italic;
    margin-bottom: 1rem;
}
.hindi-text {
    color: #3498db;
    font-size: 1rem;
    text-align: center;
    margin-bottom: 1rem;
}
.gita-response {
    background: linear-gradient(135deg, #1a1f2e 0%, #252a3a 100%);
    border-left: 4px solid #ff6b35;
    padding: 1.5rem;
    border-radius: 0 10px 10px 0;
    margin: 1rem 0;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# Header
st.title("🕉️ Bhagavad Gita AI")
st.markdown("### Your AI Guide to Ancient Wisdom for Modern Life")

# Sidebar
with st.sidebar:
    st.markdown("## 🙏 About")
    st.info("This AI brings the eternal wisdom of the Bhagavad Gita to help you navigate modern life challenges with ancient spiritual guidance.")
    
    st.markdown("## 📖 Sample Questions")
    sample_questions = [
        "How do I find peace in stressful situations?",
        "What is my purpose in life?",
        "How should I handle difficult relationships?",
        "How do I overcome fear and anxiety?",
        "What does the Gita say about success and failure?"
    ]
    
    for q in sample_questions:
        if st.button(q, key=f"sample_{hash(q)}"):
            st.session_state.current_question = q

# Main interface
if "current_question" not in st.session_state:
    st.session_state.current_question = ""

question = st.text_input(
    "Ask your question about life, dharma, spirituality, or any challenge you're facing:",
    value=st.session_state.current_question,
    placeholder="e.g., How can I find peace in difficult times?"
)

col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    if st.button("🚀 Get Wisdom", type="primary"):
        if question.strip():
            with st.spinner("🤔 Contemplating your question..."):
                # Find relevant verse
                relevant_verse = find_relevant_verse(question)
                
                # Generate AI response
                ai_response = get_ai_response(question, relevant_verse)
                
                # Display response
                st.markdown("### 🧘‍♀️ Wisdom from the Gita")
                st.markdown(f'<div class="gita-response">{ai_response}</div>', unsafe_allow_html=True)
                
                # Display the verse
                st.markdown("### 📜 Referenced Verse")
                verse_html = f"""
                <div class="verse-container">
                    <div style="text-align: center; margin-bottom: 1rem; color: #e74c3c; font-weight: bold;">
                        Chapter {relevant_verse['chapter']}, Verse {relevant_verse['verse']}
                    </div>
                    <div class="sanskrit-text">{relevant_verse['sanskrit']}</div>
                    <div class="hindi-text">{relevant_verse['hindi']}</div>
                    <div class="english-text">{relevant_verse['english']}</div>
                    <div style="text-align: center; margin-top: 1rem; color: #95a5a6;">
                        Theme: {relevant_verse['theme']}
                    </div>
                </div>
                """
                st.markdown(verse_html, unsafe_allow_html=True)
        else:
            st.warning("Please enter a question to receive guidance.")

with col2:
    if st.button("🎲 Random Verse"):
        import random
        verse_key = random.choice(list(GITA_VERSES.keys()))
        verse = GITA_VERSES[verse_key]
        
        st.markdown("### 🎲 Today's Wisdom")
        verse_html = f"""
        <div class="verse-container">
            <div style="text-align: center; margin-bottom: 1rem; color: #e74c3c; font-weight: bold;">
                Chapter {verse['chapter']}, Verse {verse['verse']}
            </div>
            <div class="sanskrit-text">{verse['sanskrit']}</div>
            <div class="hindi-text">{verse['hindi']}</div>
            <div class="english-text">{verse['english']}</div>
            <div style="text-align: center; margin-top: 1rem; color: #95a5a6;">
                Theme: {verse['theme']}
            </div>
        </div>
        """
        st.markdown(verse_html, unsafe_allow_html=True)

with col3:
    if st.button("📚 All Verses"):
        st.markdown("### 📚 Bhagavad Gita Verses")
        for verse_key, verse_data in GITA_VERSES.items():
            with st.expander(f"Chapter {verse_data['chapter']}.{verse_data['verse']}: {verse_data['theme']}"):
                st.markdown(f"**Sanskrit:** {verse_data['sanskrit']}")
                st.markdown(f"**Hindi:** {verse_data['hindi']}")
                st.markdown(f"**English:** {verse_data['english']}")

# Footer
st.markdown("---")
st.markdown("### 🙏 May this wisdom guide you on your spiritual journey")
st.caption("Built with love and devotion • Powered by AI and ancient wisdom")

# API status
if GROQ_API_KEY == "xyz":
    st.warning("⚠️ Using mock responses. Add your Groq API key for AI-powered answers.")
else:
    st.success("✅ AI-powered responses active")
