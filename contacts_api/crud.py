"""
Module for CRUD operations on Users and Contacts.
Contains functions to interact with the database using SQLAlchemy.
"""

from sqlalchemy.orm import Session
import models
import schemas
from auth_utils import get_password_hash

def get_user_by_email(db: Session, email: str):
    """
    Retrieve a user from the database by their email address.

    :param db: Database session.
    :param email: The email address to search for.
    :return: User object if found, else None.
    """
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    """
    Create a new user in the database with a hashed password.

    :param db: Database session.
    :param user: User schema containing email and password.
    :return: The newly created User object.
    """
    hashed_password = get_password_hash(user.password)
    db_user = models.User(email=user.email, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_refresh_token(db: Session, user: models.User, token: str | None):
    """
    Update the refresh token for a specific user.

    :param db: Database session.
    :param user: The User object to update.
    :param token: The new refresh token string or None to clear.
    """
    user.refresh_token = token
    db.commit()

def get_contacts(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    """
    Get a list of contacts belonging to a specific user.

    :param db: Database session.
    :param user_id: ID of the user who owns the contacts.
    :param skip: Number of records to skip (for pagination).
    :param limit: Maximum number of records to return.
    :return: List of Contact objects.
    """
    return db.query(models.Contact).filter(models.Contact.owner_id == user_id).offset(skip).limit(limit).all()

def get_contact(db: Session, contact_id: int, user_id: int):
    """
    Get a single contact by its ID and owner's ID.

    :param db: Database session.
    :param contact_id: ID of the contact.
    :param user_id: ID of the user who owns the contact.
    :return: Contact object if found, else None.
    """
    return db.query(models.Contact).filter(models.Contact.id == contact_id, models.Contact.owner_id == user_id).first()

def create_contact(db: Session, contact: schemas.ContactCreate, user_id: int):
    """
    Create a new contact for a specific user.

    :param db: Database session.
    :param contact: Contact data schema.
    :param user_id: ID of the user creating the contact.
    :return: The newly created Contact object.
    """
    db_contact = models.Contact(**contact.model_dump(), owner_id=user_id)
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact

def update_contact(db: Session, contact_id: int, contact_update: schemas.ContactCreate, user_id: int):
    """
    Update an existing contact's details.

    :param db: Database session.
    :param contact_id: ID of the contact to update.
    :param contact_update: New contact data schema.
    :param user_id: ID of the user who owns the contact.
    :return: Updated Contact object if found, else None.
    """
    db_contact = get_contact(db, contact_id, user_id)
    if db_contact:
        for key, value in contact_update.model_dump().items():
            setattr(db_contact, key, value)
        db.commit()
        db.refresh(db_contact)
    return db_contact

def delete_contact(db: Session, contact_id: int, user_id: int):
    """
    Delete a contact from the database.

    :param db: Database session.
    :param contact_id: ID of the contact to delete.
    :param user_id: ID of the user who owns the contact.
    :return: Deleted Contact object if found, else None.
    """
    db_contact = get_contact(db, contact_id, user_id)
    if db_contact:
        db.delete(db_contact)
        db.commit()
    return db_contact