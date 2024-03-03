from langchain.pydantic_v1 import BaseModel, Field
from langchain_core.messages import BaseMessage


class Input(BaseModel):
    input: str
    chat_history: list[BaseMessage] = Field(
        extra={"widget": {"type": "chat", "input": "location"}},
    )


class Output(BaseModel):
    output: str
