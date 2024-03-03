from common.retrievers import VectorModel
from weaviate.classes.config import Property, DataType


class WebDocuments(VectorModel):
    """A vector store for web documents"""

    collection_name: str = "WebDocs"
    text_property: str = "text"

    properties: list[Property] = [
        Property(name=text_property, data_type=DataType.TEXT),
        Property(name="source", data_type=DataType.TEXT),
        Property(name="title", data_type=DataType.TEXT),
        Property(name="description", data_type=DataType.TEXT),
    ]


class PDFDocuments(VectorModel):
    """A vector store for local pdf documents"""

    collection_name: str = "PDFDocs"
    text_property: str = "text"

    properties: list[Property] = [
        Property(name=text_property, data_type=DataType.TEXT),
        Property(name="source", data_type=DataType.TEXT),
        Property(name="page", data_type=DataType.INT),
    ]
