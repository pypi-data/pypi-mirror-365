# PyPI Release Instructions - Quick Start

This is a condensed version of the release instructions. For the complete guide, see [RELEASE.md](./RELEASE.md).

## ✅ Ready to Release - Package Successfully Built!

Your package has been successfully built and validated. The following files are ready for upload:

- `dist/archguide_mcp_python-0.2.0-py3-none-any.whl`
- `dist/archguide_mcp_python-0.2.0.tar.gz`

## 🚀 Quick Release Steps

### 1. Set Up PyPI Accounts & API Tokens

```bash
# Create accounts at:
# - https://pypi.org/account/register/
# - https://test.pypi.org/account/register/

# Create API tokens:
# - https://pypi.org/manage/account/token/
# - https://test.pypi.org/manage/account/token/
```

### 2. Configure Credentials

Create `~/.pypirc`:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = pypi-YOUR_PRODUCTION_TOKEN_HERE

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR_TEST_TOKEN_HERE
```

### 3. Test Upload to TestPyPI

```bash
# Upload to TestPyPI first (recommended)
twine upload --repository testpypi dist/*

# Check the test upload:
# https://test.pypi.org/project/archguide-mcp-python/
```

### 4. Test Installation from TestPyPI

```bash
# Test in a new environment
python -m venv test_env
source test_env/bin/activate  # On Windows: test_env\Scripts\activate

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ archguide-mcp-python

# Test the installation
python -c "from archguide_mcp_python.server import main; print('✅ Import successful')"
archguide-mcp --help

# Clean up
deactivate
rm -rf test_env
```

### 5. Upload to Production PyPI

**Only if TestPyPI installation worked!**

```bash
# Upload to production PyPI
twine upload dist/*

# Check the production upload:
# https://pypi.org/project/archguide-mcp-python/
```

### 6. Test Production Installation

```bash
# Test production installation
python -m venv prod_test
source prod_test/bin/activate

pip install archguide-mcp-python
python -c "from archguide_mcp_python.server import main; print('✅ Production install successful')"

# Clean up
deactivate
rm -rf prod_test
```

## 📦 Package Information

- **Name**: `archguide-mcp-python`
- **Version**: `0.2.0`
- **Description**: Architecture Guidelines MCP Server - Inject architectural best practices into AI workflows
- **Author**: Ioan Salau
- **License**: MIT
- **Python**: Requires Python 3.12+

## 🛠 Post-Release Tasks

```bash
# Tag the release
git tag -a v0.2.0 -m "Release version 0.2.0"
git push origin v0.2.0

# Create GitHub release (optional)
# Visit: https://github.com/ioansalau/archguide-mcp-python/releases/new
```

## 🔍 Troubleshooting

**Common Issues:**

1. **401 Unauthorized**: Check API token in `~/.pypirc`
2. **File already exists**: Version already uploaded, increment version number
3. **Import errors**: Check package structure and dependencies

**Validation Commands:**

```bash
# Re-validate if needed
twine check dist/*

# Check wheel contents
python -m zipfile -l dist/archguide_mcp_python-0.2.0-py3-none-any.whl
```

## 📋 Release Checklist

- [x] Package builds successfully
- [x] Package validation passes
- [x] All tests pass (46/46 ✅)
- [x] Documentation is complete
- [x] License file exists
- [ ] PyPI accounts created
- [ ] API tokens configured
- [ ] Uploaded to TestPyPI
- [ ] Tested installation from TestPyPI
- [ ] Uploaded to production PyPI
- [ ] Tested production installation
- [ ] Git tag created
- [ ] GitHub release created (optional)

## 🎉 After Release

Users can install your package with:

```bash
pip install archguide-mcp-python
```

And use it with Claude Code by adding to their MCP configuration:

```json
{
  "mcpServers": {
    "archguide": {
      "command": "archguide-mcp",
      "env": {
        "GUIDELINES_PATH": "/path/to/guidelines"
      }
    }
  }
}
```