# Skill Gap Analysis & Upskilling Agent

A powerful tool that analyzes employee skills against job role requirements and suggests personalized upskilling paths.

## Features

- **Resume Analysis**: Parse and extract skills from resumes
- **Skill Gap Analysis**: Compare employee skills with job requirements
- **Personalized Learning Paths**: Get customized upskilling recommendations
- **Interactive Dashboard**: Visualize skill gaps and progress
- **Multi-format Support**: Works with PDF, DOCX, and text resumes

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/skill-gap-analyzer.git
   cd skill-gap-analyzer
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # On Windows
   source venv/bin/activate  # On macOS/Linux
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Download the spaCy language model:
   ```bash
   python -m spacy download en_core_web_sm
   ```

## Usage

1. Start the Streamlit application:
   ```bash
   streamlit run app/main.py
   ```

2. Open your browser and navigate to `http://localhost:8501`

3. Use the navigation menu to:
   - **Home**: View instructions and overview
   - **Analyze Skills**: Upload or enter skill data
   - **Upskilling Paths**: View personalized recommendations

## Data Format

### Employee Skills
Input format (JSON):
```json
{
  "Python": 3,
  "Machine Learning": 2,
  "Project Management": 1
}
```

### Job Requirements
Input format (JSON):
```json
{
  "Python": 4,
  "Machine Learning": 3,
  "Data Analysis": 3,
  "Team Leadership": 2
}
```

## Project Structure

```
skill-gap-analyzer/
├── app/
│   ├── __init__.py
│   ├── main.py              # Main Streamlit application
│   ├── resume_parser.py     # Resume parsing functionality
│   └── utils.py            # Utility functions
├── data/
│   └── skill_ontology.json  # Skill taxonomy and relationships
├── models/
│   └── skill_matcher.py    # Skill matching algorithms
├── tests/                   # Unit and integration tests
├── .env.example            # Environment variables template
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Contributing

1. Fork the repository
2. Create a new branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with ❤️ by [Harsha P]
- Skill taxonomy based on O*NET and ESCO frameworks
- Powered by Streamlit, spaCy, and scikit-learn
