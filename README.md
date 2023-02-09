# strawberry-resources

[![build status](https://img.shields.io/endpoint.svg?url=https%3A%2F%2Factions-badge.atrox.dev%2Fblb-ventures%2Fstrawberry-resources%2Fbadge%3Fref%3Dmain&style=flat)](https://actions-badge.atrox.dev/blb-ventures/strawberry-resources/goto?ref=main)
[![coverage](https://img.shields.io/codecov/c/github/blb-ventures/strawberry-resources.svg)](https://codecov.io/gh/blb-ventures/strawberry-resources)
[![downloads](https://pepy.tech/badge/strawberry-resources)](https://pepy.tech/project/strawberry-resources)
[![PyPI version](https://img.shields.io/pypi/v/strawberry-resources.svg)](https://pypi.org/project/strawberry-resources/)
![python version](https://img.shields.io/pypi/pyversions/strawberry-resources.svg)

Introspection utilities to extract data from the schema to use as helpers in the
client, like building an automatic form for input types.

## Installation

Just install the package with pip or your preferred package manager:

```shell
pip install strawberry-resources
```

## How to use

### Usage in a query

This lib provides a `Query` type that has two queries:

- `resources`: Returns a list of all available resources in the schema
- `resource`: Returns an specific resource given its name

You can use [merge_type](https://strawberry.rocks/docs/guides/tools#merge_types)
to merge it with your own `Query` type.

Then, given this example:

```python
@strawberry.enum
class Color(enum.Enum):
    YELLOW = strawberry.enum_value("yellow", description="Color Yellow")
    RED = "red"
    ORANGE = "orange"

@strawberry.type
class Fruit:
    name: str
    color: Annotated[Color, config(label="Color")]
    weight: Annotate[float, strawberry_resource.config(label="Weight")]

@strawberry.type
class Market:
    name: Annotate[str, strawberry_resource.config(label="Market Name")]
    fruits: Annotate[List[Fruit], strawberry_resource.config(label="Fruits")]

@strawberry.type
class Query:
    market: Market
```

You can query `resource(name: "Market")` which would return:

```json
{
  "resource": {
    "name": "Market"
    "fields": [
      {
        "__typename": "Field",
        "choices": null,
        "defaultValue": null,
        "filterable": false,
        "helpText": null,
        "kind": "STRING",
        "label": "Market Name",
        "multiple": false,
        "name": "name",
        "orderable": false,
        "resource": null,
        "validation": {
          "__typename": "BaseFieldValidation",
          "required": true
        }
      },
      {
        "__typename": "FieldObject",
        "label": "Fruits",
        "name": "fruits",
        "objKind": "OBJECT_LIST"
        "fields": [
          {
            "__typename": "Field",
            "choices": null,
            "defaultValue": null,
            "filterable": false,
            "helpText": null,
            "kind": "STRING",
            "label": "name",
            "multiple": false,
            "name": "name",
            "orderable": false,
            "resource": null,
            "validation": {
              "__typename": "BaseFieldValidation",
              "required": true
            }
          },
          {
            "__typename": "Field",
            "choices": [
              {
                "group": null,
                "label": "Color Yellow",
                "value": "YELLOW"
              },
              {
                "group": null,
                "label": "RED",
                "value": "RED"
              },
              {
                "group": null,
                "label": "ORANGE",
                "value": "ORANGE"
              }
            ],
            "defaultValue": null,
            "filterable": false,
            "helpText": null,
            "kind": "STRING",
            "label": "Color",
            "multiple": false,
            "name": "color",
            "orderable": false,
            "resource": null,
            "validation": {
              "__typename": "BaseFieldValidation",
              "required": true
            }
          },
          {
            "__typename": "Field",
            "choices": null,
            "defaultValue": null,
            "filterable": false,
            "helpText": null,
            "kind": "FLOAT",
            "label": "Weight",
            "multiple": false,
            "name": "weight",
            "orderable": false,
            "resource": null,
            "validation": {
              "__typename": "BaseFieldValidation",
              "required": true
            }
          }
        ],
      }
    ],
  }
}
```

### Exporting the resources

You can also use the resources statically by exporting them by using the command:

```shell
strawberry_resources export --app-dir <schema>
```

The export functions are also exposed in `strawberry_resources.exporter`. There are
2 functions there:

- `to_dict`: Will export the resources to a dictionary
- `to_json`: Will export the resources to a json string (used by the command above)

## Customizing the resource

Strawberry resource will introspect the schema to automatically fill some information
regarding the field. However, you can customize them by annotating your fields with
your own config.

In the example above we customized the `label` for most attributes, except for `Fruit.name`.
All possible config options are:

- `kind` (`FieldKind`): The kind of the field
- `multiple` (`bool`): If the field is multivalued (i.e. a List)
- `orderable` (`bool`): If the field is orderable`
- `filterable` (`bool`): If the field is filterable`
- `label` (`str | None`): An optional human friendly label for the field
- `help_text` (`str | FieldChoice`): An optional list with available choices for the field
- `default_value` (`JSON | None`): The default value for the field
- `validation` (`BaseFieldValidation`): Validation options for the field

Check the [types.py](strawberry_resources/types.py) module for more details.

## Integrations

### Django

If you are using Django, and by extend
[strawberry-graphql-django](https://github.com/strawberry-graphql/strawberry-graphql-django) or
[strawberry-django-plus](https://github.com/blb-ventures/strawberry-django-plus), the integration
will be automatically used to configure some options by introspecting your model.

The following will be retrieved from the fields in it, specially when typing it with
`strawberry.auto`:

- `kind`: The field kind will be automatically set based on the model field type. e.g. a `CharField`
  will generate a kind of `STRING`, a `DateTimeField` will generate a kind of `DATETIME` and so on.
- `orderable`: Will be automatically filled if the django type has an
  [ordering](https://strawberry-graphql.github.io/strawberry-graphql-django/references/ordering/)
  set on it, and the field itself is there
- `filterable`: Will be automatically filled if the django type has
  [filters](https://strawberry-graphql.github.io/strawberry-graphql-django/references/filters/)
  set on it, and the field itself is there
- `label`: Will be automatically filled using the field's `verbose_name` value
- `help_text`: Will be automatically filled using the field's `help_text` value
- `choices`: Will be automatically filled using the field's `choices` value
- `default_value`: Will be automatically filled using the field's `default` value

### Creating your own integration

You can create your own extension by creating an instance of
`strawberry_resources.integrations.StrawberryResourceIntegration`. It expects 4 attributes:

- `name`: The name of the integration
- `get_extra_mappings`: A callable that should return a dict mapping a type to a `FieldKind`
- `get_field_options`: A mapping that receives the type that contains the field, the field itself,
  the resolved type of the field and if it is a list of not. It is expect to return a dict with
  the options mentioned in the section above.
- `order`: An optional order to be used when running the integrations.

The integrations will run in the `order` they are defined. The official integrations in
this repo all have an order of `0`, so you can define yours to run before them by passing
a negative value, or after them by passing something greater than `0`.

NOTE: strawberry-resources is eager to have more integrations, so feel free to open a PR
for us sending yours! :)

## How options are resolved

All options will be merged recursively to generate the final resource options. That means that
options defined later will override the ones defined earlier. The order is the following:

- The options will be created with its `kind` retrieved from the kind mapping (considering the
  ones returned by the integrations as well), and its `label` will be set the same as its name
  by default.
- The integrations will run in the order they were defined, and each option returned will
  me merged recursively with the current options.
- At last, options will be retrieved by the field's annotations and will have the highest
  priority when merging with the rest.

## Licensing

The code in this project is licensed under MIT license. See [LICENSE](./LICENSE)
for more information.
