import os
import google.generativeai as genai
from dotenv import load_dotenv
from typing import Dict, List, Optional
import json

# Load environment variables
load_dotenv()

# Configure Gemini
GEMINI_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in environment variables")

genai.configure(api_key=GEMINI_API_KEY)

# Initialize the model with Gemini 2.0 Flash
model = genai.GenerativeModel('gemini-2.0-flash')

def generate_learning_path(skill: str, current_level: int, target_level: int) -> Dict:
    """
    Generate a personalized learning path using Gemini.
    
    Args:
        skill: The skill to learn/improve
        current_level: Current proficiency level (1-5)
        target_level: Target proficiency level (1-5)
        
    Returns:
        Dictionary containing learning path details
    """
    prompt = f"""
    You are a career development and skills expert. Generate a CONCISE and ACTIONABLE learning path 
    for someone who wants to improve their {skill} skills from level {current_level} to level {target_level}.
    
    IMPORTANT: Be specific and practical. Focus on the most effective resources and steps.
    
    Provide the following in a JSON format:
    1. current_level_desc: 1-2 sentences about what level {current_level} means for {skill}
    2. target_level_desc: 1-2 sentences about what level {target_level} means for {skill}
    3. learning_path: 3-5 key milestones (be specific and time-bound)
    4. resources: 2-3 high-quality resources (include type, title, and direct URL)
    5. time_commitment: Realistic time estimate (e.g., "2-3 hours per week for 8 weeks")
    6. projects: 1-2 practical projects to apply the skill
    
    Example format (you must use this exact structure):
    {{
        "skill": "{skill}",
        "current_level": {current_level},
        "target_level": {target_level},
        "current_level_desc": "...",
        "target_level_desc": "...",
        "learning_path": ["Milestone 1", "Milestone 2", ...],
        "resources": [
            {{"type": "Course", "title": "...", "url": "..."}},
            {{"type": "Book", "title": "...", "url": "..."}}
        ],
        "time_commitment": "...",
        "projects": ["Project 1", "Project 2"]
    }}
    
    IMPORTANT: Only return the JSON object, nothing else. No markdown formatting or additional text.
    """
    
    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Clean the response to ensure it's valid JSON
        response_text = response_text.replace('```json', '').replace('```', '').strip()
        response_data = json.loads(response_text)
        
        return {
            'success': True,
            'data': response_data
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def analyze_skill_gap(resume_skills: Dict[str, int], job_requirements: Dict[str, int]) -> Dict:
    """
    Analyze skill gaps and generate personalized recommendations.
    
    Args:
        resume_skills: Dictionary of skills from resume with proficiency levels
        job_requirements: Dictionary of required skills with desired levels
        
    Returns:
        Dictionary containing gap analysis and recommendations
    """
    gap_analysis = {
        'missing_skills': {},
        'matching_skills': {},
        'below_level_skills': {}
    }
    
    # Check for missing and below-level skills
    for skill, req_level in job_requirements.items():
        if skill not in resume_skills:
            gap_analysis['missing_skills'][skill] = {
                'required_level': req_level,
                'current_level': 0
            }
        else:
            if resume_skills[skill] >= req_level:
                gap_analysis['matching_skills'][skill] = {
                    'required_level': req_level,
                    'current_level': resume_skills[skill]
                }
            else:
                gap_analysis['below_level_skills'][skill] = {
                    'required_level': req_level,
                    'current_level': resume_skills[skill]
                }
    
    # Generate learning paths for skills that need improvement
    learning_paths = {}
    
    # For missing skills
    for skill, data in gap_analysis['missing_skills'].items():
        result = generate_learning_path(
            skill=skill,
            current_level=0,
            target_level=data['required_level']
        )
        if result['success']:
            learning_paths[skill] = result['data']
    
    # For below-level skills
    for skill, data in gap_analysis['below_level_skills'].items():
        result = generate_learning_path(
            skill=skill,
            current_level=data['current_level'],
            target_level=data['required_level']
        )
        if result['success']:
            learning_paths[skill] = result['data']
    
    return {
        'gap_analysis': gap_analysis,
        'learning_paths': learning_paths
    }

def get_skill_improvement_tips(skill: str, current_level: int) -> Dict:
    """
    Get quick improvement tips for a specific skill and level.
    
    Args:
        skill: The skill to get tips for
        current_level: Current proficiency level (1-5)
        
    Returns:
        Dictionary containing improvement tips
    """
    prompt = f"""
    Provide 3-5 SPECIFIC and ACTIONABLE tips for someone at level {current_level} in {skill} 
    to improve to level {current_level + 1}.
    
    For each tip, be CONCISE but specific enough that someone could immediately act on it.
    Focus on practical, concrete actions rather than general advice.
    
    Format the response as a JSON object with this exact structure:
    {{
        "skill": "{skill}",
        "current_level": {current_level},
        "target_level": {current_level + 1},
        "tips": [
            "Specific action 1 with clear steps",
            "Specific action 2 with clear steps",
            "Specific action 3 with clear steps"
        ]
    }}
    
    Only return the JSON object, nothing else. No markdown formatting or additional text.
    """
    
    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        response_text = response_text.replace('```json', '').replace('```', '').strip()
        response_data = json.loads(response_text)
        
        return {
            'success': True,
            'data': response_data
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
