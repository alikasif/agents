# Chroma Vector Database MCP Server

A Model Context Protocol (MCP) server that exposes Chroma vector database operations through FastMCP SDK. This server provides seamless integration with Chroma, enabling LLM agents to perform vector database operations like insert, delete, search, and update.

## Overview

This MCP server acts as a bridge between LLM agents and Chroma vector databases, exposing core vector database operations through standardized MCP tools. Built with [FastMCP](https://github.com/jlopp/fastmcp), it provides a lightweight and efficient way to interact with vector databases.

## Features

- **Insert**: Add embeddings and metadata to the vector database
- **Delete**: Remove embeddings by ID or filter conditions
- **Search**: Perform similarity searches across stored embeddings
- **Update**: Modify existing embeddings and associated metadata
- **Collection Management**: Create, list, and manage multiple collections
- **Metadata Filtering**: Support for advanced filtering on document metadata

## Prerequisites

- Python 3.8 or higher
- Chroma vector database (`pip install chromadb`)
- FastMCP SDK (`pip install fastmcp`)

## Installation

1. Clone or download this project
2. Install dependencies:
   ```bash
   pip install chromadb fastmcp
   ```

3. Ensure Chroma is properly installed and accessible in your Python environment

## Quick Start

### Starting the MCP Server

```bash
python mcp_server.py
```

The server will start and expose the following tools:

- `chroma_insert` - Insert embeddings into a collection
- `chroma_delete` - Delete embeddings from a collection
- `chroma_search` - Search for similar embeddings
- `chroma_update` - Update existing embeddings
- `chroma_list_collections` - List all available collections
- `chroma_create_collection` - Create a new collection
- `chroma_delete_collection` - Delete a collection

## API Reference

### chroma_insert

Insert embeddings and metadata into a Chroma collection.

**Parameters:**
- `collection_name` (str): Name of the target collection
- `ids` (list[str]): Unique identifiers for the embeddings
- `embeddings` (list[list[float]]): Vector embeddings
- `documents` (list[str], optional): Associated text documents
- `metadatas` (list[dict], optional): Metadata for each embedding

**Example:**
```python
{
  "collection_name": "documents",
  "ids": ["doc1", "doc2"],
  "embeddings": [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]],
  "documents": ["Text 1", "Text 2"],
  "metadatas": [{"source": "web"}, {"source": "pdf"}]
}
```

### chroma_delete

Delete embeddings from a collection.

**Parameters:**
- `collection_name` (str): Name of the target collection
- `ids` (list[str]): IDs of embeddings to delete
- `where` (dict, optional): Filter conditions for deletion

**Example:**
```python
{
  "collection_name": "documents",
  "ids": ["doc1", "doc2"]
}
```

### chroma_search

Search for similar embeddings in a collection.

**Parameters:**
- `collection_name` (str): Name of the collection to search
- `query_embeddings` (list[list[float]]): Query vectors
- `n_results` (int, default: 10): Number of results to return
- `where` (dict, optional): Filter conditions
- `include` (list[str], optional): Fields to include (e.g., ["embeddings", "documents", "metadatas"])

**Example:**
```python
{
  "collection_name": "documents",
  "query_embeddings": [[0.1, 0.2, 0.3]],
  "n_results": 5,
  "include": ["documents", "metadatas", "distances"]
}
```

### chroma_update

Update existing embeddings in a collection.

**Parameters:**
- `collection_name` (str): Name of the target collection
- `ids` (list[str]): IDs of embeddings to update
- `embeddings` (list[list[float]], optional): New vector embeddings
- `documents` (list[str], optional): New document texts
- `metadatas` (list[dict], optional): New metadata

**Example:**
```python
{
  "collection_name": "documents",
  "ids": ["doc1"],
  "embeddings": [[0.2, 0.3, 0.4]],
  "metadatas": [{"source": "updated_pdf"}]
}
```

### chroma_list_collections

List all available collections in the database.

**Parameters:** None

**Returns:**
- `collections` (list): List of collection names

### chroma_create_collection

Create a new collection.

**Parameters:**
- `collection_name` (str): Name for the new collection
- `metadata` (dict, optional): Collection-level metadata

**Example:**
```python
{
  "collection_name": "new_collection",
  "metadata": {"description": "My document collection"}
}
```

### chroma_delete_collection

Delete an existing collection.

**Parameters:**
- `collection_name` (str): Name of the collection to delete

## Architecture

The MCP server follows the MCP specification and uses FastMCP SDK for:
- **Tool Registration**: Automatic registration of Chroma operations as MCP tools
- **Type Safety**: Built-in type validation and serialization
- **Error Handling**: Consistent error responses across all operations
- **Async Support**: Non-blocking operations for improved performance

## Configuration

### Chroma Client Configuration

By default, the server uses Chroma's in-memory or persistent storage. To use a remote Chroma server:

```python
import chromadb

# Persistent local storage
client = chromadb.PersistentClient(path="./chroma_data")

# Remote Chroma server
client = chromadb.HttpClient(host="localhost", port=8000)
```

## Usage Examples

### Example 1: Document Insertion and Search

```python
# Insert documents
insert_request = {
  "collection_name": "documents",
  "ids": ["doc1", "doc2"],
  "embeddings": [[0.1, 0.2], [0.3, 0.4]],
  "documents": ["Hello world", "Goodbye world"],
  "metadatas": [{"type": "greeting"}, {"type": "farewell"}]
}

# Search for similar documents
search_request = {
  "collection_name": "documents",
  "query_embeddings": [[0.15, 0.25]],
  "n_results": 2
}
```

### Example 2: Metadata Filtering

```python
# Delete with metadata filter
delete_request = {
  "collection_name": "documents",
  "where": {"type": "greeting"}
}

# Search with metadata filter
search_request = {
  "collection_name": "documents",
  "query_embeddings": [[0.1, 0.2]],
  "where": {"type": {"$eq": "greeting"}},
  "n_results": 5
}
```

## Error Handling

The server provides structured error responses:

- **Collection Not Found**: Returned when accessing non-existent collection
- **Invalid Embeddings**: Returned when embedding dimensions don't match
- **Invalid Parameters**: Returned when required parameters are missing or malformed

Example error response:
```json
{
  "error": "Collection 'documents' not found",
  "code": "COLLECTION_NOT_FOUND"
}
```

## Testing

To test the MCP server:

```bash
# Start the server
python mcp_server.py

# In another terminal, run tests or use the server with an MCP client
```

## Performance Considerations

- **Batch Operations**: Use batch inserts/deletes for better performance
- **Collection Size**: Consider splitting large collections for faster searches
- **Metadata Filtering**: Complex filters may impact search performance
- **Embedding Dimensions**: Ensure consistent embedding dimensions across operations

## Limitations

- Maximum embedding dimension compatibility with Chroma
- Batch operation size limits depend on available memory
- Network latency if using remote Chroma server

## Troubleshooting

### Collection Not Found
Ensure the collection exists before performing operations. Use `chroma_list_collections` to verify.

### Embedding Dimension Mismatch
Verify all embeddings have the same dimension as previously inserted embeddings in the collection.

### Connection Issues
If using a remote Chroma server, verify the host and port configuration.

## Contributing

Contributions are welcome! Please ensure:
- Code follows Python best practices
- All operations are properly error-handled
- Documentation is updated for new features

## License

See LICENSE file in the parent repository.

## References

- [Chroma Documentation](https://docs.trychroma.com/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
