import os
from typing import List, Optional

from langchain.docstore.document import Document

from .embedding_manager import EmbeddingManager
from .llm_interface import JarvisPlatform_LLM, LLMInterface, ToolAgent_LLM
from .query_rewriter import QueryRewriter
from .reranker import Reranker
from .retriever import ChromaRetriever
from jarvis.jarvis_utils.config import (
    get_rag_embedding_model,
    get_rag_rerank_model,
    get_rag_vector_db_path,
    get_rag_embedding_cache_path,
)


class JarvisRAGPipeline:
    """
    RAG管道的主要协调器。

    该类集成了嵌入管理器、检索器和LLM，为添加文档和查询
    提供了一个完整的管道。
    """

    def __init__(
        self,
        llm: Optional[LLMInterface] = None,
        embedding_model: Optional[str] = None,
        db_path: Optional[str] = None,
        collection_name: str = "jarvis_rag_collection",
    ):
        """
        初始化RAG管道。

        参数:
            llm: 实现LLMInterface接口的类的实例。
                 如果为None，则默认为ToolAgent_LLM。
            embedding_model: 嵌入模型的名称。如果为None，则使用配置值。
            db_path: 持久化向量数据库的路径。如果为None，则使用配置值。
            collection_name: 向量数据库中集合的名称。
        """
        # 确定嵌入模型以隔离数据路径
        model_name = embedding_model or get_rag_embedding_model()
        sanitized_model_name = model_name.replace("/", "_").replace("\\", "_")

        # 如果给定了特定的db_path，则使用它。否则，创建一个特定于模型的路径。
        _final_db_path = (
            str(db_path)
            if db_path
            else os.path.join(get_rag_vector_db_path(), sanitized_model_name)
        )
        # 始终创建一个特定于模型的缓存路径。
        _final_cache_path = os.path.join(
            get_rag_embedding_cache_path(), sanitized_model_name
        )

        self.embedding_manager = EmbeddingManager(
            model_name=model_name,
            cache_dir=_final_cache_path,
        )
        self.retriever = ChromaRetriever(
            embedding_manager=self.embedding_manager,
            db_path=_final_db_path,
            collection_name=collection_name,
        )
        # 除非提供了特定的LLM，否则默认为ToolAgent_LLM
        self.llm = llm if llm is not None else ToolAgent_LLM()
        self.reranker = Reranker(model_name=get_rag_rerank_model())
        # 使用标准LLM执行查询重写任务，而不是代理
        self.query_rewriter = QueryRewriter(JarvisPlatform_LLM())

        print("✅ JarvisRAGPipeline 初始化成功。")

    def add_documents(self, documents: List[Document]):
        """
        将文档添加到向量知识库。

        参数:
            documents: 要添加的LangChain文档对象列表。
        """
        self.retriever.add_documents(documents)

    def _create_prompt(
        self, query: str, context_docs: List[Document], source_files: List[str]
    ) -> str:
        """为LLM或代理创建最终的提示。"""
        context = "\n\n".join([doc.page_content for doc in context_docs])
        sources_text = "\n".join([f"- {source}" for source in source_files])

        prompt_template = f"""
        你是一个专家助手。请根据用户的问题，结合下面提供的参考信息来回答。

        **重要**: 提供的上下文和文件列表**仅供参考**，可能不完整或已过时。在回答前，你应该**优先使用工具（如 read_code）来获取最新、最准确的信息**。

        参考文件列表:
        ---
        {sources_text}
        ---

        参考上下文:
        ---
        {context}
        ---

        问题: {query}

        回答:
        """
        return prompt_template.strip()

    def query(self, query_text: str, n_results: int = 5) -> str:
        """
        使用多查询检索和重排管道对知识库执行查询。

        参数:
            query_text: 用户的原始问题。
            n_results: 要检索的最终相关块的数量。

        返回:
            由LLM生成的答案。
        """
        # 1. 将原始查询重写为多个查询
        rewritten_queries = self.query_rewriter.rewrite(query_text)

        # 2. 为每个重写的查询检索初始候选文档
        all_candidate_docs = []
        for q in rewritten_queries:
            print(f"🔍 正在为查询变体 '{q}' 进行混合检索...")
            candidates = self.retriever.retrieve(q, n_results=n_results * 2)
            all_candidate_docs.extend(candidates)

        # 对候选文档进行去重
        unique_docs_dict = {doc.page_content: doc for doc in all_candidate_docs}
        unique_candidate_docs = list(unique_docs_dict.values())

        if not unique_candidate_docs:
            return "我在提供的文档中找不到任何相关信息来回答您的问题。"

        # 3. 根据*原始*查询对统一的候选池进行重排
        print(
            f"🔍 正在对 {len(unique_candidate_docs)} 个候选文档进行重排（基于原始问题）..."
        )
        retrieved_docs = self.reranker.rerank(
            query_text, unique_candidate_docs, top_n=n_results
        )

        if not retrieved_docs:
            return "我在提供的文档中找不到任何相关信息来回答您的问题。"

        # 打印最终检索到的文档的来源
        sources = sorted(
            list(
                {
                    doc.metadata["source"]
                    for doc in retrieved_docs
                    if "source" in doc.metadata
                }
            )
        )
        if sources:
            print(f"📚 根据以下文档回答:")
            for source in sources:
                print(f"  - {source}")

        # 4. 创建最终提示并生成答案
        # 我们使用原始的query_text作为给LLM的最终提示
        prompt = self._create_prompt(query_text, retrieved_docs, sources)

        print("🤖 正在从LLM生成答案...")
        answer = self.llm.generate(prompt)

        return answer
