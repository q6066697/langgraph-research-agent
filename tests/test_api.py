from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

import api


class FakeGraph:
    """Stand-in for the compiled LangGraph graph: no LLM or search calls."""

    def __init__(self) -> None:
        self.calls = []

    def invoke(self, state):
        self.calls.append(state)
        return {"messages": [SimpleNamespace(content="Fake answer. Sources: https://example.com")]}


@pytest.fixture
def fake_graph(monkeypatch):
    graph = FakeGraph()
    monkeypatch.setattr(api, "graph", graph)
    return graph


@pytest.fixture
def client():
    return TestClient(api.app)


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_chat_returns_answer(client, fake_graph):
    response = client.post("/chat", json={"question": "What is LangGraph?"})
    assert response.status_code == 200
    assert response.json()["answer"] == "Fake answer. Sources: https://example.com"
    assert fake_graph.calls == [{"messages": [("user", "What is LangGraph?")]}]


def test_chat_without_question_returns_422(client, fake_graph):
    response = client.post("/chat", json={})
    assert response.status_code == 422
    assert fake_graph.calls == []
