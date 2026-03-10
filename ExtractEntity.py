import spacy
import chromadb
# requires python 3.13
# pip install spacy
# python -m spacy download en_core_web_sm
# pip instal chromadb

# Load the English NLP model
nlp = spacy.load("en_core_web_sm")

def extract_entities(text):
    entities = []
    for ent in nlp(text).ents:
        entities.append({
            "text": ent.text,
            "label": ent.label_,
            "description": spacy.explain(ent.label_)
        })
    return entities


if __name__ == "__main__":
    text = "Apple CEO Tim Cook announced new products in California on September 12, 2023."

    ents = extract_entities(text)

    for e in ents:
        print(f"{e['text']} ({e['label']}): {e['description']}")