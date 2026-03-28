"""Internationalization utilities for DE/EN bilingual support."""

from enum import Enum


class Locale(str, Enum):
    DE = "de"
    EN = "en"


def localized_field(obj: object, field_base: str, locale: Locale) -> str:
    """Get a localized field from an ORM model.

    Example: localized_field(module, "name", Locale.DE) returns module.name_de
    Falls back to German if the requested locale field is empty.
    """
    value = getattr(obj, f"{field_base}_{locale.value}", None)
    if not value and locale != Locale.DE:
        value = getattr(obj, f"{field_base}_de", None)
    return value or ""
