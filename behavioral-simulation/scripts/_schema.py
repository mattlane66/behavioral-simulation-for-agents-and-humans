"""Small dependency-free JSON Schema subset used by the repository contracts."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


def _type_ok(value: Any, expected: str) -> bool:
    if expected == "null":
        return value is None
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    return True


def validate_schema(value: Any, schema: dict[str, Any], path: str = "$") -> list[str]:
    errors: list[str] = []

    if "const" in schema and value != schema["const"]:
        errors.append(f"{path} must equal {schema['const']!r}")

    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path} must be one of {schema['enum']!r}")

    expected = schema.get("type")
    if expected is not None:
        choices = expected if isinstance(expected, list) else [expected]
        if not any(_type_ok(value, choice) for choice in choices):
            errors.append(f"{path} has invalid type; expected {choices!r}")
            return errors

    if isinstance(value, str):
        if "minLength" in schema and len(value) < int(schema["minLength"]):
            errors.append(f"{path} must have length >= {schema['minLength']}")
        if "pattern" in schema and re.search(schema["pattern"], value) is None:
            errors.append(f"{path} does not match required pattern")

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            errors.append(f"{path} must be >= {schema['minimum']}")

    if isinstance(value, dict):
        required = schema.get("required", [])
        for key in required:
            if key not in value:
                errors.append(f"{path} missing required property {key}")

        properties = schema.get("properties", {})
        additional = schema.get("additionalProperties", True)
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key in properties:
                if isinstance(properties[key], dict):
                    errors.extend(validate_schema(child, properties[key], child_path))
            elif additional is False:
                errors.append(f"{child_path} is not allowed")
            elif isinstance(additional, dict):
                errors.extend(validate_schema(child, additional, child_path))

    if isinstance(value, list) and isinstance(schema.get("items"), dict):
        item_schema = schema["items"]
        for index, child in enumerate(value):
            errors.extend(validate_schema(child, item_schema, f"{path}[{index}]"))

    return errors


def validate_file_against_schema(document: Any, schema_path: Path, label: str) -> list[str]:
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return [f"{label} schema unavailable/invalid: {exc}"]
    return [f"{label} schema: {error}" for error in validate_schema(document, schema)]
