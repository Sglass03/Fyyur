import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)

  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  #Default CORS origin is * 
  CORS(app)

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers['Access-Control-Allow'] = '*'
    return response


  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route("/categories")
  def get_categories():
      
    # Query all categories
    categories = Category.query.all()

    # Reformat categories into a dictionary
    # of id: type
    categories_ids = {
        category.id: category.type for category in categories
    }

    result = jsonify({
        'success': True,
        'categories': categories_ids
    })

    return result

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''

  # Create pagination function called in get_questions
  def paginate(questions, max_per_page, page):
      start = (page - 1) * max_per_page
      end = page * max_per_page 

      questions = questions[start:end]

      return questions

  @app.route("/questions")
  def get_questions():

      # Get page number from request
      page = request.args.get('page', default=1)
      page = int(page)
      
      # Query all questions from database and format
      questions = Question.query.all()
      questions = [question.format() for question in questions]

      # Calculate total length of request to support pagination
      max_questions = len(questions)

      # Run paginate custom function
      questions = paginate(questions, QUESTIONS_PER_PAGE, page)

      # Get all categories
      categories = Category.query.all()
      categories_ids = {
          category.id: category.type for category in categories
      }

      result = {
          'success': True,
          'questions': questions,
          'total_questions': max_questions,
          'categories': categories_ids,
          'currentCategory': None
      }

      return jsonify(result)

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route("/questions/<int:id>", methods=['DELETE'])
  def delete_question(id):
    
    question = Question.query.filter(Question.id == id).first()

    if question is None:
        abort(404)

    try:
        question.delete()
    except Exception as e:
        abort(500)

    result = jsonify({
        'success': True
    })
    return result

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route("/questions", methods=['POST'])
  def create_question():

    body = request.get_json()

    # Make sure all keys are in the request
    form_keys = ['question', 'answer', 'difficulty', 'category']
    if not all(form_key in body for form_key in form_keys):
        abort(400)

    try: 
        q = Question(question=body['question'], answer=body['answer'], 
            difficulty=body['difficulty'], category=body['category'])
        q.insert()
    except Exception as e:
        db.session.rollback()
        print(e)

    result = jsonify({
        'success': True
    })
    return result

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route("/questions/search", methods=['POST'])
  def search_questions():
    #Get search term
    body = request.get_json()
    search_term = body['searchTerm']
    
    # Find and format questions with the search team, case insensitive
    questions = Question.query.filter(Question.question.ilike('%{}%'.format(search_term))).all()
    questions = [question.format() for question in questions]

    result = {
        'success': True,
        'questions': questions,
        'totalQuestions': len(questions),
        'currentCategory': None
    }

    return jsonify(result)


  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<id>/questions')
  def question_category(id):
    category_id = id

    questions = Question.query.filter(Question.category==category_id).all()
    questions = [question.format() for question in questions]

    result = {
        'success': True,
        'questions': questions,
        'totalQuestions': len(questions),
        'currentCategory': None
    }

    return jsonify(result)


  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def play_quiz():
      
    body = request.get_json()

    # Category is object with type: string, id: int
    category = body['quiz_category']
    previous_questions = body['previous_questions']

    #Get all questions in category
    questions = Question.query.filter(Question.category==category['id'])
    
    # Get full list of question ids in the category
    question_ids = []
    for q in questions:
        question_ids.append(q.id)

    # Remove question ids if in previous questions list
    # Informed by list comprehension in following Stack Overflow answer:
    # https://stackoverflow.com/questions/4211209/remove-all-the-elements-that-occur-in-one-list-from-another/4211228
    
    potential_question_ids = [id for id in question_ids if id not in previous_questions]
    
    # Get random question from potential question ids
    if len(potential_question_ids) > 0:
        random_question_id = random.choice(potential_question_ids)

        for q in questions:
            if q.id == random_question_id:
                random_question = q.format()
    else:
        random_question = None

    result = {
        'success': True, 
        'question': random_question
    }

    return jsonify(result)

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  400, 404, 422 and 500
  '''
  @app.errorhandler(405)
  def method_not_allowed(e):
    return jsonify({
        'success': False,
        'error': 405,
        'message': 'Method not allowed'
    }), 405

  @app.errorhandler(500)
  def server_error(e):
    return jsonify({
        'success': False,
        'error': 500,
        'message': 'Internal server error'
    }), 500

  @app.errorhandler(422)
  def unprocessable_entity(e):
    return jsonify({
        'success': False,
        'error': 422,
        'message': 'Request was well formed but included semantic errors'
    }), 422

  @app.errorhandler(404)
  def not_found(e):
    return jsonify({
        'success': False,
        'error': 404,
        'message': 'Page not found'
    }), 404

  @app.errorhandler(400)
  def bad_request(e):
    return jsonify({
        'success': False,
        'error': 400,
        'message': 'Bad request'
    }), 400


  return app

    