import os
from dotenv import load_dotenv
from typing import TypedDict, Dict, Sequence, Annotated

from langchain_openrouter import ChatOpenRouter
from langchain_core.tools import tool
from langchain_core.messages import BaseMessage, SystemMessage
from langchain_community.chat_message_histories import ChatMessageHistory

from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from Tools.web_search import web_search
from Tools.gen2 import generate_mindmap
from retrieval_tool import retriever

load_dotenv()

# ================= MODEL =================

model = ChatOpenRouter(
    model="openai/gpt-oss-120b:free",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    temperature=0.7,
)

# ================= TOOLS =================

@tool
def search(query: str):
    """Search Google for latest information."""
    return web_search(query)


@tool
def retrieval_tool(query: str):
    """Return learning YouTube videos."""

    docs = retriever.invoke(query)

    videos = []

    for d in docs:
        videos.append({
            "title": d.metadata.get("title"),
            "url": d.metadata.get("url"),
            "thumbnail": d.metadata.get("thumbnail")
        })

    return videos


@tool
def create_mindmap(file_path: str):
    """Generate mind map from txt file."""
    return generate_mindmap(file_path)


tools = [search, retrieval_tool, create_mindmap]

tool_node = ToolNode(tools)

model = model.bind_tools(tools)

# ================= STATE =================

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    session_id: str

# ================= MEMORY =================

sessions: Dict[str, ChatMessageHistory] = {}

def get_history(session_id):

    if session_id not in sessions:
        sessions[session_id] = ChatMessageHistory()

    return sessions[session_id]

# ================= AGENT =================

def agent(state: AgentState):

    system = SystemMessage(
        content="""
You are an AI Study Assistant.

Rules:

If user asks for:
- videos
- youtube
- playlist
- course
- tutorial

ALWAYS call retrieval_tool.

If user asks:
- latest
- current
- recent
- search
- google

ALWAYS call search.

If user asks to generate a mind map

ALWAYS call create_mindmap.

Never answer yourself if a tool exists.
"""
    )

    history = get_history(state["session_id"])

    messages = [system]

    messages.extend(history.messages)

    messages.extend(state["messages"])

    response = model.invoke(messages)

    history.add_messages(state["messages"])
    history.add_message(response)

    return {"messages": [response]}

# ================= GRAPH =================

builder = StateGraph(AgentState)

builder.add_node("agent", agent)

builder.add_node("tools", tool_node)

builder.set_entry_point("agent")

builder.add_conditional_edges(
    "agent",
    tools_condition
)

builder.add_edge("tools", "agent")

app = builder.compile()