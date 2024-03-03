from typing import Any, Dict, List, Optional, cast, AnyStr
from langchain_core.documents import Document
import weaviate
import weaviate.classes as wvc
from weaviate.util import generate_uuid5
import os
from contextlib import contextmanager
from langchain_core.retrievers import BaseRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun


class VectorModel:
    """A vector model of a document"""

    def __init__(self) -> None:
        """Initialize the vector model"""
        # Check env vars
        if os.environ.get("WEAVIATE_API_KEY", None) is None:
            raise Exception("Missing `WEAVIATE_API_KEY` environment variable.")

        if os.environ.get("WEAVIATE_ENVIRONMENT", None) is None:
            raise Exception("Missing `WEAVIATE_ENVIRONMENT` environment variable.")

        if os.environ.get("WEAVIATE_URL", None) is None:
            raise Exception("Missing `WEAVIATE_URL` environment variable.")

        if os.environ.get("OPENAI_API_KEY", None) is None:
            raise Exception("Missing `OPENAI_API_KEY` environment variable.")

        self.vectorizer_function = wvc.config.Configure.Vectorizer.text2vec_openai

    @property
    def exists_in_weaviate(self) -> bool:
        """Does the vector model exist in weaviate?"""
        with self._get_client() as client:
            exists = client.collections.exists(self.collection_name)
        return exists

    @contextmanager
    def _get_client(self) -> Any:
        """Get the client"""

        with weaviate.connect_to_local(
            **self._get_client_connection_string()
        ) as client:
            yield client

    def _get_client_connection_string(self) -> Any:
        """Get the client"""
        return {
            "host": "weaviate",
            "port": 8080,
            "headers": {"X-OpenAI-Api-Key": os.environ["OPENAI_API_KEY"]},
        }

    def create_collection_if_missing(self) -> Any:
        """Create the collection if it is missing"""
        with self._get_client() as client:
            if not self.exists_in_weaviate:
                client.collections.create(
                    self.collection_name,
                    vectorizer_config=self.vectorizer_function(),
                    properties=self.properties,
                )
        return None

    def delete_collection(self) -> Any:
        """Delete the collection
        WARNING: This will delete all data in the vector store.
        """
        with self._get_client() as client:
            if self.exists_in_weaviate:
                client.collections.delete(self.collection_name)
        return None

    def _convert_to_dict(self, document: Document) -> Dict:
        """Convert a document to a dictionary"""
        return {
            self.text_property: document.page_content,
            **document.metadata,
        }

    def add_document(self, document: Document) -> AnyStr:
        """Add a document to the collection"""
        with self._get_client() as client:
            collection = client.collections.get(self.collection_name)
            uuid = collection.data.insert(
                self._convert_to_dict(document),
            )
        return uuid

    def add_documents(self, documents: List[Document]) -> List[AnyStr]:
        """Add documents to the collection"""
        records = [self._convert_to_dict(document) for document in documents]
        uuids: list[str] = []
        with self._get_client() as client:
            collection = client.collections.get(self.collection_name)

            with collection.batch.dynamic() as batch:
                for record in records:
                    uuid = generate_uuid5(record)
                    batch.add_object(
                        uuid=uuid,
                        properties=record,
                    )
                    uuids.append(uuid)
        return uuids

    def search_documents(
        self, query: str, hybrid_kwargs: dict[str, object] = None
    ) -> list[Document]:
        """Search for documents"""
        with self._get_client() as client:
            collection = client.collections.get(self.collection_name)
            results = collection.query.hybrid(
                query=query,
                limit=3,
                **(hybrid_kwargs or {}),
            )
        results = results.objects
        if not results:
            return []

        docs = []
        for result in results:
            result = result.properties
            text = result.pop(self.text_property)
            doc = Document(
                page_content=text,
                metadata=result,
            )
            docs.append(doc)
        return docs


class WeaviateHybridV4Retriever(BaseRetriever):
    vector_model: VectorModel

    class Config:
        """Configuration for this pydantic object."""

        arbitrary_types_allowed = True

    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager: CallbackManagerForRetrieverRun,
        where_filter: Optional[Dict[str, object]] = None,
        score: bool = False,
        hybrid_search_kwargs: Optional[Dict[str, object]] = None,
    ) -> List[Document]:
        """Look up similar documents in Weaviate.

        query: The query to search for relevant documents
         of using weviate hybrid search.

        where_filter: A filter to apply to the query.
            https://weaviate.io/developers/weaviate/guides/querying/#filtering

        score: Whether to include the score, and score explanation
            in the returned Documents meta_data.

        hybrid_search_kwargs: Used to pass additional arguments
         to the .with_hybrid() method.
            The primary uses cases for this are:
            1)  Search specific properties only -
                specify which properties to be used during hybrid search portion.
                Note: this is not the same as the (self.attributes) to be returned.
                Example - hybrid_search_kwargs={"properties": ["question", "answer"]}
            https://weaviate.io/developers/weaviate/search/hybrid#selected-properties-only

            2) Weight boosted searched properties -
                Boost the weight of certain properties during the hybrid search portion.
                Example - hybrid_search_kwargs={"properties": ["question^2", "answer"]}
            https://weaviate.io/developers/weaviate/search/hybrid#weight-boost-searched-properties

            3) Search with a custom vector - Define a different vector
                to be used during the hybrid search portion.
                Example - hybrid_search_kwargs={"vector": [0.1, 0.2, 0.3, ...]}
            https://weaviate.io/developers/weaviate/search/hybrid#with-a-custom-vector

            4) Use Fusion ranking method
                Example - from weaviate.gql.get import HybridFusion
                hybrid_search_kwargs={"fusion": fusion_type=HybridFusion.RELATIVE_SCORE}
            https://weaviate.io/developers/weaviate/search/hybrid#fusion-ranking-method
        """
        model = self.vector_model
        model.create_collection_if_missing()
        if hybrid_search_kwargs is None:
            hybrid_search_kwargs = {}

        results = model.search_documents(query, hybrid_kwargs=hybrid_search_kwargs)

        return results
