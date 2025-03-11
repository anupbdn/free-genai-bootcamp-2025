from typing import List, Dict, Any
import chromadb
from chromadb.config import Settings
from models.schemas import Transcript, TranscriptChunk, Question
from config.settings import VECTOR_STORE_DIR, COLLECTION_NAME
import uuid

class VectorStoreManager:
    """Manages vector store operations using ChromaDB"""
    
    # Add a class variable to track the client
    _client_instance = None
    
    @classmethod
    def reset_client(cls):
        """Reset the ChromaDB client for testing purposes"""
        if hasattr(chromadb.api.shared_system_client.SharedSystemClient, '_identifier_to_system'):
            chromadb.api.shared_system_client.SharedSystemClient._identifier_to_system = {}
    
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
                'video_id': transcript.video_id,
                'language': transcript.language,
                'start_index': chunk.metadata['start_index'],
                'end_index': chunk.metadata['end_index']
            }
            for chunk in transcript.chunks
        ]
        ids = [chunk.id for chunk in transcript.chunks]
        
        # Add to collection
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
    
    def add_question(self, question: Question, transcript_id: str) -> None:
        """Add question to vector store"""
        # Prepare document and metadata
        document = f"Question: {question.text}\nAnswer: {question.answer}\nExplanation: {question.explanation}"
        metadata = {
            'question_id': question.id,
            'transcript_id': transcript_id,
            'difficulty': question.difficulty,
            'context': question.context
        }
        
        # Add to collection
        self.collection.add(
            documents=[document],
            metadatas=[metadata],
            ids=[question.id]
        )
    
    def search_similar_chunks(self, query: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """Search for similar chunks"""
        # Validate input
        if query is None or not query.strip():
            raise ValueError("Query cannot be empty or None")
            
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where={"chunk_id": {"$ne": ""}}
        )
        
        # If no results are found or the results are empty, return an empty list
        if not results or not results['ids'] or not results['ids'][0]:
            return []
        
        return [
            {
                'id': results['ids'][0][i],
                'text': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i]
            }
            for i in range(len(results['ids'][0]))
        ]
    
    def search_similar_questions(self, query: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """
        Search for similar questions in the vector store
        
        Args:
            query (str): The query text to search for
            n_results (int, optional): Number of results to return. Defaults to 3.
        
        Returns:
            List[Dict[str, Any]]: List of dictionaries containing question objects and similarity scores
        """
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where={"question_id": {"$ne": ""}}  # Using empty string instead of None
            )
            
            # If no results are found or the results are empty, return an empty list
            if not results or not results['ids'] or not results['ids'][0]:
                return []
            
            return [
                {
                    'id': results['ids'][0][i],
                    'text': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i]
                }
                for i in range(len(results['ids'][0]))
            ]
        except Exception as e:
            # If there's an error with the query, log it and return an empty list
            print(f"Error searching for similar questions: {e}")
            return []
    
    def get_all_transcripts(self) -> List[Transcript]:
        """
        Get all transcripts from the vector store
        
        Returns:
            List[Transcript]: List of Transcript objects
        """
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
                    
                    # Use the metadata chunk_index if available, otherwise use the loop index
                    chunk_index = metadata.get('chunk_index', i)
                    
                    chunks.append(TranscriptChunk(
                        id=metadata.get('chunk_id', ''),
                        text=text,
                        index=chunk_index,
                        metadata=metadata
                    ))
                
                # Sort chunks by index
                chunks.sort(key=lambda x: x.index)
                
                # Get URL from metadata if available
                url = ''
                if transcript_chunks['metadatas'] and len(transcript_chunks['metadatas']) > 0:
                    # Try to find URL in any of the chunk metadatas
                    for meta in transcript_chunks['metadatas']:
                        if 'url' in meta:
                            url = meta['url']
                            break
                
                # Create Transcript object
                transcripts.append(Transcript(
                    video_id=transcript_id,
                    url=url,
                    language=metadata.get('language', 'en'),
                    chunks=chunks
                ))
            
            return transcripts
        except Exception as e:
            print(f"Error getting all transcripts: {e}")
            return []
    
    def get_questions_for_transcript(self, transcript_id: str) -> List[Question]:
        """
        Get all questions for a specific transcript
        
        Args:
            transcript_id (str): The transcript ID to get questions for
            
        Returns:
            List[Question]: List of Question objects
        """
        try:
            # First, get all documents with the given transcript_id
            results = self.collection.get(
                where={"transcript_id": transcript_id}
            )
            
            if not results or not results['ids']:
                return []
            
            # Filter results to only include questions (those with question_id)
            questions = []
            for i, metadata in enumerate(results['metadatas']):
                if 'question_id' in metadata and metadata['question_id']:
                    questions.append(Question(
                        id=metadata.get('question_id', ''),
                        text=metadata.get('question_text', ''),
                        answer=metadata.get('answer', ''),
                        explanation=metadata.get('explanation', ''),
                        difficulty=metadata.get('difficulty', 'medium'),
                        context=results['documents'][i],
                        question_type=metadata.get('question_type', 'comprehension'),
                        metadata=metadata
                    ))
            
            return questions
        except Exception as e:
            print(f"Error getting questions for transcript {transcript_id}: {e}")
            return [] 