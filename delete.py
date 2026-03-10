import chromadb

# Create or open a local persistent Chroma database on disk
client = chromadb.PersistentClient(path="./chroma_db")

# Create a collection
collection = client.get_or_create_collection(name="my_collection")

# Add some documents
collection.add(
    ids=["1", "2"],
    documents=[
        "Tim Cook is the CEO of Apple.",
        "London is the capital of the UK."
    ],
    metadatas=[
        {"source": "example1", "relation":"computers"},
        {"source": "example2","relation":"countries"}
    ]
)

# Query the collection
results = collection.query(
    query_texts=["Who is CEO of Apple?"],
    n_results=0
)

print(results)