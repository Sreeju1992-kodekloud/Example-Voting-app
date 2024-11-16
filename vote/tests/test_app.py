import pytest
import sys
import os
from flask import Flask
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app as flask_app
from unittest.mock import patch, MagicMock

# Use the test client from Flask for testing
@pytest.fixture
def client():
    with flask_app.test_client() as client:
        yield client

# Mock Redis using MagicMock
@pytest.fixture
def mock_redis():
    with patch('app.get_redis') as mock_redis_func:
        mock_redis_instance = MagicMock()
        mock_redis_func.return_value = mock_redis_instance
        yield mock_redis_instance

# Test: GET request to load the homepage
def test_homepage(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Cats' in response.data  # Check if option_a (Cats) is in the page
    assert b'Dogs' in response.data  # Check if option_b (Dogs) is in the page

# Test: POST request to cast a vote (Cats)
def test_vote_cast(client, mock_redis):
    data = {'vote': 'Cats'}
    response = client.post('/', data=data)
    assert response.status_code == 200
    assert b'Cats' in response.data  # Check if the page reflects the vote for Cats
    
    # Verify Redis interaction
    assert mock_redis.rpush.called  # Ensure rpush was called
    args, kwargs = mock_redis.rpush.call_args
    assert args[0] == 'votes'  # Ensure 'votes' list was used
    assert 'Cats' in str(args[1])  # Ensure the vote for Cats was stored in Redis

# Test: Check if voter_id cookie is set
def test_voter_id_cookie(client, mock_redis):
    response = client.get('/')
    assert response.status_code == 200
    assert 'voter_id' in response.headers['Set-Cookie']  # Check if voter_id cookie is set

# Test: Vote submission and check if voter_id cookie persists
def test_voter_id_persists(client, mock_redis):
    # Send initial request to set the voter_id cookie
    response = client.get('/')
    voter_id = response.headers['Set-Cookie'].split(';')[0].split('=')[1]

    # Use the same voter_id in the next request
    data = {'vote': 'Dogs'}
    response = client.post('/', data=data, headers={'Cookie': f'voter_id={voter_id}'})
    
    # Ensure the same voter_id is retained
    assert voter_id in response.headers['Set-Cookie']
    assert b'Dogs' in response.data  # Check if the vote for Dogs is reflected


    
