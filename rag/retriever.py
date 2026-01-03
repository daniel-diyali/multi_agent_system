from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os

class KnowledgeBaseRetriever:
    def __init__(self, docs_path: str):
        self.docs_path = docs_path
        try:
            from langchain_openai import OpenAIEmbeddings
            self.embeddings = OpenAIEmbeddings()
            self.use_embeddings = True
        except Exception:
            self.embeddings = None
            self.use_embeddings = False
        
        self.documents = self._load_documents()
        if self.use_embeddings:
            self.vectorstore = self._initialize_vectorstore()
        else:
            self.vectorstore = None
    
    def _initialize_vectorstore(self):
        if not self.use_embeddings:
            return None
            
        persist_directory = f"./data/chroma/{os.path.basename(self.docs_path)}"
        
        # Check if vectorstore already exists
        if os.path.exists(persist_directory):
            return Chroma(
                persist_directory=persist_directory,
                embedding_function=self.embeddings
            )
        
        # Create new vectorstore
        if self.documents:
            vectorstore = Chroma.from_documents(
                self.documents,
                self.embeddings,
                persist_directory=persist_directory
            )
            return vectorstore
        
        # Return empty vectorstore if no documents
        return Chroma(
            persist_directory=persist_directory,
            embedding_function=self.embeddings
        )
    
    def _load_documents(self):
        try:
            loader = DirectoryLoader(
                self.docs_path,
                glob="**/*.md",
                loader_cls=TextLoader
            )
            documents = loader.load()
            
            # Split documents into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=50,
                separators=["\n\n", "\n", " ", ""]
            )
            
            return text_splitter.split_documents(documents)
        except Exception as e:
            print(f"Error loading documents from {self.docs_path}: {e}")
            return []
    
    def retrieve(self, query: str, k: int = 3):
        """Retrieve top-k relevant documents for the query"""
        if self.use_embeddings and self.vectorstore:
            try:
                return self.vectorstore.similarity_search(query, k=k)
            except Exception:
                pass
        
        # Fallback to simple text matching
        return self._simple_text_search(query, k)
    
    def _simple_text_search(self, query: str, k: int = 3):
        """Simple keyword-based search when embeddings unavailable"""
        query_words = query.lower().split()
        scored_docs = []
        
        for doc in self.documents:
            content_lower = doc.page_content.lower()
            score = sum(1 for word in query_words if word in content_lower)
            if score > 0:
                scored_docs.append((score, doc))
        
        # Sort by score and return top k
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        return [doc for _, doc in scored_docs[:k]]
    
    def add_documents(self, documents):
        """Add new documents to the vectorstore"""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
        chunks = text_splitter.split_documents(documents)
        self.vectorstore.add_documents(chunks)