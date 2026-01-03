# Quick Reference Guide

A cheat sheet for common tasks in the AI-Testing repository.

## Common Commands

### Setup
```bash
# Clone and setup
git clone https://github.com/darshil0/AI-Testing.git
cd AI-Testing
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

### Running Evaluations
```bash
# Navigate to evaluation directory
cd ai_evaluation

# Run with different models
python3 run_evaluation.py                    # Simulated (no API needed)
python3 run_evaluation.py --model openai     # OpenAI GPT models
python3 run_evaluation.py --model anthropic  # Anthropic Claude models

# Custom directories
python3 run_evaluation.py --test-cases-dir my_tests --results-dir my_results
```

### Managing Test Cases
```bash
# Create a new test case
cd ai_evaluation/test_cases
nano my_new_test.txt  # or use your preferred editor

# List test cases
ls *.txt

# View a test case
cat reasoning_logic_puzzle.txt
```

### Viewing Results
```bash
# List all results
ls ai_evaluation/results/

# View latest result (macOS/Linux)
ls -t ai_evaluation/results/*.json | head -1 | xargs cat | python -m json.tool

# View specific result with formatted JSON
cat ai_evaluation/results/test_name_20251117_143045.json | python -m json.tool

# Count total results
ls ai_evaluation/results/*.json | wc -l
```

## File Structure
```
AI-Testing/
├── README.md                  # Main documentation
├── CONTRIBUTING.md            # Contribution guidelines
├── SETUP.md                   # Detailed setup guide
├── LICENSE                    # MIT License
├── requirements.txt           # Python dependencies
├── .env.example              # Environment template
├── .env                      # Your API keys (not in git)
├── .gitignore               # Git ignore rules
└── ai_evaluation/
    ├── run_evaluation.py    # Main script
    ├── test_cases/         # Your test files (.txt)
    │   ├── reasoning_logic_puzzle.txt
    │   ├── creativity_story.txt
    │   └── ...
    └── results/            # Evaluation outputs (.json)
        ├── test1_20251117_143045.json
        └── ...
```

## Test Case Format
```
Category: [reasoning/creativity/factual/coding/safety]
Difficulty: [easy/medium/hard]

[Your test prompt or instructions here]
```

## Result File Format
```json
{
  "test_case_name": "test_name",
  "timestamp": "2025-11-17T14:30:45",
  "test_case": "original test content",
  "response": "AI model response",
  "metadata": {
    "model_type": "anthropic",
    "max_tokens": 2000,
    "temperature": 0.7
  }
}
```

## Git Workflow
```bash
# Check status
git status

# Create feature branch
git checkout -b feature/new-test-cases

# Add changes
git add .
git commit -m "Add: New reasoning test cases"

# Push to GitHub
git push origin feature/new-test-cases

# Update from main
git checkout main
git pull origin main
```

## Environment Variables
```bash
# Required for API access
OPENAI_API_KEY=sk-proj-...
ANTHROPIC_API_KEY=sk-ant-...

# Optional configuration
MAX_TOKENS=2000
TEMPERATURE=0.7
TIMEOUT_SECONDS=60
```

## Python Virtual Environment
```bash
# Activate
source venv/bin/activate           # macOS/Linux
venv\Scripts\activate              # Windows

# Deactivate
deactivate

# Reinstall dependencies
pip install -r requirements.txt

# Update dependencies
pip install -r requirements.txt --upgrade

# Check installed packages
pip list
```

## Categories for Test Cases

- **Reasoning**: Logic, math, problem-solving
- **Creativity**: Writing, brainstorming, art
- **Factual**: Knowledge, current events, facts
- **Coding**: Programming, debugging, algorithms
- **Safety**: Harmful content, ethics, bias
- **Language**: Translation, grammar, style

## Useful Python Snippets

### Batch Process Results
```python
import json
from pathlib import Path

results_dir = Path("ai_evaluation/results")
for result_file in results_dir.glob("*.json"):
    with open(result_file) as f:
        data = json.load(f)
        print(f"{data['test_case_name']}: {len(data['response'])} chars")
```

### Compare Model Responses
```python
import json
from pathlib import Path

def load_result(filename):
    with open(f"ai_evaluation/results/{filename}") as f:
        return json.load(f)

# Compare two results for same test
result1 = load_result("test_20251117_143045.json")
result2 = load_result("test_20251117_150000.json")

print("Test:", result1['test_case_name'])
print("Model 1:", result1['metadata']['model_type'])
print("Model 2:", result2['metadata']['model_type'])
```

## API Model Options

### OpenAI Models
- `gpt-4-turbo`
- `gpt-4`
- `gpt-3.5-turbo`

### Anthropic Models
- `claude-sonnet-4-20250514`
- `claude-opus-4-20250514`
- `claude-haiku-4-20250514`

## Troubleshooting Quick Fixes

```bash
# Module not found
pip install -r requirements.txt

# Permission denied
chmod +x ai_evaluation/run_evaluation.py

# Wrong Python version
python3 --version  # Check version
python3.11 -m venv venv  # Use specific version

# API key issues
cat .env  # Verify keys exist
export ANTHROPIC_API_KEY=sk-ant-...  # Temporary set

# Clear results
rm ai_evaluation/results/*.json  # Be careful!

# Reset virtual environment
deactivate
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Help Commands
```bash
# Python help
python3 run_evaluation.py --help

# Git help
git --help
git commit --help

# Pip help
pip --help
pip install --help
```

---

**More details:** See [README.md](README.md) and [SETUP.md](SETUP.md)
