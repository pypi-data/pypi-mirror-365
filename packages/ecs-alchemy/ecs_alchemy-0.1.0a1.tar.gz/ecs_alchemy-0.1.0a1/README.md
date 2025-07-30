# ecs-alchemy

**WORK IN PROGRESS - ALPHA VERSION**

This project provides an Entity Component System (ECS) architecture module for projects using SQLAlchemy.

## Installation

```bash
pip install ecs-alchemy
```

## Usage

```python
# Example usage to be added here
```

## Building and Uploading to PyPI

**1. Install Build Tools:**

```bash
pip install --upgrade build twine
```

**2. Build the Package:**

```bash
python3 -m build
```

**3. Upload to TestPyPI (Recommended):**

```bash
python3 -m twine upload --repository testpypi dist/*
```

**4. Install from TestPyPI:**

```bash
pip install --index-url https://test.pypi.org/simple/ --no-deps ecs-alchemy
```

**5. Upload to PyPI:**

```bash
python3 -m twine upload dist/*
```
