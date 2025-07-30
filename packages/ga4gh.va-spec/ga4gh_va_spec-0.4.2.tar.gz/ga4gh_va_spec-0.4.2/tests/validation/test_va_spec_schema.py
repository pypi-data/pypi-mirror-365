"""Test that VA-Spec Python Pydantic models match corresponding JSON schemas"""

import json
from pathlib import Path

import pytest
from ga4gh.va_spec import aac_2017, acmg_2015, base, ccv_2022
from pydantic import BaseModel

from tests.conftest import (
    SUBMODULES_DIR,
    VaSpecSchema,
    get_va_spec_schema,
)

VA_SCHEMA_DIR = SUBMODULES_DIR / "schema" / "va-spec"


class VaSpecSchemaMapping(BaseModel):
    """Model for representing VA-Spec Schema concrete classes, primitives, and schema"""

    base_classes: set = set()
    concrete_classes: set = set()
    primitives: set = set()
    va_spec_schema: dict = {}


def _update_va_spec_schema_mapping(
    f_path: Path, va_spec_schema_mapping: VaSpecSchemaMapping
) -> None:
    """Update ``va_spec_schema_mapping`` properties

    :param f_path: Path to JSON Schema file
    :param va_spec_schema_mapping: VA-Spec schema mapping to update
    """
    with f_path.open() as rf:
        cls_def = json.load(rf)

    spec_class = cls_def["title"]
    va_spec_schema_mapping.va_spec_schema[spec_class] = cls_def

    if "properties" in cls_def:
        va_spec_schema_mapping.concrete_classes.add(spec_class)
    elif cls_def.get("type") in {"array", "integer", "string"}:
        va_spec_schema_mapping.primitives.add(spec_class)
    else:
        va_spec_schema_mapping.base_classes.add(spec_class)


VA_SPEC_SCHEMA_MAPPING = {schema: VaSpecSchemaMapping() for schema in VaSpecSchema}


# Get core + profiles classes
for child in VA_SCHEMA_DIR.iterdir():
    child_str = str(child)
    mapping_key = get_va_spec_schema(child_str)
    if not mapping_key:
        continue

    mapping = VA_SPEC_SCHEMA_MAPPING[mapping_key]
    for f in (child / "json").glob("*"):
        _update_va_spec_schema_mapping(f, mapping)


@pytest.mark.parametrize(
    ("va_spec_schema", "pydantic_models"),
    [
        (VaSpecSchema.AAC_2017, aac_2017),
        (VaSpecSchema.ACMG_2015, acmg_2015),
        (VaSpecSchema.BASE, base),
        (VaSpecSchema.CCV_2022, ccv_2022),
    ],
)
def test_schema_models_in_pydantic(va_spec_schema, pydantic_models):
    """Ensure that each schema model has corresponding Pydantic model"""
    mapping = VA_SPEC_SCHEMA_MAPPING[va_spec_schema]
    for schema_model in (
        mapping.base_classes | mapping.concrete_classes | mapping.primitives
    ):
        assert getattr(pydantic_models, schema_model, False), schema_model


@pytest.mark.parametrize(
    ("va_spec_schema", "pydantic_models"),
    [
        (VaSpecSchema.AAC_2017, aac_2017),
        (VaSpecSchema.ACMG_2015, acmg_2015),
        (VaSpecSchema.BASE, base),
        (VaSpecSchema.CCV_2022, ccv_2022),
    ],
)
def test_schema_class_fields(va_spec_schema, pydantic_models):
    """Check that each schema model properties exist and are required in corresponding
    Pydantic model, and validate required properties
    """
    mapping = VA_SPEC_SCHEMA_MAPPING[va_spec_schema]
    for schema_model in mapping.concrete_classes:
        schema_properties = mapping.va_spec_schema[schema_model]["properties"]
        pydantic_model = getattr(pydantic_models, schema_model)
        assert set(pydantic_model.model_fields) == set(schema_properties), schema_model

        required_schema_fields = set(mapping.va_spec_schema[schema_model]["required"])

        for prop, property_def in schema_properties.items():
            pydantic_model_field_info = pydantic_model.model_fields[prop]
            pydantic_field_required = pydantic_model_field_info.is_required()

            if prop in required_schema_fields:
                if prop in {"predicate", "type"}:
                    assert pydantic_model_field_info
                else:
                    assert pydantic_field_required, f"{pydantic_model}.{prop}"
            else:
                if prop == "date":
                    assert pydantic_model_field_info
                else:
                    assert not pydantic_field_required, f"{pydantic_model}.{prop}"

            if "description" in property_def:
                if prop not in {"date", "predicate"}:  # special exceptions
                    assert property_def["description"].replace(
                        "'", '"'
                    ) == pydantic_model_field_info.description.replace(
                        "'", '"'
                    ), f"{pydantic_model}.{prop}"
            else:
                assert (
                    pydantic_model_field_info.description is None
                ), f"{pydantic_model}.{prop}"
