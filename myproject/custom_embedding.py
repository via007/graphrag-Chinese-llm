import requests
import numpy as np
from typing import List
# from sentence_transformers import SentenceTransformer
from graphrag.cache.pipeline_cache import PipelineCache
from graphrag.callbacks.workflow_callbacks import WorkflowCallbacks
from graphrag.language_model.providers.fnllm.utils import run_coroutine_sync


class CustomEmbeddingModel:
    """A custom embedding model provider using Sentence-Transformers."""

    def __init__(
            self,
            *,
            name: str,
            config,
            callbacks: WorkflowCallbacks | None = None,
            cache: PipelineCache | None = None,
    ) -> None:
        """
        Initialize the custom embedding model.

        Args:
            name: The name of the model.
            config: Configuration object containing model settings.
            callbacks: Optional workflow callbacks for error handling or logging.
            cache: Optional cache for storing embeddings.
        """
        from graphrag.config.models.language_model_config import (
            LanguageModelConfig,
        )
        model_path = getattr(LanguageModelConfig, "model", "gte-Qwen2-7B-instruct")
        # self.model = SentenceTransformer(model_path, cache_folder='./all-MiniLM-L6-v2')
        self.model = model_path
        self.name = name
        self.callbacks = callbacks
        self.cache = cache

    async def aembed_batch(self, text_list: List[str], **kwargs) -> List[List[float]]:
        """
        Asynchronously embed a batch of texts.

        Args:
            text_list: List of texts to embed.
            kwargs: Additional arguments (ignored here for simplicity).

        Returns:
            List of embeddings for each text.
        """
        if self.callbacks:
            self.callbacks.log(f"Embedding batch of {len(text_list)} texts with {self.name}")

        # embeddings = get_embeddings(text_list, self.model)
        embeddings = get_embeddings(text_list)
        return embeddings

    async def aembed(self, text: str, **kwargs) -> List[float]:
        """
        Asynchronously embed a single text.

        Args:
            text: Text to embed.
            kwargs: Additional arguments.

        Returns:
            Embedding for the text.
        """
        embeddings = await self.aembed_batch([text], **kwargs)
        return embeddings[0]

    def embed_batch(self, text_list: List[str], **kwargs) -> List[List[float]]:
        """
        Synchronously embed a batch of texts.

        Args:
            text_list: List of texts to embed.
            kwargs: Additional arguments.

        Returns:
            List of embeddings for each text.
        """
        return run_coroutine_sync(self.aembed_batch(text_list, **kwargs))

    def embed(self, text: str, **kwargs) -> List[float]:
        """
        Synchronously embed a single text.

        Args:
            text: Text to embed.
            kwargs: Additional arguments.

        Returns:
            Embedding for the text.
        """
        return run_coroutine_sync(self.aembed(text, **kwargs))


def get_embeddings(sentences, model):

    url = ""  # 可以使用本地自己的embeddings接口
    data = {
        "sentences": sentences,
        "model_type": model
    }

    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 200:
        result = response.json()
        embeddings = result.get("embeddings")
        embeddings_array = np.array(embeddings, dtype=np.float32).tolist()
        return embeddings_array
    return []
