"""
DogStore API server implementation based on dog_store.yaml OpenAPI spec.
"""
from flask import Flask, request, jsonify, abort

app = Flask(__name__)

dogs = [
    {
        'id': 1,
        'name': 'Buddy',
        'breed': 'Golden Retriever'
    }
]

def find_dog(dog_id):
    return next((dog for dog in dogs if dog['id'] == dog_id), None)

@app.route('/dogstore/dogs', methods=['GET'])
def get_all_dogs():
    return jsonify(dogs), 200

@app.route('/dogstore/dogs', methods=['POST'])
def create_dog():
    data = request.get_json()
    if not data or 'id' not in data or 'name' not in data or 'breed' not in data:
        abort(400, 'Missing dog data')
    if find_dog(data['id']):
        abort(400, 'Dog with this ID already exists')
    dogs.append(data)
    return '', 201

@app.route('/dogstore/dogs/<int:id>', methods=['GET'])
def get_dog_by_id(id):
    dog = find_dog(id)
    if not dog:
        abort(404, 'Dog not found')
    return jsonify(dog), 200

@app.route('/dogstore/dogs/<int:id>', methods=['PUT'])
def update_dog(id):
    dog = find_dog(id)
    if not dog:
        abort(404, 'Dog not found')
    data = request.get_json()
    if not data or 'name' not in data or 'breed' not in data:
        abort(400, 'Missing dog data')
    dog['name'] = data['name']
    dog['breed'] = data['breed']
    return '', 200

@app.route('/dogstore/dogs/<int:id>', methods=['DELETE'])
def delete_dog(id):
    dog = find_dog(id)
    if not dog:
        abort(404, 'Dog not found')
    dogs.remove(dog)
    return '', 204

if __name__ == '__main__':
    app.run(debug=True)
