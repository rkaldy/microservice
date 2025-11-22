from pydantic import BaseModel, Field


class ExampleResponse(BaseModel):
    status: str = Field(
        ..., title="Example status", description="Example status", examples=["success", "failure"]
    )
