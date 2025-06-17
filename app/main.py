import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import json
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv

# Add the parent directory to the Python path
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

# Now import from the app package
from app.gemini_service import analyze_skill_gap, get_skill_improvement_tips

# Load environment variables
load_dotenv()

# Check if API key is set
if not os.getenv('GOOGLE_API_KEY'):
    st.warning("⚠️ Please set the GOOGLE_API_KEY in your .env file to enable AI-powered recommendations.")
    st.stop()

# Set page config
st.set_page_config(
    page_title="Skill Gap Analyzer",
    page_icon="📊",
    layout="wide"
)

# Initialize session state
if 'resume_data' not in st.session_state:
    st.session_state.resume_data = None
if 'job_requirements' not in st.session_state:
    st.session_state.job_requirements = None
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None

class SkillAnalyzer:
    """Core class for skill gap analysis with Gemini integration."""
    
    def __init__(self):
        # Initialize with some sample data - in production, this would come from a database
        self.skill_ontology = self._load_skill_ontology()
    
    def _load_skill_ontology(self) -> Dict:
        """Load skill ontology from file."""
        ontology_path = Path(__file__).parent.parent / 'data' / 'skill_ontology.json'
        if ontology_path.exists():
            with open(ontology_path, 'r') as f:
                return json.load(f)
        return {}
    
    def analyze_skills(self, resume_skills: Dict, job_requirements: Dict) -> Dict:
        """
        Analyze the gap between resume skills and job requirements using Gemini.
        
        Args:
            resume_skills: Dictionary of skills from resume with proficiency levels
            job_requirements: Dictionary of required skills with desired proficiency levels
            
        Returns:
            Dictionary containing gap analysis results and learning paths
        """
        # Use Gemini-powered analysis
        analysis = analyze_skill_gap(resume_skills, job_requirements)
        return analysis

def main():
    st.title("Skill Gap Analysis & Upskilling Agent")
    st.write("Analyze employee skills against job requirements and get personalized upskilling recommendations.")
    
    # Initialize the analyzer
    analyzer = SkillAnalyzer()
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Home", "Analyze Skills", "Upskilling Paths"])
    
    if page == "Home":
        show_home()
    elif page == "Analyze Skills":
        show_skill_analysis(analyzer)
    elif page == "Upskilling Paths":
        show_upskilling_paths()

def show_home():
    """Display the home page with instructions."""
    st.header("Welcome to Skill Gap Analyzer")
    st.write("""
    This tool helps you analyze the gap between employee skills and job role requirements,
    and provides personalized upskilling recommendations.
    
    ### How to use:
    1. Go to 'Analyze Skills' to upload or enter skill data
    2. View the skill gap analysis
    3. Get personalized upskilling recommendations in 'Upskilling Paths'
    """)

def show_skill_analysis(analyzer):
    """Display the skill analysis interface."""
    st.header("Skill Gap Analysis")
    
    # Input section
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Employee Skills")
        st.text_area("Paste employee skills (JSON format)", 
                    value='{"Python": 3, "Machine Learning": 2, "Project Management": 1}',
                    key='resume_skills')
    
    with col2:
        st.subheader("Job Requirements")
        st.text_area("Paste job requirements (JSON format)",
                    value='{"Python": 4, "Machine Learning": 3, "Data Analysis": 3, "Team Leadership": 2}',
                    key='job_reqs')
    
    if st.button("Analyze Skills"):
        try:
            resume_skills = json.loads(st.session_state.resume_skills)
            job_requirements = json.loads(st.session_state.job_reqs)
            
            # Perform analysis
            analysis = analyzer.analyze_skills(resume_skills, job_requirements)
            st.session_state.analysis_results = analysis
            
            # Display results
            display_analysis_results(analysis)
            
        except json.JSONDecodeError:
            st.error("Invalid JSON format. Please check your input.")

def display_analysis_results(analysis: Dict):
    """Display the results of the skill gap analysis."""
    st.subheader("Analysis Results")
    
    # Safely get the gap analysis results
    gap_analysis = analysis.get('gap_analysis', {})
    
    # Calculate summary metrics with safe dictionary access
    matching_skills = gap_analysis.get('matching_skills', {})
    below_level_skills = gap_analysis.get('below_level_skills', {})
    missing_skills = gap_analysis.get('missing_skills', {})
    
    total_required = len(matching_skills) + len(below_level_skills) + len(missing_skills)
    matched = len(matching_skills)
    below_level = len(below_level_skills)
    missing = len(missing_skills)
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Skills Matched", f"{matched}/{total_required}")
    with col2:
        st.metric("Skills Below Level", f"{below_level}/{total_required}")
    with col3:
        st.metric("Skills Missing", f"{missing}/{total_required}")
    
    # Display detailed results in tabs
    tab1, tab2, tab3 = st.tabs(["Matching Skills", "Needs Improvement", "Missing Skills"])
    
    with tab1:
        if matching_skills:
            df_matched = pd.DataFrame([{
                'Skill': skill,
                'Your Level': data.get('current_level', 'N/A'),
                'Required Level': data.get('required_level', 'N/A')
            } for skill, data in matching_skills.items()])
            st.dataframe(df_matched, use_container_width=True)
        else:
            st.info("No skills match the required levels.")
    
    with tab2:
        if below_level_skills:
            df_below = pd.DataFrame([{
                'Skill': skill,
                'Your Level': data.get('current_level', 'N/A'),
                'Required Level': data.get('required_level', 'N/A'),
                'Gap': data.get('required_level', 0) - data.get('current_level', 0)
            } for skill, data in below_level_skills.items()])
            st.dataframe(df_below, use_container_width=True)
        else:
            st.info("No skills are below the required level.")
    
    with tab3:
        if missing_skills:
            df_missing = pd.DataFrame([{
                'Skill': skill,
                'Required Level': data.get('required_level', 'N/A')
            } for skill, data in missing_skills.items()])
            st.dataframe(df_missing, use_container_width=True)
        else:
            st.info("No missing skills found.")

