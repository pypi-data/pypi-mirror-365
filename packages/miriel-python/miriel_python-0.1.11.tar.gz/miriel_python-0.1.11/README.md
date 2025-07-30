# Miriel Python Client

This is the official Python client library for interacting with the Miriel API.

## Installation

You can install the Miriel Python client using pip:

```bash
pip install miriel-python
```
And update with:

```bash
pip install --upgrade miriel-python
```

Or you can run:

```bash
pip install .
```
in the directory into which you cloned this repo.

## Basic Usage

To use the Miriel Python client, you need an API key. You can get your API key by signing up for an account on the [Miriel website](https://miriel.ai).

Once you have your API key, initialize the client and begin interacting with the API. Here’s a basic example:

```python
from miriel import Miriel

# Initialize the client with your API key
miriel_client = Miriel(api_key="your_api_key")

# Add data (string example)
miriel_client.learn(
    "The Founders of Miriel are David Garcia, Josh Paulson, and Andrew Barkett",
    wait_for_complete=True
)

# Query the documents
query_response = miriel_client.query("Who are the founders of Miriel?")
print(f"Query response: {query_response}")
```

Miriel accepts many types of data: strings, file paths, directories, URLs, S3 buckets, RTSP feeds, and more.

Before you can query data, it must first be fully ingested with `learn()`. This can take less than a second or be a few minutes depending on the data. You can run `learn()` and `query()` as separate steps (recommended), or use `wait_for_complete=True` to ensure all learn jobs finish before proceeding in a script.

Each query returns documents ranked by relevance. You can control the maximum number of results that are returned using the `num_results` parameter (default is 10). Note: This includes any pinned documents (see priority below).

```python
    ...
    
    # Query with more results
    query_response = miriel_client.query(
        "Who are the founders of Miriel?",
        num_results=20
    )
    print(f"Query response: {query_response}")
```

## Adding an Image to the Query

```python
    ...
    
    # Query with an image
    query_response = miriel_client.query(
        "What does this image show?",
        input_images="https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"
    )
    print(f"Query response: {query_response}")
```

## Setting a Structured Output for the LLM Response

```python
    ...

    # Define a schema for the structured output
    output_schema = {
        "founders" : ["string"],
        "number_of_founders": "integer"
    }

    query_response = miriel_client.query(
        "Who are the founders of Miriel?",
        response_format=output_schema
    )
    print(f"Query response: {query_response}")
```
Only "integer", "float", "string", "boolean", "array" (list), and "object" (dict) are supported.  Default values not yet supported.

## Setting Metadata

You can attach metadata to any document using the `learn()` function. Metadata is stored as key-value pairs and must be passed as a Python dictionary.

Metadata can be used to tag documents by category, source, access level, version, or any other custom label. Miriel also assigns certain metadata fields automatically—such as `priority`, `project`, image data, document permissions, and other information—unless they are explicitly overwritten. You can view metadata fields in the Miriel dashboard.

These fields can be used for filtering results or managing documents during queries.

Examples adding metadata:

```python
    ...
    
    # Adding a custom metadata field to a string
    miriel_client.learn(
        "The document ID is 12345",
        metadata={"internal_docs": True}
    )

    # Adding multiple metadata fields
    miriel_client.learn(
        "The celebration is on the forest moon",
        metadata={"department": "engineering", "team": "83"}
    )
```
You can assign any field name and value, as long as the key is a string and the value is a valid JSON-compatible type (e.g., string, number, boolean).

## Filtering Query Results by Metadata

You can filter query results using metadata fields by passing a string to the `metadata_query` parameter. This lets you narrow results based on metadata values set during the `learn()` step.

The format uses simple `field=value` syntax, with support for `AND`, `OR`, and parentheses for more advanced filtering.

Examples:

```python
    ...
    
    # Query only internal documents
    query_response = miriel_client.query(
        "What is the document ID?",
        metadata_query="internal_docs=True"
    )
    print(f"Query response: {query_response}")

    # Limit your query to the engineering department and team 83
    query_response = miriel_client.query(
        "Where is the party?",
        metadata_query="department=engineering AND team=83"
    )
    print(f"Query response: {query_response}")
```
Metadata queries are case-sensitive and must use spaces around `AND` and `OR`.

## Document Priority and Pinning

Miriel uses a priority field, attached as metadata to a document, to influence how documents are ranked during retrieval. By default, every document is assigned `priority=100` and this allows Miriel to determine each document's relative importance when ranking the results from a query. Overriding priority to set a higher value will slightly increase a document’s ranking, while lower values will slightly decrease it. You can also filter the query results by using priority as a metadata field.

Miriel supports two special priority values:

Setting `-1` or `"norank"` forces the document to not be ranked or returned in ranked results unless no other higher-ranked content exists. The document is still indexed and retrievable via metadata filters. This is useful for testing and suppressing content from search that you may still want to access programmatically.

Setting `-2` or `"pin"` forces the document to always rank above non-pinned documents. Within the pinned group, documents are still ranked by relevance. Pinned content is useful when you know a document should appear in response to nearly all queries.

**Important**: The `num_results` limit applies across all documents, including pinned ones. For example, if `num_results=10` and 11 documents have `priority="pin"`, only the 10 highest-ranking pinned documents will be returned. No unpinned content will appear unless the total pinned is less than `num_results`.

Examples:

```python
    ...
    
    # Add data that should not show up in ranked results
    miriel_client.learn(
        "archived version of this doc",
        priority="norank"
    )

    # Add data that should always be ranked highest
    miriel_client.learn(
        "important reminder relevant for all queries",
        priority="pin"
    )
```

## Projects

## Documentation
For more details on the API, see the [API Documentation](API.md).
