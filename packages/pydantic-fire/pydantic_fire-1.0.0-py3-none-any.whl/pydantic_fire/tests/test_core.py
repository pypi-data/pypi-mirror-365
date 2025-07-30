import pytest
from datetime import datetime
from pydantic import Field as PydanticField

from ..core.base import Document, Collection
from ..core.fields import Field
from ..core.exceptions import ValidationError
from ..core.types import GeoPoint, Vector

# --- Test Schema Definitions ---

class Profile(Document):
    """A simple sub-collection document."""
    class Fields:
        bio = Field(str, required=False)
        avatar_url = Field(str, required=False)

class Profiles(Collection):
    """A sub-collection of profiles."""
    _document_class = Profile
    _path_template = "profiles"

class User(Document):
    """A root-level document with various field types and a sub-collection."""

    class Fields:
        username = Field(str, required=True)
        email = Field(str, required=True)
        age = Field(int, required=False)
        created_at = Field(datetime, auto_now_add=True)
        last_login = Field(datetime, required=False, default=None)
        location = Field(GeoPoint, required=False)
        embedding = Field(Vector, required=False)
        # A field with extra pydantic configurations
        rating = Field(float, required=False, ge=0, le=5)

    class Subcollections:
        profiles = Profiles

class Users(Collection):
    """A root-level collection of users."""
    _path_template = "users"
    _document_class = User

# --- Test Cases ---

def test_document_schema_creation():
    """Tests that the Pydantic model and subcollections are created correctly."""
    assert hasattr(User, '_pydantic_model')
    assert 'username' in User._pydantic_model.model_fields
    assert 'email' in User._pydantic_model.model_fields
    assert User._pydantic_model.model_fields['username'].is_required()
    assert not User._pydantic_model.model_fields['age'].is_required()
    
    assert hasattr(User, '_subcollections')
    assert 'profiles' in User._subcollections
    assert User._subcollections['profiles'] == Profiles

def test_path_generation():
    """Tests the path generation for collections, documents, and sub-collections."""
    users_collection = Users()
    assert users_collection.path == "users"

    user_doc = users_collection.doc("user123")
    assert isinstance(user_doc, User)
    assert user_doc.path == "users/user123"

    profile_collection = user_doc.collection("profiles")
    assert isinstance(profile_collection, Profiles)
    # Note: The subcollection path is dynamically built and includes the parent path.
    # The template for the collection itself doesn't contain the parent path.
    assert profile_collection.path == "users/user123/profiles"

    profile_doc = profile_collection.doc("profile456")
    assert isinstance(profile_doc, Profile)
    assert profile_doc.path == "users/user123/profiles/profile456"

def test_full_validation_success():
    """Tests successful validation of a complete data dictionary."""
    user_data = {
        "username": "johndoe",
        "email": "john.doe@example.com",
        "age": 30
    }
    validated_data = User.validate(user_data)
    assert validated_data.username == "johndoe"  # type: ignore
    assert validated_data.age == 30  # type: ignore

def test_full_validation_failure():
    """Tests that validation fails when required fields are missing."""
    with pytest.raises(ValidationError):
        User.validate({"age": 30}) # Missing username and email

def test_pydantic_extra_args_validation():
    """Tests validation with extra pydantic arguments like 'ge' and 'le'."""
    # Success case
    User.validate({"username": "test", "email": "test@test.com", "rating": 4.5})
    
    # Failure case
    with pytest.raises(ValidationError):
        User.validate({"username": "test_fail", "email": "fail@example.com", "rating": 6.0})

def test_serialization():
    """Tests the serialization of a validated model to a dictionary."""
    user_data = {
        "username": "johndoe",
        "email": "john.doe@example.com",
        "age": 30
    }
    serialized_data = User.serialize(user_data)
    assert serialized_data['username'] == "johndoe"
    assert 'created_at' in serialized_data # from auto_now_add

def test_partial_validation():
    """Tests partial validation for updates."""
    partial_data = {"age": 31, "last_login": datetime.now()}
    validated_partial = User.validate_partial(partial_data)
    assert validated_partial['age'] == 31
    assert 'last_login' in validated_partial

    # Test with an invalid field, which should be ignored
    invalid_partial = {"invalid_field": "some_value", "age": 32}
    validated_invalid = User.validate_partial(invalid_partial)
    assert "invalid_field" not in validated_invalid
    assert validated_invalid['age'] == 32

def test_field_getters():
    """Tests the helper methods for inspecting schema fields."""
    field_names = User.get_field_names()
    assert 'username' in field_names
    assert 'created_at' in field_names

    username_info = User.get_field_info('username')
    assert username_info is not None
    assert username_info['type'] == 'str'
    assert username_info['required'] is True

    age_info = User.get_field_info('age')
    assert age_info is not None
    assert age_info['type'] == 'int'
    assert age_info['required'] is False

    assert User.get_field_info('non_existent_field') is None

def test_field_auto_now_add():
    """Tests the auto_now_add functionality for datetime fields."""
    user_data = {
        "username": "testuser",
        "email": "test@example.com"
    }
    validated_data = User.validate(user_data)
    assert isinstance(validated_data.created_at, datetime)  # type: ignore

def test_field_auto_now_add_type_error():
    """Tests that auto_now_add on a non-datetime field raises an error."""
    with pytest.raises(TypeError):
        class InvalidDoc(Document):
            class Fields:
                bad_field = Field(str, auto_now_add=True)

def test_collection_without_document_class():
    """Tests that accessing a doc on a collection without a document class fails."""
    class BadCollection(Collection):
        _path_template = "bad"

    with pytest.raises(TypeError):
        BadCollection().doc("some_id")
