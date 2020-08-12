from flask_sqlalchemy import SQLAlchemy
from functools import wraps
import json
import os
from sqlalchemy import Column, String, Integer, create_engine


database_name = "trivia"
database_path = "postgres://{}/{}".format('localhost:5432', database_name)

db = SQLAlchemy()

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''
def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()

'''
  @transaction

'''
def transaction(f):
  @wraps(f)
  def w(*args, **kwargs):
    success = None

    try:
      f(*args, **kwargs)
      db.session.commit()
      success = True
    except:
      db.session.rollback()
      success = False
    finally:
      db.session.close()

    return success
  return w


'''
ModelAdditions

'''
class ModelAdditions:
  @transaction
  def insert(self):
    db.session.add(self)

  @transaction
  def update(self):
    pass

  @transaction
  def delete(self):
    db.session.delete(self)

  def fill(self, _except=[], **kwargs):
    for key in kwargs:
      if key not in _except and hasattr(self, key):
        setattr(self, key, kwargs[key])

'''
Question

'''
class Question(ModelAdditions, db.Model):  
  __tablename__ = 'questions'

  id = Column(Integer, primary_key=True)
  question = Column(String)
  answer = Column(String)
  category = Column(String)
  difficulty = Column(Integer)

  def __init__(self, question, answer, category, difficulty):
    self.question = question
    self.answer = answer
    self.category = category
    self.difficulty = difficulty

  def format(self):
    return {
      'id': self.id,
      'question': self.question,
      'answer': self.answer,
      'category': self.category,
      'difficulty': self.difficulty
    }

'''
Category

'''
class Category(ModelAdditions, db.Model):  
  __tablename__ = 'categories'

  id = Column(Integer, primary_key=True)
  type = Column(String)

  def __init__(self, type):
    self.type = type

  def format(self):
    return {
      'id': self.id,
      'type': self.type
    }