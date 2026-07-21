import os
from typing import Annotated

from dotenv import load_dotenv
from typing_extensions import TypedDict

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch

from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

load_dotenv()

PROVIDER = os.getenv("PROVIDER", "openai")

if PROVIDER == "openai":
    llm = ChatOpenAI(model="gpt-4o-mini")
elif PROVIDER == "anthropic":
    llm = ChatAnthropic(model="claude-sonnet-5")
else:
    raise ValueError(f"Unknown PROVIDER: {PROVIDER!r} (expected 'openai' or 'anthropic')")

tools = [TavilySearch(max_results=3)]
llm_with_tools = llm.bind_tools(tools)

SYSTEM_PROMPT = (
    "You are a research assistant. Before answering any factual question, you "
    "MUST search the web using the available search tool to verify current "
    "information — never answer from memory alone. Always end your answer with "
    "a list of the source URLs you used."
)


class State(TypedDict):
    messages: Annotated[list, add_messages]


def agent(state: State) -> State:
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


graph_builder = StateGraph(State)
graph_builder.add_node("agent", agent)
graph_builder.add_node("tools", ToolNode(tools))
graph_builder.set_entry_point("agent")
graph_builder.add_conditional_edges("agent", tools_condition)
graph_builder.add_edge("tools", "agent")

graph = graph_builder.compile()


if __name__ == "__main__":
    print("Research agent. Type 'exit' or 'quit' to stop.")
    while True:
        user_input = input("\nQuestion: ").strip()
        if user_input.lower() in ("exit", "quit"):
            break
        if not user_input:
            continue
        result = graph.invoke({"messages": [("user", user_input)]})
        final_message = result["messages"][-1]
        print(f"\nAnswer: {final_message.content}")
