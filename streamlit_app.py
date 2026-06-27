import os
import streamlit as st
from langchain_core.messages import HumanMessage

from Tools.web_search import web_search
from Tools.gen2 import generate_mindmap
from retrieval_tool import retriever

st.set_page_config(
    page_title="AI Study Assistant",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 AI Study Assistant")

tab1, tab2, tab3 = st.tabs(
    [
        "🎥 Learning Videos",
        "🌐 Google Search",
        "🧠 Mind Map"
    ]
)

with tab1:

    st.header("🎥 Learning Videos")

    topic = st.text_input(
        "Enter a topic",
        key="video_topic"
    )

    if st.button("Find Videos"):

        with st.spinner("Searching videos..."):

            docs = retriever.invoke(topic)

            videos = []
            for doc in docs:
                videos.append({
                    "title": doc.metadata.get("title", "No title"),
                    "url": doc.metadata.get("url", ""),
                    "thumbnail": doc.metadata.get("thumbnail", "")
                })

        if videos:

            for video in videos:

                st.subheader(video["title"])

                if video["thumbnail"]:
                    st.image(video["thumbnail"], width=300)

                if video["url"]:
                    st.link_button(
                        "▶ Watch",
                        video["url"]
                    )

                st.divider()
        else:
            st.warning("No videos found")

with tab2:

    st.header("🌐 Google Search")

    query = st.text_input(
        "Search anything",
        key="google_query"
    )

    if st.button("Search"):

        with st.spinner("Searching..."):

            results = web_search(query, 5)

        if results:
            for i, result in enumerate(results, 1):
                st.subheader(f"{i}. {result.get('title', 'No title')}")
                st.markdown(f"**URL:** {result.get('href', 'No URL')}")
                st.write(result.get('body', 'No description'))
                st.divider()
        else:
            st.warning("No results found")

with tab3:

    st.header("🧠 Mind Map")

    uploaded_file = st.file_uploader(
        "Upload TXT File",
        type=["txt"]
    )

    if uploaded_file:

        path = f"temp_{uploaded_file.name}"

        with open(path,"wb") as f:
            f.write(uploaded_file.read())

        if st.button("Generate Mind Map"):

            with st.spinner("Generating..."):

                result = generate_mindmap(path)

            image_path = result.get("path")

            if image_path and os.path.exists(image_path):

                st.image(image_path)

                with open(image_path,"rb") as f:

                    st.download_button(
                        "Download",
                        f,
                        file_name="mindmap.png"
                    )
            else:
                st.error("Failed to generate mind map")
