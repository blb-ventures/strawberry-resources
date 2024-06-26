import strawberry
import strawberry_django
from strawberry.tools import merge_types
from typing_extensions import Annotated

from strawberry_resources.queries import Query as _Query
from strawberry_resources.types import config
from tests.app.models import Person, Role

from .utils import resource_query


@strawberry_django.type(Role)
class RoleType:
    name: strawberry.auto


@strawberry_django.type(Person)
class PersonType:
    status: strawberry.auto
    name: strawberry.auto
    birthday: Annotated[strawberry.auto, config(label="User Birthday")]
    age: strawberry.auto
    role: Annotated[RoleType, config(label="Role")]


@strawberry_django.input(Person)
class PersonInput:
    status: strawberry.auto
    name: strawberry.auto
    birthday: Annotated[strawberry.auto, config(label="User Birthday")]
    age: strawberry.auto


@strawberry.type
class Query:
    person: PersonType


@strawberry.type
class Mutation:
    @strawberry_django.mutation
    def create_person(self, input: PersonInput) -> PersonType:  # noqa: A002
        ...


schema = strawberry.Schema(
    query=merge_types(
        "Query",
        (
            _Query,
            Query,
        ),
    ),
    mutation=Mutation,
)


def test_query():
    res = schema.execute_sync(resource_query, {"name": "PersonType"})
    assert res.errors is None
    assert res.data == {
        "resource": {
            "fields": [
                {
                    "__typename": "Field",
                    "choices": [
                        {"group": None, "label": "Active", "value": "ACTIVE"},
                        {"group": None, "label": "Inactive", "value": "INACTIVE"},
                    ],
                    "defaultValue": Person.Status.ACTIVE,
                    "filterable": False,
                    "helpText": None,
                    "kind": "STRING",
                    "label": "Status",
                    "multiple": False,
                    "name": "status",
                    "orderable": False,
                    "resource": None,
                    "validation": {
                        "__typename": "StringFieldValidation",
                        "maxLength": 8,
                        "minLength": 1,
                        "required": True,
                    },
                },
                {
                    "__typename": "Field",
                    "choices": None,
                    "defaultValue": None,
                    "filterable": False,
                    "helpText": None,
                    "kind": "STRING",
                    "label": "Name",
                    "multiple": False,
                    "name": "name",
                    "orderable": False,
                    "resource": None,
                    "validation": {
                        "__typename": "StringFieldValidation",
                        "maxLength": 255,
                        "minLength": 1,
                        "required": True,
                    },
                },
                {
                    "__typename": "Field",
                    "choices": None,
                    "defaultValue": None,
                    "filterable": False,
                    "helpText": None,
                    "kind": "DATE",
                    "label": "User Birthday",
                    "multiple": False,
                    "name": "birthday",
                    "orderable": False,
                    "resource": None,
                    "validation": {
                        "__typename": "BaseFieldValidation",
                        "required": False,
                    },
                },
                {
                    "__typename": "Field",
                    "choices": None,
                    "defaultValue": None,
                    "filterable": False,
                    "helpText": None,
                    "kind": "INT",
                    "label": "Age",
                    "multiple": False,
                    "name": "age",
                    "orderable": False,
                    "resource": None,
                    "validation": {
                        "__typename": "BaseFieldValidation",
                        "required": True,
                    },
                },
                {
                    "__typename": "FieldObject",
                    "fields": [
                        {
                            "__typename": "Field",
                            "choices": None,
                            "defaultValue": None,
                            "filterable": False,
                            "helpText": None,
                            "kind": "STRING",
                            "label": "Name",
                            "multiple": False,
                            "name": "name",
                            "orderable": False,
                            "resource": None,
                            "validation": {
                                "__typename": "StringFieldValidation",
                                "maxLength": 255,
                                "minLength": 1,
                                "required": True,
                            },
                        },
                    ],
                    "label": "Role",
                    "name": "role",
                    "objKind": "OBJECT",
                },
            ],
            "name": "PersonType",
        },
    }


def test_query_input_type():
    res = schema.execute_sync(resource_query, {"name": "PersonInput"})
    assert res.errors is None
    assert res.data == {
        "resource": {
            "fields": [
                {
                    "__typename": "Field",
                    "choices": [
                        {"group": None, "label": "Active", "value": "ACTIVE"},
                        {"group": None, "label": "Inactive", "value": "INACTIVE"},
                    ],
                    "defaultValue": Person.Status.ACTIVE,
                    "filterable": False,
                    "helpText": None,
                    "kind": "STRING",
                    "label": "Status",
                    "multiple": False,
                    "name": "status",
                    "orderable": False,
                    "resource": None,
                    "validation": {
                        "__typename": "StringFieldValidation",
                        "maxLength": 8,
                        "minLength": 1,
                        "required": False,
                    },
                },
                {
                    "__typename": "Field",
                    "choices": None,
                    "defaultValue": None,
                    "filterable": False,
                    "helpText": None,
                    "kind": "STRING",
                    "label": "Name",
                    "multiple": False,
                    "name": "name",
                    "orderable": False,
                    "resource": None,
                    "validation": {
                        "__typename": "StringFieldValidation",
                        "maxLength": 255,
                        "minLength": 1,
                        "required": True,
                    },
                },
                {
                    "__typename": "Field",
                    "choices": None,
                    "defaultValue": None,
                    "filterable": False,
                    "helpText": None,
                    "kind": "DATE",
                    "label": "User Birthday",
                    "multiple": False,
                    "name": "birthday",
                    "orderable": False,
                    "resource": None,
                    "validation": {
                        "__typename": "BaseFieldValidation",
                        "required": False,
                    },
                },
                {
                    "__typename": "Field",
                    "choices": None,
                    "defaultValue": None,
                    "filterable": False,
                    "helpText": None,
                    "kind": "INT",
                    "label": "Age",
                    "multiple": False,
                    "name": "age",
                    "orderable": False,
                    "resource": None,
                    "validation": {
                        "__typename": "BaseFieldValidation",
                        "required": True,
                    },
                },
            ],
            "name": "PersonInput",
        },
    }
