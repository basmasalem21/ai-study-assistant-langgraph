import os
import re
from dotenv import load_dotenv
from graphviz import Digraph
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.3,
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

    try:
        response = model.invoke(prompt)
        output = response.content
    except Exception as e:
        print(f"LLM error: {e}, falling back to rule-based extraction")
        # Fallback to rule-based extraction
        relationships = []
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        main_topic = sentences[0].split()[0] if sentences else "Topic"
        main_topic = main_topic.capitalize()
        relationships.append((main_topic, "Main Topic"))
        
        stop_words = {'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'need', 'dare', 'ought', 'used', 'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by', 'from', 'as', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'between', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 'just', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once'}
        
        for sentence in sentences[:10]:
            words = sentence.split()
            if len(words) >= 3:
                for word in reversed(words):
                    if word.lower() not in stop_words and len(word) > 2:
                        object_ = word.capitalize()
                        if object_ != main_topic:
                            relationships.append((main_topic, object_))
                            break
        
        seen = set()
        unique_relationships = []
        for rel in relationships:
            if rel not in seen:
                seen.add(rel)
                unique_relationships.append(rel)
        
        output = "\n".join([f"{a} --> {b}" for a, b in unique_relationships])

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