"""
Vector database service for resume embeddings
"""
import json
import hashlib
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from sentence_transformers import SentenceTransformer
import numpy as np

from app.core.config import settings


class VectorService:
    """Vector database service for resume embeddings and retrieval"""
    
    def __init__(self):
        self.client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY
        )
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.collection_name = "resume_embeddings"
        self.embedding_dim = 384  # all-MiniLM-L6-v2 dimension
        
        # Initialize collection
        self._ensure_collection_exists()
    
    def _ensure_collection_exists(self):
        """Ensure the collection exists in Qdrant"""
        try:
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.embedding_dim,
                        distance=Distance.COSINE
                    )
                )
                print(f"Created collection: {self.collection_name}")
        except Exception as e:
            print(f"Error ensuring collection exists: {e}")
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text"""
        try:
            embedding = self.embedding_model.encode(text)
            return embedding.tolist()
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return []
    
    def index_resume_content(self, user_id: int, resume_id: int, parsed_data: Dict[str, Any]) -> bool:
        """Index resume content in vector database"""
        try:
            # Extract text content from parsed data
            content_parts = []
            
            # Add raw text
            if 'raw_text' in parsed_data:
                content_parts.append(parsed_data['raw_text'])
            
            # Add skills
            if 'skills' in parsed_data and parsed_data['skills']:
                skills_text = "Skills: " + ", ".join(parsed_data['skills'])
                content_parts.append(skills_text)
            
            # Add experience
            if 'experience' in parsed_data and parsed_data['experience']:
                experience_text = "Experience: " + " ".join(parsed_data['experience'])
                content_parts.append(experience_text)
            
            # Add education
            if 'education' in parsed_data and parsed_data['education']:
                education_text = "Education: " + " ".join(parsed_data['education'])
                content_parts.append(education_text)
            
            # Add summary
            if 'summary' in parsed_data and parsed_data['summary']:
                content_parts.append(f"Summary: {parsed_data['summary']}")
            
            # Create chunks for indexing
            chunks = []
            for i, part in enumerate(content_parts):
                if len(part.strip()) > 50:  # Only index substantial content
                    # Generate embedding
                    embedding = self.generate_embedding(part)
                    if embedding:
                        # Create point ID
                        point_id = f"{user_id}_{resume_id}_{i}"
                        
                        # Create payload
                        payload = {
                            "user_id": user_id,
                            "resume_id": resume_id,
                            "content": part,
                            "content_type": self._get_content_type(part),
                            "created_at": parsed_data.get('created_at', ''),
                            "skills": parsed_data.get('skills', []),
                            "experience_years": parsed_data.get('experience_years'),
                            "education_level": parsed_data.get('education_level'),
                            "current_role": parsed_data.get('current_role')
                        }
                        
                        chunks.append(PointStruct(
                            id=point_id,
                            vector=embedding,
                            payload=payload
                        ))
            
            # Upsert points to Qdrant
            if chunks:
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=chunks
                )
                print(f"Indexed {len(chunks)} chunks for resume {resume_id}")
                return True
            
            return False
            
        except Exception as e:
            print(f"Error indexing resume content: {e}")
            return False
    
    def _get_content_type(self, content: str) -> str:
        """Determine content type based on content"""
        content_lower = content.lower()
        
        if content_lower.startswith('skills:'):
            return 'skills'
        elif content_lower.startswith('experience:'):
            return 'experience'
        elif content_lower.startswith('education:'):
            return 'education'
        elif content_lower.startswith('summary:'):
            return 'summary'
        else:
            return 'general'
    
    def search_similar_content(self, query: str, user_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for similar content in user's resumes"""
        try:
            # Generate embedding for query
            query_embedding = self.generate_embedding(query)
            if not query_embedding:
                return []
            
            # Search in Qdrant
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                query_filter=Filter(
                    must=[
                        FieldCondition(
                            key="user_id",
                            match=MatchValue(value=user_id)
                        )
                    ]
                ),
                limit=limit
            )
            
            # Format results
            results = []
            for result in search_results:
                results.append({
                    "content": result.payload.get("content", ""),
                    "content_type": result.payload.get("content_type", ""),
                    "resume_id": result.payload.get("resume_id"),
                    "skills": result.payload.get("skills", []),
                    "experience_years": result.payload.get("experience_years"),
                    "education_level": result.payload.get("education_level"),
                    "current_role": result.payload.get("current_role"),
                    "score": result.score
                })
            
            return results
            
        except Exception as e:
            print(f"Error searching similar content: {e}")
            return []
    
    def get_user_skills(self, user_id: int) -> List[str]:
        """Get all skills for a user from their resumes"""
        try:
            search_results = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=Filter(
                    must=[
                        FieldCondition(
                            key="user_id",
                            match=MatchValue(value=user_id)
                        ),
                        FieldCondition(
                            key="content_type",
                            match=MatchValue(value="skills")
                        )
                    ]
                ),
                limit=100
            )
            
            all_skills = set()
            for result in search_results[0]:  # scroll returns (points, next_page_offset)
                skills = result.payload.get("skills", [])
                if isinstance(skills, list):
                    all_skills.update(skills)
            
            return list(all_skills)
            
        except Exception as e:
            print(f"Error getting user skills: {e}")
            return []
    
    def delete_user_data(self, user_id: int) -> bool:
        """Delete all vector data for a user"""
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=Filter(
                    must=[
                        FieldCondition(
                            key="user_id",
                            match=MatchValue(value=user_id)
                        )
                    ]
                )
            )
            print(f"Deleted vector data for user {user_id}")
            return True
            
        except Exception as e:
            print(f"Error deleting user data: {e}")
            return False
    
    def delete_resume_data(self, user_id: int, resume_id: int) -> bool:
        """Delete vector data for a specific resume"""
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=Filter(
                    must=[
                        FieldCondition(
                            key="user_id",
                            match=MatchValue(value=user_id)
                        ),
                        FieldCondition(
                            key="resume_id",
                            match=MatchValue(value=resume_id)
                        )
                    ]
                )
            )
            print(f"Deleted vector data for resume {resume_id}")
            return True
            
        except Exception as e:
            print(f"Error deleting resume data: {e}")
            return False
