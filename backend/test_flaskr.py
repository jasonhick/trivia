import json
import unittest
from os import environ
from unittest.mock import patch

from flask_sqlalchemy import SQLAlchemy
from flaskr import create_app
from models import Category, Question, setup_db


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client

        # Set up database connection
        database_name = environ.get("DATABASE_NAME", "trivia_test")
        database_host = environ.get("DATABASE_HOST", "localhost")
        database_port = environ.get("DATABASE_PORT", "5432")
        database_path = (
            f"postgresql://{database_host}:{database_port}/{database_name}"
        )

        # Set up the app with the test database
        self.app.config["SQLALCHEMY_DATABASE_URI"] = database_path
        self.app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        setup_db(self.app)

        # Binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # Create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_categories(self):
        """Test GET request for categories"""
        response = self.client().get("/categories")
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["categories"])

    def test_get_categories_404(self):
        """Test 404 error for requesting categories"""
        with patch("flaskr.Category.query") as mock_query:
            mock_query.order_by().all.return_value = []
            response = self.client().get("/categories")

        self.assertEqual(response.status_code, 404)

    def test_get_questions(self):
        """Test GET request for questions"""
        response = self.client().get("/questions")
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["questions"])
        self.assertTrue(len(data["questions"]) <= 10)
        self.assertTrue(data["total_questions"])
        self.assertTrue(data["categories"])
        self.assertIsNone(data["current_category"])

    def test_get_questions_404(self):
        """Test 404 error for requesting questions beyond valid page"""
        response = self.client().get("/questions?page=1000")
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Resource not found")

    # def test_delete_question(self):
    #     """Test DELETE request for questions"""
    #     response = self.client().delete("/questions/5")
    #     data = json.loads(response.data)

    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(data["success"], True)
    #     self.assertEqual(data["deleted"], 5)

    def test_create_question(self):
        """Test POST request for questions"""
        response = self.client().post(
            "/questions",
            json={
                "question": "What is the capital of France?",
                "answer": "Paris",
                "category": 1,
                "difficulty": 1,
            },
        )
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["created"])
        self.assertTrue(data["total_questions"])

    def test_create_question_400(self):
        """Test 400 error for creating a question with missing fields"""
        response = self.client().post(
            "/questions",
            json={
                "question": "What is the capital of France?",
                "answer": "Paris",
                # Missing 'category' and 'difficulty' fields
            },
        )
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Bad request")

    def test_create_question_422(self):
        """Test 422 error for creating a question with invalid data"""
        response = self.client().post(
            "/questions",
            json={
                "question": "What is the capital of France?",
                "answer": "Paris",
                "category": "invalid",  # Should be an integer
                "difficulty": 1,
            },
        )
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Unprocessable entity")

    def test_search_questions(self):
        """Test POST request for searching questions"""
        response = self.client().post(
            "/questions/search",
            json={"searchTerm": "capital"},
        )
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["questions"])

    def test_get_questions_by_category(self):
        """Test GET request for questions by category"""
        response = self.client().get("/categories/1/questions")
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["questions"])
        self.assertTrue(data["total_questions"])

    def test_delete_question(self):
        """Test DELETE request for questions"""
        # Create a question to delete
        question = Question(
            question="Test question",
            answer="Test answer",
            category=1,
            difficulty=1,
        )
        question.insert()

        response = self.client().delete(f"/questions/{question.id}")
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["deleted"], question.id)

        # Verify the question is deleted
        deleted_question = Question.query.get(question.id)
        self.assertIsNone(deleted_question)

    def test_delete_question_404(self):
        """Test 404 error for deleting a non-existent question"""
        response = self.client().delete("/questions/9999")
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Resource not found")

    def test_search_questions_no_results(self):
        """Test POST request for searching questions with no results"""
        response = self.client().post(
            "/questions/search",
            json={"searchTerm": "xyzxyzxyz"},
        )
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(len(data["questions"]), 0)
        self.assertEqual(data["total_questions"], 0)

    def test_get_questions_by_category_404(self):
        """Test 404 error for requesting questions for a non-existent category"""
        response = self.client().get("/categories/9999/questions")
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Resource not found")

    def test_play_quiz(self):
        """Test POST request for playing quiz"""
        response = self.client().post(
            "/quizzes",
            json={
                "previous_questions": [],
                "quiz_category": {"id": 1, "type": "Science"},
            },
        )
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["question"])
        self.assertIn("id", data["question"])
        self.assertIn("question", data["question"])
        self.assertIn("answer", data["question"])
        self.assertIn("category", data["question"])
        self.assertIn("difficulty", data["question"])

    def test_play_quiz_no_more_questions(self):
        """Test POST request for playing quiz when no more questions are available"""
        # Get all question ids for a category
        category_id = 1
        questions = Question.query.filter(
            Question.category == str(category_id)
        ).all()
        question_ids = [q.id for q in questions]

        response = self.client().post(
            "/quizzes",
            json={
                "previous_questions": question_ids,
                "quiz_category": {"id": category_id, "type": "Science"},
            },
        )
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertIsNone(data["question"])


if __name__ == "__main__":
    unittest.main()
