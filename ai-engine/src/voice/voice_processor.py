"""
Voice processing using free services
"""

import asyncio
import logging
import io
import json
from typing import Optional, Dict, Any

import numpy as np
import vosk
import edge_tts
import soundfile as sf

logger = logging.getLogger(__name__)

class VoiceProcessor:
    def __init__(self):
        self.models = {}
        self.load_models()
        
        # Voice configurations
        self.voice_configs = {
            'en': {
                'female': 'en-US-JennyNeural',
                'male': 'en-US-GuyNeural'
            },
            'hi': {
                'female': 'hi-IN-SwaraNeural',
                'male': 'hi-IN-MadhurNeural'
            },
            'ta': {
                'female': 'ta-IN-PallaviNeural',
                'male': 'ta-IN-ValluvarNeural'
            }
        }
    
    def load_models(self):
        """Load Vosk models for STT"""
        try:
            # English model
            self.models['en'] = vosk.Model(
                "models/vosk/vosk-model-small-en-us-0.15"
            )
            logger.info("Loaded English STT model")
            
            # Hindi model
            self.models['hi'] = vosk.Model(
                "models/vosk/vosk-model-small-hi-0.22"
            )
            logger.info("Loaded Hindi STT model")
            
        except Exception as e:
            logger.warning(f"Could not load Vosk models: {e}")
            logger.info("Will use browser-based STT")
    
    async def speech_to_text(
        self,
        audio_data: bytes,
        language: str = 'en'
    ) -> str:
        """Convert speech to text"""
        
        model = self.models.get(language, self.models.get('en'))
        
        if not model:
            raise ValueError("No STT model available")
        
        # Create recognizer
        recognizer = vosk.KaldiRecognizer(model, 16000)
        
        # Process audio
        recognizer.AcceptWaveform(audio_data)
        result = json.loads(recognizer.FinalResult())
        
        return result.get('text', '')
    
    async def text_to_speech(
        self,
        text: str,
        language: str = 'en',
        gender: str = 'female'
    ) -> bytes:
        """Convert text to speech using Edge TTS"""
        
        # Get voice
        voice = self.voice_configs.get(
            language, 
            self.voice_configs['en']
        ).get(gender, self.voice_configs['en']['female'])
        
        # Create audio buffer
        audio_buffer = io.BytesIO()
        
        # Generate speech
        communicate = edge_tts.Communicate(text, voice)
        
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_buffer.write(chunk["data"])
        
        return audio_buffer.getvalue()
    
    async def process_voice_input(
        self,
        audio_data: bytes,
        language: str = 'en'
    ) -> Dict[str, Any]:
        """Process voice input and return text"""
        
        # Convert speech to text
        text = await self.speech_to_text(audio_data, language)
        
        return {
            'text': text,
            'language': language,
            'confidence': 0.9  # Estimated confidence
        }