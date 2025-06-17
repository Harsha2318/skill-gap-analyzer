import re
import PyPDF2
import docx
import spacy
from pathlib import Path
from typing import Dict, List, Optional, Union
import json

class ResumeParser:
    """
    A class to parse resumes in various formats (PDF, DOCX, TXT) and extract skills.
    """
    
    def __init__(self):
        """Initialize the resume parser with NLP model."""
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            # If the model is not found, download it
            import subprocess
            import sys
            subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
            self.nlp = spacy.load("en_core_web_sm")
        
        # Load skill ontology
        self.skill_ontology = self._load_skill_ontology()
    
    def _load_skill_ontology(self) -> Dict:
        """Load the skill ontology from JSON file."""
        ontology_path = Path(__file__).parent.parent / 'data' / 'skill_ontology.json'
        if ontology_path.exists():
            with open(ontology_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"skills": {}}
    
    def extract_text_from_pdf(self, file_path: Union[str, Path]) -> str:
        """Extract text from a PDF file."""
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text
    
    def extract_text_from_docx(self, file_path: Union[str, Path]) -> str:
        """Extract text from a DOCX file."""
        doc = docx.Document(file_path)
        return "\n".join([paragraph.text for paragraph in doc.paragraphs])
    
    def extract_text_from_txt(self, file_path: Union[str, Path]) -> str:
        """Extract text from a plain text file."""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    
    def extract_text(self, file_path: Union[str, Path]) -> str:
        """Extract text from a file based on its extension."""
        file_path = Path(file_path)
        suffix = file_path.suffix.lower()
        
        if suffix == '.pdf':
            return self.extract_text_from_pdf(file_path)
        elif suffix == '.docx':
            return self.extract_text_from_docx(file_path)
        elif suffix == '.txt':
            return self.extract_text_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file format: {suffix}")
    
    def _extract_skills_with_nlp(self, text: str) -> List[str]:
        """Extract skills using NLP techniques."""
        doc = self.nlp(text.lower())
        
        # Extract noun chunks and named entities
        skills = set()
        
        # Check for skills in the skill ontology
        for category, skills_data in self.skill_ontology.get('skills', {}).items():
            for skill in skills_data.keys():
                # Simple keyword matching (can be enhanced with more sophisticated matching)
                if skill.lower() in text.lower():
                    skills.add(skill)
        
        # Add additional NLP-based extraction
        for token in doc:
            # Check for skills mentioned with proficiency levels
            if token.text.lower() in ['experience', 'proficient', 'skilled', 'familiar'] and token.head.text.lower() != 'with':
                # Look for skills mentioned nearby
                for child in token.head.children:
                    if child.dep_ in ('dobj', 'attr', 'conj'):
                        skills.add(child.text)
        
        return list(skills)
    
    def _estimate_proficiency(self, skill: str, text: str) -> int:
        """Estimate proficiency level (1-5) based on context."""
        text_lower = text.lower()
        skill_lower = skill.lower()
        
        # Look for proficiency indicators
        if any(phrase in text_lower for phrase in [
            f'expert in {skill_lower}',
            f'advanced {skill_lower}',
            f'senior {skill_lower}',
            f'5+ years of {skill_lower}'
        ]):
            return 5  # Expert
        
        if any(phrase in text_lower for phrase in [
            f'proficient in {skill_lower}',
            f'strong {skill_lower} skills',
            f'3-5 years of {skill_lower}'
        ]):
            return 4  # Advanced
        
        if any(phrase in text_lower for phrase in [
            f'experience with {skill_lower}',
            f'working knowledge of {skill_lower}',
            f'1-3 years of {skill_lower}'
        ]):
            return 3  # Intermediate
        
        if any(phrase in text_lower for phrase in [
            f'familiar with {skill_lower}',
            f'basic {skill_lower} knowledge',
            f'beginner level {skill_lower}'
        ]):
            return 2  # Basic
        
        return 1  # Awareness level
    
    def parse_resume(self, file_path: Union[str, Path]) -> Dict[str, int]:
        """
        Parse a resume and extract skills with estimated proficiency levels.
        
        Args:
            file_path: Path to the resume file (PDF, DOCX, or TXT)
            
        Returns:
            Dictionary mapping skills to proficiency levels (1-5)
        """
        # Extract text from the resume
        try:
            text = self.extract_text(file_path)
        except Exception as e:
            raise ValueError(f"Error extracting text from {file_path}: {str(e)}")
        
        # Extract skills using NLP
        skills = self._extract_skills_with_nlp(text)
        
        # Estimate proficiency for each skill
        skill_levels = {}
        for skill in skills:
            # Only include skills that are in our ontology
            skill_found = False
            for category, skills_data in self.skill_ontology.get('skills', {}).items():
                if skill in skills_data:
                    skill_found = True
                    break
            
            if skill_found:
                skill_levels[skill] = self._estimate_proficiency(skill, text)
        
        return skill_levels

# Example usage
if __name__ == "__main__":
    parser = ResumeParser()
    
    # Example with a sample text (in practice, you would pass a file path)
    sample_resume = """
    John Doe
    Senior Software Engineer
    
    SKILLS
    - Python (5+ years)
    - Machine Learning (Expert)
    - Data Analysis (Proficient)
    - Team Leadership (3 years experience)
    
    EXPERIENCE
    - Led a team of 5 developers to build a recommendation system using Python and TensorFlow
    - Developed and deployed machine learning models in production
    - Mentored junior developers in Python best practices
    """
    
    # Save sample to a temporary file
    import tempfile
    with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as f:
        f.write(sample_resume.encode('utf-8'))
        temp_path = f.name
    
    try:
        skills = parser.parse_resume(temp_path)
        print("Extracted skills:")
        for skill, level in skills.items():
            print(f"- {skill}: Level {level}")
    finally:
        # Clean up temporary file
        import os
        os.unlink(temp_path)
