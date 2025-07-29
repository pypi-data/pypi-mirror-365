# Release Instructions for ArchGuide MCP Python

This guide provides step-by-step instructions for releasing and uploading the ArchGuide MCP Python package to PyPI.

## Prerequisites

### 1. Install Required Tools

```bash
# Install build tools
pip install --upgrade pip build twine

# Or if using uv
uv add --dev build twine
```

### 2. Create PyPI Account

1. Go to [PyPI.org](https://pypi.org/account/register/) and create an account
2. Go to [TestPyPI.org](https://test.pypi.org/account/register/) and create an account (for testing)
3. Enable 2FA on both accounts (required for uploading)

### 3. Create API Tokens

1. **For PyPI (Production)**:
   - Go to https://pypi.org/manage/account/token/
   - Click "Add API token"
   - Name: `archguide-mcp-python-release`
   - Scope: Select "Entire account" or limit to this project later
   - Copy the token (starts with `pypi-`)

2. **For TestPyPI (Testing)**:
   - Go to https://test.pypi.org/manage/account/token/
   - Follow same steps as above

### 4. Configure Credentials

Create or update `~/.pypirc`:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = pypi-YOUR_TOKEN_HERE

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR_TESTPYPI_TOKEN_HERE
```

## Pre-Release Checklist

### 1. Code Quality Checks

```bash
# Run all tests
python -m pytest tests/ -v

# Check test coverage
python -m pytest tests/ --cov=src/archguide_mcp_python --cov-report=term-missing

# Run linting (if configured)
ruff check src/
black --check src/

# Type checking (if configured)
mypy src/
```

### 2. Version and Metadata Verification

Check `pyproject.toml`:
- [ ] Version number is correct
- [ ] Description is accurate
- [ ] Dependencies are up to date
- [ ] Author/maintainer info is correct
- [ ] Keywords and classifiers are relevant
- [ ] URLs point to correct repositories

### 3. Documentation

- [ ] README.md is up to date
- [ ] CHANGELOG.md exists and has current version notes
- [ ] License file exists
- [ ] All example code works

## Release Process

### Step 1: Update Version

```bash
# Edit pyproject.toml and update version
# Example: 0.1.0 -> 0.1.1 (patch) or 0.1.0 -> 0.2.0 (minor)
```

### Step 2: Clean Previous Builds

```bash
# Remove old build artifacts
rm -rf dist/ build/ *.egg-info/
```

### Step 3: Build the Package

```bash
# Build source distribution and wheel
python -m build

# Verify build contents
ls -la dist/
```

You should see two files:
- `archguide_mcp_python-X.Y.Z.tar.gz` (source distribution)
- `archguide_mcp_python-X.Y.Z-py3-none-any.whl` (wheel)

### Step 4: Test the Build

```bash
# Check package contents
python -m zipfile -l dist/archguide_mcp_python-X.Y.Z-py3-none-any.whl

# Validate package metadata
twine check dist/*
```

### Step 5: Test Upload to TestPyPI

```bash
# Upload to TestPyPI first
twine upload --repository testpypi dist/*

# Verify the upload
# Visit: https://test.pypi.org/project/archguide-mcp-python/
```

### Step 6: Test Installation from TestPyPI

```bash
# Create a new virtual environment for testing
python -m venv test_env
source test_env/bin/activate  # On Windows: test_env\Scripts\activate

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ archguide-mcp-python

# Test the installation
python -c "from archguide_mcp_python.server import main; print('✅ Import successful')"

# Test CLI command
archguide-mcp --help

# Deactivate and remove test environment
deactivate
rm -rf test_env
```

### Step 7: Upload to Production PyPI

**Only proceed if TestPyPI installation worked correctly!**

```bash
# Upload to production PyPI
twine upload dist/*

# Verify the upload
# Visit: https://pypi.org/project/archguide-mcp-python/
```

### Step 8: Test Production Installation

```bash
# Create another test environment
python -m venv prod_test_env
source prod_test_env/bin/activate

# Install from PyPI
pip install archguide-mcp-python

# Test functionality
python -c "from archguide_mcp_python.server import main; print('✅ Production install successful')"
archguide-mcp --help

# Clean up
deactivate
rm -rf prod_test_env
```

## Post-Release Tasks

### 1. Create Git Tag

```bash
# Tag the release
git tag -a v0.1.0 -m "Release version 0.1.0"
git push origin v0.1.0

# Or create release on GitHub UI
```

### 2. Update Documentation

- [ ] Update README.md with new version info
- [ ] Update CHANGELOG.md with release notes
- [ ] Update any installation instructions

### 3. Announce Release

- [ ] Create GitHub Release with changelog
- [ ] Update any documentation sites
- [ ] Notify users/community if applicable

## Troubleshooting

### Common Issues

1. **401 Unauthorized Error**:
   - Check API token is correct
   - Ensure token has proper permissions
   - Verify `.pypirc` configuration

2. **400 Bad Request - File already exists**:
   - Version already uploaded to PyPI
   - Increment version number and rebuild

3. **403 Forbidden**:
   - Account may not have permissions
   - Project name might be reserved
   - Enable 2FA if not already enabled

4. **Import Errors After Installation**:
   - Check package structure in built wheel
   - Verify `pyproject.toml` configuration
   - Ensure all dependencies are listed

### Validation Commands

```bash
# Validate package structure
python setup.py check --restructuredtext --strict

# Check wheel contents
python -m wheel unpack dist/archguide_mcp_python-X.Y.Z-py3-none-any.whl
ls -la archguide_mcp_python-X.Y.Z/

# Test in isolated environment
tox  # If tox.ini is configured
```

## Security Notes

- Never commit API tokens to version control
- Use API tokens instead of username/password
- Enable 2FA on PyPI accounts
- Regularly rotate API tokens
- Use `testpypi` for testing releases

## Automation (Optional)

Consider setting up GitHub Actions for automated releases:

```yaml
# .github/workflows/release.yml
name: Release to PyPI

on:
  release:
    types: [published]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v3
      with:
        python-version: '3.12'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    - name: Build package
      run: python -m build
    - name: Publish to PyPI
      uses: pypa/gh-action-pypi-publish@release/v1
      with:
        password: ${{ secrets.PYPI_API_TOKEN }}
```

## Quick Reference

```bash
# Complete release workflow
rm -rf dist/ build/ *.egg-info/
python -m build
twine check dist/*
twine upload --repository testpypi dist/*
# Test installation from testpypi
twine upload dist/*
# Test production installation
git tag -a v0.1.0 -m "Release version 0.1.0"
git push origin v0.1.0
```