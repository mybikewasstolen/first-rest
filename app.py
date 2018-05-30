#!flask/bin/python
from flask import Flask, jsonify, abort, make_response, request, url_for
from flask_httpauth import HTTPBasicAuth
import json
import config

auth = HTTPBasicAuth()

app = Flask(__name__)

with open('tasks.json') as json_file:
    tasks = json.load(json_file)





def make_public_task(task):
    new_task = {}
    for field in task:
        if field == 'id':
            new_task['uri'] = url_for('get_task', task_id=task['id'], _external=True)
        else:
            new_task[field] = task[field]
    return new_task


@app.route('/tor_rest/api/v1.0/tasks', methods=['GET'])
@auth.login_required
def get_tasks():
    new_tasks = []
    for task in tasks:
        new_tasks.append(make_public_task(task))
    return jsonify({'tasks': new_tasks})


@app.route('/tor_rest/api/v1.0/tasks/<int:task_id>', methods=['GET'])
@auth.login_required
def get_task(task_id):
    task = list(filter(lambda t: t['id'] == task_id, tasks))
    if len(task) == 0:
        abort(404)
    return jsonify({'task': task[0]})


@app.route('/tor_rest/api/v1.0/tasks', methods=['POST'])
@auth.login_required
def create_task():
    if not request.json or not 'task_name' in request.json:
        abort(400)
    task = {
        'id': tasks[-1]['id'] + 1,
        'task_name': request.json['task_name'],
        'resource': request.json.get('resource', 'rutra'),
        'tor_number': request.json['tor_number'],
        'dir_dest': request.json.get('dir_dest', 'movies'),
        'done': False
    }
    tasks.append(task)
    with open('tasks.json', 'w') as outfile:
        json.dump(tasks, outfile)
    return jsonify({'task': task}), 201


@app.route('/tor_rest/api/v1.0/tasks/<int:task_id>', methods=['DELETE'])
@auth.login_required
def delete_task(task_id):
    task = list(filter(lambda t: t['id'] == task_id, tasks))
    if len(task) == 0:
        abort(404)
    tasks.remove(task[0])
    with open('tasks.json', 'w') as outfile:
        json.dump(tasks, outfile)
    return jsonify({'result': True})


@app.route('/tor_rest/api/v1.0/tasks/<int:task_id>', methods=['PUT'])
@auth.login_required
def update_task(task_id):
    task = list(filter(lambda t: t['id'] == task_id, tasks))
    if len(task) == 0:
        abort(404)
    if not request.json:
        abort(400)
    if 'done' in request.json and type(request.json['done']) is not bool:
        abort(400)
    if 'task_name' in request.json:
        task[0]['task_name'] = request.json.get('task_name', task[0]['task_name'])
    if 'resource' in request.json:
        task[0]['resource'] = request.json.get('resource', task[0]['resource'])
    if 'tor_number' in request.json:
        task[0]['tor_number'] = request.json.get('tor_number', task[0]['tor_number'])
    if 'dir_dest' in request.json:
        task[0]['dir_dest'] = request.json.get('dir_dest', task[0]['dir_dest'])
    if 'done' in request.json:
        task[0]['done'] = request.json.get('done', task[0]['done'])
    with open('tasks.json', 'w') as outfile:
            json.dump(tasks, outfile)
    return jsonify({'task': task[0]})


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@auth.get_password
def get_password(username):
    if username == config.username:
        return config.password
    return None


@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)


if __name__ == '__main__':
    app.run(debug=True)