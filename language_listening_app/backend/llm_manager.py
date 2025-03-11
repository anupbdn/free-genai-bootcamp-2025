from typing import List, Dict, Any, Optional
import boto3
import requests
from models.schemas import Question
from config.settings import (
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    AWS_REGION,
    OLLAMA_API_URL,
    DEFAULT_OLLAMA_MODEL,
    DEFAULT_BEDROCK_MODEL
)
import json
import uuid

class LLMManager:
    """Manages interactions with different LLM providers"""
    
    def __init__(self, provider: str = "ollama", model: Optional[str] = None):
        self.provider = provider
        self.model = model or (
            DEFAULT_OLLAMA_MODEL if provider == "ollama"
            else DEFAULT_BEDROCK_MODEL
        )
        
        if provider == "bedrock":
            # Check if AWS credentials are available
            if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY:
                raise ValueError(
                    "AWS credentials are missing. Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY in your .env file."
                )
            
            try:
                self.bedrock_client = boto3.client(
                    "bedrock-runtime",
                    aws_access_key_id=AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                    region_name=AWS_REGION
                )
            except Exception as e:
                raise ValueError(f"Failed to initialize AWS Bedrock client: {str(e)}")
    
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