from pathlib import Path

Path("app/__init__.py").touch()
Path("app/data/__init__.py").touch()
Path("app/services/__init__.py").touch()


from pathlib import Path

# Make sure the directories exist first
Path("app/data").mkdir(parents=True, exist_ok=True)
Path("app/services").mkdir(parents=True, exist_ok=True)

# Then create __init__.py files
Path("app/__init__.py").touch(exist_ok=True)
Path("app/data/__init__.py").touch(exist_ok=True)
Path("app/services/__init__.py").touch(exist_ok=True)
