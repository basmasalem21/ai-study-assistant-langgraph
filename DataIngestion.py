from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document

loader=TextLoader('/home/basma/Documents/AI  Studying Assistant with LangGraph/Tools/video_resources.txt', encoding="utf8")
documents=loader.load()
print(documents)
text = documents[0].page_content
#print(text)


# تقسيم حسب الفاصل
videos = text.split("----------------------------------------")

# تنظيف الفراغات
videos = [v.strip() for v in videos if v.strip()]

# chunking كل 3 فيديوهات
chunks = []

chunk_size = 10

for i in range(0, len(videos), chunk_size):

    chunk = "\n\n".join(videos[i:i + chunk_size])

    chunks.append(chunk)
    
docs = []
for i, chunk in enumerate(chunks):

    docs.append(
        Document(
            page_content=chunk,
            metadata={"chunk_id": i}
        )
    )
#print(chunks[-1])
