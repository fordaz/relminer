# Overview

The goal of this project is to use LLMs to extract relations from a given input text. The relations are extracted as triplets of the form (subject, relation, object), for example: ("Steve Jobs", "Founder_Of", "Apple").

Beyond this simple goal, the project is an excuse the play with LLMs, the OpenAI api, LangChain.

# Pre-requisites

1) Please use the Python environment manager of your choice (conda or venv) and create an environemnt for this project using python 3.8.
2) Configure your OpenAI OPENAI_API_KEY environment variable.

# Setup

This script sets up the PYTHONPATH and pip installs the needed dependencies

```
./setup.sh
```

# Extracting relations

In order to run the relation extraction on a given piece of text. Use a command like this:

```
python scripts/extract_relations.py "Steve Jobs" data.txt
```

# Listing predefined relations

There are some predefined relations to be used as few-shot examples for the LLM. These relations are stored in `data/relations/ootb_relations.avro`. This scripts list the content of that file:

```
python scripts/list_relations.py
```

# (Re)Initialize predefined relations

This allows to reconstruct the predefined relations stored in `data/relations/ootb_relations.avro`. 

```
python scripts/init_relations.py
```

# Unit test

There are two unit tests which mock the response from OpenAI, which help to do refactoring and make sure everything works fine.

```
python -m unittest tests/test_relminer.py
```