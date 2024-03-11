from fastapi import status

from pagination import PageParams
from routers.admin import get_db, get_current_user
from .utils import *


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

page_params = PageParams(page=1, size=10)


def test_admin_get_all_receipts_authenticated(test_receipt):
    query_params = {
        "page": page_params.page,
        "size": page_params.size
    }
    response = client.get("/admin/receipts", params=query_params)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "total_results": 1,
        "page": 1,
        "pages": 1,
        "size": 10,
        "results": [
            {"id": "daafa0dc-06bb-40fd-8472-c8fa6ed47a43",
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
             "owner_id": 1}
        ]
    }


def test_admin_delete_receipt(test_receipt):
    response = client.delete(
        "/admin/receipt/daafa0dc-06bb-40fd-8472-c8fa6ed47a43")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    model = db.query(Receipts).filter(
        Receipts.id == "daafa0dc-06bb-40fd-8472-c8fa6ed47a43").first()
    assert model is None


def test_admin_delete_receipt_not_found(test_receipt):
    response = client.delete(
        "/admin/receipt/11111111-1111-1111-1111-111111111111")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
        "detail": "Receipt not found"}
