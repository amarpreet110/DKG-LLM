from neo4j import GraphDatabase
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction


# -----------------------------
# Config
# -----------------------------
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "Whyh3ll0th3r31"

CHROMA_PATH = "./chroma_db"

EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"


# -----------------------------
# Neo4j -> Chroma converter
# -----------------------------
class Neo4jToChroma:
    def __init__(self, neo4j_uri, neo4j_user, neo4j_password, chroma_path):
        self.driver = GraphDatabase.driver(
            neo4j_uri,
            auth=(neo4j_user, neo4j_password)
        )

        self.embedding_fn = SentenceTransformerEmbeddingFunction(
            model_name=EMBEDDING_MODEL
        )

        self.client = chromadb.PersistentClient(path=chroma_path)

        self.entity_collection = self.client.get_or_create_collection(
            name="kg_entities",
            embedding_function=self.embedding_fn
        )

        self.triple_collection = self.client.get_or_create_collection(
            name="kg_triples",
            embedding_function=self.embedding_fn
        )

    def close(self):
        self.driver.close()

    # -------------------------
    # Export nodes
    # -------------------------
    def fetch_nodes(self):
        query = """
        MATCH (n)
        RETURN elementId(n) AS node_id,
               labels(n) AS labels,
               properties(n) AS props
        """
        with self.driver.session() as session:
            return [record.data() for record in session.run(query)]

    # -------------------------
    # Export relationships
    # -------------------------
    def fetch_relationships(self):
        query = """
        MATCH (a)-[r]->(b)
        RETURN elementId(r) AS rel_id,
               type(r) AS rel_type,
               properties(r) AS rel_props,
               elementId(a) AS source_id,
               elementId(b) AS target_id,
               labels(a) AS source_labels,
               labels(b) AS target_labels,
               properties(a) AS source_props,
               properties(b) AS target_props
        """
        with self.driver.session() as session:
            return [record.data() for record in session.run(query)]

    # -------------------------
    # Convert node -> text
    # -------------------------
    def node_to_document(self, node):
        labels = ", ".join(node["labels"]) if node["labels"] else "Entity"
        props = node["props"] or {}

        name = (
            props.get("name")
            or props.get("title")
            or props.get("id")
            or node["node_id"]
        )

        prop_text = ", ".join(f"{k}: {v}" for k, v in props.items())
        document = f"{labels} {name}. {prop_text}".strip()

        metadata = {
            "type": "entity",
            "neo4j_id": node["node_id"],
            "labels": "|".join(node["labels"]) if node["labels"] else "",
            "name": str(name),
        }

        for k, v in props.items():
            metadata[f"prop_{k}"] = str(v)

        return {
            "id": f"node_{node['node_id']}",
            "document": document,
            "metadata": metadata
        }

    # -------------------------
    # Convert relationship -> text
    # -------------------------
    def relationship_to_document(self, rel):
        source_props = rel["source_props"] or {}
        target_props = rel["target_props"] or {}

        subject = (
            source_props.get("name")
            or source_props.get("title")
            or source_props.get("id")
            or rel["source_id"]
        )
        obj = (
            target_props.get("name")
            or target_props.get("title")
            or target_props.get("id")
            or rel["target_id"]
        )

        predicate = rel["rel_type"]

        rel_props = rel["rel_props"] or {}
        rel_prop_text = ", ".join(f"{k}: {v}" for k, v in rel_props.items())

        document = f"{subject} {predicate} {obj}"
        if rel_prop_text:
            document += f". {rel_prop_text}"

        metadata = {
            "type": "triple",
            "neo4j_rel_id": rel["rel_id"],
            "subject": str(subject),
            "predicate": str(predicate),
            "object": str(obj),
            "source_id": rel["source_id"],
            "target_id": rel["target_id"],
            "source_labels": "|".join(rel["source_labels"]) if rel["source_labels"] else "",
            "target_labels": "|".join(rel["target_labels"]) if rel["target_labels"] else "",
        }

        for k, v in rel_props.items():
            metadata[f"relprop_{k}"] = str(v)

        return {
            "id": f"rel_{rel['rel_id']}",
            "document": document,
            "metadata": metadata
        }

    # -------------------------
    # Store nodes in Chroma
    # -------------------------
    def export_nodes_to_chroma(self):
        nodes = self.fetch_nodes()
        records = [self.node_to_document(node) for node in nodes]

        if not records:
            print("No nodes found.")
            return

        self.entity_collection.upsert(
            ids=[r["id"] for r in records],
            documents=[r["document"] for r in records],
            metadatas=[r["metadata"] for r in records]
        )

        print(f"Stored {len(records)} nodes in kg_entities")

    # -------------------------
    # Store relationships in Chroma
    # -------------------------
    def export_relationships_to_chroma(self):
        relationships = self.fetch_relationships()
        records = [self.relationship_to_document(rel) for rel in relationships]

        if not records:
            print("No relationships found.")
            return

        self.triple_collection.upsert(
            ids=[r["id"] for r in records],
            documents=[r["document"] for r in records],
            metadatas=[r["metadata"] for r in records]
        )

        print(f"Stored {len(records)} relationships in kg_triples")

    # -------------------------
    # Run full export
    # -------------------------
    def run(self):
        self.export_nodes_to_chroma()
        self.export_relationships_to_chroma()


if __name__ == "__main__":
    exporter = Neo4jToChroma(
        neo4j_uri=NEO4J_URI,
        neo4j_user=NEO4J_USER,
        neo4j_password=NEO4J_PASSWORD,
        chroma_path=CHROMA_PATH
    )

    try:
        exporter.run()
    finally:
        exporter.close()