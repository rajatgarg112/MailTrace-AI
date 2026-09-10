import pytest
from sqlalchemy.exc import IntegrityError
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse


def test_create_user(db_session):
    user = User(email="user@example.com")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    assert user.id is not None
    assert len(user.id) == 36  # UUID v4 string length
    assert user.email == "user@example.com"
    assert user.created_at is not None
    assert user.updated_at is not None


def test_user_email_uniqueness(db_session):
    user1 = User(email="unique@example.com")
    db_session.add(user1)
    db_session.commit()

    user2 = User(email="unique@example.com")
    db_session.add(user2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_user_pydantic_schema_serialization(db_session):
    user = User(email="schema@example.com")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    schema_data = UserResponse.model_validate(user)
    assert schema_data.id == user.id
    assert schema_data.email == "schema@example.com"
    assert schema_data.created_at == user.created_at
    assert schema_data.updated_at == user.updated_at


def test_user_str_repr():
    user = User(id="test-uuid-1234", email="repr@example.com")
    assert repr(user) == "<User(id='test-uuid-1234', email='repr@example.com')>"
