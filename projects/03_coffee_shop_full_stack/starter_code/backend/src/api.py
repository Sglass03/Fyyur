import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

# Instantiate the Flask app, DB, and CORS
app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

## ROUTES


'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks')
def get_drinks():
    # Query all drinks in the DB
    drinks = Drink.query.all()

    # Format the drink objects for the front-end
    drinks = [drink.short() for drink in drinks]

    # Create the returned JSON object
    resp = jsonify({
        "success": True, 
        "drinks": drinks
    })

    return resp, 200


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def drinks_detail(payload):
    
    # Query all drinks
    drinks = Drink.query.all()

    # Format drink objects
    drinks = [drink.long() for drink in drinks]
    
    return jsonify({
        'success': True, 
        'drinks': drinks
    }), 200


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def drinks_post(payload):
    
    # Get JSON request 
    data = request.json

    # Create a new Drink object from JSON object and insert into DB
    drink = Drink(title=data['title'], recipe=json.dumps(data['recipe']))
    drink.insert()
    
    return jsonify({
        'success': True, 
        'drinks': drink.long()
    }), 200

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def drink_update(payload, id):

    body = request.get_json(force=True)
    title = body.get('title', None)
    recipe = json.dumps(body.get('recipe', None))

    drink = Drink.query.filter(Drink.id == id).all()

    if drink is None:
        #ID not found
        abort(404)

    try:
        drink[0].title = title if type(title) == str else json.dumps(title)
        drink[0].recipe = recipe if type(recipe) == str else json.dumps(recipe)
        drink[0].update()
    except Exception as e:
        print(e)
        abort(500)
    
    return jsonify({
        'success': True, 
        'drinks': [drink[0].long()]
    }), 200



'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def drinks_delete(payload, id):
    
    drink = Drink.query.filter(Drink.id == id).first()

    if drink is None:
        abort(404)

    try:
        drink.delete()
    except Exception as e:
        print(e)
        abort(500)
    
    return jsonify({
        'success': True, 
        'delete': id
    }), 200



## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

@app.errorhandler(403)
def permission_denied(error):
    return jsonify({
                    "success": False, 
                    "error": 403,
                    "message": "You do not have proper authorization to execute that operation"
                    }), 403


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''
@app.errorhandler(404)
def not_found(error):
    return jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''

@app.errorhandler(AuthError)
def authentication_failed(e):
    print(AuthError)
    print(e.status_code)
    return jsonify({
                    "success": False, 
                    "error": e.error['code'],
                    "message": e.error['description']
                    }), e.status_code
