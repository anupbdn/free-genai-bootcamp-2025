from typing import List, Optional
from .transcript_processor import TranscriptProcessor
from .vector_store import VectorStoreManager
from .llm_manager import LLMManager
from models.schemas import Transcript, Question, QuestionSet
from config.settings import QUESTION_TYPES, DEFAULT_NUM_QUESTIONS
# from language_listening_app.models.schemas import Transcript, Question, QuestionSet
# from language_listening_app.config.settings import QUESTION_TYPES, DEFAULT_NUM_QUESTIONS
import uuid

class AppService:
    """Main application service coordinating different components"""
    
    def __init__(self):
        self.transcript_processor = TranscriptProcessor()
        self.vector_store = VectorStoreManager()
        self.llm_manager = None  # Will be initialized when needed
    
    def process_video(
        self,
        url: str,
        language: str = "en",
        provider: str = "ollama",
        model: Optional[str] = None
    ) -> QuestionSet:
        """Process a YouTube video and generate questions"""
        # Initialize LLM manager
        self.llm_manager = LLMManager(provider=provider, model=model)
        
        # Process transcript
        transcript = self.transcript_processor.process_transcript(url, language)
        
        # Add transcript to vector store
        self.vector_store.add_transcript(transcript)
        
        # Generate questions for each chunk
        all_questions = []
        for chunk in transcript.chunks:
            questions = self.llm_manager.generate_questions(
                text=chunk.text,
                num_questions=DEFAULT_NUM_QUESTIONS,
                question_types=QUESTION_TYPES
            )
            all_questions.extend(questions)
            
            # Add questions to vector store
            for question in questions:
                self.vector_store.add_question(question, transcript.video_id)
        
        # Create question set
        question_set = QuestionSet(
            id=str(uuid.uuid4()),
            transcript_id=transcript.video_id,
            questions=all_questions,
            metadata={
                'url': url,
                'language': language,
                'provider': provider,
                'model': model,
                'total_questions': len(all_questions)
            }
        )
        
        return question_set
    
    def search_similar_questions(
        self,
        query: str,
        n_results: int = 3
    ) -> List[dict]:
        """Search for similar questions in the vector store"""
        return self.vector_store.search_similar_questions(query, n_results)
    
    def search_similar_chunks(
        self,
        query: str,
        n_results: int = 3
    ) -> List[dict]:
        """Search for similar transcript chunks in the vector store"""
        return self.vector_store.search_similar_chunks(query, n_results) 