# Running unit tests

1. Activate the virtual environment.

2. If the test dependencies weren't installed as part of the environment setup, install them now:

```bash
poetry install --with tests
```

3. Run unit tests:

```bash
pytest -p no:faulthandler --cov=ansys.solutions --cov-report=term --cov-report=xml --cov-report=html -vv
```
