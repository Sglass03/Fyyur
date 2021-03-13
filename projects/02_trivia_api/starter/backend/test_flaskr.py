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
        self.database_path = "postgres://postgres:root@{}/{}".format('localhost:5432', self.database_name)
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



    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    # Test the GET endpoint for getting categories
    def test_get_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])

    # Test the GET endpoint for getting questions
    def test_get_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])

    # Test the DELETE endpoint for deleting questions
    def test_delete_question(self):
        res = self.client().delete("/questions/20")
        data = json.loads(res.data)

        #Actually delete
        question = Question.query.filter(Question.id == 20).first()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertFalse(question)

    # Test delete endpoint for 404
    def test_delete_question_404(self):
        res = self.client().delete("/questions/100")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    # Test post endpoint for creating a question
    def test_create_question(self):
        res = self.client().post("/questions", json={
                'question': "Who let the dogs out?",
                'answer': "Who Who Who Who!", 
                'difficulty': 1,
                'category': 3
                }
            )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)

    # Test missing data in post endpoint for creating a question
    def test_create_question(self):
        res = self.client().post("/questions", json={
                'answer': "Who Who Who Who!", 
                'difficulty': 1,
                'category': 3
                }
            )
        data = json.loads(res.data)

        self.assertTrue(res.status_code, 400)

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()