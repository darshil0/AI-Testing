# Implementation Checklist for AI-Testing v2.0.1 Fixes

## Files to Update

### ✅ 1. requirements.txt
**Action**: Replace entire file  
**Priority**: Critical  
**Changes**:
- Remove duplicate `tenacity` entries
- Remove duplicate `pytest` entries
- Remove duplicate `pytest-mock` entries
- Remove duplicate `pyyaml` entries
- Consolidate to single clean list

**File Location**: `requirements.txt` (root directory)

---

### ✅ 2. ai_evaluation/run_evaluation.py
**Action**: Replace entire file  
**Priority**: Critical  
**Changes**:
- Enhanced path resolution in `__init__`
- Improved `_pii_scan` error handling
- Robust `judge_response` JSON parsing
- Score validation with clamping
- Better `_parse_test_case` error handling
- Added `print_summary` method
- Enhanced `run_suite` with empty directory handling
- Improved `export` with better logging
- Enhanced `main` block with better CLI

**File Location**: `ai_evaluation/run_evaluation.py`

---

### ✅ 3. README.md
**Action**: Replace entire file  
**Priority**: High  
**Changes**:
- Restructured for better readability
- Added comprehensive feature descriptions
- Updated Quick Start section
- Added usage examples
- Enhanced troubleshooting section
- Updated model provider table
- Added Docker deployment instructions
- Better organization and formatting

**File Location**: `README.md` (root directory)

---

### ✅ 4. CHANGELOG.md
**Action**: Add new section at top, keep existing content  
**Priority**: High  
**Changes**:
- Add v2.0.1 section with all fixes
- Document breaking changes (none)
- Add migration notes
- Keep all previous version history

**File Location**: `CHANGELOG.md` (root directory)

**Implementation**:
- Add the new [2.0.1] section at the top
- Keep all existing content below it

---

### ✅ 5. docs/CONTRIBUTING.md
**Action**: Replace entire file  
**Priority**: High  
**Changes**:
- Complete rewrite with more detail
- Added table of contents
- Step-by-step contribution guide
- Code examples for adding features
- Testing guidelines
- Documentation standards
- Bug reporting template

**File Location**: `docs/CONTRIBUTING.md`

---

### ✅ 6. tests/test_run_evaluation.py
**Action**: Replace entire file  
**Priority**: Medium  
**Changes**:
- Fixed fixture setup
- Added new test cases
- Improved mocking strategy
- Better edge case coverage
- Added tests for all new functionality

**File Location**: `tests/test_run_evaluation.py`

---

## New Files to Create

### 📄 1. MIGRATION_GUIDE.md
**Action**: Create new file  
**Priority**: Medium  
**Content**: Migration guide for upgrading to v2.0.1  
**File Location**: `docs/MIGRATION_GUIDE.md`

---

### 📄 2. FIXES_SUMMARY.md
**Action**: Create new file  
**Priority**: Low (optional)  
**Content**: Detailed summary of all fixes  
**File Location**: `docs/FIXES_SUMMARY.md`

---

## Verification Steps

### Step 1: Update Files
```bash
# 1. Update requirements.txt
# Replace with fixed version

# 2. Update run_evaluation.py
# Replace with fixed version

# 3. Update README.md
# Replace with updated version

# 4. Update CHANGELOG.md
# Add v2.0.1 section at top

# 5. Update CONTRIBUTING.md
# Replace with comprehensive version

# 6. Update test file
# Replace tests/test_run_evaluation.py

# 7. Create migration guide (optional)
# Create docs/MIGRATION_GUIDE.md
```

### Step 2: Test Installation
```bash
# Remove old virtual environment
rm -rf venv/

# Create fresh virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies (verify no duplicates)
pip install -r requirements.txt

# Check for duplicates
pip list | grep -E "(tenacity|pytest|pyyaml)"
# Should see each package only once
```

### Step 3: Run Tests
```bash
# Run all tests
pytest

# Should see output like:
# tests/test_run_evaluation.py::test_aievaluator_initialization PASSED
# tests/test_run_evaluation.py::test_parse_test_case_txt PASSED
# ... (all tests passing)

# Check coverage
pytest --cov=ai_evaluation --cov-report=term-missing

# Should see >80% coverage
```

### Step 4: Test Functionality
```bash
# Test from root directory
python ai_evaluation/run_evaluation.py --models simulated:default

# Test from ai_evaluation directory
cd ai_evaluation
python run_evaluation.py --models simulated:default
cd ..

# Both should work and show summary table
```

