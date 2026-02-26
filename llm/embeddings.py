import faiss
import time
from langchain_text_splitters import MarkdownTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from uuid import uuid4
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_core.documents import Document
from config.config import Config

def get_top_chunks(pages: list[dict], question: str) -> list[Document]:
    
    docs = []
    
    text_splitter = MarkdownTextSplitter(
        chunk_size=1500,   
        chunk_overlap=300  
    )
    
    for page in pages:
        url = page['url']
        content = page['content']
        
        if len(content) < 2000:
            docs.append(Document(page_content=content, metadata={"url": url}))
        else:
            chunks = text_splitter.split_text(content)
            for chunk in chunks:
                docs.append(Document(page_content=chunk, metadata={"url": url}))
                
    print(f"Текст разбит на {len(docs)} чанков.")
    
    print(f"Загружаем модель эмбеддингов: {Config.EMBEDDING_MODEL}")
    embeddings = HuggingFaceEmbeddings(
        model_name=Config.EMBEDDING_MODEL,
        model_kwargs={'device': Config.DEVICE}
    )
    
    
    
    # index = faiss.IndexFlatL2(len(embeddings.embed_query("questions")))

    # vector_store = FAISS(
    #     embedding_function=embeddings,
    #     index=index,
    #     docstore=InMemoryDocstore(),
    #     index_to_docstore_id={},
    # )
    # vectorstore = FAISS.load_local(
    #             folder_path = "./faiss_data",
    #             embeddings = embeddings,
    #             allow_dangerous_deserialization = True
    #         )
    
    print(f"подгружаем документы")
    # # uuids = [str(uuid4()) for _ in range(len(docs))]
    # # vector_store.add_documents(documents=docs, ids=uuids)
    vectorstore = FAISS.from_documents(docs, embeddings)

    print(f"Сохранение в бд")
    vectorstore.save_local("./faiss_data")
    

    # print(f"Загрузка из бд")
    # FAISS.load_local("./faiss_data", embeddings, allow_dangerous_deserialization = True)


    print(f"Ищем топ{Config.TOP_K} ссылок")
    retriever = vectorstore.as_retriever(search_kwargs={"k": Config.TOP_K})
    top_chunks = retriever.invoke(question)
    
    return top_chunks
