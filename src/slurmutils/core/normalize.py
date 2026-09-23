# Copyright 2026 Canonical Ltd.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License version 3 as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Normalize configuration values before jsonschema validation."""

from typing import Any

_BOOL_STRINGS = {
    "yes": True,
    "no": False,
    "true": True,
    "false": False,
}


def normalize_for_schema(instance: Any, schema: dict[str, Any]) -> Any:
    """Normalize instance values to match slurmutils schema expectations.

    Slurm configuration values are case-insensitive. This function lowercases
    enum strings and coerces common boolean string representations (``yes``/``no``,
    ``true``/``false``, and their uppercase forms) before schema validation.
    """
    return _normalize_value(instance, schema)


def _normalize_value(value: Any, schema: dict[str, Any]) -> Any:
    if "oneOf" in schema:
        return _normalize_oneof(value, schema["oneOf"])

    schema_type = schema.get("type")
    if schema_type == "object" and isinstance(value, dict):
        return _normalize_object(value, schema)

    if schema_type == "array" and isinstance(value, list):
        items = schema.get("items", {})
        return [_normalize_value(item, items) for item in value]

    if isinstance(value, str):
        return _normalize_string(value, schema)

    return value


def _normalize_oneof(value: Any, one_of: list[dict[str, Any]]) -> Any:
    if isinstance(value, str):
        return _normalize_oneof_string(value, one_of)

    if isinstance(value, bool) and _any_subschema_type(one_of, "boolean"):
        return value

    if isinstance(value, int) and not isinstance(value, bool) and _any_subschema_type(one_of, "integer"):
        return value

    return value


def _normalize_oneof_string(value: str, one_of: list[dict[str, Any]]) -> Any:
    for subschema in one_of:
        if (normalized := _normalize_enum_string(value, subschema, require_match=True)) is not None:
            return normalized

    if _any_subschema_type(one_of, "boolean"):
        if (normalized := _normalize_bool_string(value, {"type": "boolean"})) is not None:
            return normalized

    if _any_subschema_type(one_of, "string", exclude_enum=True):
        return value

    return value


def _normalize_string(value: str, schema: dict[str, Any]) -> Any:
    if (normalized := _normalize_enum_string(value, schema, require_match=False)) is not None:
        return normalized

    if (normalized := _normalize_bool_string(value, schema)) is not None:
        return normalized

    return value


def _normalize_enum_string(value: str, schema: dict[str, Any], *, require_match: bool) -> str | None:
    if "enum" not in schema:
        return None

    lowered = value.lower()
    if require_match and lowered not in schema["enum"]:
        return None

    return lowered


def _normalize_bool_string(value: str, schema: dict[str, Any]) -> bool | None:
    if schema.get("type") != "boolean":
        return None

    return _BOOL_STRINGS.get(value.lower())


def _any_subschema_type(
    one_of: list[dict[str, Any]], schema_type: str, *, exclude_enum: bool = False
) -> bool:
    return any(
        subschema.get("type") == schema_type and (not exclude_enum or "enum" not in subschema)
        for subschema in one_of
    )


def _normalize_object(obj: dict[str, Any], schema: dict[str, Any]) -> dict[str, Any]:
    properties = schema.get("properties", {})
    pattern_properties = schema.get("patternProperties", {})
    result: dict[str, Any] = {}

    for key, value in obj.items():
        if key in properties:
            result[key] = _normalize_value(value, properties[key])
        elif pattern_properties:
            for prop_schema in pattern_properties.values():
                result[key] = _normalize_value(value, prop_schema)
                break
        else:
            result[key] = value

    return result

