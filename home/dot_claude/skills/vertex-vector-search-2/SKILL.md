---
name: vertex-vector-search-2
description: Use when writing Python code for Google Cloud Vertex AI Vector Search 2.0 - collections, data objects, embeddings, semantic search, hybrid search, or ANN indexes
---

# Vertex AI Vector Search 2.0

Google Cloud's fully managed, self-tuning vector database built on ScaNN algorithm.

## Quick Reference

| Component | Purpose |
|-----------|---------|
| **Collection** | Schema-enforced container (data schema + vector schema) |
| **DataObject** | Individual item with data fields + vector embeddings |
| **Index** | Optional ANN index for production-scale search |

## SDK Clients

```python
from google.cloud import vectorsearch_v1beta

# Three specialized clients
vector_search_client = vectorsearch_v1beta.VectorSearchServiceClient()  # Collections, Indexes
data_object_client = vectorsearch_v1beta.DataObjectServiceClient()       # CRUD operations
search_client = vectorsearch_v1beta.DataObjectSearchServiceClient()      # Search, Query
```

## Creating Collections

```python
request = vectorsearch_v1beta.CreateCollectionRequest(
    parent=f"projects/{PROJECT_ID}/locations/{LOCATION}",
    collection_id="my-collection",
    collection={
        "data_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "category": {"type": "string"},
                "price": {"type": "number"},
            },
        },
        "vector_schema": {
            "title_embedding": {
                "dense_vector": {
                    "dimensions": 768,
                    "vertex_embedding_config": {
                        "model_id": "gemini-embedding-001",
                        "text_template": "{title}",
                        "task_type": "RETRIEVAL_DOCUMENT",
                    },
                },
            },
        },
    },
)
operation = vector_search_client.create_collection(request=request)
operation.result()  # Wait for completion
```

## DataObject Operations

### Create Single

```python
request = vectorsearch_v1beta.CreateDataObjectRequest(
    parent=f"projects/{PROJECT_ID}/locations/{LOCATION}/collections/{collection_id}",
    data_object_id="item-123",  # Must be RFC1035 compliant
    data_object={
        "data": {"title": "Product Name", "category": "Electronics", "price": 99.99},
        "vectors": {},  # Empty = auto-generate embeddings
    },
)
data_object_client.create_data_object(request=request)
```

### Batch Create (max 250 per batch for auto-embeddings)

```python
batch_request = [
    {"data_object_id": item["id"], "data_object": {"data": item["data"], "vectors": {}}}
    for item in items[:250]
]
request = vectorsearch_v1beta.BatchCreateDataObjectsRequest(
    parent=f"projects/{PROJECT_ID}/locations/{LOCATION}/collections/{collection_id}",
    requests=batch_request,
)
data_object_client.batch_create_data_objects(request)
```

### Get DataObject

```python
request = vectorsearch_v1beta.GetDataObjectRequest(
    name=f"projects/{PROJECT_ID}/locations/{LOCATION}/collections/{collection_id}/dataObjects/{id}"
)
data_object = data_object_client.get_data_object(request=request)

# Robust extraction (handles SDK version differences)
def extract_data(data_object) -> dict:
    """Extract data dict from DataObject, handling SDK version differences."""
    if hasattr(data_object, "data") and data_object.data:
        return dict(data_object.data)
    if hasattr(data_object, "struct_data") and data_object.struct_data:
        return dict(data_object.struct_data)  # Older SDK versions
    return {}

data = extract_data(data_object)
```

## Search Operations

### Semantic Search (natural language)

```python
request = vectorsearch_v1beta.SearchDataObjectsRequest(
    parent=f"projects/{PROJECT_ID}/locations/{LOCATION}/collections/{collection_id}",
    semantic_search=vectorsearch_v1beta.SemanticSearch(
        search_text="comfortable running shoes",
        search_field="title_embedding",
        task_type="QUESTION_ANSWERING",  # Pair with RETRIEVAL_DOCUMENT
        top_k=10,
        output_fields=vectorsearch_v1beta.OutputFields(
            data_fields=["title", "category", "price"]
        ),
    ),
)
results = search_client.search_data_objects(request)
```

