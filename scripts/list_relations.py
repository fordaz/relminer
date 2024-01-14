from relminer.relation_store import FastRelationStore

import logging

relation_store = FastRelationStore()
relations = relation_store.load_relations()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

for relation in relations:
    logger.info(f"\n{relation}")
