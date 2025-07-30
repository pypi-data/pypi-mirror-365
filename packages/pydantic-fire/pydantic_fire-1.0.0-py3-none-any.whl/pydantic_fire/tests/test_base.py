"""
Test cases for the base Firestore schema functionality.

This module contains tests for the core Firestore schema classes:
- FirestoreNode
- Document
- Collection

Tests cover:
- Path template handling
- Document validation
- Field inheritance
- Subcollection management
- Error conditions
"""

import unittest
from datetime import datetime
from typing import TypedDict, Callable

from ..core.base import Document, Collection, DocumentType, SubcollectionType
from ..core.fields import Field
from ..core.exceptions import ValidationError


# --- Test Schemas ---

class UserProfileDocument(Document):
    _path_template = "profile" # This is a static document, so path is fixed
    class Fields:
        bio = Field(str)

class UserProfileCollection(Collection):
    _path_template = "profiles" # Path for the collection itself
    PROFILE: UserProfileDocument # The static document accessor
    class DocumentTypes:
        # Define the static document using DocumentType
        PROFILE = DocumentType(UserProfileDocument, is_static=True, static_id="user_profile")

class UserDocument(Document):
    _path_template = "{user_id}"
    PROFILE: UserProfileCollection # Type hint for the dynamic subcollection accessor
    class PathParams(TypedDict):
        user_id: str
    class Fields:
        name = Field(str, required=True)
    class Subcollections:
        # Subcollections should point to Collection classes
        PROFILE = SubcollectionType(UserProfileCollection)

class UsersCollection(Collection):
    _path_template = "users"
    USER: Callable[..., UserDocument]
    class DocumentTypes:
        USER = DocumentType(UserDocument)

# --- Deep Nesting Schemas ---

class ProjectDocument(Document):
    _path_template = "{project_id}"
    class PathParams(TypedDict):
        project_id: str

class ProjectsCollection(Collection):
    _path_template = "projects"
    PROJECT: Callable[..., ProjectDocument]
    class DocumentTypes:
        PROJECT = DocumentType(ProjectDocument)

class TeamDocument(Document):
    _path_template = "{team_id}"
    PROJECTS: ProjectsCollection # Type hint for the dynamic subcollection accessor
    class PathParams(TypedDict):
        team_id: str
    class Subcollections:
        PROJECTS = SubcollectionType(ProjectsCollection)

class TeamsCollection(Collection):
    _path_template = "teams"
    TEAM: Callable[..., TeamDocument]
    class DocumentTypes:
        TEAM = DocumentType(TeamDocument)

class OrgDocument(Document):
    _path_template = "{org_id}"
    TEAMS: TeamsCollection # Type hint for the dynamic subcollection accessor
    class PathParams(TypedDict):
        org_id: str
    class Subcollections:
        TEAMS = SubcollectionType(TeamsCollection)

class OrgsCollection(Collection):
    _path_template = "orgs"
    ORG: Callable[..., OrgDocument]
    class DocumentTypes:
        ORG = DocumentType(OrgDocument)


# --- Test Cases ---

class TestDocumentValidation(unittest.TestCase):
    """Tests for document field validation and Pydantic model generation."""

    def test_required_fields(self):
        with self.assertRaises(ValidationError):
            UserDocument.validate({"name": None})
        with self.assertRaises(ValidationError):
            UserDocument.validate({}) # Missing name
        validated = UserDocument.validate({"name": "John"})
        self.assertEqual(validated.model_dump()["name"], "John")

    def test_partial_update_validation(self):
        class TestDoc(Document):
            class Fields:
                name = Field(str, required=True)
                age = Field(int)
        
        # Should pass, only validating 'age'
        validated = TestDoc.validate_partial({"age": 42}, fields_to_update=["age"])
        self.assertEqual(validated, {"age": 42})

        # Should fail, 'name' is required but not being updated
        with self.assertRaises(ValidationError):
            TestDoc.validate_partial({"age": "invalid"}, fields_to_update=["age"])


class TestPathGeneration(unittest.TestCase):
    """Tests for static and dynamic path generation."""

    def test_collection_path(self):
        self.assertEqual(UsersCollection.path(), "users")

    def test_document_path_from_class(self):
        user_doc = UsersCollection.USER(doc_id="user123")
        self.assertEqual(user_doc.instance_path, "users/user123")

    def test_subcollection_path(self):
        user_doc = UsersCollection.USER(doc_id="user123")
        profile_coll = user_doc.PROFILE
        self.assertEqual(profile_coll.instance_path, "users/user123/profiles")

    def test_static_document_in_subcollection_path(self):
        user_doc = UsersCollection.USER(doc_id="user123")
        # Access the subcollection first, then the static doc
        profile_doc = user_doc.PROFILE.PROFILE
        self.assertEqual(profile_doc.instance_path, "users/user123/profiles/user_profile")

    def test_path_validation(self):
        class DocWithParams(Document):
            _path_template = "{param1}/{param2}"
            class PathParams(TypedDict):
                param1: str
                param2: int
        with self.assertRaises(ValidationError):
            DocWithParams.path(param1="hello", param2="world") # bad type
        path = DocWithParams.path(param1="hello", param2=123)
        self.assertEqual(path, "hello/123")

    def test_document_path_from_instance(self):
        users = UsersCollection(base_path="")
        user_doc = users.USER(doc_id="user456")
        self.assertEqual(user_doc.instance_path, "/users/user456")


class TestDeepNesting(unittest.TestCase):
    """Tests path generation for deeply nested structures (4+ levels)."""

    def test_six_level_path_generation(self):
        """Tests orgs/{org_id}/teams/{team_id}/projects/{project_id}"""
        # Path generation from class
        org_doc_path = OrgsCollection.ORG(doc_id="my-org").instance_path
        self.assertEqual(org_doc_path, "orgs/my-org")

        # Path generation from instance
        orgs = OrgsCollection(base_path="")
        org_doc = orgs.ORG(doc_id="my-org")
        self.assertEqual(org_doc.instance_path, "/orgs/my-org")

        teams_coll = org_doc.TEAMS
        team_doc = teams_coll.TEAM(doc_id="dev-team")
        self.assertEqual(team_doc.instance_path, "/orgs/my-org/teams/dev-team")

        projects_coll = team_doc.PROJECTS
        project_doc = projects_coll.PROJECT(doc_id="skunkworks")
        self.assertEqual(project_doc.instance_path, "/orgs/my-org/teams/dev-team/projects/skunkworks")


if __name__ == "__main__":
    unittest.main()
