# 📦 Publishing chatty to PyPI

This guide will help you publish the `chatty` package to PyPI.

## 🚀 Quick Start

1. **Test the package locally:**
   ```bash
   uv run python test_chatty.py
   ```

2. **Build the package:**
   ```bash
   uv build
   ```

3. **Publish to TestPyPI (recommended first):**
   ```bash
   python publish.py --test
   ```

4. **Publish to PyPI:**
   ```bash
   python publish.py
   ```

## 📋 Prerequisites

### 1. PyPI Account
- Create an account at [pypi.org](https://pypi.org/account/register/)
- Verify your email address
- Enable 2FA (recommended)

### 2. API Token
- Go to [Account Settings](https://pypi.org/manage/account/token/)
- Create a new API token
- Set scope to "Entire account" or specific to this project
- **Save the token securely** - you won't see it again!

### 3. TestPyPI Account (Optional but Recommended)
- Create an account at [test.pypi.org](https://test.pypi.org/account/register/)
- Create an API token there too
- Use this for testing uploads

## 🔧 Manual Publishing (Alternative)

If you prefer to publish manually:

### Install twine:
```bash
uv add --dev twine
```

### Build the package:
```bash
uv build
```

### Upload to TestPyPI:
```bash
uv run python -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*
```

### Upload to PyPI:
```bash
uv run python -m twine upload dist/*
```

## 🔐 Authentication

When prompted for credentials:
- **Username:** `__token__`
- **Password:** Your API token (including the `pypi-` prefix)

## ✅ Verification

After publishing:

### TestPyPI:
- Check: https://test.pypi.org/project/chatty/
- Install: `pip install -i https://test.pypi.org/simple/ chatty`

### PyPI:
- Check: https://pypi.org/project/chatty/
- Install: `pip install chatty`

## 🔄 Updating the Package

To publish a new version:

1. **Update version in `pyproject.toml`:**
   ```toml
   version = "0.1.1"  # Increment version
   ```

2. **Update version in `src/chatty/__init__.py`:**
   ```python
   __version__ = "0.1.1"
   ```

3. **Rebuild and republish:**
   ```bash
   uv build
   python publish.py
   ```

## 🐛 Troubleshooting

### Common Issues:

1. **"File already exists"**
   - Version already published
   - Increment version number

2. **"Invalid credentials"**
   - Check username is `__token__`
   - Verify API token is correct
   - Ensure token has proper permissions

3. **"Package name already taken"**
   - Choose a different package name
   - Update `name` in `pyproject.toml`

4. **"Build failed"**
   - Check `pyproject.toml` syntax
   - Ensure all files are present
   - Run tests first

## 📝 Package Information

- **Name:** chatty
- **Current Version:** 0.1.0
- **Description:** A simple and friendly command-line chat interface with colorful output
- **Author:** zokrezyl
- **License:** MIT

## 🎉 Success!

Once published, users can install your package with:

```bash
pip install chatty
```

And use it with:

```bash
chatty --help
chatty --name "Alice"
```

Happy publishing! 🚀