import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy.sql.expression import func

from models import setup_db, Question, Category, Transaction

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)

  CORS(app, resources={r"*": {"origins": "*"}})

  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
    return response

  @app.route('/categories')
  def list_categories():
    categories = {category.id: category.type for category in Category.query.all()}
    return jsonify({ 'categories': categories, 'success': True })

  @app.route('/questions')
  def list_questions():
    pagination = Question.query.paginate(per_page=QUESTIONS_PER_PAGE)

    return jsonify({
      'questions': [question.format() for question in pagination.items],
      'total_questions': pagination.total,
      'categories': {category.id: category.type for category in Category.query.all()},
      'current_category': None,
      'success': True
    })

  @app.route('/questions/<int:id>', methods=['DELETE'])
  def delete_question(id):
    question = Question.query.get(id)
    if question is None: abort(404)

    Transaction(lambda: question.delete()).fail(lambda: abort(422))()

    return jsonify({ 'success': True })

  @app.route('/questions', methods=['POST'])
  def create_question():
    try: question = Question(**request.get_json())
    except: abort(422)

    Transaction(lambda: question.insert()).fail(lambda: abort(422))()

    return jsonify({ 'success': True }), 201

  @app.route('/question-searches', methods=['POST'])
  def search():
    q = request.get_json().get('searchTerm', '')
    
    pagination = Question.query.filter(Question.question.ilike(f'%{q}%')).paginate(per_page=QUESTIONS_PER_PAGE)

    return jsonify({
      'questions': [question.format() for question in pagination.items],
      'total_questions': pagination.total,
      'current_category': None,
      'success': True
    })

  @app.route('/categories/<int:id>/questions')
  def get_category_questions(id):
    category = Category.query.get(id)
    if category is None: abort(404)
    
    pagination = Question.query.filter(Question.category == category.id).paginate(per_page=QUESTIONS_PER_PAGE)

    return jsonify({
      'questions': [question.format() for question in pagination.items],
      'total_questions': pagination.total,
      'current_category': id,
      'success': True
    })

  @app.route('/quizzes', methods=['POST'])
  def get_next_question():
    json = request.get_json()
    
    previous_questions = json.get('previous_questions', [])
    quiz_category = json.get('quiz_category')

    query = Question.query.filter(~Question.id.in_(previous_questions)).order_by(func.random())
    if quiz_category: query.filter(Question.category == quiz_category['id'])
    question = query.first()

    return jsonify({
      'question': question.format() if question else None,
      'success': True
    })

  @app.errorhandler(404)
  def error_not_found(error):
    return jsonify({
      'error': 404,
      'message': 'Not Found',
      'success': False
    }), 404

  @app.errorhandler(405)
  def error_method_not_allowed(error):
    return jsonify({
      'error': 405,
      'message': 'Method Not Allowed',
      'success': False
    }), 405

  @app.errorhandler(422)
  def error_unprocessable_entity(error):
    return jsonify({
      'error': 422,
      'message': 'Unprocessable Entity',
      'success': False
    }), 422

  @app.errorhandler(500)
  def error_internal_server_error(error):
    return jsonify({
      'error': 500,
      'message': 'Internal Server Error',
      'success': False
    }), 500
  
  return app
