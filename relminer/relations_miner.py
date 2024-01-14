from typing import List, Dict
import logging
from langchain.chat_models import ChatOpenAI

import langchain.chat_models as lcmodels
from langchain.output_parsers import PydanticOutputParser
from langchain.pydantic_v1 import BaseModel, Field
from langchain.schema import HumanMessage
from langchain.prompts import PromptTemplate

from relminer.relation_store import FastRelationStore
from relminer.domain import Relation
from relminer.relations_miner_utils import (
    make_prompt,
    process_result_triplets,
    build_few_shot_prompt,
    get_template
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from ratelimiter import RateLimiter
import json

logger = logging.getLogger(__name__)

EXPLAIN_RELATION_TEMPLATE = "explain_relation.txt"
EXTRACT_RELATIONS = "extract_relations.txt"
MODEL_NAME = "gpt-3.5-turbo-1106"

class RelationTriplets(BaseModel):
    relations: List[List[str]] = Field(
        description="List of triples that represent the extracted relations"
    )
    explanation: str = Field(
        description="The explanation of the extracted relations from the text"
    )


class RelationInfo(BaseModel):
    sentence: str = Field(
        description="The generated sentence for the given relationship"
    )
    explanation: str = Field(
        description="The generated explanation for the given relationship"
    )

class RelationsMiner:
    def __init__(self, relation_store: FastRelationStore):
        self.relation_store: FastRelationStore = relation_store
        self.llm: ChatOpenAI = ChatOpenAI(model_name=MODEL_NAME)
        self.chat_llm: lcmodels.ChatOpenAI = lcmodels.ChatOpenAI(
            model_name=MODEL_NAME,
            model_kwargs={"response_format": {"type": "json_object"}},
        )
        self.text_splitter: RecursiveCharacterTextSplitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=0,
            length_function=len,
            is_separator_regex=False,
        )
        self.rel_triplets_parser: PydanticOutputParser = PydanticOutputParser(pydantic_object=RelationTriplets)
        self.rel_info_parser: PydanticOutputParser = PydanticOutputParser(pydantic_object=RelationInfo)

    @RateLimiter(max_calls=100, period=60)
    def extract_relations_simple(self, subject: str, input_text: str) -> List[Relation]:
        template = get_template(EXTRACT_RELATIONS)

        prompt_template = PromptTemplate(
            template=template, 
            input_variables=["relation_types", "subject", "input_text"]
        )

        relations = self.relation_store.load_relations()

        # getting the list of unique relations
        relation_types = set([relation.name for relation in relations])

        chunked_text = self.text_splitter.create_documents([input_text])

        results, num_chunks = [], len(chunked_text)
        for i, chunked_input_text in enumerate(chunked_text):
            context = {
                "relation_types": relation_types,
                "subject": subject,
                "input_text": chunked_input_text.page_content
            }

            prompt = prompt_template.format(**context)

            chat_messages = [HumanMessage(content=prompt)]
            logger.debug(f"Chat message prompt \n\n{chat_messages}")

            chat_generations = self.chat_llm.invoke(chat_messages)

            logger.debug(f"Generations \n\n[[{chat_generations.content}]]")

            extracted_triples = json.loads(chat_generations.content)
            results.extend(process_result_triplets(extracted_triples))

            if i % 10 == 0:
                logger.info(
                    f"Processed {i}/{num_chunks} chunk. Current detected {len(results)} relations"
                )

        logger.info(f"Processed all chunks. Detected {len(results)} relations")

        return results


    @RateLimiter(max_calls=100, period=60)
    def register_relation(self, relation: Relation):
        template = get_template(EXPLAIN_RELATION_TEMPLATE)

        format_instructions = self.rel_info_parser.get_format_instructions()
        prompt_template = PromptTemplate(
            template=template, 
            input_variables=["subject", "name", "object", "description"], 
            partial_variables={"format_instructions": format_instructions}
        )

        context = relation.to_dict(exclude=["explanation", "sentence"])
        prompt = prompt_template.format(**context)

        chat_messages = [HumanMessage(content=prompt)]
        chat_generations = self.chat_llm.invoke(chat_messages)

        relation_info = self.rel_info_parser.parse(chat_generations.content)

        relation.sentence = relation_info.sentence
        relation.explanation = relation_info.explanation

        logger.info(f"Adding relation \n{relation}")
        self.relation_store.add_relations([relation])

    def register_relations(self, relations: List[Relation]):
        for relation in relations:
            self.register_relation(relation)

    @RateLimiter(max_calls=100, period=60)
    def extract_relations(self, subject: str, input_text: str) -> List[Relation]:
        # loading the existing relations to use them for few shot learning
        relations = self.relation_store.load_relations()

        # getting the list of unique relations
        relation_names = set([relation.name for relation in relations])

        # building the few shot prompt with the existing relations as examples
        few_shot_prompt = build_few_shot_prompt(relations, self.rel_triplets_parser)

        # chunking the description into smaller pieces yields more extracted relations
        chunked_text = self.text_splitter.create_documents([input_text])

        results, num_chunks = [], len(chunked_text)
        for i, chunked_description in enumerate(chunked_text):
            chat_messages = make_prompt(
                few_shot_prompt, relation_names, subject, chunked_description.page_content
            )
            logger.debug(f"Chat message prompt \n\n{chat_messages}")

            chat_generations = self.chat_llm.invoke(chat_messages)
            logger.info(f"Generations [[\n\n{chat_generations}]]")

            # parsing the relations represented as list of list
            out_relations = self.rel_triplets_parser.parse(chat_generations.content)

            results.extend(process_result_triplets(out_relations))

            if i % 10 == 0:
                logger.info(
                    f"Processed {i}/{num_chunks} chunk. Current detected {len(results)} relations"
                )

        logger.info(f"Processed all chunks. Detected {len(results)} relations")

        return results

    def extract_common_relations(
        self, subject_a: str, description_a: str, subject_b: str, description_b: str
    ) -> Dict:
        relations_a = self.extract_relations(subject_a, description_a)
        relations_b = self.extract_relations(subject_b, description_b)

        shared_relations = Relation.detect_shared_relations(relations_a, relations_b)

        return {
            "relations_left": relations_a,
            "relations_right": relations_b,
            "shared_relations": shared_relations,
        }
