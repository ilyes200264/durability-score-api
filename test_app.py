import pytest
import json
from app import app, db, Submission

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # base temporaire
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

def test_score_endpoint(client):
    response = client.post("/score", json={
        "product_name": "Test Bottle",
        "materials": ["plastic"],
        "weight_grams": 300,
        "transport": "air",
        "packaging": "non-recyclable"
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data["product_name"] == "Test Bottle"
    assert "sustainability_score" in data
    assert "rating" in data
    assert isinstance(data["suggestions"], list)

def test_history_endpoint(client):
    client.post("/score", json={
        "product_name": "History Test",
        "materials": ["plastic"],
        "weight_grams": 100,
        "transport": "road",
        "packaging": "non-recyclable"
    })
    response = client.get("/history")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert "product_name" in data[0]

def test_score_summary(client):
    client.post("/score", json={
        "product_name": "Summary 1",
        "materials": ["recycled"],
        "weight_grams": 100,
        "transport": "rail",
        "packaging": "recyclable"
    })
    client.post("/score", json={
        "product_name": "Summary 2",
        "materials": ["plastic"],
        "weight_grams": 800,
        "transport": "air",
        "packaging": "non-recyclable"
    })
    response = client.get("/score-summary")
    assert response.status_code == 200
    data = response.get_json()
    assert "total_products" in data
    assert "average_score" in data
    assert "ratings" in data
    assert "top_issues" in data

def test_missing_field(client):
    response = client.post("/score", json={
        "product_name": "Missing Transport",
        "materials": ["plastic"],
        "weight_grams": 100,
        "packaging": "recyclable"
    })
    assert response.status_code == 400
    data = response.get_json()
    assert "transport" in data["error"]

def test_invalid_type_materials(client):
    response = client.post("/score", json={
        "product_name": "Invalid Materials",
        "materials": "plastic",
        "weight_grams": 300,
        "transport": "road",
        "packaging": "recyclable"
    })
    assert response.status_code == 400
    data = response.get_json()
    assert "materials" in data["error"]

def test_invalid_transport_value(client):
    response = client.post("/score", json={
        "product_name": "Invalid Transport",
        "materials": ["plastic"],
        "weight_grams": 300,
        "transport": "spaceship",
        "packaging": "recyclable"
    })
    assert response.status_code == 400
    data = response.get_json()
    assert "transport" in data["error"]

def test_invalid_packaging_value(client):
    response = client.post("/score", json={
        "product_name": "Invalid Packaging",
        "materials": ["plastic"],
        "weight_grams": 300,
        "transport": "road",
        "packaging": "unwrapped"
    })
    assert response.status_code == 400
    data = response.get_json()
    assert "packaging" in data["error"]
