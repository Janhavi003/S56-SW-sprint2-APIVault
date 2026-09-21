# FastAPI v0.110.0 - Path Parameters and Routing

## Declaring Path Parameters

In FastAPI v0.110.0, path parameters are fully integrated with Pydantic v2 and `typing.Annotated`.

```python
from typing import Annotated
from fastapi import FastAPI, Path

app = FastAPI()

@app.get("/items/{item_id}")
def read_item(item_id: Annotated[int, Path(title="The ID of the item to get", ge=1)]):
    return {"item_id": item_id}
```

## Pydantic v2 Migration Notes

FastAPI v0.110.0 uses Pydantic v2 for internal schema generation and validation.

Key changes:
- `regex` parameter in `Path` is replaced by `pattern`.
- Custom root validators should use `@model_validator` instead of `@root_validator`.
- Enhanced performance and strict typing validation out of the box.
