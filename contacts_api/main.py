from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

import models, schemas, crud
from database import engine, Base, SessionLocal

Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/contacts", response_model=schemas.Contact)
def create(contact: schemas.ContactCreate, db: Session = Depends(get_db)):
    return crud.create_contact(db, contact)


@app.get("/contacts")
def read_all(db: Session = Depends(get_db)):
    return crud.get_contacts(db)


@app.get("/contacts/{contact_id}")
def read_one(contact_id: int, db: Session = Depends(get_db)):
    return crud.get_contact(db, contact_id)


@app.delete("/contacts/{contact_id}")
def delete(contact_id: int, db: Session = Depends(get_db)):
    return crud.delete_contact(db, contact_id)