def display_learning_path(learning_path: Dict):
    """Display a learning path in an expandable section."""
    if not learning_path or 'data' not in learning_path or not learning_path['success']:
        st.warning("Could not generate learning path. Please try again later.")
        return
    
    data = learning_path['data']
    skill = data.get('skill', 'Unknown Skill')
    
    with st.expander(f"{skill} - Path to Level {data.get('target_level', '?')}"):
        # Current and target level descriptions
        st.markdown(f"**Current Level ({data.get('current_level', '?')}):** {data.get('current_level_desc', 'Not specified')}")
        st.markdown(f"**Target Level ({data.get('target_level', '?')}):** {data.get('target_level_desc', 'Not specified')}")
        
        # Learning path milestones
        st.markdown("### 🎯 Learning Path")
        for i, milestone in enumerate(data.get('learning_path', []), 1):
            st.markdown(f"{i}. {milestone}")
        
        # Recommended resources
        st.markdown("### 📚 Recommended Resources")
        for resource in data.get('resources', []):
            st.markdown(f"- **{resource.get('type', 'Resource')}:** "
                      f"[{resource.get('title', 'Untitled')}]({resource.get('url', '#')})")
        
        # Practice projects
        st.markdown("### 🛠️ Practice Projects")
        for i, project in enumerate(data.get('projects', []), 1):
            st.markdown(f"{i}. {project}")
        
        # Time commitment
        st.markdown(f"### ⏱️ Estimated Time Commitment: {data.get('time_commitment', 'Not specified')}")

def show_upskilling_paths():
    """Display AI-powered upskilling recommendations."""
    st.header("Personalized Upskilling Paths")
    
    if 'analysis_results' not in st.session_state or not st.session_state.analysis_results:
        st.warning("Please run a skill analysis first to get personalized recommendations.")
        return
    
    analysis = st.session_state.analysis_results
    
    # Show loading state while generating recommendations
    with st.spinner("Generating personalized learning paths..."):
        # Check if we already have learning paths in the analysis
        if 'learning_paths' not in analysis or not analysis['learning_paths']:
            st.error("Could not generate learning paths. Please check your API key and try again.")
            return
        
        learning_paths = analysis['learning_paths']
        
        # Display missing skills section
        if 'gap_analysis' in analysis and analysis['gap_analysis'].get('missing_skills'):
            st.subheader("🆕 New Skills to Acquire")
            for skill, data in analysis['gap_analysis']['missing_skills'].items():
                if skill in learning_paths:
                    display_learning_path({'success': True, 'data': learning_paths[skill]})
        
        # Display skills to improve section
        if 'gap_analysis' in analysis and analysis['gap_analysis'].get('below_level_skills'):
            st.subheader("📈 Skills to Improve")
            for skill, data in analysis['gap_analysis']['below_level_skills'].items():
                if skill in learning_paths:
                    display_learning_path({'success': True, 'data': learning_paths[skill]})
        
        # Display matching skills section
        if 'gap_analysis' in analysis and analysis['gap_analysis'].get('matching_skills'):
            with st.expander("✅ Skills You Already Have"):
                for skill, data in analysis['gap_analysis']['matching_skills'].items():
                    st.markdown(f"- **{skill}** (Level {data['current_level']} - Target: {data['required_level']})")
                    
                    # Show tips for further improvement
                    if st.button(f"Get tips to master {skill}", key=f"tips_{skill}"):
                        with st.spinner(f"Generating tips for {skill}..."):
                            tips = get_skill_improvement_tips(skill, data['current_level'])
                            if tips['success'] and 'tips' in tips['data']:
                                st.markdown("**Tips to improve:**")
                                for tip in tips['data']['tips']:
                                    st.markdown(f"- {tip}")
                            else:
                                st.warning("Could not generate tips. Please try again later.")
        # This is intentionally left empty as the matching skills are now handled in the expander above

if __name__ == "__main__":
    main()
