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
        self.database_name = "trivia"
        self.database_path = f'postgresql://hamzamare@localhost:5432/{self.database_name}'
        setup_db(self.app, self.database_path)

        self.new_question = {"question": "Which country hoosted world cup in 20210?", "answer":"South Africa", "category":"6", "difficulty":"3"}
        self.search_term = {'search': 'world cup'}

        self.id_to_delete = 35


        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        res = self.client().get('/categories')
        datas = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(datas['success'], True)
        self.assertTrue(datas['total_categories'])

    
    def test_get_failed_404_categories(self):
        res = self.client().get('/categor')
        datas = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(datas['success'], False)
        self.assertTrue(datas['message'])
        self.assertTrue(datas['error'])
    
    def test_get_questions(self):
        res = self.client().get('/questions')
        datas = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(datas['success'], True)
        self.assertTrue(datas['categories'])
    
    def test_get_failed_404_questions(self):
        res = self.client().get('/quest')
        datas = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(datas['success'], False)
        self.assertTrue(datas['message'])
        self.assertTrue(datas['error'])
    
    def test_get_specific_question_by_id(self):
        res = self.client().get('/questions/10')
        datas = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(datas['success'], True)
        self.assertTrue(datas['Question'])
    
    def test_get_failed_404_specific_question_behond_valid_page(self):
        res = self.client().get('/questions/5000')
        datas = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(datas['success'], False)
        self.assertTrue(datas['message'])
        self.assertTrue(datas['error'])
    
    def test_delete_question(self):
        res = self.client().delete(f'/questions/{self.id_to_delete}')
        datas= json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(datas['success'], True)
        self.assertEqual(datas['deleted'], self.id_to_delete)
    
    def test_404_if_question_does_not_exist(self):
        res = self.client().delete("/questions/1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertTrue(data["message"])

    def test_post_newQuestion(self):
        res = self.client().post('/questions', json=self.new_question)
        datas = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(datas['success'], True)
        self.assertTrue(datas['created'])
    
    def test_search_term(self):
        res = self.client().post('/questions', json=self.search_term)
        datas = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(datas['success'], True)

    def test_405_if_question_creation_not_allowed(self):
        res = self.client().post("/questions/45", json=self.new_question)
        datas = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(datas["success"], False)
        self.assertEqual(datas["message"], "Method not allowed")
    
    def test_get_questions_per_specific_category(self):
        res = self.client().get('/categories/2/questions')
        datas = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(datas['totalQuestions'])
        self.assertEqual(datas['success'], True)
    
    def test_422_if_question_beyond_category_unprocessable(self):
        res = self.client().get("/categories/45555/questions")
        datas = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(datas["success"], False)
        self.assertTrue(datas["message"])
    
    def test_quizzes(self):
        res = self.client().post('/quizzes', json={"quiz_category": "ALL"})
        datas = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(datas['success'],True)
        self.assertTrue(datas['Question'])
    
    def test_failed_422_quizzes(self):
        res = self.client().post('/quizzes')
        datas = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertTrue(datas['message'])
        self.assertEqual(datas['success'], False)

#  Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()