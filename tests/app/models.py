from django.db import models
from strawberry_django_plus import gql
from typing_extensions import Annotated

from strawberry_resources.types import config


class Role(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name="Name",
    )


class Person(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name="Name",
    )
    birthday = models.DateField(
        verbose_name="Birthday",
        null=True,
        default=None,
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        verbose_name="Role",
        null=True,
        default=None,
    )

    @gql.model_property
    def age(self) -> Annotated[int, config(label="Age")]:  # pragma: nocover
        ...
