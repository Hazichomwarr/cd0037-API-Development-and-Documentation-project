from bdb import set_trace
from crypt import methods
import json
import os
from sre_parse import CATEGORIES
from termios import PARODD
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def pagination(request, select_questions):
    page = request.args.get('page', 1, type=int)
    start_index = (page - 1) * QUESTIONS_PER_PAGE
    end_index = start_index + QUESTIONS_PER_PAGE
    formatted_questions = [question.format() for question in select_questions]
    return formatted_questions[start_index:end_index]
    


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app)
    # CORS(app, resources={r"*/api/*" : {'origins': '*'}})

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Headers', 'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories')
    def list_categories():
        categories = Category.query.order_by(Category.id).all()
        categories_formatted = [category.format() for category in categories]

        return jsonify({
            'success': True,
            'categories': categories_formatted,
            'total_categories': len(categories_formatted)
            })

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.


    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions')
    def list_questions():
        list_questions = Question.query.order_by(Question.id).all()
        categories = Category.query.order_by(Category.id).all()
        categories_formatted = [category.format() for category in categories]

        return jsonify({
            'success': True,
            'totalQuestions': len(list_questions),
            'questions': pagination(request, list_questions),
            'categories': pagination(request, categories)
        })
    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:question_id>', methods=['GET', 'DELETE'])
    def delete_question(question_id):
        question = Question.query.get_or_404(question_id)
        if request.method == 'DELETE':
            question.delete()

            return jsonify({
                'success': True,
                'deleted': question.id
            })
        else:
            return jsonify({
                'success': True,
                'Question': question.format()
            })


    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """


    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """


    @app.route('/questions', methods=['GET', 'POST'])
    def create_question():
        # handling 'POST' requests here
        if request.method == 'POST':
            
            body = request.get_json()
            
            # this 'POST' block checks handles a search
            # first: get the search term from the front-end
            if body.get('searchTerm'):
                body = request.get_json()
                search_term = body.get('searchTerm')

                # then search in the db and return the reponse
                searchTerm = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
                formatted_search = [search.format() for search in searchTerm]
                return jsonify({
                    'success': True,
                    'searchTerm': formatted_search,
                    'total_search': len(searchTerm)
                })

            # this 'POST' block creates a new_book
            else:
                new_question = Question(
                    question=body.get('question'), 
                    answer=body.get('answer'), 
                    category=body.get('category'), 
                    difficulty=body.get('difficulty'),
                )
                # add it in the db
                new_question.insert()

                questions = Question.query.order_by(Question.id).all()
                questions_paginated = pagination(request, questions)
                return jsonify({
                    'success': True,
                    'created': new_question.id,
                    'questions': questions_paginated,
                    'totalQuestions': len(questions)
                })

        # handling 'GET' requests here
        else:
            list_questions = Question.query.order_by(Question.id).all()
            categories = Category.query.order_by(Category.id).all()
            # categories_formatted = [category.format() for category in categories]

            return jsonify({
                'success': True,
                'categories': pagination(request, categories),
                'current_category': pagination(request, categories),
                'questions': pagination(request, list_questions),
                'totalQuestions': QUESTIONS_PER_PAGE,
            })

    

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:cat_numb>/questions')
    def category_questions(cat_numb):
        # result = request.args.get(cat_numb)
        relativ_questions = Question.query.filter(Question.category==cat_numb).all()
        if relativ_questions:
            format_relativ_questions = [question.format() for question in relativ_questions]
            return jsonify({
                'success': True,
                'questions': format_relativ_questions,
                'totalQuestions': len(relativ_questions)
            })
        else:
            abort(422)


    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """ 

    @app.route('/quizzes', methods=['POST'])
    def play_quizzes():
        try:
            data = request.get_json()
            data_category = data.get('quiz_category')
            previous_questions = data.get('previous_questions', [0])

            
            # if 'all' category is selected
            if data_category.upper() == 'ALL':
                all_questions = Question.query.filter(Question.id.notin_(previous_questions)).all()
                # import pdb
                # pdb.set_trace()
                return jsonify({
                    'success': True,
                    'Question': random.choice(all_questions).format()
                })
            else:
                category = Category.query.filter(Category.type==data_category).one_or_none()
                cat_questions = Question.query.filter(Question.category==category.id and Question.id.notin_(previous_questions)).all()
                return jsonify({
                    'success': True,
                    'Question': random.choice(cat_questions).format()
                })
        except:
            abort(422)

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'ressource not found'
        }), 404
    
    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'request unprocessable'
        }), 422
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'Bad request'
        }), 400

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'success': False,
            'error': 405,
            'message': 'Method not allowed'
        }), 405

    return app

