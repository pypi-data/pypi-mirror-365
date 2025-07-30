import numpy as np
import pickle
import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Union
from ._lsd_core import LSDEngine as _LSDEngine, LSDParams
from .text_processor import TextProcessor
from .utils import normalize_embeddings

class LSdembed:
    def __init__(self, params: Optional[Dict] = None):
        self.params = LSDParams()
        if params:
            for key, value in params.items():
                setattr(self.params, key, value)
        
        self.engine = _LSDEngine(self.params)
        self.text_processor = TextProcessor()
        self.is_fitted = False
        
    def fit(self, texts: List[str], chunk_size: int = 1000):
        """Fit the model on a corpus of texts"""
        # Process texts and calculate IDF
        chunks = self.text_processor.chunk_texts(texts, chunk_size)
        self.idf_scores = self.text_processor.calculate_idf(chunks)
        
        # Build embeddings
        token_chunks = [self.text_processor.tokenize(chunk) for chunk in chunks]
        raw_embeddings = self.engine.embed_chunks(token_chunks, self.idf_scores)
        
        # Normalize vector space
        self.corpus_center, self.final_embeddings = normalize_embeddings(
            np.array(raw_embeddings)
        )
        self.chunks = chunks
        self.is_fitted = True
        
    def embed_query(self, query: str) -> np.ndarray:
        """Embed a single query"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before embedding queries")
            
        tokens = self.text_processor.tokenize(query)
        raw_embedding = self.engine.embed_tokens(tokens, self.idf_scores)
        
        # Apply same normalization as corpus
        centered = np.array(raw_embedding) - self.corpus_center
        norm = np.linalg.norm(centered)
        return centered / (norm + 1e-6)
    
    def search(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """Search for similar chunks"""
        query_emb = self.embed_query(query)
        similarities = self.final_embeddings @ query_emb
        
        top_indices = np.argpartition(similarities, -top_k)[-top_k:]
        sorted_indices = top_indices[np.argsort(similarities[top_indices])][::-1]
        
        return [(self.chunks[i], float(similarities[i])) for i in sorted_indices]
    
    def save_model(self, filepath: Union[str, Path], compress: bool = True):
        """Save the fitted model to disk"""
        if not self.is_fitted:
            raise ValueError("Cannot save unfitted model. Call fit() first.")
        
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Prepare model data
        model_data = {
            'params': {
                'd': self.params.d,
                'dt': self.params.dt,
                'alpha': self.params.alpha,
                'beta': self.params.beta,
                'gamma': self.params.gamma,
                'r_cutoff': self.params.r_cutoff,
                'scale': self.params.scale,
                'seed': self.params.seed
            },
            'idf_scores': self.idf_scores,
            'corpus_center': self.corpus_center,
            'final_embeddings': self.final_embeddings,
            'chunks': self.chunks,
            'text_processor_config': {
                'token_pattern': self.text_processor.token_pattern.pattern
            },
            'version': '0.1.0'
        }
        
        # Save with compression option
        if compress:
            import gzip
            with gzip.open(f"{filepath}.gz", 'wb') as f:
                pickle.dump(model_data, f, protocol=pickle.HIGHEST_PROTOCOL)
        else:
            with open(filepath, 'wb') as f:
                pickle.dump(model_data, f, protocol=pickle.HIGHEST_PROTOCOL)
    
    def load_model(self, filepath: Union[str, Path]):
        """Load a saved model from disk"""
        filepath = Path(filepath)
        
        # Handle compressed files
        if filepath.suffix == '.gz' or (filepath.with_suffix('.gz')).exists():
            if filepath.suffix != '.gz':
                filepath = filepath.with_suffix(filepath.suffix + '.gz')
            import gzip
            with gzip.open(filepath, 'rb') as f:
                model_data = pickle.load(f)
        else:
            with open(filepath, 'rb') as f:
                model_data = pickle.load(f)
        
        # Restore parameters
        params_dict = model_data['params']
        for key, value in params_dict.items():
            setattr(self.params, key, value)
        
        # Recreate engine with loaded params
        self.engine = _LSDEngine(self.params)
        
        # Restore text processor
        processor_config = model_data.get('text_processor_config', {})
        token_pattern = processor_config.get('token_pattern', r'\w+')
        self.text_processor = TextProcessor(token_pattern)
        
        # Restore fitted data
        self.idf_scores = model_data['idf_scores']
        self.corpus_center = model_data['corpus_center']
        self.final_embeddings = model_data['final_embeddings']
        self.chunks = model_data['chunks']
        self.is_fitted = True
    
    def export_embeddings(self, filepath: Union[str, Path], format: str = 'npz'):
        """Export embeddings in various formats for external use"""
        if not self.is_fitted:
            raise ValueError("Cannot export unfitted model. Call fit() first.")
        
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        if format.lower() == 'npz':
            np.savez_compressed(
                filepath,
                embeddings=self.final_embeddings,
                corpus_center=self.corpus_center,
                chunks=np.array(self.chunks, dtype=object)
            )
        elif format.lower() == 'csv':
            import pandas as pd
            df = pd.DataFrame(self.final_embeddings)
            df['text'] = self.chunks
            df.to_csv(filepath, index=False)
        elif format.lower() == 'json':
            export_data = {
                'embeddings': self.final_embeddings.tolist(),
                'corpus_center': self.corpus_center.tolist(),
                'chunks': self.chunks,
                'dimension': self.final_embeddings.shape[1]
            }
            with open(filepath, 'w') as f:
                json.dump(export_data, f, indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}. Use 'npz', 'csv', or 'json'")
    
    def get_model_info(self) -> Dict:
        """Get comprehensive information about the fitted model"""
        if not self.is_fitted:
            return {"status": "unfitted"}
        
        return {
            "status": "fitted",
            "num_chunks": len(self.chunks),
            "embedding_dimension": self.final_embeddings.shape[1],
            "vocabulary_size": len(self.idf_scores),
            "parameters": {
                "d": self.params.d,
                "dt": self.params.dt,
                "alpha": self.params.alpha,
                "beta": self.params.beta,
                "gamma": self.params.gamma,
                "r_cutoff": self.params.r_cutoff,
                "scale": self.params.scale,
                "seed": self.params.seed
            },
            "memory_usage_mb": {
                "embeddings": self.final_embeddings.nbytes / 1024 / 1024,
                "corpus_center": self.corpus_center.nbytes / 1024 / 1024,
                "total_approximate": (
                    self.final_embeddings.nbytes + 
                    self.corpus_center.nbytes
                ) / 1024 / 1024
            }
        }
    
    def update_params(self, **kwargs):
        """Update model parameters"""
        for key, value in kwargs.items():
            if hasattr(self.params, key):
                setattr(self.params, key, value)
        self.engine.set_params(self.params)
    
    @classmethod
    def from_pretrained(cls, filepath: Union[str, Path]):
        """Create a new instance from a saved model"""
        model = cls()
        model.load_model(filepath)
        return model