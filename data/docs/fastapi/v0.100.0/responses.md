# FastAPI v0.100.0 - Response Models and Status Codes

## Response Model Declaration

In FastAPI v0.100.0, use the `response_model` argument in route decorators to filter output data and validate responses.

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class ItemOut(BaseModel):
    name: str
    price: float

@app.post("/items/", response_model=ItemOut)
def create_item(item: ItemOut):
    return item
```

The response model enforces output validation using Pydantic v1 schemas.

## Response Status Codes and Exceptions

Set default HTTP status codes on endpoint decorators, and raise `HTTPException` for error conditions.

```python
from fastapi import FastAPI, HTTPException, status

app = FastAPI()

@app.get("/items/{item_id}", status_code=status.HTTP_200_OK)
def get_item(item_id: int):
    if item_id not in [1, 2, 3]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    return {"item_id": item_id}
```
