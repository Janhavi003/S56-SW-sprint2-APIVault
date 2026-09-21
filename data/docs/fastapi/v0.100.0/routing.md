# FastAPI v0.100.0 - Path Parameters and Routing

## Declaring Path Parameters

You can declare path parameters using standard Python format strings.

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id}
```

The value of the path parameter `item_id` will be passed to your function as the argument `item_id`.

## Path Parameters with Types

You can declare the type of a path parameter in the function using standard Python type annotations.

If you run this example and open your browser at `http://127.0.0.1:8000/items/3`, you will see a response of:

```json
{"item_id": 3}
```

### Data Validation

Data validation is performed automatically by Pydantic v1 in FastAPI v0.100.0. If you pass an invalid type like `http://127.0.0.1:8000/items/foo`, HTTP 422 Unprocessable Entity is returned.
