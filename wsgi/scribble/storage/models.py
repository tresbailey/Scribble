__author__ = 'tresback'

from mongoalchemy.document import Index
from pymongo.objectid import ObjectId
from scribble import db


class ScribData(db.Document):
    def filter_out_fields(self, remove_keys):
        return dict([(key_, getattr(self, key_)) for key_ in self.get_fields().iterkeys() if key_ not in remove_keys and hasattr(self, key_)])

class Scruser(ScribData):
    user_id = db.StringField()
    first_name = db.StringField()
    last_name = db.StringField()
    email = db.StringField()
    id_index = Index().ascending('user_id')

class Scribble(ScribData):
    user_id = db.StringField()
    canvas_data = db.ListField(db.TupleField(db.TupleField(
                    db.IntField(), db.IntField()), 
                    db.IntField(), db.IntField(), 
                    db.IntField(), db.IntField()), 
                    allow_none=True)
    marks_points = db.ListField(db.TupleField(db.TupleField(db.IntField(), db.IntField()), db.StringField()))
    tags = db.ListField(db.StringField(), allow_none=True)
    base_html = db.StringField()
    base_url = db.StringField()
    image_data = db.StringField()
    original_width = db.IntField()
    user_index = Index().ascending('user_id')
    tags_index = Index().ascending('tags')
