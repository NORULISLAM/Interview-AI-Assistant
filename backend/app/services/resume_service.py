"""
Resume parsing and processing service
"""
import json
import tempfile
from typing import Dict, Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import spacy
from pdfminer.high_level import extract_text as pdf_extract_text
from docx import Document
import asyncio
from concurrent.futures import ThreadPoolExecutor

from app.models.user import Resume
from app.schemas.user import ResumeCreate


class ResumeService:
    """Resume parsing and processing service"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.nlp = spacy.load("en_core_web_sm")
        self.executor = ThreadPoolExecutor(max_workers=2)
    
    async def create_resume(self, user_id: int, resume_data: ResumeCreate) -> Resume:
        """Create new resume record"""
        resume = Resume(
            user_id=user_id,
            filename=resume_data.filename,
            file_size=resume_data.file_size,
            mime_type=resume_data.mime_type,
            storage_uri=resume_data.storage_uri,
            sha256_hash=resume_data.sha256_hash
        )
        
        self.db.add(resume)
        await self.db.commit()
        await self.db.refresh(resume)
        
        return resume
    
    async def parse_resume(self, content: bytes, mime_type: str) -> Dict[str, Any]:
        """Parse resume content and extract structured data"""
        
        # Extract text based on file type
        if mime_type == "application/pdf":
            text = await self._extract_pdf_text(content)
        elif mime_type in ["application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
            text = await self._extract_docx_text(content)
        else:
            text = content.decode('utf-8', errors='ignore')
        
        # Parse with spaCy
        doc = self.nlp(text)
        
        # Extract entities and information
        parsed_data = {
            "raw_text": text,
            "entities": self._extract_entities(doc),
            "skills": self._extract_skills(doc),
            "education": self._extract_education(doc),
            "experience": self._extract_experience(doc),
            "contact_info": self._extract_contact_info(doc),
            "summary": self._extract_summary(text)
        }
        
        return parsed_data
    
    async def _extract_pdf_text(self, content: bytes) -> str:
        """Extract text from PDF"""
        loop = asyncio.get_event_loop()
        
        def extract():
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
                tmp.write(content)
                tmp.flush()
                return pdf_extract_text(tmp.name)
        
        return await loop.run_in_executor(self.executor, extract)
    
    async def _extract_docx_text(self, content: bytes) -> str:
        """Extract text from DOCX"""
        loop = asyncio.get_event_loop()
        
        def extract():
            with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as tmp:
                tmp.write(content)
                tmp.flush()
                doc = Document(tmp.name)
                return '\n'.join([paragraph.text for paragraph in doc.paragraphs])
        
        return await loop.run_in_executor(self.executor, extract)
    
    def _extract_entities(self, doc) -> Dict[str, list]:
        """Extract named entities"""
        entities = {
            "PERSON": [],
            "ORG": [],
            "GPE": [],  # Geopolitical entities
            "DATE": [],
            "MONEY": [],
            "PERCENT": []
        }
        
        for ent in doc.ents:
            if ent.label_ in entities:
                entities[ent.label_].append(ent.text)
        
        return entities
    
    def _extract_skills(self, doc) -> list:
        """Extract technical skills"""
        skills = []
        
        # Common technical skills patterns
        skill_patterns = [
            r'\b(Python|Java|JavaScript|TypeScript|React|Vue|Angular|Node\.js|Django|Flask|FastAPI)\b',
            r'\b(AWS|Azure|GCP|Docker|Kubernetes|Git|SQL|MongoDB|PostgreSQL)\b',
            r'\b(Machine Learning|AI|Data Science|Analytics|Statistics)\b'
        ]
        
        import re
        text = doc.text
        
        for pattern in skill_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            skills.extend(matches)
        
        return list(set(skills))
    
    def _extract_education(self, doc) -> list:
        """Extract education information"""
        education = []
        
        # Look for education-related patterns
        education_keywords = ['university', 'college', 'degree', 'bachelor', 'master', 'phd', 'diploma']
        
        sentences = [sent.text for sent in doc.sents]
        
        for sent in sentences:
            if any(keyword in sent.lower() for keyword in education_keywords):
                education.append(sent.strip())
        
        return education
    
    def _extract_experience(self, doc) -> list:
        """Extract work experience"""
        experience = []
        
        # Look for experience-related patterns
        exp_keywords = ['experience', 'worked', 'responsible', 'developed', 'managed', 'led']
        
        sentences = [sent.text for sent in doc.sents]
        
        for sent in sentences:
            if any(keyword in sent.lower() for keyword in exp_keywords):
                experience.append(sent.strip())
        
        return experience
    
    def _extract_contact_info(self, doc) -> Dict[str, str]:
        """Extract contact information"""
        contact = {}
        
        import re
        
        # Email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, doc.text)
        if emails:
            contact['email'] = emails[0]
        
        # Phone
        phone_pattern = r'(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'
        phones = re.findall(phone_pattern, doc.text)
        if phones:
            contact['phone'] = ''.join(phones[0])
        
        return contact
    
    def _extract_summary(self, text: str) -> str:
        """Extract or generate summary"""
        # Simple summary - first few sentences
        sentences = text.split('.')
        summary = '. '.join(sentences[:3]) + '.'
        return summary[:500]  # Limit length
    
    async def update_parsed_content(self, resume_id: int, parsed_data: Dict[str, Any]):
        """Update resume with parsed content"""
        result = await self.db.execute(
            select(Resume).where(Resume.id == resume_id)
        )
        resume = result.scalar_one_or_none()
        
        if resume:
            resume.parsed_json = json.dumps(parsed_data)
            
            # Extract key fields for quick access
            skills = parsed_data.get('skills', [])
            resume.skills = json.dumps(skills) if skills else None
            
            # Estimate experience years (simple heuristic)
            experience_text = ' '.join(parsed_data.get('experience', []))
            years = self._estimate_experience_years(experience_text)
            resume.experience_years = years
            
            # Extract education level
            education = parsed_data.get('education', [])
            resume.education_level = self._extract_highest_education(education)
            
            # Extract current role (from entities)
            entities = parsed_data.get('entities', {})
            persons = entities.get('PERSON', [])
            resume.current_role = persons[0] if persons else None
            
            await self.db.commit()
            await self.db.refresh(resume)
    
    def _estimate_experience_years(self, experience_text: str) -> Optional[int]:
        """Estimate years of experience from text"""
        import re
        
        # Look for year patterns
        year_patterns = [
            r'(\d+)\+?\s*years?',
            r'(\d+)\+?\s*yrs?',
            r'experience.*?(\d+)',
        ]
        
        for pattern in year_patterns:
            matches = re.findall(pattern, experience_text, re.IGNORECASE)
            if matches:
                try:
                    return int(matches[0])
                except ValueError:
                    continue
        
        return None
    
    def _extract_highest_education(self, education: list) -> Optional[str]:
        """Extract highest education level"""
        if not education:
            return None
        
        education_text = ' '.join(education).lower()
        
        if 'phd' in education_text or 'doctorate' in education_text:
            return 'PhD'
        elif 'master' in education_text:
            return 'Masters'
        elif 'bachelor' in education_text or 'bsc' in education_text or 'ba' in education_text:
            return 'Bachelors'
        elif 'diploma' in education_text:
            return 'Diploma'
        
        return 'Other'
