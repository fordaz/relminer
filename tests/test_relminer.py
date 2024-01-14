import unittest
from unittest.mock import patch
import langchain
import json
from collections import namedtuple

from relminer.relations_miner import RelationsMiner
from relminer.relation_store import FastRelationStore
from relminer.relations_miner import RelationsMiner
from relminer.domain import Relation

relation_store = FastRelationStore()

Generations = namedtuple("Generations", ["content"])

class TestRelMiner(unittest.TestCase):
    def setUp(self) -> None:
        self.rel_miner = RelationsMiner(relation_store=relation_store)
        return super().setUp()

    def mock_extract_triplets(arg1, arg2):
        generations = json.dumps(
            {
                "relations": [
                    ["Joe", "Lives_At", "Boston"],
                    ["Joe", "Born_In", "Miami"],
                ],
                "explanation": "Joe lives in Boston and was born in Miami",
            }
        )
        return Generations(generations)

    @patch.object(langchain.chat_models.ChatOpenAI, "invoke", mock_extract_triplets)
    def test_extract_relations(self):
        extracted_relations = self.rel_miner.extract_relations(
            "Joe", "Joe lives in Boston and was born in Miami"
        )
        print(extracted_relations)

    def mock_explain_relation(arg1, arg2):
        generations = json.dumps(
            {
                "sentence": "This is an example sentence of the relation",
                "explanation": "This explains why the relation holds in this sentence",
            }
        )
        return Generations(generations)

    @patch.object(langchain.chat_models.ChatOpenAI, "invoke", mock_explain_relation)
    def test_explain_relation(self):
        rel = Relation("TheSubject", "TheRelName", "TheObject", "TheDescription")
        extracted_relations = self.rel_miner.register_relation(rel)
        print(extracted_relations)
