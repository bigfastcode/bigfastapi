import sqlalchemy as sa
from sqlalchemy.orm import mapper, class_mapper, relation
from bigfastapi.database import Base, db_engine
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy.inspection import inspect

DEFAULT_PRIMARY_KEY_INDEX = 0

class BaseComment(object):
    def __init__(self, *, rel_id, text, name, email) -> None:
        self.rel_id = rel_id
        self.text = text
        self.name = name
        self.email = email
        super().__init__()
    
    @hybrid_method
    def upvote(self):
        self.upvotes += 1
    
    @hybrid_method
    def downvote(self):
        self.downvotes += 1

def build_comment_model(clazz):
    class_table_name = str(class_mapper(clazz).local_table)
    metadata = clazz.metadata
    try: 
        # Declare a custom Primary Key Index corresponding to the Column Number of the Primary Key Column
        primary_key_index = int(getattr(clazz, "_primary_key_index"))
    except AttributeError:
        # No custom index defined, use default
        primary_key_index = DEFAULT_PRIMARY_KEY_INDEX
    
    comment_class_name = clazz.__name__ + 'Comment'
    comment_class = type(comment_class_name, (BaseComment,), {})
    comment_table_name = class_table_name + '_comments'
    
    primary_key = inspect(clazz).primary_key[primary_key_index].name
    
    comment_table = sa.Table(comment_table_name, metadata,
                                sa.Column('id', sa.Integer, primary_key=True),
                                sa.Column('rel_id', sa.Integer, sa.ForeignKey(class_table_name + f'.{primary_key}')),
                                sa.Column('text', sa.String),
                                sa.Column('name', sa.String(100)),
                                sa.Column('email', sa.String(100)),
                                sa.Column('downvotes', sa.Integer, default=0),
                                sa.Column('upvotes', sa.Integer, default=0),) 
    comment_table.create(db_engine, checkfirst=True)
    mapper(comment_class, comment_table)
    
    return comment_class, comment_table

def commentable(clazz):
    comment_class, comment_table = build_comment_model(clazz)
    clazz.Comment = comment_class
    setattr(clazz, 'comments', relation(comment_class))

    def add_comment(self, comment):
        self.comments.append(comment)
    
    setattr(clazz, 'add_comment', add_comment)
    
    return clazz
