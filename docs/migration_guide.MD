# Migration Guide: Upgrading to AI-Testing v2.0.1

## Quick Start for Existing Users

If you're already using AI-Testing, here's how to upgrade:

```bash
# 1. Pull latest changes
git pull origin main

# 2. Reinstall dependencies (fixes duplicates)
pip install -r requirements.txt --force-reinstall

# 3. Run tests to verify
pytest

# 4. You're done! No code changes needed.
```

---

## What Changed in v2.0.1

### ✅ No Breaking Changes
**Good news**: All your existing test cases, configurations, and scripts will continue to work without modification.

### 🔧 Behind-the-Scenes Improvements
1. **Dependencies cleaned up** - duplicate packages removed
2. **Error handling improved** - better error messages
3. **Path resolution fixed** - works from any directory
4. **Judge scoring more reliable** - robust JSON parsing
5. **Better validation** - scores clamped to valid ranges

---

## For Different User Types

### If You're Using Standard CLI

**Before (v2.0.0)**:
```bash
python ai_evaluation/run_evaluation.py --models openai:gpt-4o
```

**After (v2.0.1)**:
```bash
# Exactly the same! No changes needed
python ai_evaluation/run_evaluation.py --models openai:gpt-4o

# Plus you now get:
# - Better error messages
# - Summary table after run
# - Works from any directory
```

### If You're Using Docker

**Before**:
```bash
docker-compose up
```

**After**:
```bash
# Rebuild to get latest fixes
docker-compose build
docker-compose up

# Everything else works the same
```

### If You're Contributing/Developing

**Before**:
```bash
pip install -r requirements.txt
pytest
```

**After**:
```bash
# Same commands, but:
# - No more duplicate dependency warnings
# - Tests are more comprehensive
# - Better test coverage

pip install -r requirements.txt
pytest
```

---

## New Features You Can Use

### 1. Sequential Mode (for debugging)
```bash
# Run tests one at a time instead of parallel
python ai_evaluation/run_evaluation.py \
  --models openai:gpt-4o \
  --sequential
```

**Use when**: Debugging issues or when rate limits are a concern

### 2. Better Console Output
After running evaluations, you'll now see:
- **Summary table** with all results
- **Average score** across all tests
- **Total cost** estimation
- **PII warnings** if detected

### 3. Run from Anywhere
```bash
# These all work now:
cd AI-Testing/
python ai_evaluation/run_evaluation.py --models simulated:default

cd ai_evaluation/
python run_evaluation.py --models simulated:default

cd ~/anywhere/
python ~/AI-Testing/ai_evaluation/run_evaluation.py --models simulated:default
```

---

## Common Issues After Upgrade

### Issue 1: Old virtual environment
**Symptom**: Import errors or duplicate package warnings

