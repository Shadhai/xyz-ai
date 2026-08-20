"""
XYZ AI - Main AI Engine
Human-Like School Assistant with $0 Budget
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from nlp.intent_classifier import IntentClassifier
from nlp.entity_extractor import EntityExtractor
from nlp.language_detector import LanguageDetector
from nlp.context_manager import ContextManager
from persona.persona_factory import PersonaFactory
from voice.voice_processor import VoiceProcessor
from core.authorization import AuthorizationManager
from core.security import SecurityManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class XYZAISystem:
    """Main AI System orchestrator"""
    
    def __init__(self):
        logger.info("Initializing XYZ AI System...")
        
        # Initialize components
        self.intent_classifier = IntentClassifier()
        self.entity_extractor = EntityExtractor()
        self.language_detector = LanguageDetector()
        self.context_manager = ContextManager()
        self.persona_factory = PersonaFactory()
        self.voice_processor = VoiceProcessor()
        self.auth_manager = AuthorizationManager()
        self.security_manager = SecurityManager()
        
        logger.info("XYZ AI System initialized successfully")
    
    async def process_query(
        self,
        query: str,
        user_id: str,
        session_id: str,
        input_type: str = "text"
    ) -> Dict[str, Any]:
        """Process user query and generate response"""
        
        try:
            # Step 1: Security Check
            if not self.security_manager.validate_input(query):
                return self.generate_error_response("Invalid input detected")
            
            # Step 2: Language Detection
            language = self.language_detector.detect(query)
            logger.info(f"Detected language: {language}")
            
            # Step 3: Get user context
            user_context = await self.context_manager.get_context(
                user_id, session_id
            )
            
            # Step 4: Intent Classification
            intent = await self.intent_classifier.classify(
                query,
                language=language,
                context=user_context
            )
            logger.info(f"Detected intent: {intent}")
            
            # Step 5: Entity Extraction
            entities = await self.entity_extractor.extract(
                query,
                intent=intent,
                language=language
            )
            
            # Step 6: Permission Validation
            if not await self.auth_manager.validate_action(
                user_id=user_id,
                intent=intent,
                entities=entities
            ):
                return self.generate_error_response(
                    "You don't have permission to perform this action"
                )
            
            # Step 7: Create Persona
            persona = self.persona_factory.create_persona(
                role=user_context.get('role', 'student'),
                language=language
            )
            
            # Step 8: Process Intent
            response = await self.process_intent(
                intent=intent,
                entities=entities,
                persona=persona,
                user_context=user_context
            )
            
            # Step 9: Update Context
            await self.context_manager.update_context(
                user_id=user_id,
                session_id=session_id,
                query=query,
                response=response,
                intent=intent
            )
            
            # Step 10: Generate voice if needed
            if input_type == "voice" or response.get('voice_required'):
                audio_data = await self.voice_processor.text_to_speech(
                    response['text'],
                    language=language
                )
                response['audio'] = audio_data
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return self.generate_error_response(str(e))
    
    async def process_intent(
        self,
        intent: Dict,
        entities: Dict,
        persona: Any,
        user_context: Dict
    ) -> Dict[str, Any]:
        """Process detected intent"""
        
        intent_type = intent.get('type')
        
        if intent_type == 'view_attendance':
            return await self.handle_attendance_query(
                entities, persona, user_context
            )
        elif intent_type == 'mark_attendance':
            return await self.handle_attendance_marking(
                entities, persona, user_context
            )
        elif intent_type == 'escalation':
            return await self.handle_escalation(
                entities, persona, user_context
            )
        else:
            return persona.generate_response(
                intent_type, entities, user_context
            )
    
    def generate_error_response(self, message: str) -> Dict:
        """Generate error response"""
        return {
            'status': 'error',
            'text': message,
            'intent': 'error',
            'timestamp': asyncio.get_event_loop().time()
        }

# Create FastAPI app
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting XYZ AI System...")
    app.state.ai_system = XYZAISystem()
    yield
    # Shutdown
    logger.info("Shutting down XYZ AI System...")

app = FastAPI(
    title="XYZ AI - Human-Like School Assistant",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "XYZ AI System Running", "status": "active"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/api/v1/chat")
async def chat_endpoint(request: Dict[str, Any]):
    """Handle chat requests"""
    ai_system = app.state.ai_system
    
    response = await ai_system.process_query(
        query=request.get('query'),
        user_id=request.get('user_id'),
        session_id=request.get('session_id'),
        input_type=request.get('input_type', 'text')
    )
    
    return JSONResponse(response)

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """Handle WebSocket chat"""
    await websocket.accept()
    ai_system = app.state.ai_system
    
    try:
        while True:
            data = await websocket.receive_json()
            
            response = await ai_system.process_query(
                query=data.get('query'),
                user_id=data.get('user_id'),
                session_id=data.get('session_id'),
                input_type=data.get('input_type', 'text')
            )
            
            await websocket.send_json(response)
            
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )