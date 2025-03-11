"""
This file contains modified versions of the backend modules with direct imports
instead of relative imports to work with Streamlit.
"""

from typing import List, Optional, Dict, Any
import re
import uuid
import json
import os
import boto3
import requests
import chromadb
from chromadb.config import Settings
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import models directly
from models.schemas import Transcript, TranscriptChunk, Question, QuestionSet

# Import settings directly
from config.settings import (
    CHUNK_SIZE, 
    CHUNK_OVERLAP,
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    AWS_REGION,
    OLLAMA_API_URL,
    DEFAULT_OLLAMA_MODEL,
    DEFAULT_BEDROCK_MODEL,
    VECTOR_STORE_DIR,
    COLLECTION_NAME,
    QUESTION_TYPES,
    DEFAULT_NUM_QUESTIONS
)

# TranscriptProcessor with direct imports
class DirectTranscriptProcessor:
    """Handles YouTube transcript extraction and processing"""
    
    @staticmethod
    def extract_video_id(url: str) -> str:
        """Extract video ID from YouTube URL"""
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?]+)',
            r'youtube\.com\/embed\/([^&\n?]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        raise ValueError("Invalid YouTube URL format")
    
    @staticmethod
    def get_transcript(video_id: str, language: str = 'en') -> List[dict]:
        """Get transcript from YouTube API"""
        try:
            return YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
        except (TranscriptsDisabled, NoTranscriptFound) as e:
            raise ValueError(f"No transcript found for language: {language}")
        except Exception as e:
            raise ValueError(f"Error fetching transcript: {str(e)}")
    
    @staticmethod
    def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
        """Split text into chunks with overlap"""
        words = text.split()
        
        if len(words) <= chunk_size:
            return [text]
        
        chunks = []
        i = 0
        
        while i < len(words):
            # Get chunk_size words or remaining words if less than chunk_size
            chunk = words[i:i + chunk_size]
            chunks.append(" ".join(chunk))
            
            # Move forward by chunk_size - overlap words
            i += chunk_size - overlap
        
        return chunks
    
    def process_transcript(self, url: str, language: str = 'en') -> Transcript:
        """Process YouTube transcript and return structured data"""
        # Extract video ID
        video_id = self.extract_video_id(url)
        
        # Get transcript
        transcript_data = self.get_transcript(video_id, language)
        
        # Combine all transcript segments into a single text
        full_text = " ".join([item['text'] for item in transcript_data])
        
        # Chunk the text
        text_chunks = self.chunk_text(full_text)
        
        # Create TranscriptChunk objects
        chunks = []
        for i, chunk_text in enumerate(text_chunks):
            chunks.append(TranscriptChunk(
                id=str(uuid.uuid4()),
                text=chunk_text,
                index=i
            ))
        
        # Create and return Transcript object
        return Transcript(
            video_id=video_id,
            url=url,
            language=language,
            chunks=chunks
        )

# LLMManager with direct imports
class DirectLLMManager:
    """Manages interactions with different LLM providers"""
    
    def __init__(self, provider: str = "ollama", model: Optional[str] = None):
        self.provider = provider
        self.model = model or (
            DEFAULT_OLLAMA_MODEL if provider == "ollama"
            else DEFAULT_BEDROCK_MODEL
        )
        
        if provider == "bedrock":
            self.bedrock_client = boto3.client(
                "bedrock-runtime",
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                region_name=AWS_REGION
            )
    
    def generate_questions(
        self,
        text: str,
        num_questions: int = 5,
        question_types: Optional[List[str]] = None
    ) -> List[Question]:
        """Generate questions from text using the selected LLM"""
        if self.provider == "ollama":
            return self._generate_questions_ollama(text, num_questions, question_types)
        else:
            return self._generate_questions_bedrock(text, num_questions, question_types)
    
    def _generate_questions_ollama(
        self,
        text: str,
        num_questions: int,
        question_types: Optional[List[str]]
    ) -> List[Question]:
        """Generate questions using Ollama"""
        prompt = self._create_question_prompt(text, num_questions, question_types)
        
        response = requests.post(
            OLLAMA_API_URL,
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to generate questions: {response.text}")
        
        response_text = response.json().get("response", "")
        
        return self._parse_questions(response_text, num_questions)
    
    def _generate_questions_bedrock(
        self,
        text: str,
        num_questions: int,
        question_types: Optional[List[str]]
    ) -> List[Question]:
        """Generate questions using AWS Bedrock"""
        prompt = self._create_question_prompt(text, num_questions, question_types)
        
        # Different request formats for different models
        if self.model.startswith("anthropic"):
            request_body = {
                "prompt": f"\n\nHuman: {prompt}\n\nAssistant:",
                "max_tokens_to_sample": 1000,
                "temperature": 0.7,
                "stop_sequences": ["\n\nHuman:"]
            }
        else:  # amazon models like nova
            request_body = {
                "inferenceConfig": {
                    "max_new_tokens": 1000
                },
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "text": prompt
                            }
                        ]
                    }
                ]
            }
        
        response = self.bedrock_client.invoke_model(
            modelId=self.model,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(request_body)
        )
        
        # Handle different response formats
        try:
            # Try to parse as JSON directly from the response body
            response_body = json.loads(response.get("body").read())
            
            # Handle different response structures based on model type
            if self.model.startswith("anthropic"):
                response_text = response_body.get("completion", "")
            else:  # amazon models
                if "output" in response_body and "message" in response_body["output"]:
                    content = response_body["output"]["message"]["content"]
                    if isinstance(content, list) and len(content) > 0:
                        response_text = content[0].get("text", "")
                    else:
                        response_text = str(content)
                else:
                    # Fallback to using the entire response body as text
                    response_text = str(response_body)
        except (json.JSONDecodeError, AttributeError, KeyError, TypeError) as e:
            # If we can't parse the JSON or access the expected fields,
            # try to use the raw response
            try:
                if hasattr(response.get("body"), "read"):
                    response_text = response.get("body").read().decode("utf-8")
                else:
                    response_text = str(response)
            except Exception:
                # Last resort fallback
                response_text = str(response)
        
        return self._parse_questions(response_text, num_questions)
    
    def _create_question_prompt(
        self,
        text: str,
        num_questions: int,
        question_types: Optional[List[str]]
    ) -> str:
        """Create prompt for question generation"""
        types_str = ", ".join(question_types) if question_types else "comprehension, analysis, and application"
        
        return f"""Generate {num_questions} questions based on the following text. 
        Include a mix of {types_str} questions.
        For each question, provide:
        1. The question text
        2. The correct answer
        3. An explanation of the answer
        4. The difficulty level (easy, medium, or hard)
        5. The relevant context from the text

        Text:
        {text}

        Format your response as a JSON array of objects with the following structure:
        [
            {{
                "text": "question text",
                "answer": "correct answer",
                "explanation": "explanation of the answer",
                "difficulty": "difficulty level",
                "context": "relevant context"
            }}
        ]
        """
    
    def _parse_questions(self, response_text: str, num_questions: int = None) -> List[Question]:
        """
        Parse LLM response into Question objects
        
        Args:
            response_text: The JSON response from the LLM
            num_questions: Maximum number of questions to return (optional)
        
        Returns:
            List of Question objects
        """
        try:
            questions_data = json.loads(response_text)
            
            # Limit the number of questions if specified
            if num_questions is not None:
                questions_data = questions_data[:num_questions]
                
            return [
                Question(
                    id=str(uuid.uuid4()),
                    # Use 'text' field if available, otherwise use 'question' field
                    text=q.get("text", q.get("question", "")),
                    answer=q.get("answer", ""),
                    explanation=q.get("explanation", ""),
                    difficulty=q.get("difficulty", "medium"),
                    # Provide a default empty context if not available
                    context=q.get("context", "")
                )
                for q in questions_data
            ]
        except json.JSONDecodeError:
            raise Exception("Failed to parse LLM response as JSON")

