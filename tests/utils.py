resource_query = """\
fragment resourceFieldFrag on Field {
  __typename
  name
  kind
  label
  multiple
  orderable
  filterable
  helpText
  choices {
    label
    value
    group
  }
  resource
  defaultValue
  validation {
    __typename
    ... on BaseFieldValidation {
      required
    }
    ... on StringFieldValidation {
      required
      minLength
      maxLength
    }
    ... on IntFieldValidation {
      required
      minValue
      maxValue
    }
    ... on DecimalFieldValidation {
      required
      minValue
      maxValue
      maxDigits
      decimalPlaces
    }
  }
}

fragment resourceFieldObjectFrag on FieldObject {
  __typename
  name
  label
  objKind
  fields {
    __typename
    ... on Field {
      ...resourceFieldFrag
    }
    ... on FieldObject {
      name
      objKind
      fields {
        __typename
        ... on Field {
          ...resourceFieldFrag
        }
        ... on FieldObject {
          name
          objKind
          fields {
            __typename
            ... on Field {
              ...resourceFieldFrag
            }
            ... on FieldObject {
              name
              objKind
              # We are stopping the recursion here
            }
          }
        }
      }
    }
  }
}

query Resource($name: String!) {
  resource(name: $name) {
    name
    fields {
      __typename
      ... on Field {
        ...resourceFieldFrag
      }
      ... on FieldObject {
        ...resourceFieldObjectFrag
      }
    }
  }
}
"""
