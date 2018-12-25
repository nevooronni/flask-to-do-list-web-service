#!flask/bin/python
from flask import Flask, jsonify, abort, make_response, request, url_for
from flask_httpauth import HTTPBasicAuth

app = Flask(__name__)
auth = HTTPBasicAuth()

#memory database composed on an list of dictionaries
tasks = [
  {
    'id': 1,
    'title': u'Buy groceries',
    'description': u'Milk, Cheese, Pizza, Fruit, Tyleno',
    'done': False
  },
  {
    'id': 2,
    'title': u'Learn Python',
    'description': u'Need to find a good Python tutorial on the web',
    'done': False
  },
  {
    'id': 3,
    'title': u'Learn Game',
    'description': u'Need scheducel time to learn game and get real world results',
    'done': False
  }
]

#authentication for web service
#in a more complex system this could check a user database, but in this case we just have a single user so need for that
@auth.get_password
def get_password(username):
  if username == 'miguel':
    return 'python'
  return None

@auth.error_handler
def unauthorized():
  return make_response(jsonify({'error': 'Unauthorized access'}), 403)

#helper function to return uri's instead of id's so the client get the URIs ready to be used
def make_public_task(task):
  new_task = {}
  for field in task:
    if field == 'id':
      new_task['uri'] = url_for('get_task', task_id=task['id'], _external=True)
    else:
      new_task[field] = task[field]
  
  return new_task

#only allow the get method and returns json data
#testing this kind of service with a web browser isn't the best option browsers cannot easily generate all types of http requests
#instead we use curl
#curl is a command line tool for transering data using url's
@app.route('/todo/api/v1.0/tasks', methods=['GET'])
@auth.login_required
def get_tasks():
  return jsonify({'tasks': [make_public_task(task) for task in tasks]})

#find task we package it as json with jsonify otherwise we return a 404 error
@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['GET'])
@auth.login_required
def get_task(task_id):
  task = [task for task in tasks if task['id'] == task_id]
  if len(task) == 0:
    abort(404)
  return jsonify({'task': [make_public_task(task[0])]})

@app.errorhandler(404)
def not_found(error):
  return make_response(jsonify({'error': 'Not found'}), 404)

@app.route('/todo/api/v1.0/tasks', methods=['POST'])
@auth.login_required
def create_task():
  if not request.json or not 'title' in request.json:
    abort(400) #bad request error
  task = {
    'id': tasks[-1]['id'] + 1,
    'title': request.json['title'],
    'description': request.json.get('description', ""),
    'done': False
  }

  tasks.append(task)
  return jsonify({'task': task}), 201  #return 201 for succesfully creating a new resource

@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['PUT'])
@auth.login_required
def update_task(task_id):
  #get specific resource to update
  task = [task for task in tasks if task['id'] == task_id]

  #validate our request data this is to prevent bugs we want to make sure that anything that the client provides is in the expected format before we try to incorporate it into our database
  if len(task) == 0:
    abort(404)
  if not request.json:
    abort(400)
  if 'title' in request.json and type(request.json['title']) != unicode:
    abort(400)
  if 'description' in request.json and type(request.json['description']) is not unicode:
    abort(400)
  if 'done' in request.json and type(request.json['done']) is not bool:
    abort(400)
  
  #update our data
  task[0]['title'] = request.json.get('title', task[0]['title'])
  task[0]['description'] = request.json.get('description', task[0]['description'])
  task[0]['done'] = request.json.get('done', task[0]['done'])

  return jsonify({'task': task[0]})

@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['DELETE'])
@auth.login_required
def delete_task(task_id):
  task = [task for task in tasks if task['id'] == task_id]
  
  #data validation
  if len(task) == 0:
    abort(404)
  tasks.remove(task[0])

  return jsonify({'result': True})


if __name__ == '__main__':
  app.run(debug=True)