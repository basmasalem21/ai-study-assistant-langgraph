#=============IMPORTS=========
import os
from dotenv import load_dotenv
from typing import TypedDict, Dict, Sequence, Annotated

from langchain_openrouter import ChatOpenRouter
from langchain_core.tools import tool
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_community.chat_message_histories import ChatMessageHistory

from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from Tools.web_search import web_search
from Tools.gen2 import generate_mindmap
from retrieval_tool import retriever


#=============LOAD KEY=========
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

#=============MODEL=========
model = ChatOpenRouter(
    model="openai/gpt-oss-120b:free",
    temperature=0.7,
    api_key=OPENROUTER_API_KEY,
)

#=============TOOLS=============

@tool
def search(topic: str, k: int = 5):
    """Web search tool."""
    return web_search(topic, k)


@tool
def retrieval_tool(topic: str):
    """Retrieve YouTube videos of a specific topic."""

    results = retriever.invoke(topic)

    videos = []

    for r in results:

        videos.append({
            "title": r.metadata.get("title", "No Title"),
            "url": r.metadata.get("url", ""),
            "thumbnail": r.metadata.get("thumbnail", "")
        })

    return videos

@tool
def create_mindmap(text_file: str):
    """Create mind map from file."""

    return generate_mindmap(text_file)

tools = [search, retrieval_tool, create_mindmap]

tool_node = ToolNode(tools)

model = model.bind_tools(tools)

#=============STATE=========
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    session_id: str

#=============MEMORY=========
sessions: Dict[str, ChatMessageHistory] = {}

def get_history(session_id: str):
    if session_id not in sessions:
        sessions[session_id] = ChatMessageHistory()
    return sessions[session_id]

#=============AGENT=========
def AgentNode(state: AgentState):

    system = SystemMessage(content="""
You are a helpful AI assistant.

RULES:
- videos → retrieval_tool
- web → search
- mind map → create_mind_map
USE TOOLS ALWAYS when possible.
""")

    history = get_history(state["session_id"])

    messages = [system] + list(history.messages) + list(state["messages"])

    response = model.invoke(messages)

    for msg in state["messages"]:
        history.add_message(msg)

    history.add_message(response)

    return {"messages": [response]}

#=============ROUTING=========
def should_continue(state: AgentState):
    last = state["messages"][-1]
    return "tools" if getattr(last, "tool_calls", None) else END

#=============GRAPH=========
graph = StateGraph(AgentState)

graph.add_node("agent", AgentNode)
graph.add_node("tools", tool_node)

graph.set_entry_point("agent")

graph.add_conditional_edges("agent", should_continue)
graph.add_edge("tools", "agent")

app = graph.compile()