### Text Search (keyword matching)

```python
request = vectorsearch_v1beta.SearchDataObjectsRequest(
    parent=collection_name,
    text_search=vectorsearch_v1beta.TextSearch(
        search_text="Nike",
        data_field_names=["title"],
        top_k=10,
        output_fields=vectorsearch_v1beta.OutputFields(data_fields=["*"]),
    ),
)
```

### Hybrid Search (semantic + text with RRF)

```python
request = vectorsearch_v1beta.BatchSearchDataObjectsRequest(
    parent=collection_name,
    searches=[
        vectorsearch_v1beta.Search(
            semantic_search=vectorsearch_v1beta.SemanticSearch(
                search_text=query, search_field="title_embedding",
                task_type="QUESTION_ANSWERING", top_k=20,
                output_fields=vectorsearch_v1beta.OutputFields(data_fields=["*"]),
            )
        ),
        vectorsearch_v1beta.Search(
            text_search=vectorsearch_v1beta.TextSearch(
                search_text=query, data_field_names=["title"], top_k=20,
                output_fields=vectorsearch_v1beta.OutputFields(data_fields=["*"]),
            )
        ),
    ],
    combine=vectorsearch_v1beta.BatchSearchDataObjectsRequest.CombineResultsOptions(
        ranker=vectorsearch_v1beta.Ranker(
            rrf=vectorsearch_v1beta.ReciprocalRankFusion(weights=[1.0, 1.0])
        )
    ),
)
results = search_client.batch_search_data_objects(request)
# Combined results in: results.results[0].results
```

### Query with Filters (SQL-like)

```python
# Operators: $eq, $ne, $gt, $gte, $lt, $lte, $and, $or, $in, $nin
request = vectorsearch_v1beta.QueryDataObjectsRequest(
    parent=collection_name,
    filter={"$and": [{"category": {"$eq": "Electronics"}}, {"price": {"$lt": 100}}]},
    output_fields=vectorsearch_v1beta.OutputFields(data_fields=["*"]),
)
results = search_client.query_data_objects(request)
```

## ANN Indexes (Production)

```python
# Create index (takes 30+ minutes)
request = vectorsearch_v1beta.CreateIndexRequest(
    parent=f"projects/{PROJECT_ID}/locations/{LOCATION}/collections/{collection_id}",
    index_id="title-index",
    index={
        "index_field": "title_embedding",
        "filter_fields": ["category", "price"],
        "store_fields": ["title"],
    },
)
lro = vector_search_client.create_index(request)
lro.result()  # Wait for completion

# Searches automatically use index when field matches
```

## Common Mistakes

### Field Naming Constraints

Data field names must follow strict rules:
- Only alphanumeric characters, underscores, and hyphens allowed
- The `$schema` field is **NOT allowed** (causes validation errors)

```python
# WRONG - invalid characters
"data_schema": {
    "$schema": "...",           # $schema not allowed
    "properties": {
        "item.name": {...},     # dots not allowed
        "user@email": {...},    # @ not allowed
    }
}

# CORRECT - valid field names
"data_schema": {
    "properties": {
        "item_name": {...},
        "user_email": {...},
    }
}
```

### Schema Errors

```python
# WRONG - bare object type causes 400 error
"metadata": {"type": "object"}

# CORRECT - define nested properties
"metadata": {
    "type": "object",
    "properties": {
        "author": {"type": "string"},
        "tags": {"type": "array", "items": {"type": "string"}}
    }
}
```

### DataObject ID (RFC1035)

```python
import re
def to_rfc1035_id(s: str) -> str:
    """IDs must: start with lowercase letter, only [a-z0-9-], max 63 chars."""
    s = s.lower().replace(' ', '-').replace('_', '-')
    s = re.sub(r'[^a-z0-9\-]', '', s)
    s = re.sub(r'^[^a-z]+', '', s)
    return s.rstrip('-')[:63] or 'item'
```

