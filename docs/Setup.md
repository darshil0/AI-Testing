# Setup Guide for AI-Testing

This guide will walk you through setting up the AI-Testing evaluation framework on your local machine.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8 or higher** - [Download Python](https://www.python.org/downloads/)
- **pip** (Python package manager) - Usually comes with Python
- **git** - [Download Git](https://git-scm.com/downloads)

### Verify Installations

```bash
python3 --version  # Should show 3.8 or higher
pip3 --version
git --version
```

## Step-by-Step Setup

### 1. Clone the Repository

```bash
git clone https://github.com/darshil0/AI-Testing.git
cd AI-Testing
```

### 2. Create a Virtual Environment

Creating a virtual environment keeps your project dependencies isolated:

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

You should see `(venv)` appear in your terminal prompt, indicating the virtual environment is active.

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install all necessary Python packages including:
- OpenAI API client
- Anthropic API client
- pandas for data analysis
- python-dotenv for environment management

### 4. Configure Environment Variables

Create a `.env` file in the root directory:

```bash
cp .env.example .env
```

Edit the `.env` file with your actual API keys:

```bash
# On macOS/Linux
nano .env

# On Windows
notepad .env
```

**Getting API Keys:**

- **OpenAI**: Visit [OpenAI Platform](https://platform.openai.com/api-keys)
- **Anthropic**: Visit [Anthropic Console](https://console.anthropic.com/)

Example `.env` configuration:
```
OPENAI_API_KEY=sk-proj-...your-key...
ANTHROPIC_API_KEY=sk-ant-...your-key...
MAX_TOKENS=2000
TEMPERATURE=0.7
```

### 5. Create Directory Structure

Ensure the necessary directories exist:

```bash
mkdir -p ai_evaluation/test_cases
mkdir -p ai_evaluation/results
```

### 6. Add Test Cases

Copy the example test cases or create your own:

**Example test case** (`ai_evaluation/test_cases/simple_test.txt`):
```
Category: reasoning
Difficulty: easy

What is 2 + 2? Explain your answer.
```

Create test case files:
```bash
cd ai_evaluation/test_cases
echo "What is the capital of France?" > geography_test.txt
cd ../..
```

### 7. Verify Setup

Test that everything is working:

```bash
cd ai_evaluation
python3 run_evaluation.py --model simulated
```

You should see output indicating test cases are being processed and results saved.

## Running Evaluations

### Basic Usage

**Run with simulated responses** (no API keys needed):
```bash
python3 run_evaluation.py
```

**Run with OpenAI:**
```bash
python3 run_evaluation.py --model openai
```

**Run with Anthropic Claude:**
```bash
python3 run_evaluation.py --model anthropic
```

### Advanced Options

**Specify custom directories:**
```bash
python3 run_evaluation.py \
  --model anthropic \
  --test-cases-dir custom_tests \
  --results-dir custom_results
```

**View help:**
```bash
python3 run_evaluation.py --help
```

## Viewing Results

Results are saved as JSON files in `ai_evaluation/results/`:

```bash
ls ai_evaluation/results/
# Output: test_case_name_20251117_143045.json

# View a result file
cat ai_evaluation/results/test_case_name_20251117_143045.json | python -m json.tool
```

Each result file contains:
- Test case name and content
- Model response
- Timestamp
- Metadata (model type, tokens, temperature, etc.)

## Troubleshooting

### Common Issues

**Problem: `ModuleNotFoundError: No module named 'openai'`**
```bash
# Solution: Ensure virtual environment is activated and install dependencies
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

**Problem: API authentication error**
```bash
# Solution: Check your .env file has correct API keys
cat .env  # Verify keys are present and correctly formatted
```

**Problem: No test cases found**
```bash
# Solution: Ensure test case files exist
ls ai_evaluation/test_cases/
# If empty, add some test case .txt files
```

**Problem: Permission denied when running script**
```bash
# Solution: Make the script executable
chmod +x ai_evaluation/run_evaluation.py
```

### Getting Help

If you encounter issues:

1. Check the [Issues](https://github.com/darshil0/AI-Testing/issues) page
2. Create a new issue with:
   - Your Python version
   - Error message (full output)
   - Steps to reproduce
3. Review logs in `evaluation.log` (if logging is enabled)

## Next Steps

Now that you're set up:

1. **Add more test cases** in `ai_evaluation/test_cases/`
2. **Run evaluations** with different models
3. **Analyze results** in the `results/` directory
4. **Contribute** by following [CONTRIBUTING.md](CONTRIBUTING.md)

## Updating

To update to the latest version:

```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

## Deactivating Virtual Environment

When you're done:

```bash
deactivate
```

## Uninstalling

To remove the project:

```bash
cd ..
rm -rf AI-Testing
```

---

**Need help?** Open an issue or check the [README.md](README.md) for more information.
