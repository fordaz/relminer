from typing import List, Dict
import logging

from langchain.prompts.few_shot import FewShotPromptTemplate
from langchain.schema import HumanMessage, BaseMessage
from langchain.prompts import PromptTemplate

from relminer.domain import Relation

from typing import List
import os

logger = logging.getLogger(__name__)

TMPLT_BASE_DIR = os.path.dirname(__file__)

FEW_SHOT_EXAMPLE_TEMPLATE = "few_shot_example.txt"
FEW_SHOT_PREFIX_TEMPLATE = "few_shot_prefix_template.txt"
FEW_SHOT_SUFFIX_TEMPLATE = "few_shot_suffix_template.txt"


def make_prompt(few_shot_prompt, relation_names, subject, chunked_description) -> List[BaseMessage]:
    # all the instructions of the full prompt per chunk
    full_prompt = few_shot_prompt.format(
        relation_types=relation_names, subject=subject, input=chunked_description
    )
    return [HumanMessage(content=full_prompt)]


def process_result_triplets(out_relations) -> List[Relation]:
    relations = []
    # A relation is parsed as list with subject, relation, object.
    # Ex: ['Luis Rodriguez', 'Lived_At', 'Techville']
    extracted_triplets = []
    if hasattr(out_relations, "relations"):
        extracted_triplets = out_relations.relations
    if isinstance(out_relations, dict) and "relations" in out_relations:
        extracted_triplets = out_relations["relations"]

    for triplet in extracted_triplets:
        logger.info(f"Extrated Relation {triplet}")
        rel = Relation.from_list(triplet)
        if not rel:
            logger.warning(f"Invalid relation {triplet}")
            continue
        relations.append(rel)
    return relations


def get_few_shot_examples(relations: List[Relation]) -> List[Dict]:
    few_shot_examples = []
    for r in relations:
        explanation = r.explanation.replace("\n", "")
        triplet = [[r.subject, r.name, r.object]]
        shot_example = {
            "example_text": r.sentence,
            "example_relations": str(triplet),
            "example_explanation": explanation,
        }
        few_shot_examples.append(shot_example)
    return few_shot_examples


def build_few_shot_prompt(relations: List[Relation], output_parser) -> FewShotPromptTemplate:
    format_instructions = output_parser.get_format_instructions()

    few_shot_example_prompt = get_prompt_template(FEW_SHOT_EXAMPLE_TEMPLATE)
    few_shot_suffix = get_template(FEW_SHOT_SUFFIX_TEMPLATE)
    few_shot_prefix = get_template(FEW_SHOT_PREFIX_TEMPLATE)

    few_shot_examples = get_few_shot_examples(relations)

    few_shot_prompt = FewShotPromptTemplate(
        prefix=few_shot_prefix,
        examples=few_shot_examples,
        example_prompt=few_shot_example_prompt,
        suffix=few_shot_suffix,
        partial_variables={"output_instructions": format_instructions},
        input_variables=["relation_types", "subject", "input"],
    )

    return few_shot_prompt


def get_prompt_template(name: str) -> PromptTemplate:
    location = os.path.join(TMPLT_BASE_DIR, "../templates", name)
    with open(location, "r") as f:
        promp_template = f.read()
    return PromptTemplate.from_template(promp_template)


def get_template(name: str) -> str:
    location = os.path.join(TMPLT_BASE_DIR, "../templates", name)
    with open(location, "r") as f:
        template = f.read()
    return template