### Step 5: Verify Output
After running evaluation, verify you see:
- ✅ Progress bar during execution
- ✅ Summary table with results
- ✅ Average score display
- ✅ Total cost display
- ✅ PII warnings (if applicable)
- ✅ Export confirmation message

### Step 6: Code Quality
```bash
# Format code
black ai_evaluation/

# Check linting
flake8 ai_evaluation/

# Should see no warnings
```

---

## Deployment Checklist

### For Maintainers

- [ ] All files updated as specified
- [ ] Tests pass locally
- [ ] No flake8 warnings
- [ ] Documentation reviewed
- [ ] Changelog updated
- [ ] Version number updated (if applicable)
- [ ] Git commit with clear message
- [ ] Git tag created for v2.0.1
- [ ] Changes pushed to main branch
- [ ] GitHub release created
- [ ] Users notified of update

### Git Commands

```bash
# Stage all changes
git add requirements.txt
git add ai_evaluation/run_evaluation.py
git add README.md
git add CHANGELOG.md
git add docs/CONTRIBUTING.md
git add tests/test_run_evaluation.py

# Commit with descriptive message
git commit -m "Release v2.0.1: Critical bug fixes and improvements

- Fix: Remove duplicate dependencies in requirements.txt
- Fix: Improve path resolution for config files
- Fix: Enhance judge response parsing robustness
- Fix: Add score validation and clamping
- Fix: Better empty directory handling
- Improve: Enhanced error messages throughout
- Improve: Add summary table output
- Docs: Update README, CHANGELOG, and CONTRIBUTING
- Test: Expand test coverage with new edge cases"

# Create version tag
git tag -a v2.0.1 -m "Version 2.0.1 - Bug fixes and improvements"

# Push changes and tags
git push origin main
git push origin v2.0.1
```

---

## Communication Checklist

### Announce Changes

- [ ] Update project README on GitHub
- [ ] Create release notes on GitHub Releases
- [ ] Update documentation website (if applicable)
- [ ] Notify users via:
  - [ ] GitHub Discussions
  - [ ] Discord/Slack (if applicable)
  - [ ] Mailing list (if applicable)
- [ ] Update any tutorial videos or guides
- [ ] Update Docker Hub images (if applicable)

### Release Notes Template

```markdown
# AI-Testing v2.0.1 Released

We're pleased to announce AI-Testing v2.0.1, a maintenance release focused on bug fixes and improvements.

## 🐛 Bug Fixes
- Fixed duplicate dependencies in requirements.txt
- Improved path resolution for better cross-platform support
- Enhanced judge response parsing for more reliable scoring
- Added score validation to ensure valid ranges

## ✨ Improvements
- Better error messages and user feedback
- Enhanced console output with summary tables
- Improved test coverage
- Updated documentation

## 📦 Upgrade
```bash
git pull origin main
pip install -r requirements.txt --force-reinstall
```

## 📚 Documentation
- [Migration Guide](docs/MIGRATION_GUIDE.md)
- [Complete Changelog](CHANGELOG.md)
- [Contributing Guidelines](docs/CONTRIBUTING.md)

**This is a backwards-compatible release** - no code changes needed!
```

---

## Quality Assurance

### Before Merging
- [ ] All automated tests pass
- [ ] Manual testing completed
- [ ] Documentation reviewed
- [ ] No regressions identified
- [ ] Performance acceptable
- [ ] Security review (if applicable)

### After Merging
- [ ] Monitor for issues
- [ ] Respond to user feedback
- [ ] Update roadmap
- [ ] Plan next release

---

## Rollback Plan

If critical issues are discovered:

```bash
# Revert to v2.0.0
git checkout v2.0.0

# Or revert specific commit
git revert <commit-hash>

# Notify users immediately
# Document the issue
# Plan hotfix
```

---

## Success Criteria

This release is successful when:
- ✅ All tests pass
- ✅ No duplicate dependencies
- ✅ Can run from any directory
- ✅ Empty directories handled gracefully
- ✅ Scores always in valid range
- ✅ Documentation is accurate
- ✅ No regression bugs
- ✅ Users can upgrade smoothly
- ✅ Positive user feedback

---

## Post-Release Tasks

1. Monitor GitHub Issues for new problems
2. Update project board/roadmap
3. Plan features for next release
4. Review and merge community PRs
5. Update project statistics/metrics

---

**Checklist Version**: 1.0  
**Created**: January 3, 2026  
**For Release**: v2.0.1
