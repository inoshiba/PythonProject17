import unittest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
import crud
import models
import schemas

class TestCRUD(unittest.TestCase):
    def setUp(self):
        self.db = MagicMock(spec=Session)
        self.user_id = 1
        self.mock_user = models.User(id=1, email="test@mail.com", password="hashed_password")

    def test_get_user_by_email(self):
        self.db.query().filter().first.return_value = self.mock_user
        result = crud.get_user_by_email(self.db, "test@mail.com")
        self.assertEqual(result, self.mock_user)

    def test_create_user(self):
        user_data = schemas.UserCreate(email="new@mail.com", password="password123")
        self.db.refresh.side_effect = lambda x: setattr(x, "id", 2)
        result = crud.create_user(self.db, user_data)
        self.assertEqual(result.email, "new@mail.com")
        self.db.add.assert_called_once()

    def test_update_refresh_token(self):
        crud.update_refresh_token(self.db, self.mock_user, "new_token")
        self.assertEqual(self.mock_user.refresh_token, "new_token")

    def test_get_contacts(self):
        contacts = [models.Contact(id=1, first_name="A"), models.Contact(id=2, first_name="B")]
        self.db.query().filter().offset().limit().all.return_value = contacts
        result = crud.get_contacts(self.db, user_id=self.user_id)
        self.assertEqual(len(result), 2)

    def test_get_contact_found(self):
        contact = models.Contact(id=1, first_name="John", owner_id=self.user_id)
        self.db.query().filter().first.return_value = contact
        result = crud.get_contact(self.db, contact_id=1, user_id=self.user_id)
        self.assertEqual(result, contact)

    def test_get_contact_not_found(self):
        self.db.query().filter().first.return_value = None
        result = crud.get_contact(self.db, contact_id=999, user_id=self.user_id)
        self.assertIsNone(result)

    def test_update_contact_found(self):
        contact = models.Contact(id=1, first_name="Old", owner_id=self.user_id)
        self.db.query().filter().first.return_value = contact
        contact_update = schemas.ContactCreate(
            first_name="New", last_name="Doe", email="j@mail.com", phone="123", birthday="2000-01-01"
        )
        result = crud.update_contact(self.db, 1, contact_update, self.user_id)
        self.assertEqual(result.first_name, "New")

    def test_update_contact_not_found(self):
        self.db.query().filter().first.return_value = None
        contact_update = schemas.ContactCreate(
            first_name="New", last_name="Doe", email="j@mail.com", phone="123", birthday="2000-01-01"
        )
        result = crud.update_contact(self.db, 999, contact_update, self.user_id)
        self.assertIsNone(result)

    def test_delete_contact_found(self):
        contact = models.Contact(id=1, first_name="To Delete", owner_id=self.user_id)
        self.db.query().filter().first.return_value = contact
        result = crud.delete_contact(self.db, 1, self.user_id)
        self.db.delete.assert_called_once_with(contact)

    def test_delete_contact_not_found(self):
        self.db.query().filter().first.return_value = None
        result = crud.delete_contact(self.db, 999, self.user_id)
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()