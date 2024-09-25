from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.document_loaders import CSVLoader


def retrieve_info(query: str, db, k = 4):
    docs = db.similarity_search(query, k=k)
    doc_objs = [doc.dict() for doc in docs]
    return doc_objs


def create_faiss_db_from_csv(csv_file, faiss_index_name=None) -> FAISS:
    embeddings = OpenAIEmbeddings()

    loader = CSVLoader(csv_file)
    documents = loader.load()
    db = FAISS.from_documents(documents, embeddings)

    if faiss_index_name is not None:
        db.save_local(faiss_index_name)

    return db