**Solution**:
```bash
# Recreate virtual environment
deactivate
rm -rf venv/
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Issue 2: Cached results confusing
**Symptom**: Results don't match what you expect

**Solution**:
```bash
# Clear old results (backup first if needed)
mkdir -p ai_evaluation/results_backup
mv ai_evaluation/results/*.json ai_evaluation/results_backup/
```

### Issue 3: Tests failing
**Symptom**: `pytest` shows failures

**Solution**:
```bash
# Update test fixtures
pip install pytest pytest-mock pytest-cov --upgrade

# Clear pytest cache
rm -rf .pytest_cache/
pytest --cache-clear
```

---

## Recommended Actions After Upgrade

### 1. Verify Installation
```bash
# Check no duplicate packages
pip list | grep -E "(tenacity|pytest|pyyaml)"

# Should see each only once:
# pytest                    7.x.x
# pytest-mock               3.x.x
# pyyaml                    6.x.x
# tenacity                  8.x.x
```

### 2. Run Test Suite
```bash
# All tests should pass
pytest

# Verify coverage
pytest --cov=ai_evaluation
# Should see >80% coverage
```

### 3. Test Your Workflow
```bash
# Run a quick evaluation to verify everything works
python ai_evaluation/run_evaluation.py \
  --models simulated:default

# Check for the new summary table at the end
```

### 4. Update Your Documentation
If you have custom docs or scripts:
- Update any references to old behavior
- Add notes about new features
- Update troubleshooting sections

---

## API Changes (None!)

Good news: No API changes in this release. All functions have the same signatures:

```python
# This still works exactly as before
from ai_evaluation.run_evaluation import AIEvaluator

evaluator = AIEvaluator()
evaluator.run_suite(model_ids=["simulated:default"])
evaluator.export()
```

---

## Configuration Changes (None!)

Your existing `config.yaml` files are 100% compatible:

```yaml
# All these settings still work
directories:
  test_cases: "ai_evaluation/test_cases"
  results: "ai_evaluation/results"

max_workers: 5

judge:
  model: "openai:gpt-4o"

# No changes needed!
```

---

## Test Case Changes (None!)

Both formats continue to work without modification:

**Text format (.txt)**:
```text
Category: Reasoning
Difficulty: Medium

Your prompt here
```

**YAML format (.yaml)**:
```yaml
category: Coding
difficulty: Hard
prompt: Your prompt here
expectations:
  - Expectation 1
  - Expectation 2
```

---

## For CI/CD Users

### GitHub Actions
Your workflows should continue working, but update for reliability:

```yaml
# .github/workflows/ci.yml
- name: Install dependencies
  run: |
    pip install -r requirements.txt
    
# After upgrade, you get:
# - Faster installation (no duplicates)
# - More reliable tests
# - Better error messages in logs
```

### Docker Builds
Rebuild your images after upgrading:

```bash
# In your CI pipeline
docker build -t ai-testing:latest .
docker push your-registry/ai-testing:latest

# Benefits:
# - Smaller image (no duplicate packages)
# - More reliable execution
```

---

## Performance Impact

### Improvements
- ✅ **Faster installation**: No duplicate packages to install
- ✅ **More reliable execution**: Better error handling
- ✅ **Clearer output**: Rich console tables
- ✅ **Better resource usage**: Fixed edge cases

### No Negative Impact
- ⚖️ Execution speed: Same as before
- ⚖️ Memory usage: Same as before
- ⚖️ Disk usage: Slightly less (fewer duplicates)

---

## Rollback Instructions

If you need to rollback to v2.0.0:

```bash
# 1. Checkout previous version
git checkout v2.0.0

# 2. Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# 3. Verify
python ai_evaluation/run_evaluation.py --models simulated:default
```

**Note**: We don't recommend rolling back as v2.0.1 fixes critical issues, but the option is available if needed.

---

## Getting Help

### Resources
1. **Documentation**: Check updated [README.md](README.md)
2. **Issues**: [GitHub Issues](https://github.com/darshil0/AI-Testing/issues)
3. **Changelog**: See [CHANGELOG.md](CHANGELOG.md) for all changes

### Reporting Problems
If you encounter issues after upgrading:

```markdown
**Issue Template**:
- Version upgraded from: [e.g., 2.0.0]
- Version upgraded to: [2.0.1]
- Python version: [e.g., 3.11]
- Operating system: [e.g., macOS 14.0]
- Error message: [paste error]
- Steps to reproduce: [list steps]
```

---

## Summary: Do I Need to Change Anything?

**Short answer: No!** 

Your existing code, test cases, and configurations will all work without modification. This release focuses on:
- Fixing bugs
- Improving reliability
- Better error messages
- Enhanced user experience

The only action required is to pull the latest code and reinstall dependencies.

---

## Next Steps

1. ✅ Pull latest code
2. ✅ Reinstall dependencies
3. ✅ Run tests to verify
4. ✅ Enjoy improved reliability!

Optional:
- 📖 Read updated documentation
- 🎯 Try new sequential mode
- 📊 Explore new summary tables
- 🤝 Contribute improvements

---

**Migration Guide Version**: 1.0  
**Last Updated**: January 3, 2026  
**Applies to**: Upgrade from v2.0.0 to v2.0.1
