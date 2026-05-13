import os
import re
from dotenv import load_dotenv
from graphviz import Digraph
from langchain_openrouter import ChatOpenRouter

load_dotenv()

model = ChatOpenRouter(
    model="openai/gpt-oss-120b:free",
    temperature=0.3,
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

def generate_mindmap(text_file: str):

    with open(text_file, "r", encoding="utf-8") as f:
        text = f.read()

    prompt = f"""
You are a knowledge graph extractor.

Extract a mind map in the format:
A --> B

RULES:
1. Merge repeated relationships with the same subject.
2. Combine similar objects using "and".
3. Do not repeat identical relationships.
4. Keep output concise.

Example:
Input:
Basma loves bananas. Basma loves apples.

Output:
Basma --> loves bananas and apples

TEXT:
{text}
"""

    response = model.invoke(prompt)
    output = response.content

    # ===== GRAPH =====
    g = Digraph("MindMap")

    g.attr(
        rankdir="LR",
        splines="ortho",
        nodesep="1",
        ranksep="1.2",
        overlap="false",
        pad="0.5",
        dpi="300"
    )

    g.attr("node", fontname="Arial")

    pattern = r"(.*?)\s*-->\s*(.*)"

    added_nodes = set()
    added_edges = set()

    for line in output.split("\n"):

        m = re.match(pattern, line)

        if not m:
            continue

        a, b = m.groups()

        a = a.strip()
        b = b.strip()

        # ===== MAIN NODE =====
        if a not in added_nodes:

            g.node(
                a,
                shape="box",
                style="rounded,filled",
                fillcolor="#93C5FD",
                color="#1D4ED8",
                fontcolor="black",
                fontsize="16",
                penwidth="2"
            )

            added_nodes.add(a)

        # ===== CHILD NODE =====
        if b not in added_nodes:

            g.node(
                b,
                shape="box",
                style="filled",
                fillcolor="#F9A8D4",
                color="#BE185D",
                fontcolor="black",
                fontsize="13"
            )

            added_nodes.add(b)

        # ===== EDGE =====
        if (a, b) not in added_edges:

            g.edge(
                a,
                b,
                color="#6B7280",
                penwidth="2"
            )

            added_edges.add((a, b))

    path = g.render(
        "mindmap",
        format="png",
        cleanup=True
    )

    return {"path": path}