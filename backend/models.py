from flask_sqlalchemy import SQLAlchemy
from functools import wraps
import json
import os
from sqlalchemy import Column, String, Integer, ForeignKey, create_engine
from sys import stderr


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
    if not Category.query.count():
      types = ['Art', 'Entertainment', 'Geography', 'History', 'Science', 'Sports']
      
      @Transaction
      def seed_categories():
        for type in types: Category(type=type).insert()

      seed_categories()
      

'''
  Transaction

'''
class Transaction:
  def __init__(self, t):
    self.__transaction = t
  

  def __call__(self, *args, **kwargs):
    response = None

    try:
      response = self.__transaction(*args, **kwargs)
      db.session.commit()
    except Exception as e:
      print(e, file=stderr)
      db.session.rollback()
      if hasattr(self, '__fail') and callable(self.__fail): response = self.__fail(response)
    finally:
      db.session.close()

    return response

  def success(self, s):
    self.__success = s
    return self

  def fail(self, f):
    self.__fail = f
    return self

'''
ModelAdditions

'''
class ModelAdditions:
  def __init__(self, _except=[], **kwargs):
    self.fill(_except, **kwargs)

  def insert(self):
    db.session.add(self)

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
  question = Column(String, nullable=False)
  answer = Column(String, nullable=False)
  category = Column(Integer, ForeignKey('categories.id'))
  difficulty = Column(Integer, nullable=False)

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
  type = Column(String, nullable=False)

  def format(self):
    return {
      'id': self.id,
      'type': self.type
    }