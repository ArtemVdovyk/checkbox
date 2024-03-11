from fastapi import APIRouter, Depends, HTTPException, status, Path
from typing import Annotated
from sqlalchemy.orm import Session

from .auth import get_current_user
from .receipts import ReceiptSchema
from database import SessionLocal
from models import Receipts
from pagination import PagedResponseSchema, PageParams, paginate


router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/receipts", status_code=status.HTTP_200_OK,
            response_model=PagedResponseSchema[ReceiptSchema])
async def get_all_receipts(user: user_dependency, db: db_dependency,
                           page_params: PageParams = Depends()):
    if user is None or user.get("is_admin") != True:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Authentication failed")

    receipts_model = db.query(Receipts).order_by(Receipts.created_at.desc())

    response = paginate(page_params, receipts_model, ReceiptSchema)

    if not response.results:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Receipts not found")

    return response


@router.delete("/receipt/{receipt_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_receipt(user: user_dependency, db: db_dependency,
                         receipt_id: str = Path(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")):
    if user is None or user.get("is_admin") != True:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Authentication failed")

    receipt_model = db.query(Receipts).filter(
        Receipts.id == receipt_id).first()

    if not receipt_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Receipt not found")

    db.query(Receipts).filter(Receipts.id == receipt_id).delete()
    db.commit()
