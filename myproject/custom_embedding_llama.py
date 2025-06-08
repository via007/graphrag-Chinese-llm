import requests
import numpy as np
from typing import List

from graphrag.cache.pipeline_cache import PipelineCache
from graphrag.callbacks.workflow_callbacks import WorkflowCallbacks
from graphrag.language_model.providers.fnllm.utils import run_coroutine_sync


def get_embeddings(sentences: List[str]) -> List[List[float]]:
    """
    通过调用本地 llama-server API 获取文本的向量嵌入。
    """
    VECTOR_DIM = 8192
    API_URL = "http://localhost:8080/embedding"

    if not sentences:
        return []

    valid_sentences = []
    valid_indices = []
    for idx, text in enumerate(sentences):
        if text and isinstance(text, str) and text.strip():
            valid_sentences.append(text)
            valid_indices.append(idx)

    if not valid_sentences:
        return [[0.0] * VECTOR_DIM for _ in sentences]

    headers = {"Content-Type": "application/json"}
    payload = {"content": valid_sentences}

    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=300)
        response.raise_for_status()
        response_data = response.json()

        if not isinstance(response_data, list) or len(response_data) != len(valid_sentences):
            raise ValueError(f"Mismatched length: requested {len(valid_sentences)}, received {len(response_data)}.")

        final_embeddings = [[0.0] * VECTOR_DIM for _ in sentences]

        for i, item in enumerate(response_data):
            original_index = valid_indices[i]
            embedding = item.get("embedding")

            if embedding and isinstance(embedding, list) and len(embedding) == VECTOR_DIM:
                final_embeddings[original_index] = embedding
            else:                
                final_embeddings[original_index] = [0.0] * VECTOR_DIM
        
        return final_embeddings

    except requests.exceptions.Timeout:
        print(f"Error: Read timed out after 300 seconds while embedding a batch of {len(valid_sentences)} texts.")
        return [[0.0] * VECTOR_DIM for _ in sentences]
    except Exception as e:
        print(f"An unexpected error occurred in get_embeddings: {e}")
        return [[0.0] * VECTOR_DIM for _ in sentences]


class CustomEmbeddingModel:
    """
    一个 GraphRAG 嵌入策略，通过 API 调用本地运行的 llama-server。
    """

    def __init__(
            self,
            *,
            name: str,
            config=None, # config 仍然可以传入，用于未来可能的配置，如 API URL
            callbacks: WorkflowCallbacks | None = None,
            cache: PipelineCache | None = None,
    ) -> None:
        """
        初始化本地嵌入策略。
        """
        self.name = name
        self.api_url = getattr(config, "api_url", "http://localhost:8080/embedding") 
        self.callbacks = callbacks
        self.cache = cache
        print(f"Custom local embedding strategy initialized. Target API: {self.api_url}")

    async def aembed_batch(self, text_list: List[str], **kwargs) -> List[List[float]]:
        """
        异步地嵌入一批文本 (在当前实现中，它包装了一个同步的HTTP请求)。
        """
        if self.callbacks:
            self.callbacks.log(f"Embedding batch of {len(text_list)} texts using local server strategy.")

        # 注意：requests 是同步库。为了真正实现异步，需要使用像 aiohttp 这样的库。
        # 但对于 GraphRAG 的内部工作方式，通常它会在一个线程池中运行这个方法，所以同步请求也可以接受。
        embeddings = get_embeddings(text_list)
        return embeddings

    async def aembed(self, text: str, **kwargs) -> List[float]:
        """
        异步地嵌入单个文本。
        """
        embeddings = await self.aembed_batch([text], **kwargs)
        return embeddings[0]

    def embed_batch(self, text_list: List[str], **kwargs) -> List[List[float]]:
        return run_coroutine_sync(self.aembed_batch(text_list, **kwargs))

    def embed(self, text: str, **kwargs) -> List[float]:
        return run_coroutine_sync(self.aembed(text, **kwargs))