# FastAPI v0.100.0 - Dependency Injection

## Basic Dependencies with Depends

FastAPI provides a powerful Dependency Injection system using the `Depends` function. You can declare dependencies as function parameters.

```python
from fastapi import Depends, FastAPI

app = FastAPI()

def common_parameters(q: str = None, skip: int = 0, limit: int = 100):
    return {"q": q, "skip": skip, "limit": limit}

@app.get("/items/")
def read_items(commons: dict = Depends(common_parameters)):
    return commons
```

In FastAPI v0.100.0, dependencies are declared directly with default arguments assigning `Depends(dependency_function)`.

## Yield Dependencies and Clean-up

To execute code before and after a request (such as opening and closing a database session), use standard Python generators with `yield`.

```python
from fastapi import Depends

def get_db():
    db = DBSession()
    try:
        yield db
    finally:
        db.close()
```

The code prior to `yield` runs before the route handler, and the code inside `finally` runs after the response is delivered.

## Dependency Overrides for Testing

During testing, you can override dependencies on the application instance using `app.dependency_overrides`.

```python
from fastapi.testclient import TestClient

def override_get_db():
    return TestingSessionLocal()

app.dependency_overrides[get_db] = override_get_db
```
