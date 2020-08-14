import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_01_list_categories(self):
        res = self.client().get('/categories')
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.is_json)

        data = json.loads(res.data)
        self.assertEqual(data['success'], True)
        self.assertIsInstance(data['categories'], dict)

    def test_02_create_question(self):
        category = Category.query.first()
        self.assertIsNotNone(category)

        question = {
            'question': 'SomeQuestion',
            'answer': 'SomeAnswer',
            'category': category.id,
            'difficulty': 1
        }

        res = self.client().post('/questions', json=question)
        self.assertEqual(res.status_code, 201)
        self.assertTrue(res.is_json)

        data = json.loads(res.data)
        self.assertEqual(data['success'], True)

    def test_03_list_questions(self):
        res = self.client().get('/questions')
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.is_json)

        data = json.loads(res.data)
        self.assertEqual(data['success'], True)
        self.assertIsInstance(data['questions'], list)
        self.assertLessEqual(len(data['questions']), 10)
        self.assertIsInstance(data['total_questions'], int)
        self.assertGreaterEqual(data['total_questions'], 1)
        self.assertIsInstance(data['categories'], dict)

    def test_04_search(self):
        question = Question.query.first()
        self.assertIsNotNone(question)

        res = self.client().post(f'/question-searches', json={ 'searchTerm': 'meques' })
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.is_json)

        data = json.loads(res.data)
        self.assertEqual(data['success'], True)
        self.assertIsInstance(data['questions'], list)
        self.assertLessEqual(len(data['questions']), 10)
        self.assertGreaterEqual(len(data['questions']), 1)
        self.assertIsInstance(data['total_questions'], int)
        self.assertGreaterEqual(data['total_questions'], 1)

    def test_05_get_category_questions(self):
        category = Category.query.first()
        self.assertIsNotNone(category)

        res = self.client().get(f'/categories/{category.id}/questions')
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.is_json)

        data = json.loads(res.data)
        self.assertEqual(data['success'], True)
        self.assertIsInstance(data['questions'], list)
        self.assertLessEqual(len(data['questions']), 10)
        self.assertIsInstance(data['total_questions'], int)
        self.assertGreaterEqual(data['total_questions'], 1)

    def test_06_get_next_question(self):
        question = Question.query.first()
        self.assertIsNotNone(question)

        category = Category.query.get(question.category)
        self.assertIsNotNone(category)

        payload = {
            'previous_questions': [question.id],
            'quiz_category': category.format()
        }

        res = self.client().post('/quizzes', json=payload)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.is_json)

        data = json.loads(res.data)
        self.assertEqual(data['success'], True)

    def test_07_delete_question(self):
        question = Question.query.first()
        self.assertIsNotNone(question)

        res = self.client().delete(f'/questions/{question.id}')
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.is_json)

        data = json.loads(res.data)
        self.assertEqual(data['success'], True)

    def test_08_error_not_found(self):
        res = self.client().get('/')
        self.assertEqual(res.status_code, 404)
        self.assertTrue(res.is_json)

        data = json.loads(res.data)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], 'Not Found')

    def test_09_error_method_not_allowed(self):
        res = self.client().post('/categories')
        self.assertEqual(res.status_code, 405)
        self.assertTrue(res.is_json)

        data = json.loads(res.data)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 405)
        self.assertEqual(data['message'], 'Method Not Allowed')

    def test_10_error_unprocessable_entry(self):
        res = self.client().post('/questions', json={ 'category': 10000 })
        self.assertEqual(res.status_code, 422)
        self.assertTrue(res.is_json)

        data = json.loads(res.data)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 422)
        self.assertEqual(data['message'], 'Unprocessable Entity')

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()