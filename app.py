import os
import warnings
import logging
import streamlit as st
from uuid import uuid4

from langchain_core.messages import HumanMessage, AIMessage
from main import app



# ===== CONFIG =====
warnings.filterwarnings("ignore")

os.environ["TRANSFORMERS_VERBOSITY"] = "error"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

logging.getLogger("transformers").setLevel(logging.ERROR)


# ========== SESSION ==========
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

if "current_session" not in st.session_state:
    st.session_state.current_session = "default"

if "sessions" not in st.session_state:
    st.session_state.sessions = {}


st.title("🤖 AI Assistant")


# ========== FILE UPLOAD ==========
uploaded_file = st.file_uploader("Upload TXT", type=["txt"])

if uploaded_file:

    file_path = f"temp_{uploaded_file.name}"

    with open(file_path, "wb") as f:
        f.write(uploaded_file.read())

    st.session_state["uploaded_path"] = file_path

    st.success("Uploaded ✅")

# ========== BUTTON ==========
if st.button("Generate Mindmap"):

    file_path = st.session_state.get("uploaded_path")

    if not file_path:
        st.error("Upload file first")
        st.stop()

    with st.spinner("🧠 Generating Mindmap..."):

        result = app.invoke({
            "messages": [
                HumanMessage(
                    content=f"create mind map from {file_path}"
                )
            ],
            "session_id": st.session_state.session_id
        })

    mindmap_path = None

    # ===== GET TOOL RESULT =====
    for msg in result["messages"]:

        if msg.__class__.__name__ == "ToolMessage":

            tool_content = msg.content

            # لو dict
            if isinstance(tool_content, dict):

                mindmap_path = tool_content.get("path")

            # لو string
            elif isinstance(tool_content, str):

                try:
                    data = eval(tool_content)

                    if isinstance(data, dict):
                        mindmap_path = data.get("path")

                    else:
                        mindmap_path = tool_content

                except:
                    mindmap_path = tool_content

            break

    # ===== SHOW IMAGE =====
    if mindmap_path and os.path.exists(mindmap_path):

        st.image(
            mindmap_path,
            caption="Generated Mindmap",
            use_container_width=True
        )

        with open(mindmap_path, "rb") as f:

            st.download_button(
                "⬇ Download Mindmap",
                f,
                file_name="mindmap.png",
                mime="image/png"
            )

    else:
        st.error("Mindmap not found")
#=============CHAT=========


def get_messages():
    sid = st.session_state.current_session
    return st.session_state.sessions.setdefault(sid, [])




messages = get_messages()

for msg in messages:

    role = msg["role"]
    content = msg["content"]

    with st.chat_message(role):

        # ===== VIDEOS =====
        if isinstance(content, list):

            for video in content:

                st.markdown(f"### 🎥 {video.get('title')}")

                if video.get("thumbnail"):
                    st.image(video["thumbnail"], width=300)

                if video.get("url"):
                    st.markdown(
                        f"[▶ Watch Video]({video['url']})",
                        unsafe_allow_html=True
                    )

                st.divider()

        else:
            st.write(content)

#=============USER INPUT=========
user_input = st.chat_input("Type message...")

if user_input:

    st.chat_message("user").write(user_input)

    messages.append({
        "role": "user",
        "content": user_input
    })

    with st.spinner("🤖 Thinking..."):

        result = app.invoke({
            "messages": [
                HumanMessage(content=m["content"])
                if m["role"] == "user"
                else AIMessage(content=str(m["content"]))
                for m in messages
            ],
            "session_id": st.session_state.current_session
        })

    last_msg = result["messages"][-1]

    ai_content = last_msg.content

    # ===== لو فيه tool output =====
    if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:

        tool_result = result["messages"][-2].content

        try:
            ai_content = eval(tool_result)
        except:
            ai_content = tool_result

    messages.append({
        "role": "assistant",
        "content": ai_content
    })

    # ===== DISPLAY =====
    with st.chat_message("assistant"):

        if isinstance(ai_content, list):

            for video in ai_content:

                st.markdown(f"### 🎥 {video.get('title')}")

                if video.get("thumbnail"):
                    st.image(video["thumbnail"], width=300)

                if video.get("url"):
                    st.markdown(
                        f"[▶ Watch Video]({video['url']})",
                        unsafe_allow_html=True
                    )

                st.divider()

        else:
            st.write(ai_content)