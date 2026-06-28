from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session


import models
import schemas
import crud
from database import engine, get_db
from auth_utils import verify_password, create_token
from dependencies import get_current_user

models.Base.metadata.create_all(bind=engine)

app = FastAPI()




@app.post("/api/auth/signup", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    return crud.create_user(db=user, user=user)


@app.post("/api/auth/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, email=form_data.username)
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_token(data={"sub": user.email}, token_type="access")
    refresh_token = create_token(data={"sub": user.email}, token_type="refresh")

    crud.update_refresh_token(db, user, refresh_token)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}




@app.post("/api/contacts", response_model=schemas.Contact, status_code=status.HTTP_201_CREATED)
def create_contact(
        contact: schemas.ContactCreate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    return crud.create_contact(db=db, contact=contact, user_id=current_user.id)


@app.get("/api/contacts", response_model=list[schemas.Contact])
def read_contacts(
        skip: int = 0, limit: int = 100,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    return crud.get_contacts(db, user_id=current_user.id, skip=skip, limit=limit)


@app.delete("/api/contacts/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contact(
        contact_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    db_contact = crud.delete_contact(db, contact_id=contact_id, user_id=current_user.id)
    if db_contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return None