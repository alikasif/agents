"""
DogStore REST client for interacting with dog_store_server.py APIs.
"""
import requests

BASE_URL = 'http://127.0.0.1:5000/dogstore'

class DogStoreClient:
    def get_all_dogs(self):
        resp = requests.get(f'{BASE_URL}/dogs')
        resp.raise_for_status()
        return resp.json()

    def get_dog_by_id(self, dog_id):
        resp = requests.get(f'{BASE_URL}/dogs/{dog_id}')
        resp.raise_for_status()
        return resp.json()

    def create_dog(self, dog):
        resp = requests.post(f'{BASE_URL}/dogs', json=dog)
        resp.raise_for_status()
        return resp.status_code

    def update_dog(self, dog_id, dog):
        resp = requests.put(f'{BASE_URL}/dogs/{dog_id}', json=dog)
        resp.raise_for_status()
        return resp.status_code

    def delete_dog(self, dog_id):
        resp = requests.delete(f'{BASE_URL}/dogs/{dog_id}')
        resp.raise_for_status()
        return resp.status_code

if __name__ == '__main__':
    client = DogStoreClient()
    print('All dogs:', client.get_all_dogs())
    print('Get dog by ID:', client.get_dog_by_id(1))
    new_dog = {'id': 2, 'name': 'Max', 'breed': 'Beagle'}
    print('Create dog:', client.create_dog(new_dog))
    print('Update dog:', client.update_dog(2, {'name': 'Maximus', 'breed': 'Beagle'}))
    print('Delete dog:', client.delete_dog(2))
