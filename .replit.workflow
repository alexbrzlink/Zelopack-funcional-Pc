run = ["gunicorn", "--bind", "0.0.0.0:5000", "--reuse-port", "--reload", "main:app"]
hidden = ["__pycache__", "*.pyc", "*.pyo", ".pytest_cache", ".coverage", "htmlcov"]
onBoot = ["python simple_background_checker.py &"]

[env]
PYTHONUNBUFFERED = "1"
PYTHONDONTWRITEBYTECODE = "1"
FLASK_DEBUG = "1"

[packager]
language = "python3"
ignoredPaths = [".git", ".config", "venv", ".venv"]

[languages.python3]
pattern = "**/*.py"
syntax = "python"

[languages.html]
pattern = "**/*.html"
syntax = "html"

[languages.css]
pattern = "**/*.css"
syntax = "css"

[languages.javascript]
pattern = "**/*.js"
syntax = "javascript"