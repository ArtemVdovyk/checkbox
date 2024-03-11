import uuid
from datetime import datetime
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Path,
    Query,
)
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, ConfigDict
from typing import Annotated, List, Dict, Union
from sqlalchemy import String, func
from sqlalchemy.orm import Session

from .auth import get_current_user
from database import SessionLocal
from models import Receipts, Users
from pagination import PagedResponseSchema, PageParams, paginate


router = APIRouter(
    tags=["receipts"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class ReceiptRequest(BaseModel):
    products: List[Dict[str, Union[int, str, float]]]
    payment: Dict[str, Union[int, str, float]]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "products": [
                    {
                        "name": "Bar of chocolate",
                        "price": 10.50,
                        "quantity": 2,
                    },
                    {
                        "name": "Bottle of sparkling water",
                        "price": 5.50,
                        "quantity": 3,
                    }
                ],
                "payment": {
                    "type": "cash/cashless",
                    "amount": 40.00
                }
            }
        }
    )


class ReceiptSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    products: List[Dict[str, Union[int, str, float]]]
    payment: Dict[str, Union[int, str, float]]
    total: float
    rest: float
    created_at: datetime
    owner_id: int


@router.get("/receipts", status_code=status.HTTP_200_OK,
            response_model=PagedResponseSchema[ReceiptSchema])
async def get_all_receipts(user: user_dependency, db: db_dependency,
                           page_params: PageParams = Depends()):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Authentication failed")

    receipts_model = db.query(Receipts).filter(
        Receipts.owner_id == user.get("id")).order_by(Receipts.created_at.desc())

    response = paginate(page_params, receipts_model, ReceiptSchema)

    if not response.results:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Receipts not found")

    return response


@router.get("/receipts/", status_code=status.HTTP_200_OK,
            response_model=PagedResponseSchema[ReceiptSchema])
async def get_receipts_by_payment_type(user: user_dependency, db: db_dependency,
                                       payment_type: str = Query(
                                           pattern="^cash(less)?$"),
                                       page_params: PageParams = Depends()):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Authentication failed")

    receipts_model = db.query(Receipts).filter(Receipts.payment.op("->>")("type").cast(String) == payment_type)\
        .filter(Receipts.owner_id == user.get("id")).order_by(Receipts.created_at.desc())

    response = paginate(page_params, receipts_model, ReceiptSchema)

    if not response.results:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Receipts not found")

    return response


@router.get("/receipts/last_month/", status_code=status.HTTP_200_OK,
            response_model=PagedResponseSchema[ReceiptSchema])
async def get_receipts_created_within_last_month(user: user_dependency,
                                                 db: db_dependency,
                                                 page_params: PageParams = Depends()):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Authentication failed")

    last_month = datetime.now().month - 1
    current_year = datetime.now().year

    receipts_model = db.query(Receipts).filter(
        func.extract('month', Receipts.created_at) == last_month,
        func.extract('year', Receipts.created_at) == current_year)\
        .filter(Receipts.owner_id == user.get("id"))\
        .order_by(Receipts.created_at.desc())

    response = paginate(page_params, receipts_model, ReceiptSchema)

    if not response.results:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Receipts not found")

    return response


@router.get("/receipts/{total_amount}/", status_code=status.HTTP_200_OK,
            response_model=PagedResponseSchema[ReceiptSchema])
async def get_receipts_by_total_amount(user: user_dependency, db: db_dependency,
                                       total_amount: float = Path(gt=0),
                                       page_params: PageParams = Depends()):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Authentication failed")

    receipts_model = db.query(Receipts).filter(Receipts.total >= total_amount)\
        .filter(Receipts.owner_id == user.get("id"))\
        .order_by(Receipts.created_at.desc())

    response = paginate(page_params, receipts_model, ReceiptSchema)

    if not response.results:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Receipts not found")

    return response


