from pydantic import BaseModel
from typing import TypedDict
from semantic_kernel.data.vector import VectorStoreField, vectorstoremodel
from typing import Annotated
from dataclasses import dataclass
from semantic_kernel.connectors.ai.open_ai import OpenAITextEmbedding
import os


class RAGState(BaseModel):

    document_path: str
    document_read: bool
    document_indexed: bool
    user_query: str
    db_response: str
    llm_response: str


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

    # def __post_init__(self):
    #     if self.vector is None:
    #         self.vector = f"Id: {self.id}, Content: {self.content}"