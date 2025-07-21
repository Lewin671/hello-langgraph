import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add project root to Python path for module import
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from langchain_community.document_loaders import WebBaseLoader

urls = ["https://www.anthropic.com/engineering/building-effective-agents"]

docs = [WebBaseLoader(url).load() for url in urls]

from langchain_text_splitters import RecursiveCharacterTextSplitter

docs_list = [item for sublist in docs for item in sublist]

text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=100, chunk_overlap=50
)
doc_splits = text_splitter.split_documents(docs_list)

from langchain_core.vectorstores import InMemoryVectorStore

# Doubao Embedding 自定义实现
from langchain.embeddings.base import Embeddings
from typing import List

import requests
import os


class DoubaoEmbeddings(Embeddings):
    def __init__(self, api_key: str, api_url: str, model: str = None):
        self.api_key = api_key
        self.api_url = api_url
        self.model = model

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        payload = {
            "encoding_format": "float",
            "input": texts,
        }
        if self.model:
            payload["model"] = self.model
        response = requests.post(
            url=self.api_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
        )
        response.raise_for_status()
        data = response.json()["data"]
        # 按 index 排序，确保顺序和输入一致
        data_sorted = sorted(data, key=lambda x: x["index"])
        return [item["embedding"] for item in data_sorted]

    def embed_query(self, text: str) -> List[float]:
        # 单条输入也用批量接口，保证一致性
        return self.embed_documents([text])[0]


# 加载 .env 配置
project_root = Path(__file__).parent.parent
env_path = os.path.join(project_root, ".env")
if os.path.exists(env_path):
    load_dotenv(env_path)

# 从 .env 读取 Doubao 配置
DOUBAO_API_KEY = os.getenv("DOUBAO_API_KEY", "your-doubao-key")
DOUBAO_EMBEDDING_URL = os.getenv(
    "DOUBAO_EMBEDDING_URL", "https://ark.cn-beijing.volces.com/api/v3/embeddings"
)
DOUBAO_EMBEDDING_MODEL = os.getenv("DOUBAO_EMBEDDING_MODEL", None)

embedding = DoubaoEmbeddings(
    api_key=DOUBAO_API_KEY, api_url=DOUBAO_EMBEDDING_URL, model=DOUBAO_EMBEDDING_MODEL
)

vectorstore = InMemoryVectorStore.from_documents(
    documents=doc_splits, embedding=embedding
)
retriever = vectorstore.as_retriever()

from langchain.tools.retriever import create_retriever_tool

retriever_tool = create_retriever_tool(
    retriever,
    "retrieve_blog_posts",
    "Search and return information about the key points of building effective agents",
)


print(retriever_tool.invoke({"query": "types of reward hacking"}))
