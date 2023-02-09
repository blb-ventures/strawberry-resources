from django.db import models
from django.utils.translation import gettext_lazy as _
from django_choices_field import TextChoicesField
from strawberry_django_plus import gql
from typing_extensions import Annotated

from strawberry_resources.types import config


class Role(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name="Name",
    )


class Person(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", _("Active")
        INACTIVE = "INACTIVE", _("Inactive")

    status = TextChoicesField(
        verbose_name="Status",
        help_text="The current status for the user",
        choices_enum=Status,
        default=Status.ACTIVE,
    )
    name = models.CharField(
        max_length=255,
        verbose_name="Name",
    )
    birthday = models.DateField(
        verbose_name="Birthday",
        help_text="When the user was born",
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
