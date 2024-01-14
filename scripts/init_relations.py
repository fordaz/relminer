from relminer.relation_store import FastRelationStore
from relminer.domain import Relation
import logging

ootb_relatiotion_dicts = [
    {"name": "Student_Of", "description": "a person who was or is a student of another person who is the teacher of a particular discipline", "subject": "Joshua", "object": "Geff Hinton", "sentence": "Joshua is a Student_Of Geff Hinton.", "explanation": "Joshua was or is a student of Geff Hinton who is the teacher of a particular discipline."},
    {"name": "Published", "description": "a person that published an article", "subject": "Jenny Ryan", "object": "Attention is all your need white paper", "sentence": "Jenny Ryan published the Attention is all you need white paper.", "explanation": "Jenny Ryan is the author of the Attention is all you need white paper thus the relation 'Published' holds because she is the one who published it."},
    {"name": "Moved_To", "description": "a person that used to live at one place but moved to a new place", "subject": "Jerry McGuire", "object": "Miami", "sentence": "Jerry McGuire moved to Miami", "explanation": "The sentence holds the relation 'Moved_To' which means that Jerry McGuire previously lived at one place but has now moved to a new place in this case Miami FL."},
    {"name": "Lived_At", "description": "a person that lived or is living at a given place or location", "subject": "Jim Ozark", "object": "Mountain View", "sentence": "Jim Ozark has lived at Mountain View", "explanation": "Jim Ozark has been living at Mountain View CA for an extended period of time"},
    {"name": "Friend_Of", "description": "a person who is a friend and well acquianted with another", "subject": "Cassie Kane", "object": "Rick Jones", "sentence": "Cassie Kane and Rick Jones are friends of each other", "explanation": "They have been part of each other's lives for some time and have become well acquainted through mutual activities such as work"},
    {"name": "Studied_At", "description": "a person who studied at a given elementary", "subject": "Mary Lane", "object": "Stanford University", "sentence": "Mary Lane studied at Stanford University.", "explanation": "The relation holds because Mary Lane is a person and Stanford University is an educational institution that she studied at."},
    {"name": "Born_At", "description": "a person born at a place or location", "subject": "Joe Clark", "object": "Ontario", "sentence": "Joe Clark was born in Ontario", "explanation": "Joe Clark is the subject and Ontario"},
    {"name": "Father_Of", "description": "a person who is the father of another person", "subject": "Rick", "object": "Jimmy", "sentence": "Rick is the Father_Of Jimmy.", "explanation": "Rick is the father of Jimmy because they have a biological relationship"},
    {"name": "Born_In", "description": "a person being born in a given date", "subject": "Joe Jackson", "object": "October 10", "sentence": "Joe Jackson was born in October 10", "explanation": "Joe Jackson is the subject of the sentence and October 10"},
    {"name": "Traveled_To", "description": "Traveled_To describes the feact that a person traveled to a given location", "subject": "Joe", "object": "France", "sentence": "Joe traveled to France", "explanation": "The relation holds because Joe visited the country of France for a vacation."}
]

ootb_relations = []
for rel_dict in ootb_relatiotion_dicts:
    rel = Relation(**rel_dict)
    ootb_relations.append(rel)

relation_store = FastRelationStore()
relation_store.add_relations(ootb_relations, append=False)
