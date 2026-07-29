"""FastAPI service exposing the LangGraph research agent over HTTP."""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from agent import graph

app = FastAPI(
    title="LangGraph Research Agent API",
    description="HTTP wrapper around a LangGraph ReAct research agent (web search + source citation).",
    version="1.0.0",
)


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, examples=["What is the latest stable Python version?"])


class ChatResponse(BaseModel):
    answer: str


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    try:
        result = graph.invoke({"messages": [("user", request.question)]})
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"Agent error: {exc}") from exc
    answer = result["messages"][-1].content
    return ChatResponse(answer=answer)
