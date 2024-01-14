from relminer.relation_store import FastRelationStore
from relminer.relations_miner import RelationsMiner
from relminer.domain import Relation

import argparse
import logging

description = """
Allows to register a new relation type, which can be used later as a few-shot example to extract relations from a given text.
In this way you can add your custom relation types to ground the relation extraction for the LLM.

* It Takes the subject, relation type, object, and description of a new relation type.
* It uses OpenAI to generate a example sentence for this relation, and its explanation.

Example:

Given the subject:"Joe", relation type:"Traveled_To", object:"France" and a description:"Traveled_To describes the feact that a person traveled to a given location"
It uses gpt-3.5-turbo-1106 to generate this example sentece with its explanation:

sentence: "Joe traveled to France"
explanation:"The relation 'Traveled_To' holds because Joe physically journeyed to the location of France"

"""

parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("sub", help="The subject for which the relations will be extracted")
parser.add_argument("file", help="The file name containing the text from which the relations will be extracted from")
parser.add_argument( '-l', '--loglevel', default='info', help='Example --loglevel debug, default=info' )

args = parser.parse_args()

logging.basicConfig(level=args.loglevel.upper())
logger = logging.getLogger(__name__)

with open(args.file) as f:
    input_text = f.read()

relation_store = FastRelationStore()

rel_miner = RelationsMiner(relation_store=relation_store)

extracted_relations = rel_miner.extract_relations_simple(args.sub, input_text)

logger.info(f"The following relations were extracted \n{extracted_relations}")