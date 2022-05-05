import pytest
from bigfastapi.models import product_models
from sqlalchemy import func
from main import app


first_product = {
                "name": "product1",
                "description": "this is the first product",
                "price": 150,
                "images": "No images",
                "discount": 5,
                "business_id": "test"}

update_product = {
                "name": "updated product",
                "description": "this is the updated product",
                "price": 150,
                "images": "No images",
                "discount": 5,
                "business_id": "test"}

def test_create_product(authorized_client, test_user):
    response = authorized_client.post("/product", json=first_product)
    assert response.status_code == 201
    assert response.json().get("name") == "product1"

def test_unauthorized_client_cannot_create_product(client, test_user):
    response = client.post("/product", json=first_product)
    assert response.status_code == 401


def test_price_history_added_when_product_added(authorized_client, test_user, session):
    response = authorized_client.post("/product", json=first_product)
    record = session.query(product_models.PriceHistory).filter(product_models.PriceHistory.product_id == response.json().get('id')).first()
    assert record

def test_get_business_products(client, test_products):
    response = client.get(f"/product/{test_products[0].business_id}")
    assert response.status_code == 200
    assert len(response.json()) == 3


def test_get_product(client, test_products):
    response = client.get(f"/product/{test_products[0].business_id}/{test_products[0].id}")
    assert response.status_code == 200
    assert response.json().get('id') == test_products[0].id


def test_update_product(authorized_client, test_products):
    business_id = test_products[0].business_id
    product_id = test_products[0].id
    response = authorized_client.put(f'/product/{business_id}/{product_id}', json=update_product)
    assert response.status_code == 200

def test_unauthorized_client_cannot_update_product(client, test_products):
    business_id = test_products[0].business_id
    product_id = test_products[0].id
    response = client.put(f'/product/{business_id}/{product_id}', json=update_product)
    assert response.status_code == 401

def test_delete_product(authorized_client, test_products):
    business_id = test_products[0].business_id
    product_id = test_products[0].id
    response = authorized_client.delete(f'/product/{business_id}/{product_id}')
    assert response.status_code == 200

def test_unauthorized_client_cannot_delete_product(client, test_products):
    business_id = test_products[0].business_id
    product_id = test_products[0].id
    response = client.delete(f'/product/{business_id}/{product_id}')
    assert response.status_code == 401









