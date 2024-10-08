import dataclasses
import functools
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Optional,
    Type,
    TypeVar,
    Union,
    cast,
)

from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.db.models.fields import NOT_PROVIDED
from strawberry import UNSET
from strawberry.scalars import JSON
from strawberry.types import has_object_definition
from strawberry.types.base import StrawberryOptional, WithStrawberryObjectDefinition
from strawberry_django.fields.types import (
    DjangoFileType,
    DjangoImageType,
    resolve_model_field_name,
)
from strawberry_django.utils.typing import get_django_definition
from typing_extensions import Annotated, get_args, get_origin

from strawberry_resources.types import (
    FieldObjectKind,
    FieldObjectOptions,
    FieldOrFieldObjectOptions,
)

from .base import StrawberryResourceIntegration

# Geos might not be installed
try:
    from django.contrib.gis.db.models.fields import PointField, PolygonField
except (ImportError, ImproperlyConfigured):
    PointField = None
    PolygonField = None

# phonenumbers might not be installed
try:
    from phonenumber_field.modelfields import PhoneNumberField
except ImportError:
    PhoneNumberField = None

# strawberry-django-plus might not be installed
try:
    from strawberry_django.descriptors import ModelProperty
    from strawberry_django.fields.types import K, ListInput
except ImportError:
    ModelProperty = None
    ListInput = None
    K = None

if TYPE_CHECKING:
    from strawberry.types.field import StrawberryField

    from strawberry_resources.types import FieldKind

# Try to use the smaller/faster cache decorator if available
try:
    _cache = functools.cache  # type:ignore
except AttributeError:  # pragma:nocover
    _cache = functools.lru_cache


@_cache
def _get_model_field(
    model: Type[models.Model],
    field: str,
) -> Optional[Union[models.Field, models.ForeignObjectRel]]:
    meta = model._meta
    for f in meta.get_fields():
        name = cast(str, resolve_model_field_name(f, is_input=False, is_filter=False))
        if name == field:
            return f

    return None


def get_extra_mappings() -> Dict[type, "FieldKind"]:
    from strawberry_resources.types import FieldKind

    return {
        DjangoImageType: FieldKind.IMAGE,
        DjangoFileType: FieldKind.FILE,
    }


