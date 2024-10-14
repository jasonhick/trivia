import os
import random

from dotenv import load_dotenv
from flask import Flask, abort, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

load_dotenv()

from models import Category, Question, setup_db

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)

        # Override config with environment variables
        app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URI")

        setup_db(app)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)
        database_path = test_config.get("SQLALCHEMY_DATABASE_URI")
        setup_db(app, database_path=database_path)

    """
    @DONE: Use the after_request decorator to set Access-Control-Allow
    """

    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response

    """
    @DONE: Create an endpoint to handle GET requests for all available categories.
    """

    @app.route("/categories", methods=["GET"])
    def get_categories():
        categories = Category.query.order_by(Category.id).all()
        categories_dict = {
            category.id: category.type for category in categories
        }

        if len(categories_dict) == 0:
            abort(404)

        return jsonify({"success": True, "categories": categories_dict})

    """
    @DONE: 
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    @DONE: 
    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """

    @app.route("/questions", methods=["GET"])
    def get_questions():
        PAGE_SIZE = 10

        # Get page from query parameters, default to 1
        page = request.args.get("page", 1, type=int)

        # Get all questions, paginated
        questions = Question.query.order_by(Question.id).paginate(
            page=page, per_page=PAGE_SIZE, error_out=False
        )

        # If no questions found for the requested page, return 404
        if not questions.items:
            abort(404)

        # Format questions
        formatted_questions = [
            question.format() for question in questions.items
        ]

        # Get all categories
        categories = Category.query.order_by(Category.id).all()
        categories_dict = {
            category.id: category.type for category in categories
        }

        return jsonify(
            {
                "success": True,
                "questions": formatted_questions,
                "total_questions": questions.total,
                "categories": categories_dict,
                "current_category": None,
            }
        )

    """
    @DONE: 
    Create an endpoint to DELETE question using a question ID.
    
    @DONE: TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """

    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        question = Question.query.get(question_id)
        if question is None:
            abort(404)

        try:
            question.delete()

            return jsonify({"success": True, "deleted": question_id})
        except:
            abort(422)

    """
    @DONE:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    @DONE: TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    @app.route("/questions", methods=["POST"])
    def create_question():
        data = request.get_json()

        # Check if all required fields are present
        required_fields = ["question", "answer", "category", "difficulty"]
        if not all(field in data for field in required_fields):
            abort(400)

        new_question = Question(
            question=data["question"],
            answer=data["answer"],
            category=data["category"],
            difficulty=data["difficulty"],
        )

        try:
            new_question.insert()
            return (
                jsonify(
                    {
                        "success": True,
                        "created": new_question.id,
                        "total_questions": Question.query.count(),
                    }
                ),
                201,
            )
        except:
            abort(422)

    """
    @DONE:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    @DONE: TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    @app.route("/questions/search", methods=["POST"])
    def search_questions():

        data = request.get_json()
        search_term = data.get("searchTerm")

        if not search_term:
            abort(400)

        # Perform case-insensitive search
        questions = Question.query.filter(
            Question.question.ilike(f"%{search_term}%")
        ).all()

        formatted_questions = [question.format() for question in questions]

        return jsonify(
            {
                "success": True,
                "questions": formatted_questions,
                "total_questions": len(formatted_questions),
                "current_category": None,
            }
        )

    """
    @DONE:
    Create a GET endpoint to get questions based on category.

    @DONE: TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

    @app.route("/categories/<int:category_id>/questions")
    def get_questions_by_category(category_id):

        # Get questions for the specified category
        questions = Question.query.filter(
            Question.category == str(category_id)
        ).all()

        # If no questions found for the category, return 404

        if len(questions) == 0:
            abort(404)

        try:
            # Format the questions
            formatted_questions = [question.format() for question in questions]

            # Get the category
            category = Category.query.get(category_id)
            if not category:
                abort(404)

            return jsonify(
                {
                    "success": True,
                    "questions": formatted_questions,
                    "total_questions": len(formatted_questions),
                    "current_category": category.type,
                }
            )
        except:
            abort(500)

    """
    @DONE:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    @app.route("/quizzes", methods=["POST"])
    def play_quiz():
        try:
            body = request.get_json()
            previous_questions = body.get("previous_questions", [])
            quiz_category = body.get("quiz_category")

            if quiz_category:
                category_id = quiz_category.get("id")
                if category_id == 0:  # "All" category
                    available_questions = Question.query.filter(
                        ~Question.id.in_(previous_questions)
                    ).all()
                else:
                    available_questions = Question.query.filter(
                        Question.category == str(category_id),
                        ~Question.id.in_(previous_questions),
                    ).all()
            else:
                available_questions = Question.query.filter(
                    ~Question.id.in_(previous_questions)
                ).all()

            if not available_questions:
                return jsonify({"success": True, "question": None})

            random_question = random.choice(available_questions)
            formatted_question = random_question.format()

            return jsonify({"success": True, "question": formatted_question})

        except:
            abort(422)

    """
    @DONE:
    Create error handlers for all expected errors including 404 and 422.
    """

    def create_error_response(error_code, message):
        return (
            jsonify(
                {"success": False, "error": error_code, "message": message}
            ),
            error_code,
        )

    error_messages = {
        400: "Bad request",
        404: "Resource not found",
        422: "Unprocessable entity",
        500: "Internal server error",
    }

    for error_code, message in error_messages.items():
        app.errorhandler(error_code)(
            lambda e, code=error_code, msg=message: create_error_response(
                code, msg
            )
        )

    return app
