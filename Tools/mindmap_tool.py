#===============LOADING LIBRARIES====================================
from langchain_openrouter import ChatOpenRouter
import os
from graphviz import Digraph
from dotenv import load_dotenv
import re


def generate_mindmap(text_file):


   
    #opening file and extracting text from it
    with open(text_file, "r", encoding="utf-8") as f:
        text = f.read()
    
    model = ChatOpenRouter(
        model="openai/gpt-oss-120b:free",
        temperature=0.3,
        api_key=os.getenv("OPENROUTER_API_KEY"),
    )

    prompt = f"""
        Extract a structured knowledge graph from the text.

        Return ONLY in this format:

        Concept A --relation--> Concept B

        Rules:
        - relation must be: contains, has, includes, uses, depends on, is a type of, such as
        - one relation per line
        - no extra text

        TEXT:
        {text}
        """
    response = model.invoke(prompt)
    output = response.content

    ##print(output)
    g = Digraph("MindMap")

    g.attr(
    bgcolor="ghostwhite",
    rankdir="LR"
    )

    pattern = r"(.*?)\s*--(.*?)-->\s*(.*)"

    for line in output.split("\n"):
        match = re.match(pattern, line)
        if match:
            parent = match.group(1).strip()
            relation = match.group(2).strip()
            child = match.group(3).strip()

            # ===== NODE STYLING =====
            g.node(parent, shape="box", style="filled", color="lightblue")
            g.node(child, shape="ellipse", style="filled", color="pink")

            # ===== EDGE STYLING =====
            g.edge(parent, child, label=relation, color="gray", fontsize="10")

    # ================== SAVE ==================
    output_path = g.render("mindmap", format="png", view=False)

    with open(output_path, "rb") as f:
        image_bytes = f.read()

    return image_bytes

    
    



    


