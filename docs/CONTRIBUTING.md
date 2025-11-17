# Contributing to AI-Testing

Thank you for your interest in contributing to the AI-Testing repository! This document provides guidelines and instructions for contributing.

## How to Contribute

### Reporting Issues

If you find a bug or have a suggestion:
1. Check if the issue already exists in the [Issues](https://github.com/darshil0/AI-Testing/issues) section
2. If not, create a new issue with a clear title and description
3. Include relevant details such as:
   - Steps to reproduce (for bugs)
   - Expected vs actual behavior
   - Your environment (Python version, OS, etc.)

### Adding Test Cases

Test cases are the core of this repository. To add a new test case:

1. **Create a Test Case File**
   - Navigate to `ai_evaluation/test_cases/`
   - Create a new `.txt` file with a descriptive name (e.g., `reasoning_logic_puzzle.txt`)
   - Use lowercase with underscores for file names

2. **Test Case Format**
   ```
   Category: [reasoning/creativity/safety/factual/coding/etc.]
   Difficulty: [easy/medium/hard]
   
   [Your test prompt/instructions here]
   ```

3. **Test Case Best Practices**
   - Be specific and clear in your instructions
   - Include the expected type of response when relevant
   - Test one capability or aspect at a time
   - Consider edge cases and potential failure modes
   - Avoid ambiguous or trick questions unless testing for that specifically

### Test Case Categories

When creating test cases, consider these categories:

- **Reasoning**: Logic puzzles, mathematical reasoning, causal inference
- **Creativity**: Story writing, brainstorming, creative problem-solving
- **Factual**: Knowledge retrieval, fact-checking, current events
- **Coding**: Programming tasks, code review, debugging
- **Safety**: Harmful content detection, bias identification, ethical scenarios
- **Language**: Translation, grammar, style adaptation
- **Multimodal**: Tasks involving multiple types of input/output

### Code Contributions

If you're contributing code improvements:

1. **Fork the Repository**
   ```bash
   # Fork via GitHub UI, then clone your fork
   git clone https://github.com/YOUR_USERNAME/AI-Testing.git
   cd AI-Testing
   ```

2. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make Your Changes**
   - Follow Python PEP 8 style guidelines
   - Add comments for complex logic
   - Update documentation as needed
   - Test your changes thoroughly

4. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "Add: Brief description of your changes"
   ```
   
   Use conventional commit messages:
   - `Add:` for new features
   - `Fix:` for bug fixes
   - `Update:` for modifications
   - `Refactor:` for code improvements
   - `Docs:` for documentation changes

5. **Push to Your Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request**
   - Go to the original repository on GitHub
   - Click "New Pull Request"
   - Select your fork and branch
   - Provide a clear description of your changes
   - Link any related issues

### Pull Request Guidelines

- Keep PRs focused on a single feature or fix
- Include a clear description of what changed and why
- Reference any related issues
- Ensure all tests pass (if applicable)
- Be responsive to feedback and review comments

### Code Style

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings for functions and classes
- Keep functions focused and modular
- Maximum line length: 100 characters

### Testing Guidelines

Before submitting code changes:
- Test your code with multiple test cases
- Verify that existing functionality still works
- Add new tests for new features when applicable

## Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/darshil0/AI-Testing.git
   cd AI-Testing
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

## Community Guidelines

- Be respectful and constructive in all interactions
- Welcome newcomers and help them get started
- Focus on the issue, not the person
- Accept constructive criticism gracefully
- Give credit where credit is due

## Questions?

If you have questions about contributing, feel free to:
- Open an issue with the `question` label
- Start a discussion in the Discussions tab (if enabled)
- Reach out to the maintainers

Thank you for helping improve AI-Testing!
