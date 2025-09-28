from semantic_kernel.data.vector import VectorStoreField, vectorstoremodel
from typing import Annotated
from dataclasses import dataclass
from semantic_kernel.connectors.ai.open_ai import OpenAITextEmbedding

@vectorstoremodel
@dataclass
class DataModel:

    content: Annotated[str, VectorStoreField('data', is_indexed=True, is_full_text_indexed=True)]
    id: Annotated[str, VectorStoreField('key')]
    vector: Annotated[list[float] | str | None, VectorStoreField(
        'vector', 
        dimensions=1536, 
        distance_function="cosine",
        embedding_generator=OpenAITextEmbedding(ai_model_id="text-embedding-3-small"),
    )] = None