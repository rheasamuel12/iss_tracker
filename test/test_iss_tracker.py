import pytest
import requests
from datetime import datetime
import json
URL = 'http://127.0.0.1:5000'
#Used ChatGPT to understand how to use unit testing with flask routes and fix errors

@pytest.fixture(scope='module')
def sample_epoch():
    response = requests.get(f'{URL}/epochs')
    assert isinstance(response.json(), list) == True
    assert response.status_code == 200
    return response.json()[0]['EPOCH']

def test_comment_route():
    response = requests.get(f'{URL}/comment')
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0

def test_header_route():
    response = requests.get(f'{URL}/header')
    assert response.status_code == 200
    assert isinstance(response.json(), dict) == True
def test_metadata_route():
    response = requests.get(f'{URL}/metadata')
    assert response.status_code == 200
    assert isinstance(response.json(), dict) == True
def test_location_route(sample_epoch):
    epoch = sample_epoch
    response = requests.get(f'{URL}/epochs/{epoch}/location')
    assert response.status_code == 200
    data = response.json()
    assert 'latitude' in data
    assert 'longitude' in data
    assert 'altitude' in data
    assert 'geoposition' in data

def test_now_route():
    response = requests.get(f'{URL}/now')
    assert response.status_code == 200
    data = response.json()
    assert 'latitude' in data
    assert 'longitude' in data
    assert 'altitude' in data
    assert 'geoposition' in data

def test_epochs_route():
    response = requests.get(f'{URL}/epochs')
    assert response.status_code == 200
    assert isinstance(response.json(), list) == True

def test_specific_epoch_route(sample_epoch):
    epoch = sample_epoch
    response = requests.get(f'{URL}/epochs/{epoch}')
    assert response.status_code == 200
    assert isinstance(response.json(), dict) == True

def test_speed_route(sample_epoch):
    epoch = sample_epoch
    response = requests.get(f'{URL}/epochs/{epoch}/speed')
    assert response.status_code == 200
    assert isinstance(float(response.text), float) == True

if __name__ == '__main__':
    pytest.main()



