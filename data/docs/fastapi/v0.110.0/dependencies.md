# FastAPI v0.110.0 - Dependency Injection & Lifespan

## Annotated Dependencies

FastAPI v0.110.0 recommends declaring dependencies with `typing.Annotated`. This avoids code duplication and improves static analysis support.

```python
from typing import Annotated
from fastapi import Depends, FastAPI

app = FastAPI()

def common_parameters(q: str | None = None, skip: int = 0, limit: int = 100):
    return {"q": q, "skip": skip, "limit": limit}

CommonsDep = Annotated[dict, Depends(common_parameters)]

@app.get("/items/")
def read_items(commons: CommonsDep):
    return commons
```

## Lifespan Events Context Manager

In FastAPI v0.110.0, the legacy `@app.on_event("startup")` and `@app.on_event("shutdown")` decorators are replaced by the `lifespan` context manager.

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    print("Database pool initialized")
    yield
    # Shutdown logic
    print("Database pool closed")

app = FastAPI(lifespan=lifespan)
```

## Global Dependencies with Dependencies Parameter

You can add global dependencies to the entire FastAPI application or APIRouter:

```python
from fastapi import FastAPI, Depends

app = FastAPI(dependencies=[Depends(verify_token), Depends(verify_key)])
```
