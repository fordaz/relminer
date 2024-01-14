import fastavro
import os
from typing import List
from relminer.domain import Relation

RELATIONS_BASE_DIR = os.path.dirname(__file__)
RELATION_FILE = os.path.join(RELATIONS_BASE_DIR, "../data/relations/ootb_relations.avro")

relation_schema_def = {
    "name": "relation.miner.domain.Relation",
    "type": "record",
    "fields": [
        {"name": "name", "type": "string"},
        {"name": "description", "type": "string"},
        {"name": "subject", "type": "string"},
        {"name": "object", "type": "string"},
        {"name": "sentence", "type": "string"},
        {"name": "explanation", "type": "string"},
    ],
}

class FastRelationStore:
    def __init__(self):
        self.relation_schema = fastavro.parse_schema(relation_schema_def)
        self.relations = []

    def add_relations(self, relations: List[Relation], append: bool = True):
        records = [relation.to_dict() for relation in relations]
        mode = "a+b" if append else "w+b"
        with open(RELATION_FILE, mode) as f:
            fastavro.writer(f, self.relation_schema, records)

    def load_relations(self) -> List[Relation]:
        if not os.path.exists(RELATION_FILE):
            return []

        with open(RELATION_FILE, "rb") as f:
            reader = fastavro.reader(f)
            self.relations = [Relation(**relation) for relation in reader]

        return self.relations