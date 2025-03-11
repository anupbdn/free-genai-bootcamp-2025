from typing import List, Optional, Dict, Any
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
                question_types=QUESTION_TYPES,
                language=language  # Pass the language parameter
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
    
    def get_transcript(
        self,
        url: str,
        language: str = "en"
    ) -> Transcript:
        """Get transcript from a YouTube video"""
        # Process transcript
        transcript = self.transcript_processor.process_transcript(url, language)
        
        # Add transcript to vector store
        self.vector_store.add_transcript(transcript)
        
        return transcript
    
    def generate_questions(
        self,
        transcript: Transcript,
        provider: str = "ollama",
        model: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        num_questions: int = DEFAULT_NUM_QUESTIONS
    ) -> QuestionSet:
        """Generate questions for a transcript"""
        # Initialize LLM manager if not already initialized
        if self.llm_manager is None:
            self.llm_manager = LLMManager(provider=provider, model=model)
        
        # Calculate questions per chunk based on total requested
        # We'll distribute questions evenly across chunks, with a minimum of 1 per chunk
        num_chunks = len(transcript.chunks)
        if num_chunks == 0:
            raise ValueError("Transcript has no chunks")
        
        # Determine how many questions to generate per chunk
        # For small transcripts, we might generate more questions per chunk
        # For larger transcripts, we'll distribute them more evenly
        if num_chunks <= 3:
            # For small transcripts, generate more questions per chunk
            questions_per_chunk = max(2, num_questions // num_chunks)
        else:
            # For larger transcripts, distribute questions more evenly
            # but ensure we get at least the requested total
            questions_per_chunk = max(1, (num_questions + num_chunks - 1) // num_chunks)
        
        # Get the language from the transcript
        language = transcript.language
        
        # Generate questions for each chunk
        all_questions = []
        for chunk in transcript.chunks:
            questions = self.llm_manager.generate_questions(
                text=chunk.text,
                num_questions=questions_per_chunk,
                question_types=QUESTION_TYPES,
                language=language  # Pass the language parameter
            )
            all_questions.extend(questions)
            
            # Add questions to vector store
            for question in questions:
                self.vector_store.add_question(question, transcript.video_id)
            
            # If we've reached or exceeded the requested number of questions, stop
            if len(all_questions) >= num_questions:
                break
        
        # Limit to the requested number of questions
        all_questions = all_questions[:num_questions]
        
        # Create metadata if not provided
        if metadata is None:
            metadata = {
                'language': transcript.language,
                'provider': provider,
                'model': model,
                'total_questions': len(all_questions)
            }
        else:
            # Add additional metadata
            metadata.update({
                'provider': provider,
                'model': model,
                'total_questions': len(all_questions)
            })
        
        # Create question set
        question_set = QuestionSet(
            id=str(uuid.uuid4()),
            transcript_id=transcript.video_id,
            questions=all_questions,
            metadata=metadata
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