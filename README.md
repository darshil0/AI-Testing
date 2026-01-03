# AI-Testing 🤖

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?logo=docker&logoColor=white)](https://www.docker.com/)
[![CI](https://github.com/darshil0/AI-Testing/actions/workflows/ci.yml/badge.svg)](https://github.com/darshil0/AI-Testing/actions/workflows/ci.yml)

A professional, enterprise-ready evaluation framework for benchmarking AI models across various domains. Test and compare models from OpenAI, Anthropic, Google, and local LLMs with standardized metrics, automated judging, and professional analytics.

---

## ✨ Key Features

### 🔌 Universal Model Support
- **Cloud APIs**: OpenAI (GPT-4o), Anthropic (Claude), Google (Gemini)
- **Local Models**: Ollama integration for Llama, Mistral, and other open-source models
- **Simulated Mode**: Test without API keys for development

### ⚖️ Intelligent Evaluation
- **LLM-as-a-Judge**: Automated scoring using state-of-the-art models
- **Specialized Personas**: Evaluate from different perspectives (Critic, Helper, Security Auditor)
- **Custom Criteria**: Define expectations for each test case

### 📊 Professional Analytics
- **Automated Charts**: Generate publication-ready performance visualizations
- **Interactive Dashboard**: Explore results with Streamlit web interface
- **Cost Tracking**: Real-time token usage and API cost estimation
- **Performance Metrics**: Latency, accuracy, and quality scoring

### 🛡️ Security & Quality
- **PII Detection**: Automatic scanning for privacy leaks
- **Multi-dimensional Testing**: Categories include reasoning, coding, creativity, safety
- **Reproducible Results**: Timestamped JSON exports for all evaluations

### 🚀 Developer Experience
- **Rich CLI**: Beautiful terminal interface with progress bars
- **Parallel Processing**: Fast evaluation with concurrent execution
- **Docker Ready**: Containerized environment for consistency
- **CI/CD Integration**: GitHub Actions for automated testing

---

## 📂 Project Structure

```
AI-Testing/
├── ai_evaluation/
│   ├── config.yaml              # Centralized configuration
│   ├── models.py                # Model adapters (OpenAI, Anthropic, etc.)
│   ├── run_evaluation.py        # Main evaluation engine
│   ├── analytics.py             # Chart generation
│   ├── test_cases/              # Test prompts (.txt, .yaml)
│   │   ├── reasoning_logic_puzzle.txt
│   │   ├── code_optimization.yaml
│   │   └── ...
│   └── results/                 # Generated reports
│       ├── latest_results.json
│       └── run_20260103_143000.json
├── tests/                       # Unit tests
├── dashboard.py                 # Streamlit dashboard
├── Dockerfile                   # Container definition
├── requirements.txt             # Python dependencies
└── docs/                        # Documentation
    ├── CONTRIBUTING.md
    ├── Setup.md
    └── Quick Reference.md
```

---

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/darshil0/AI-Testing.git
cd AI-Testing

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit with your API keys
nano .env  # or your preferred editor
```

Required API keys (at least one):
```bash
OPENAI_API_KEY=sk-proj-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=your-google-key
```

### 3. Run Your First Evaluation

```bash
# Test without API keys (simulated mode)
python ai_evaluation/run_evaluation.py --models simulated:default

# Run with real models
python ai_evaluation/run_evaluation.py --models openai:gpt-4o

# Compare multiple models
python ai_evaluation/run_evaluation.py --models openai:gpt-4o anthropic:claude-sonnet-4-20250514
```

---

## 💻 Usage Guide

### Basic Evaluation

```bash
# Single model with default judge
python ai_evaluation/run_evaluation.py --models openai:gpt-4o

# Multiple models in parallel
python ai_evaluation/run_evaluation.py --models openai:gpt-4o ollama:llama3

# Use specialized judge persona
python ai_evaluation/run_evaluation.py --models openai:gpt-4o --persona critic

# Sequential execution (for debugging)
python ai_evaluation/run_evaluation.py --models openai:gpt-4o --sequential
```

### Model Format

Models are specified as `provider:model_name`:

| Provider | Example |
|----------|---------|
| OpenAI | `openai:gpt-4o` |
| Anthropic | `anthropic:claude-sonnet-4-20250514` |
| Google | `gemini:gemini-1.5-pro` |
| Ollama | `ollama:llama3` |
| Simulated | `simulated:default` |

### Judge Personas

- `default`: Objective, balanced evaluation
- `critic`: Strict scoring, penalizes minor errors
- `helper`: Focus on clarity and helpfulness
- `auditor`: Security-focused, checks for safety violations

### Generate Analytics

```bash
# Create performance charts
python ai_evaluation/analytics.py

# View in results/benchmark_report.png
```

### Launch Interactive Dashboard

```bash
# Start Streamlit app
streamlit run dashboard.py

# Opens at http://localhost:8501
```

---

## 📝 Creating Test Cases

### Simple Text Format (.txt)

```text
Category: Reasoning
Difficulty: Medium

Solve this logic puzzle: There are three boxes labeled...
```

### Advanced YAML Format (.yaml)

```yaml
name: code_optimization_task
category: Coding
difficulty: Hard
prompt: |
  Optimize this Python function for better time complexity:
  def find_duplicates(arr):
      # inefficient code here
      
expectations:
  - "Mention using a set for O(n) complexity"
  - "Provide working implementation"
  - "Explain the optimization"
  
metadata:
  tags: ["python", "algorithms", "optimization"]
```

### Test Categories

- **Reasoning**: Logic puzzles, math problems, critical thinking
- **Coding**: Programming, debugging, algorithms
- **Creativity**: Writing, brainstorming, creative solutions
- **Factual**: Knowledge, trivia, current events
- **Safety**: Harmful content detection, ethical dilemmas
- **Language**: Translation, grammar, style

---

## 🔧 Configuration

Edit `ai_evaluation/config.yaml` to customize:

```yaml
# Execution settings
max_workers: 5  # Parallel threads

# Model parameters
default_model_params:
  max_tokens: 2000
  temperature: 0.7

# Judge configuration
judge:
  model: "openai:gpt-4o"

# Pricing (per million tokens)
pricing:
  "gpt-4o": { "input": 5.0, "output": 15.0 }
  
# PII detection patterns
pii_patterns:
  email: "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}"
```

---

## 🐳 Docker Deployment

```bash
# Build container
docker build -t ai-testing .

# Run evaluation
docker run --env-file .env ai-testing

# With custom command
docker run --env-file .env ai-testing \
  python ai_evaluation/run_evaluation.py --models openai:gpt-4o

# Using docker-compose
docker-compose up
```

---

## 🧪 Development

### Running Tests

```bash
# Run all tests
pytest

# With coverage
pytest --cov=ai_evaluation

# Run specific test file
pytest tests/test_run_evaluation.py
```

### Code Quality

```bash
# Format code
black ai_evaluation/

# Lint
flake8 ai_evaluation/

# Type checking
mypy ai_evaluation/
```

### Adding a New Model Provider

1. Add model class to `ai_evaluation/models.py`:
```python
class NewProviderModel(BaseModel):
    def call(self, prompt: str) -> Tuple[str, int, int]:
        # Implementation
        pass
```

2. Register in `get_model()` factory function
3. Add pricing to `config.yaml`
4. Update documentation

---

## 📊 Results Format

Results are exported as JSON with comprehensive metadata:

```json
{
  "test_case_name": "reasoning_logic_puzzle",
  "category": "Reasoning",
  "difficulty": "Hard",
  "model_type": "openai:gpt-4o",
  "prompt": "...",
  "response": "...",
  "duration_seconds": 2.34,
  "tokens_input": 150,
  "tokens_output": 300,
  "estimated_cost": 0.0023,
  "judge_score": 0.85,
  "judge_reasoning": "Clear logical reasoning...",
  "pii_found": false,
  "pii_types": [],
  "timestamp": "2026-01-03T14:30:00"
}
```

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](docs/CONTRIBUTING.md) for details.

### Quick Contribution Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest`)
5. Format code (`black .`)
6. Commit changes (`git commit -m 'Add amazing feature'`)
7. Push to branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

---

## 📖 Documentation

- [Setup Guide](docs/Setup.md) - Detailed installation instructions
- [Quick Reference](docs/Quick%20Reference.md) - Common commands and workflows
- [Contributing](docs/CONTRIBUTING.md) - How to contribute
- [Changelog](CHANGELOG.md) - Version history

---

## 🔒 Security

- Never commit `.env` files with real API keys
- Use environment variables for sensitive data
- PII detection is basic - review responses manually for sensitive applications
- Local models (Ollama) run entirely on your machine

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- OpenAI, Anthropic, and Google for their powerful APIs
- Ollama for making local LLMs accessible
- The open-source community for amazing tools (Rich, Streamlit, etc.)

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/darshil0/AI-Testing/issues)
- **Discussions**: [GitHub Discussions](https://github.com/darshil0/AI-Testing/discussions)
- **Email**: Create an issue for general inquiries

---

**Made with ❤️ by the AI-Testing Team**

[⬆ Back to Top](#ai-testing-)