# VectorStoreManager with direct imports
class DirectVectorStoreManager:
    """Manages vector store operations using ChromaDB"""
    
    def __init__(self, persist_directory=None, collection_name=None):
        """
        Initialize the vector store manager
        
        Args:
            persist_directory (str, optional): Directory to persist the vector store.
                If None, uses the value from settings.VECTOR_STORE_DIR.
            collection_name (str, optional): Name of the collection to use.
                If None, uses the value from settings.COLLECTION_NAME.
        """
        # Use the provided directory or fall back to the one from settings
        persist_dir = persist_directory or VECTOR_STORE_DIR
        # Use the provided collection name or fall back to the one from settings
        coll_name = collection_name or COLLECTION_NAME
        
        self.client = chromadb.Client(Settings(
            persist_directory=persist_dir,
            anonymized_telemetry=False
        ))
        self.collection = self.client.get_or_create_collection(
            name=coll_name,
            metadata={"hnsw:space": "cosine"}
        )
    
    def add_transcript(self, transcript: Transcript) -> None:
        """Add transcript chunks to vector store"""
        # Prepare documents and metadata
        documents = [chunk.text for chunk in transcript.chunks]
        metadatas = [
            {
                'chunk_id': chunk.id,
                'chunk_index': chunk.index,
                'transcript_id': transcript.video_id,
                'url': transcript.url,
                'language': transcript.language,
                'question_id': ""  # Empty string to indicate this is not a question
            }
            for chunk in transcript.chunks
        ]
        ids = [f"chunk_{chunk.id}" for chunk in transcript.chunks]
        
        # Add to collection
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
    
    def add_question(self, question: Question, transcript_id: str) -> None:
        """Add question to vector store"""
        # Prepare document and metadata
        document = question.text
        metadata = {
            'question_id': question.id,
            'question_text': question.text,
            'answer': question.answer,
            'explanation': question.explanation,
            'difficulty': question.difficulty,
            'context': question.context,
            'transcript_id': transcript_id,
            'chunk_id': ""  # Empty string to indicate this is not a chunk
        }
        id = f"question_{question.id}"
        
        # Add to collection
        self.collection.add(
            documents=[document],
            metadatas=[metadata],
            ids=[id]
        )
    
    def search_similar_chunks(self, query: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """Search for similar transcript chunks"""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where={"chunk_id": {"$ne": ""}}  # Using empty string instead of None
            )
            
            # If no results are found or the results are empty, return an empty list
            if not results or not results['ids'] or not results['ids'][0]:
                return []
            
            # Process results
            processed_results = []
            for i in range(len(results['ids'][0])):
                chunk_id = results['metadatas'][0][i]['chunk_id']
                chunk_index = results['metadatas'][0][i]['chunk_index']
                transcript_id = results['metadatas'][0][i]['transcript_id']
                text = results['documents'][0][i]
                score = results['distances'][0][i] if 'distances' in results else 0
                
                # Create TranscriptChunk object
                chunk = TranscriptChunk(
                    id=chunk_id,
                    text=text,
                    index=chunk_index
                )
                
                processed_results.append({
                    'chunk': chunk,
                    'transcript_id': transcript_id,
                    'score': score
                })
            
            return processed_results
        except Exception as e:
            # If there's an error with the query, log it and return an empty list
            print(f"Error searching for similar chunks: {e}")
            return []
    
    def search_similar_questions(self, query: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """Search for similar questions"""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where={"question_id": {"$ne": ""}}  # Using empty string instead of None
            )
            
            # If no results are found or the results are empty, return an empty list
            if not results or not results['ids'] or not results['ids'][0]:
                return []
            
            # Process results
            processed_results = []
            for i in range(len(results['ids'][0])):
                metadata = results['metadatas'][0][i]
                score = results['distances'][0][i] if 'distances' in results else 0
                
                # Create Question object
                question = Question(
                    id=metadata['question_id'],
                    text=metadata['question_text'],
                    answer=metadata['answer'],
                    explanation=metadata['explanation'],
                    difficulty=metadata['difficulty'],
                    context=metadata['context']
                )
                
                processed_results.append({
                    'question': question,
                    'transcript_id': metadata['transcript_id'],
                    'score': score
                })
            
            return processed_results
        except Exception as e:
            # If there's an error with the query, log it and return an empty list
            print(f"Error searching for similar questions: {e}")
            return []
    
    def get_all_transcripts(self) -> List[Transcript]:
        """Get all transcripts from the vector store"""
        try:
            # Query for all chunks with transcript_id
            results = self.collection.get(
                where={"chunk_id": {"$ne": ""}}  # Get all chunks
            )
            
            if not results or not results['ids']:
                return []
            
            # Extract unique transcript IDs
            transcript_ids = set()
            for metadata in results['metadatas']:
                if 'transcript_id' in metadata:
                    transcript_ids.add(metadata['transcript_id'])
            
            # Create Transcript objects
            transcripts = []
            for transcript_id in transcript_ids:
                # Get all chunks for this transcript
                transcript_chunks = self.collection.get(
                    where={"transcript_id": transcript_id}
                )
                
                if not transcript_chunks or not transcript_chunks['ids']:
                    continue
                
                # Create TranscriptChunk objects
                chunks = []
                for i, chunk_id in enumerate(transcript_chunks['ids']):
                    metadata = transcript_chunks['metadatas'][i]
                    text = transcript_chunks['documents'][i]
                    
                    chunks.append(TranscriptChunk(
                        id=metadata.get('chunk_id', ''),
                        text=text,
                        index=metadata.get('chunk_index', 0)
                    ))
                
                # Sort chunks by index
                chunks.sort(key=lambda x: x.index)
                
                # Create Transcript object
                transcripts.append(Transcript(
                    video_id=transcript_id,
                    url=metadata.get('url', ''),
                    language=metadata.get('language', 'en'),
                    chunks=chunks
                ))
            
            return transcripts
        except Exception as e:
            print(f"Error getting all transcripts: {e}")
            return []
    
    def get_questions_for_transcript(self, transcript_id: str) -> List[Question]:
        """Get all questions for a specific transcript"""
        try:
            # Query for all questions with the given transcript_id
            results = self.collection.get(
                where={
                    "transcript_id": transcript_id,
                    "question_id": {"$ne": ""}
                }
            )
            
            if not results or not results['ids']:
                return []
            
            # Create Question objects
            questions = []
            for i, question_id in enumerate(results['ids']):
                metadata = results['metadatas'][i]
                
                questions.append(Question(
                    id=metadata.get('question_id', ''),
                    text=metadata.get('question_text', ''),
                    answer=metadata.get('answer', ''),
                    explanation=metadata.get('explanation', ''),
                    difficulty=metadata.get('difficulty', 'medium'),
                    context=metadata.get('context', '')
                ))
            
            return questions
        except Exception as e:
            print(f"Error getting questions for transcript {transcript_id}: {e}")
            return []

# AppService with direct imports
class DirectAppService:
    """Main application service coordinating different components"""
    
    def __init__(self):
        self.transcript_processor = DirectTranscriptProcessor()
        self.vector_store = DirectVectorStoreManager()
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
        self.llm_manager = DirectLLMManager(provider=provider, model=model)
        
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