def get_field_options(
    origin: Type[WithStrawberryObjectDefinition],
    field: "StrawberryField",
    resolved_type: type,
    is_list: bool,
) -> FieldOrFieldObjectOptions:
    from strawberry_resources.types import (
        DecimalFieldValidation,
        FieldChoice,
        FieldKind,
        FieldOptions,
        FieldOptionsConfig,
        HiddenField,
        HiddenFieldError,
        StringFieldValidation,
    )

    options: FieldOptions = {}

    if (dj_type := get_django_definition(origin)) is not None:
        model = dj_type.model
        model_attr = getattr(model, field.name, None)
    else:
        model = None
        model_attr = None

    # Try to populate options from the model property
    if (
        ModelProperty is not None
        and model_attr is not None
        and isinstance(model_attr, ModelProperty)
        and (
            get_origin(annotation := model_attr.func.__annotations__.get("return"))
            is Annotated
        )
    ):
        for opt in get_args(annotation)[1:]:
            if isinstance(opt, HiddenField):
                raise HiddenFieldError

            if not isinstance(opt, FieldOptionsConfig):
                continue

            options.update(opt.options)

    dj_field = _get_model_field(model, field.name) if model is not None else None

    if has_object_definition(resolved_type):
        field_obj_options: FieldObjectOptions = {}

        assert isinstance(resolved_type, type)
        if ListInput is not None and issubclass(resolved_type, ListInput):
            assert isinstance(K, TypeVar)
            field_obj_options["obj_kind"] = FieldObjectKind.LIST_INPUT

        label = options.get("label")
        if label is None and dj_field is not None:
            label = getattr(dj_field, "verbose_name", None)
        if label is not None:
            field_obj_options["label"] = label

        return field_obj_options

    choices: Optional[List[FieldChoice]] = None
    default_value = (
        v
        if dj_field and (v := getattr(dj_field, "default", None)) is not NOT_PROVIDED
        else None
    )
    if isinstance(resolved_type, type) and issubclass(resolved_type, models.Choices):
        if choices is None:
            choices = [
                FieldChoice(label=lbl, value=cast(JSON, value))
                for lbl, value in zip(resolved_type.labels, resolved_type.names)
            ]
        default_value = (
            resolved_type(default_value).name if default_value is not None else None
        )
    elif choices is None and dj_field and (items := getattr(dj_field, "choices", None)):
        if isinstance(items, dict):
            items = items.items()

        choices = []
        for value, label in items:
            if isinstance(label, (list, tuple)):
                group = value
                for group_value, group_lbl in label:
                    choices.append(
                        FieldChoice(label=group_lbl, value=group_value, group=group)
                    )
            else:
                choices.append(FieldChoice(label=label, value=value))

    # FIXME: We could call default_value(), but for places like timezone.now it is worse than
    # passing it. We might need to find a proper solution in the future
    if callable(default_value):
        default_value = None

    options["default_value"] = cast(Any, default_value)
    if choices is not None:
        options["choices"] = choices

    if dj_type:
        if (order := dj_type.order) and order is not UNSET:
            options["orderable"] = field.name in {
                f.name for f in dataclasses.fields(order)
            }
        if (filters := dj_type.filters) and filters is not UNSET:
            options["filterable"] = field.name in {
                f.name for f in dataclasses.fields(filters)
            }

    if dj_field:
        if (label := getattr(dj_field, "verbose_name", None) or None) is not None:
            options["label"] = label

        if (help_text := getattr(dj_field, "help_Text", None) or None) is not None:
            options["help_text"] = help_text

        if isinstance(dj_field, models.ImageField):
            options["kind"] = FieldKind.IMAGE
        elif isinstance(dj_field, models.FileField):
            options["kind"] = FieldKind.FILE
        elif PhoneNumberField is not None and isinstance(dj_field, PhoneNumberField):
            options["kind"] = FieldKind.PHONE
        elif isinstance(dj_field, models.TextField):
            options["kind"] = FieldKind.MULTILINE
        elif isinstance(
            dj_field, (models.IPAddressField, models.GenericIPAddressField)
        ):
            options["kind"] = FieldKind.IP
        elif isinstance(dj_field, models.EmailField):
            options["kind"] = FieldKind.EMAIL
        elif isinstance(dj_field, models.CharField):
            options["kind"] = FieldKind.STRING
            options["validation"] = StringFieldValidation(
                required=not isinstance(field.type, StrawberryOptional),
                min_length=0 if dj_field.blank else 1,
                max_length=dj_field.max_length,
            )
        elif isinstance(dj_field, models.UUIDField):
            options["kind"] = FieldKind.UUID
        elif isinstance(dj_field, models.URLField):
            options["kind"] = FieldKind.URL
        elif isinstance(dj_field, models.DecimalField):
            options["kind"] = FieldKind.DECIMAL
            options["validation"] = DecimalFieldValidation(
                required=not isinstance(field.type, StrawberryOptional),
                max_digits=dj_field.max_digits,
                decimal_places=dj_field.decimal_places,
            )
        elif isinstance(dj_field, models.FloatField):
            options["kind"] = FieldKind.FLOAT
        elif isinstance(dj_field, models.AutoField):
            options["kind"] = FieldKind.ID
        elif isinstance(dj_field, models.IntegerField):
            options["kind"] = FieldKind.INT
        elif isinstance(dj_field, models.BooleanField):
            options["kind"] = FieldKind.BOOLEAN
        elif isinstance(dj_field, models.DateTimeField):
            options["kind"] = FieldKind.DATETIME
        elif isinstance(dj_field, models.DateField):
            options["kind"] = FieldKind.DATE
        elif isinstance(dj_field, models.TimeField):
            options["kind"] = FieldKind.TIME
        elif isinstance(
            dj_field,
            (models.ForeignKey, models.OneToOneRel, models.OneToOneField),
        ):
            options["kind"] = FieldKind.ID
        elif isinstance(
            dj_field,
            (models.ManyToManyField, models.ManyToManyRel, models.ManyToOneRel),
        ):
            options["kind"] = FieldKind.ID
            options["multiple"] = True
        elif isinstance(dj_field, models.JSONField):
            options["kind"] = FieldKind.JSON
        elif PolygonField is not None and isinstance(dj_field, PolygonField):
            options["kind"] = FieldKind.POLYGON
        elif PointField is not None and isinstance(dj_field, PointField):
            options["kind"] = (
                FieldKind.GEOPOINT
                if dj_field.srid == 4326  # type: ignore  # noqa: PLR2004
                else FieldKind.POINT
            )

    return options


integration = StrawberryResourceIntegration(
    name="django",
    get_extra_mappings=get_extra_mappings,
    get_field_options=get_field_options,
)
