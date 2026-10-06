# FastAPI v0.110.0 - Response Models & Return Type Annotations

## Automatic Response Model Inference

In FastAPI v0.110.0, function return type annotations are automatically used as the `response_model`, simplifying endpoint signatures.

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float

@app.get("/items/{item_id}")
def get_item(item_id: int) -> Item:
    return Item(name="Widget", price=19.99)
```

FastAPI uses Pydantic v2 under the hood to automatically filter output fields and validate the response structure.

## JSONResponse with Pydantic v2 Serialization

FastAPI v0.110.0 provides high-performance JSON serialization using Pydantic v2 `model_dump(mode='json')`.

```python
from fastapi.responses import JSONResponse

@app.get("/custom-response")
def custom_response():
    data = {"status": "ok", "version": "v0.110.0"}
    return JSONResponse(content=data, status_code=200)
```
