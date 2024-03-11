from dotenv import load_dotenv
from fastapi import FastAPI, status

from database import engine
from models import Base
from routers import admin, auth, receipts, users


load_dotenv()

app = FastAPI()

Base.metadata.create_all(bind=engine)


@app.get("/healthy", status_code=status.HTTP_200_OK)
def health_check():
    return {"status": "Healthy"}


app.include_router(admin.router)
app.include_router(auth.router)
app.include_router(receipts.router)
app.include_router(users.router)
