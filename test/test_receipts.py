from datetime import datetime
from dateutil.relativedelta import relativedelta
from fastapi import status
import copy
import re

from pagination import PageParams
from models import Receipts
from routers.receipts import get_db, get_current_user
from .utils import *


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

receipt_response = {
    "id": "daafa0dc-06bb-40fd-8472-c8fa6ed47a43",
    "products": [
        {
            "name": "Bar of chocolate",
            "price": 10.38,
            "quantity": 2.0,
            "total": 20.76
        },
        {
            "name": "Bottle of sparkling water",
            "price": 5.65,
            "quantity": 3.0,
            "total": 16.95
        }
    ],
    "payment": {"type": "cash", "amount": 40.00},
    "total": 37.71,
    "rest": 2.29,
    "created_at": "2024-03-06T17:29:59.073344",
    "owner_id": 1
}

receipts_response = {
    "total_results": 1,
    "page": 1,
    "pages": 1,
    "size": 10,
    "results": [receipt_response]
}

page_params = PageParams(page=1, size=10)


def test_get_all_receipts_authenticated(test_receipt):
    query_params = {
        "page": page_params.page,
        "size": page_params.size
    }
    response = client.get("/receipts", params=query_params)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == receipts_response


def test_get_receipts_by_payment_type_authenticated_success(test_receipt):
    query_params = {
        "payment_type": "cash",
        "page": page_params.page,
        "size": page_params.size
    }
    response = client.get("/receipts/", params=query_params)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == receipts_response


def test_get_receipts_by_payment_type_authenticated_not_found(test_receipt):
    query_params = {
        "payment_type": "cashless",
        "page": page_params.page,
        "size": page_params.size
    }
    response = client.get("/receipts/", params=query_params)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Receipts not found"}


def test_get_receipts_created_within_last_month_authenticated_success(test_receipt):
    receipt_date = datetime.strptime(
        receipts_response["results"][0]["created_at"], "%Y-%m-%dT%H:%M:%S.%f")

    receipt_date_last_month = receipt_date - relativedelta(months=1)

    receipts_response_copy = copy.deepcopy(receipts_response)
    receipts_response_copy["results"][0]["id"] = "daafa0dc-1111-40fd-8472-c8fa6ed47a43"
    receipts_response_copy["results"][0]["created_at"] = receipt_date_last_month.strftime(
        "%Y-%m-%dT%H:%M:%S.%f")

    db = TestingSessionLocal()
    new_receipt = Receipts(
        id=uuid.UUID("daafa0dc-1111-40fd-8472-c8fa6ed47a43"),
        products=[
            {
                "name": "Bar of chocolate",
                "price": 10.38,
                "quantity": 2.0,
                "total": 20.76
            },
            {
                "name": "Bottle of sparkling water",
                "price": 5.65,
                "quantity": 3.0,
                "total": 16.95
            }
        ],
        payment={"type": "cash", "amount": 40.00},
        total=37.71,
        rest=2.29,
        created_at=receipt_date_last_month.strftime("%Y-%m-%dT%H:%M:%S.%f"),
        owner_id=1
    )
    db.add(new_receipt)
    db.commit()

    query_params = {
        "page": page_params.page,
        "size": page_params.size
    }
    response = client.get("/receipts/last_month", params=query_params)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == receipts_response_copy


def test_get_receipts_created_within_last_month_authenticated_not_found(test_receipt):
    query_params = {
        "page": page_params.page,
        "size": page_params.size
    }
    response = client.get("/receipts/last_month", params=query_params)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Receipts not found"}


def test_get_receipts_by_total_amount_authenticated_success(test_receipt):
    query_params = {
        "page": page_params.page,
        "size": page_params.size
    }
    response = client.get("/receipts/36/", params=query_params)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == receipts_response


def test_get_receipts_by_total_amount_authenticated_not_found(test_receipt):
    query_params = {
        "page": page_params.page,
        "size": page_params.size
    }
    response = client.get("/receipts/45/", params=query_params)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Receipts not found"}


def test_get_receipt_by_id_authenticated_success(test_receipt):
    response = client.get("/receipt/daafa0dc-06bb-40fd-8472-c8fa6ed47a43")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == receipt_response


def test_get_receipt_by_id_authenticated_not_found(test_receipt):
    response = client.get("/receipt/11111111-1111-1111-1111-111111111111")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Receipt not found"}


def test_create_receipt(test_receipt):
    request_data = {
        "products": [
            {
                "name": "Bar of chocolate",
                "price": 20.00,
                "quantity": 2,
            },
            {
                "name": "Bottle of sparkling water",
                "price": 5.00,
                "quantity": 3,
            }
        ],
        "payment": {
            "type": "cash",
            "amount": 60.00
        }
    }
    receipt_response_products = [
        {
            "name": "Bar of chocolate",
            "price": 20.00,
            "quantity": 2.0,
            "total": 40.00
        },
        {
            "name": "Bottle of sparkling water",
            "price": 5.00,
            "quantity": 3.0,
            "total": 15.00
        }
    ]
    receipt_response_payment = {"type": "cash", "amount": 60.00}
    id_pattern = "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"

    response = client.post("/receipt", json=request_data)
    assert response.status_code == status.HTTP_201_CREATED
    assert re.match(id_pattern, response.json()["id"]) is not None
    assert response.json()["products"] == receipt_response_products
    assert response.json()["payment"] == receipt_response_payment

    db = TestingSessionLocal()
    model = db.query(Receipts).filter(Receipts.total == 55).first()
    assert re.match(id_pattern, str(model.id)) is not None
    assert model.products == receipt_response_products
    assert model.payment == receipt_response_payment
    assert model.total == 55
    assert model.rest == 5


def test_delete_receipt_success(test_receipt):
    response = client.delete("/receipt/daafa0dc-06bb-40fd-8472-c8fa6ed47a43")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    model = db.query(Receipts).filter(
        Receipts.id == "daafa0dc-06bb-40fd-8472-c8fa6ed47a43").first()
    assert model is None


def test_delete_receipt_not_found(test_receipt):
    response = client.delete("/receipt/11111111-1111-1111-1111-111111111111")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Receipt not found"}


def test_get_receipt_text(test_receipt):
    query_params = {
        "max_characters_per_line": 50
    }
    response = client.get(
        "/receipt/daafa0dc-06bb-40fd-8472-c8fa6ed47a43/text",
        params=query_params)
    assert response.status_code == status.HTTP_200_OK
    assert response.text.strip() != ""


def test_get_receipt_text_not_found(test_receipt):
    query_params = {
        "max_characters_per_line": 50
    }
    response = client.get(
        "/receipt/11111111-1111-1111-1111-111111111111/text",
        params=query_params)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Receipt not found"}