@router.get("/receipt/{receipt_id}", status_code=status.HTTP_200_OK)
async def get_receipt_by_id(user: user_dependency, db: db_dependency,
                            receipt_id: str = Path(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Authentication failed")

    receipt_model = db.query(Receipts).filter(Receipts.id == receipt_id)\
        .filter(Receipts.owner_id == user.get("id")).first()

    if not receipt_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Receipt not found")

    return receipt_model


@router.post("/receipt", status_code=status.HTTP_201_CREATED)
async def create_receipt(user: user_dependency, db: db_dependency,
                         receipt_request: ReceiptRequest):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Authentication failed")

    receipt = receipt_request.model_dump()
    total_per_receipt = 0
    for product in receipt["products"]:
        total_per_product = round(product["price"] * product["quantity"], 2)
        total_per_receipt += total_per_product
        product.update({"total": total_per_product})

    receipt.update({
        "total": round(total_per_receipt, 2),
        "rest": round(receipt["payment"]["amount"] - total_per_receipt, 2),
        "created_at": datetime.utcnow()
    })

    receipt_model = Receipts(**receipt, owner_id=user.get("id"))
    db.add(receipt_model)
    db.commit()

    receipt.update({"id": receipt_model.id})

    return receipt


@router.delete("/receipt/{receipt_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_receipt(user: user_dependency, db: db_dependency,
                         receipt_id: str = Path(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Authentication failed")

    receipt_model = db.query(Receipts).filter(Receipts.id == receipt_id)\
        .filter(Receipts.owner_id == user.get("id")).first()

    if not receipt_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Receipt not found")

    db.query(Receipts).filter(Receipts.id == receipt_id)\
        .filter(Receipts.owner_id == user.get("id")).delete()
    db.commit()


@router.get("/receipt/{receipt_id}/text", status_code=status.HTTP_200_OK)
async def get_receipt_text(db: db_dependency,
                           receipt_id: str = Path(
                               pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"),
                           max_characters_per_line: int = Query(default=50, gt=0)):

    receipt_model = db.query(Receipts).filter(
        Receipts.id == receipt_id).first()

    if not receipt_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Receipt not found")

    user_model = db.query(Users).filter(
        Users.id == receipt_model.owner_id).first()

    receipt_issuer_name = f"ФОП {user_model.first_name.upper()} {user_model.last_name.upper()}"
    total = f"{receipt_model.total:.2f}"
    payment_amount = f"{receipt_model.payment['amount']:.2f}"
    payment_type = "Картка" if receipt_model.payment['type'] == "cashless" else "Готівка"
    rest = f"{receipt_model.rest:.2f}"
    receipt_date = receipt_model.created_at.strftime("%d.%m.%Y %H:%M:%S")

    receipt_content = ""
    receipt_content += f"\n{receipt_issuer_name.center(max_characters_per_line)}\n"
    receipt_content += f"{'=' * max_characters_per_line}\n"

    for product in receipt_model.products:
        receipt_content += f"{product['quantity']:.2f} x {product['price']:.2f}\n"

        total_per_product = f"{product['quantity'] * product['price']:.2f}"
        product_name = product['name']
        if len(product_name) >= max_characters_per_line-len(total_per_product):
            product_name_in_words = product_name.split(" ")
            while product_name_in_words:
                name_part = []
                length_of_name_part = 0
                i = 0
                for i in range(len(product_name_in_words)):
                    length_of_name_part += len(product_name_in_words[i])+1
                    if length_of_name_part >= max_characters_per_line-len(total_per_product)-5:
                        receipt_content += f"{(' ').join(name_part)}\n"
                        break

                    name_part.append(product_name_in_words[i])

                    if i == len(product_name_in_words)-1:
                        receipt_content += f"{(' ').join(name_part): <{max_characters_per_line-len(total_per_product)}}{total_per_product}\n"

                product_name_in_words = [
                    word for word in product_name_in_words if word not in name_part]
        else:
            receipt_content += f"{product_name: <{max_characters_per_line-len(total_per_product)}}{total_per_product}\n"

        receipt_content += f"{'-' * max_characters_per_line}\n"

    receipt_content += f"{'=' * max_characters_per_line}\n"
    receipt_content += f"{'СУМА': <{max_characters_per_line-len(total)}}{total}\n"
    receipt_content += f"{payment_type: <{max_characters_per_line - len(payment_amount)}}{payment_amount}\n"
    receipt_content += f"{'Решта': <{max_characters_per_line - len(rest)}}{rest}\n"
    receipt_content += f"{'=' * max_characters_per_line}\n"
    receipt_content += f"{receipt_date.center(max_characters_per_line)}\n"
    receipt_content += f"{'Дякуємо за покупку!'.center(max_characters_per_line)}\n"

    return PlainTextResponse(content=receipt_content)
