"""
Intent Classification using free models
"""

import torch
import logging
from typing import Dict, Any, List
from transformers import pipeline
from sentence_transformers import SentenceTransformer
import numpy as np

logger = logging.getLogger(__name__)

class IntentClassifier:
    def __init__(self):
        # Use free models
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Intent labels
        self.intents = [
            'view_attendance',
            'mark_attendance',
            'view_analytics',
            'escalation_request',
            'general_query',
            'greeting',
            'farewell',
            'help',
            'complaint',
            'feedback'
        ]
        
        # Load embedding model for semantic similarity
        self.embedding_model = SentenceTransformer(
            'paraphrase-multilingual-MiniLM-L12-v2'
        )
        
        # Intent examples (few-shot learning)
        self.intent_examples = {
            'view_attendance': [
                "What is my attendance?",
                "How much attendance does my child have?",
                "Show me attendance percentage",
                "मेरी उपस्थिति कितनी है?",
                "मेरे बच्चे की उपस्थिति कितनी है?"
            ],
            'mark_attendance': [
                "Mark Rahul absent today",
                "Update attendance for class 10",
                "Rahul is present",
                "आज राहुल को अनुपस्थित चिह्नित करें"
            ],
            'escalation_request': [
                "I want to talk to teacher",
                "Contact school management",
                "I am not satisfied",
                "मुझे शिक्षक से बात करनी है"
            ],
            'greeting': [
                "Hello",
                "Hi",
                "Good morning",
                "नमस्ते"
            ]
        }
        
        # Pre-compute intent embeddings
        self.intent_embeddings = self._compute_intent_embeddings()
    
    def _compute_intent_embeddings(self) -> Dict[str, np.ndarray]:
        """Compute embeddings for intent examples"""
        embeddings = {}
        for intent, examples in self.intent_examples.items():
            example_embeddings = self.embedding_model.encode(examples)
            embeddings[intent] = np.mean(example_embeddings, axis=0)
        return embeddings
    
    async def classify(
        self,
        query: str,
        language: str = 'en',
        context: Dict = None
    ) -> Dict[str, Any]:
        """Classify user intent"""
        
        # Get query embedding
        query_embedding = self.embedding_model.encode([query])[0]
        
        # Calculate similarity with each intent
        similarities = {}
        for intent, intent_embedding in self.intent_embeddings.items():
            similarity = np.dot(query_embedding, intent_embedding) / (
                np.linalg.norm(query_embedding) * 
                np.linalg.norm(intent_embedding)
            )
            similarities[intent] = similarity
        
        # Get best intent
        best_intent = max(similarities, key=similarities.get)
        confidence = similarities[best_intent]
        
        # Check context for better classification
        if context and context.get('conversation_history'):
            context_intent = self._check_context_intent(
                query, context['conversation_history']
            )
            if context_intent and confidence < 0.7:
                best_intent = context_intent
                confidence = 0.8
        
        return {
            'type': best_intent,
            'confidence': confidence,
            'language': language
        }
    
    def _check_context_intent(self, query: str, history: List[Dict]) -> str:
        """Use conversation history for better intent detection"""
        if not history:
            return None
        
        # Check last 3 messages
        recent_messages = history[-3:]
        
        # If user is responding to a question about attendance
        for msg in recent_messages:
            if 'attendance' in msg.get('response', '').lower():
                if any(word in query.lower() for word in ['yes', 'हाँ', 'haan']):
                    return 'view_attendance'
        
        return None