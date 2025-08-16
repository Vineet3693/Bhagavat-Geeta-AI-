"""
Text embedding generation for semantic search
"""
import numpy as np
import pandas as pd
import pickle
from pathlib import Path
from typing import List, Optional, Tuple
import logging
from sentence_transformers import SentenceTransformer
import faiss
from config.settings import DATA_DIR, DATA_CONFIG

class GitaEmbedder:
    """Generate and manage embeddings for Gita verses"""
    
    def __init__(self, model_name: str = None):
        self.model_name = model_name or DATA_CONFIG["embedding_model"]
        self.model = None
        self.embeddings = None
        self.index = None
        self.texts = []
        self.logger = logging.getLogger(__name__)
        
        # File paths
        self.embeddings_file = DATA_DIR / "processed" / "embeddings.pkl"
        self.index_file = DATA_DIR / "processed" / "faiss_index.index"
        
    def load_model(self):
        """Load the embedding model"""
        try:
            self.logger.info(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            self.logger.info("✅ Embedding model loaded successfully")
        except Exception as e:
            self.logger.error(f"❌ Error loading embedding model: {e}")
            raise
    
    def generate_embeddings(self, gita_df: pd.DataFrame, force_regenerate: bool = False) -> np.ndarray:
        """
        Generate embeddings for Gita verses
        
        Args:
            gita_df: DataFrame containing Gita verses
            force_regenerate: Whether to regenerate even if cached embeddings exist
            
        Returns:
            Array of embeddings
        """
        
        # Check if cached embeddings exist
        if not force_regenerate and self.embeddings_file.exists():
            return self.load_embeddings()
        
        if self.model is None:
            self.load_model()
        
        try:
            # Prepare texts for embedding
            self.texts = self._prepare_texts(gita_df)
            
            self.logger.info(f"Generating embeddings for {len(self.texts)} verses...")
            
            # Generate embeddings
            self.embeddings = self.model.encode(
                self.texts,
                convert_to_numpy=True,
                show_progress_bar=True
            )
            
            # Save embeddings
            self.save_embeddings(self.embeddings, self.texts)
            
            self.logger.info("✅ Embeddings generated and saved successfully")
            return self.embeddings
            
        except Exception as e:
            self.logger.error(f"❌ Error generating embeddings: {e}")
            raise
    
    def _prepare_texts(self, gita_df: pd.DataFrame) -> List[str]:
        """Prepare text data for embedding generation"""
        
        # Combine different text fields for better search
        combined_texts = []
        
        for _, row in gita_df.iterrows():
            # Combine Sanskrit, Hindi, English, theme, and keywords
            combined_text = f"""
            Chapter {row['chapter']}, Verse {row['verse']}
            Sanskrit: {row['sanskrit']}
            Hindi: {row['hindi']}
            English: {row['english']}
            Theme: {row['theme']}
            Keywords: {row['keywords']}
            """.strip()
            
            combined_texts.append(combined_text)
        
        return combined_texts
    
    def save_embeddings(self, embeddings: np.ndarray, texts: List[str]):
        """Save embeddings and texts to file"""
        try:
            # Ensure processed directory exists
            (DATA_DIR / "processed").mkdir(exist_ok=True)
            
            # Save embeddings and texts
            with open(self.embeddings_file, 'wb') as f:
                pickle.dump({
                    'embeddings': embeddings,
                    'texts': texts,
                    'model_name': self.model_name
                }, f)
            
            self.logger.info(f"✅ Embeddings saved to {self.embeddings_file}")
            
        except Exception as e:
            self.logger.error(f"❌ Error saving embeddings: {e}")
            raise
    
    def load_embeddings(self) -> np.ndarray:
        """Load cached embeddings"""
        try:
            with open(self.embeddings_file, 'rb') as f:
                data = pickle.load(f)
            
            self.embeddings = data['embeddings']
            self.texts = data['texts']
            
            self.logger.info(f"✅ Loaded {len(self.embeddings)} cached embeddings")
            return self.embeddings
            
        except Exception as e:
            self.logger.error(f"❌ Error loading embeddings: {e}")
            raise
    
    def create_faiss_index(self, embeddings: np.ndarray = None) -> faiss.Index:
        """Create FAISS index for fast similarity search"""
        
        if embeddings is None:
            embeddings = self.embeddings
        
        if embeddings is None:
            raise ValueError("No embeddings available. Generate embeddings first.")
        
        try:
            # Create FAISS index
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatIP(dimension)  # Inner product (cosine similarity)
            
            # Normalize embeddings for cosine similarity
            faiss.normalize_L2(embeddings)
            
            # Add embeddings to index
            self.index.add(embeddings.astype('float32'))
            
            # Save index
            faiss.write_index(self.index, str(self.index_file))
            
            self.logger.info(f"✅ FAISS index created with {self.index.ntotal} vectors")
            return self.index
            
        except Exception as e:
            self.logger.error(f"❌ Error creating FAISS index: {e}")
            raise
    
    def load_faiss_index(self) -> faiss.Index:
        """Load existing FAISS index"""
        try:
            if self.index_file.exists():
                self.index = faiss.read_index(str(self.index_file))
                self.logger.info(f"✅ Loaded FAISS index with {self.index.ntotal} vectors")
                return self.index
            else:
                raise FileNotFoundError("FAISS index not found")
                
        except Exception as e:
            self.logger.error(f"❌ Error loading FAISS index: {e}")
            raise
    
    def search_similar(self, query: str, k: int = 5) -> List[Tuple[str, float]]:
        """
        Search for similar verses
        
        Args:
            query: Search query
            k: Number of results to return
            
        Returns:
            List of (text, similarity_score) tuples
        """
        
        if self.model is None:
            self.load_model()
        
        if self.index is None:
            try:
                self.load_faiss_index()
            except:
                # Create index if it doesn't exist
                if self.embeddings is None:
                    self.load_embeddings()
                self.create_faiss_index()
        
        try:
            # Encode query
            query_embedding = self.model.encode([query], convert_to_numpy=True)
            faiss.normalize_L2(query_embedding)
            
            # Search
            scores, indices = self.index.search(query_embedding.astype('float32'), k)
            
            # Format results
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < len(self.texts):
                    results.append((self.texts[idx], float(score)))
            
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Error in similarity search: {e}")
            raise

# Utility functions
def setup_embeddings(gita_df: pd.DataFrame, force_regenerate: bool = False) -> GitaEmbedder:
    """
    Setup embeddings for the Gita dataset
    
    Args:
        gita_df: DataFrame containing Gita verses
        force_regenerate: Whether to regenerate embeddings
        
    Returns:
        GitaEmbedder instance ready for search
    """
    embedder = GitaEmbedder()
    
    # Generate or load embeddings
    embeddings = embedder.generate_embeddings(gita_df, force_regenerate)
    
    # Create or load FAISS index
    try:
        embedder.load_faiss_index()
    except:
        embedder.create_faiss_index(embeddings)
    
    return embedder
