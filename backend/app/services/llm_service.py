"""
LLM service for generating AI suggestions
"""
import json
from typing import List, Optional, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
from openai import AsyncOpenAI

from app.models.user import TranscriptSegment, Resume


class LLMService:
    """LLM service for AI suggestions"""
    
    def __init__(self, client: AsyncOpenAI, db: AsyncSession):
        self.client = client
        self.db = db
    
    async def generate_suggestion(
        self,
        segments: List[TranscriptSegment],
        resume: Optional[Resume],
        suggestion_type: str
    ) -> str:
        """Generate AI suggestion based on context"""
        
        # Build context from transcript
        context = self._build_context(segments)
        
        # Get resume context
        resume_context = self._get_resume_context(resume)
        
        # Create prompt based on suggestion type
        prompt = self._create_prompt(suggestion_type, context, resume_context)
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an AI interview assistant. Provide helpful, concise suggestions based on the conversation context and user's background. Keep responses under 3 bullet points and be specific."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"Error generating suggestion: {str(e)}"
    
    def _build_context(self, segments: List[TranscriptSegment]) -> str:
        """Build context string from transcript segments"""
        if not segments:
            return "No conversation context available."
        
        context_parts = []
        for segment in segments[-5:]:  # Last 5 segments
            speaker = segment.speaker or "Unknown"
            context_parts.append(f"{speaker}: {segment.text}")
        
        return "\n".join(context_parts)
    
    def _get_resume_context(self, resume: Optional[Resume]) -> str:
        """Get relevant context from resume"""
        if not resume or not resume.parsed_json:
            return "No resume information available."
        
        try:
            parsed_data = json.loads(resume.parsed_json)
            
            context_parts = []
            
            # Add skills
            skills = parsed_data.get('skills', [])
            if skills:
                context_parts.append(f"Skills: {', '.join(skills[:10])}")  # Top 10 skills
            
            # Add experience
            experience_years = resume.experience_years
            if experience_years:
                context_parts.append(f"Experience: {experience_years} years")
            
            # Add current role
            current_role = resume.current_role
            if current_role:
                context_parts.append(f"Current Role: {current_role}")
            
            # Add education
            education_level = resume.education_level
            if education_level:
                context_parts.append(f"Education: {education_level}")
            
            return "\n".join(context_parts) if context_parts else "Basic profile available."
            
        except Exception:
            return "Resume data available but parsing failed."
    
    def _create_prompt(self, suggestion_type: str, context: str, resume_context: str) -> str:
        """Create prompt based on suggestion type"""
        
        base_prompt = f"""
Context from conversation:
{context}

User background:
{resume_context}

Suggestion type: {suggestion_type}
"""
        
        if suggestion_type == "answer":
            return base_prompt + """
Based on the question being asked, provide a structured answer suggestion that incorporates the user's background and experience. Format as bullet points.
"""
        
        elif suggestion_type == "question":
            return base_prompt + """
Suggest thoughtful follow-up questions the user could ask to show engagement and interest. Make them relevant to the conversation.
"""
        
        elif suggestion_type == "tip":
            return base_prompt + """
Provide helpful interview tips or advice based on what's happening in the conversation. Focus on practical suggestions.
"""
        
        elif suggestion_type == "code":
            return base_prompt + """
If this is a coding interview, provide code examples or algorithmic approaches. Keep it concise and relevant to the discussion.
"""
        
        else:
            return base_prompt + """
Provide general helpful suggestions for this interview situation. Be concise and actionable.
"""
    
    async def chat(self, message: str, user_id: int) -> str:
        """General chat with AI"""
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an AI interview assistant. Help with interview preparation, tips, and general career advice. Be helpful and encouraging."
                    },
                    {
                        "role": "user",
                        "content": message
                    }
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}"
    
    async def generate_interview_questions(self, job_title: str, company: str, resume: Optional[Resume]) -> List[str]:
        """Generate potential interview questions"""
        
        resume_context = self._get_resume_context(resume)
        
        prompt = f"""
Generate 5 relevant interview questions for a {job_title} position at {company}.

Candidate background:
{resume_context}

Provide questions that are:
- Specific to the role and company
- Appropriate for the candidate's experience level
- Mix of technical and behavioral questions
- Relevant to current industry trends

Format as a numbered list.
"""
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert interview coach. Generate relevant, thoughtful interview questions."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=400,
                temperature=0.8
            )
            
            content = response.choices[0].message.content.strip()
            # Parse numbered list into individual questions
            questions = [q.strip() for q in content.split('\n') if q.strip() and q[0].isdigit()]
            return questions
            
        except Exception as e:
            return [f"Error generating questions: {str(e)}"]