**ID Preservation Pattern**: Store the original ID in a data field for lookups:

```python
# Store original ID in data, RFC1035 version as object ID
data_object = {
    "data": {
        "original_id": "My Item #123",  # Preserved for display/lookup
        "title": "...",
    },
    "vectors": {},
}
# Object ID: "my-item-123" (RFC1035)
# data["original_id"]: "My Item #123" (original)

# Lookup by original ID:
def get_by_original_id(original_id: str) -> dict:
    safe_id = to_rfc1035_id(original_id)
    request = vectorsearch_v1beta.GetDataObjectRequest(
        name=f"{collection}/dataObjects/{safe_id}"
    )
    return extract_data(data_object_client.get_data_object(request))
```

### Query Without output_fields Returns Empty

```python
# WRONG - data will be empty
request = vectorsearch_v1beta.QueryDataObjectsRequest(parent=collection)

# CORRECT - always specify output_fields
request = vectorsearch_v1beta.QueryDataObjectsRequest(
    parent=collection,
    output_fields=vectorsearch_v1beta.OutputFields(data_fields=["*"]),
)
```

### No ListDataObjectsRequest

```python
# WRONG - this doesn't exist
request = vectorsearch_v1beta.ListDataObjectsRequest(...)

# CORRECT - use QueryDataObjectsRequest with pagination
request = vectorsearch_v1beta.QueryDataObjectsRequest(
    parent=collection_name,
    page_size=100,
    page_token=page_token if page_token else "",
    output_fields=vectorsearch_v1beta.OutputFields(data_fields=["*"]),
)
```

### Nested Fields in output_fields Fail

```python
# WRONG - nested objects cause 400 error
output_fields=vectorsearch_v1beta.OutputFields(data_fields=["nested_object"])

# WORKAROUND - use GetDataObject for full nested data
data_object = data_object_client.get_data_object(name=f"{collection}/dataObjects/{id}")
```

### MapComposite Conversion

```python
def convert_mapcomposite(obj):
    """Recursively convert protobuf MapComposite to plain dict."""
    if obj is None:
        return None
    type_name = type(obj).__name__
    if type_name == "MapComposite" or hasattr(obj, "items"):
        try:
            return {k: convert_mapcomposite(v) for k, v in obj.items()}
        except (TypeError, AttributeError):
            pass
    if type_name == "RepeatedComposite" or (
        hasattr(obj, "__iter__") and not isinstance(obj, (str, bytes, dict))
    ):
        try:
            return [convert_mapcomposite(item) for item in obj]
        except TypeError:
            pass
    return obj

# Usage
data = convert_mapcomposite(data_object.data)
```

## Embedding Models

| Model | Dimensions | Max Tokens/Request | Notes |
|-------|-----------|-------------------|-------|
| gemini-embedding-001 | 768 (default), up to 3072 | 20,000 | Best quality |
| text-embedding-004 | 768 | 20,000 | Alternative |

**Task Types**: `RETRIEVAL_DOCUMENT` for indexing, `QUESTION_ANSWERING` or `RETRIEVAL_QUERY` for search.

## Cleanup (Avoid Costs)

```python
# 1. Delete indexes first
request = vectorsearch_v1beta.DeleteIndexRequest(name=f"{collection}/indexes/{index_id}")
lro = vector_search_client.delete_index(request)
lro.result()

# 2. Then delete collection (deletes all DataObjects too)
request = vectorsearch_v1beta.DeleteCollectionRequest(name=collection_name)
vector_search_client.delete_collection(request)
```

## Documentation

- [Overview](https://cloud.google.com/vertex-ai/docs/vector-search-2/overview)
- [Collections](https://cloud.google.com/vertex-ai/docs/vector-search-2/collections/collections)
- [Data Objects](https://cloud.google.com/vertex-ai/docs/vector-search-2/data-objects/data-objects)
- [Search Guide](https://cloud.google.com/vertex-ai/docs/vector-search-2/query-search/search)
- [Python SDK](https://cloud.google.com/python/docs/reference/vectorsearch/latest)
