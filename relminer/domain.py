from typing import List, TypeVar, Type
import json

T = TypeVar("T", bound="Relation")

class Relation:
    def __init__(
        self,
        subject: str,
        name: str,
        object: str,
        description: str = "",
        sentence: str = "",
        explanation: str = "",
    ):
        self.name = name
        self.description = description
        self.subject = subject
        self.object = object
        self.sentence = sentence
        self.explanation = explanation

    def to_dict(self, exclude=[]) -> dict:
        d = {
            "subject": self.subject,
            "name": self.name,
            "object": self.object,
            "description": self.description,
            "sentence": self.sentence,
            "explanation": self.explanation,
        }
        for k in exclude:
            del d[k]
        return d

    @classmethod
    def detect_shared_relations(cls: Type[T], rels_1: List[T], rels_2: List[T]) -> List[T]:
        set_1 = set([rel.name for rel in rels_1])
        set_2 = set([rel.name for rel in rels_2])
        shared_rel_name = set_1 & set_2
        results = [rel for rel in rels_1 if rel.name in shared_rel_name]
        results.extend([rel for rel in rels_2 if rel.name in shared_rel_name])
        return results

    @classmethod
    def from_list(cls: Type[T], rel: List[str]) -> T:
        if len(rel) != 3:
            return None
        return Relation(rel[0], rel[1].lower(), rel[2])

    def __str__(self) -> str:
        return json.dumps(self.to_dict(exclude=['description', 'sentence', 'explanation']))

    def __repr__(self) -> str:
        return self.__str__()
