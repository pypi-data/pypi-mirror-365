from typing import Any, Callable, Dict

from .error_handler import ERROR_HANDLER, ErrorSeverity, log_warning

# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================


def validate_object(
    value: Any,
    name: str,
    context: Dict[str, Any] | None = None,
    attributes: list[str] | None = None,
) -> Any:
    """
    Validates that an object exists and optionally has required
    attributes/methods.

    This function checks if the provided `obj` is not `None`. If `attributes` is
    provided, it further checks if the object possesses all specified
    attributes. If any validation fails, an error is logged, and a `ValueError`
    is raised.

    Args:
        obj: The object to validate.
        name: The human-readable name for the object, used in error messages.
        context: An optional dictionary of additional context for logging.
        attributes: An optional list of strings, where each string is the name
        of an attribute or method that `obj` must possess.

    Returns:
        The validated object if all checks pass.

    Raises:
        ValueError: If the object is `None` or is missing any of the `attributes`.
    """
    if value is None:
        ERROR_HANDLER.handle(
            error=f"Required value '{name}' is None",
            severity=ErrorSeverity.HIGH,
            context=context or {},
            exception=Exception(f"Required value '{name}' is None"),
            raise_exception=True,
        )
    # If we have attributes to check, validate them.
    if attributes:
        # Gather missing attributes.
        missing_attrs: list[str] = []
        for attribute in attributes:
            if not hasattr(value, attribute):
                missing_attrs.append(attribute)
        # If any attributes are missing, log an error.
        if missing_attrs:
            ERROR_HANDLER.handle(
                error=f"{name} missing required attributes: {missing_attrs}",
                severity=ErrorSeverity.HIGH,
                context={
                    **(context or {}),
                    "object_name": name,
                    "missing_attributes": missing_attrs,
                    "object_type": type(value).__name__,
                },
                exception=Exception(
                    f"{name} missing required attributes: {missing_attrs}"
                ),
                raise_exception=True,
            )
    # If we reach here, the object is valid.
    return value


def validate_type(
    value: Any,
    name: str,
    expected_type: type,
    context: dict[str, Any] | None = None,
) -> Any:
    """
    Validates that a value is of the specified type.

    If the validation fails, an error is logged and a ValueError is raised.

    Args:
        value: The value to validate.
        expected_type: The expected type (e.g., str, int, list, etc.).
        name: The name of the parameter being validated, used in error messages.
        context: An optional dictionary of additional context for logging.

    Returns:
        The validated value if it is of the expected type.

    Raises:
        ValueError: If the value is not of the expected type.
    """
    # First, validate that the value is not None.
    validate_object(value, name, context)
    # Then, check the type.
    if not isinstance(value, expected_type):
        ERROR_HANDLER.handle(
            error=f"{name} must be of type {expected_type.__name__}, "
            f"got: {type(value).__name__}",
            severity=ErrorSeverity.HIGH,
            context={
                **(context or {}),
                "name": name,
                "expected_type": expected_type.__name__,
                "actual_type": type(value).__name__,
                "value": value,
            },
            exception=ValueError(
                f"Invalid {name}: expected {expected_type.__name__}, "
                f"got {type(value).__name__}"
            ),
            raise_exception=True,
        )
    return value


# =============================================================================
# CONVERSION FUNCTIONS
# =============================================================================


def ensure_string(
    value: Any,
    name: str,
    default: str = "",
    context: dict[str, Any] | None = None,
) -> str:
    """
    Ensures a value is a string, converting it if possible or using a default.

    This function attempts to convert the provided `value` to a string. If the
    `value` is not already a string, a warning is logged. If conversion is not
    possible (e.g., `value` is `None` and no default is provided), the specified
    `default` string is returned.

    Args:
        value: The value to be ensured as a string.
        name: The name of the parameter being processed, used in log messages.
        default: The default string value to return if `value` cannot be
        converted or is `None`. Defaults to an empty string.
        context: An optional dictionary of additional context for logging.

    Returns:
        The `value` as a string, or the `default` string if conversion fails.
    """
    if not isinstance(value, str):
        log_warning(
            f"{name} should be string, got: {type(value).__name__}, converting",
            {
                **(context or {}),
                "name": name,
                "value": value,
                "type": type(value).__name__,
            },
        )
        return str(value) if value is not None else default
    return value


def ensure_non_negative_int(
    value: Any,
    name: str,
    default: int = 0,
    context: dict[str, Any] | None = None,
) -> int:
    """
    Ensures a value is a non-negative integer, correcting it if necessary.

    This function attempts to convert the provided `value` to an integer and
    ensures it is not negative. If the `value` is not an integer, is negative,
    or cannot be converted, a warning is logged, and the specified `default`
    value is returned or the value is clamped to 0 if it's a negative number.

    Args:
        value: The value to be ensured as a non-negative integer.
        name: The name of the parameter being processed, used in log messages.
        default: The default integer value to return if `value` is invalid.
        Defaults to 0.
        context: An optional dictionary of additional context for logging.

    Returns:
        The corrected non-negative integer value.
    """
    if not isinstance(value, int) or value < 0:
        log_warning(
            f"{name} must be non-negative integer, got: {value}, "
            f"correcting to {default}",
            {
                **(context or {}),
                "name": name,
                "value": value,
                "corrected_to": default,
            },
        )
        return max(0, int(value) if isinstance(value, (int, float)) else default)
    return value


def ensure_int_in_range(
    value: Any,
    name: str,
    min_val: int,
    max_val: int | None = None,
    default: int | None = None,
    context: dict[str, Any] | None = None,
) -> int:
    """
    Ensures a value is an integer within a specified range, correcting it if
    necessary.

    This function attempts to convert the provided `value` to an integer and
    checks if it falls within the `min_val` and `max_val` (inclusive). If the
    `value` is not an integer, is outside the range, or cannot be converted, a
    warning is logged, and the value is corrected to `min_val`, `max_val`, or
    the specified `default`.

    Args:
        value: The value to be ensured as an integer within the range.
        name: The name of the parameter being processed, used in log messages.
        min_val: The minimum allowed integer value (inclusive).
        max_val: The maximum allowed integer value (inclusive). If `None`, there
        is no upper limit.
        default: The default integer value to return if `value` is invalid or
        out of range. If `None`, `min_val` is used as the default.
        context: An optional dictionary of additional context for logging.

    Returns:
        The corrected integer value within the specified range.
    """
    if default is None:
        default = min_val

    if (
        not isinstance(value, int)
        or value < min_val
        or (max_val is not None and value > max_val)
    ):
        range_desc = (
            f">= {min_val}" if max_val is None else f"between {min_val} and {max_val}"
        )
        log_warning(
            f"{name} must be integer {range_desc}, got: {value}, "
            f"correcting to {default}",
            {
                **(context or {}),
                "name": name,
                "value": value,
                "min_val": min_val,
                "max_val": max_val,
                "corrected_to": default,
            },
        )

        # Try to convert and clamp
        try:
            converted = int(value) if isinstance(value, (int, float)) else default
            if converted < min_val:
                return min_val
            elif max_val is not None and converted > max_val:
                return max_val
            else:
                return converted
        except (ValueError, TypeError):
            return default
    return value


def ensure_list_of_type(
    value: Any,
    name: str,
    expected_type: type,
    default: list | None = None,
    converter: Callable[[Any], Any] | None = None,
    validator: Callable[[Any], bool] | None = None,
    context: dict[str, Any] | None = None,
) -> list:
    """
    Ensures a value is a list containing items of a specified type, correcting
    if needed.

    This function validates that `value` is a list. It then iterates through the
    list to ensure each item is of `expected_type`. Invalid items are either
    converted using a `converter` function, or a default conversion is attempted
    for common types (str, int, float). Items can also be validated with a
    `validator` function. Warnings are logged for invalid items, but execution
    continues with a cleaned list.

    Args:
        value: The value to validate, expected to be a list.
        expected_type: The `type` that all items in the list should conform to.
        name: The name of the parameter being processed, used in log messages.
        default: The default list to return if `value` is `None` or not a list.
        Defaults to an empty list.
        converter: An optional callable that takes an item and attempts to
        convert it to `expected_type`. If conversion fails or returns a wrong
        type, the item is skipped.
        validator: An optional callable that takes an item of `expected_type`
        and returns returns `True` if the item is valid, `False` otherwise.
        Invalid items are skipped.
        context: An optional dictionary of additional context for logging.

    Returns:
        A new list containing only the valid and/or converted items of `expected_type`.
    """
    if default is None:
        default = []

    if value is None:
        return default

    if not isinstance(value, list):
        log_warning(
            f"{name} should be list, got: {type(value).__name__}, "
            f"using default: {default}",
            {
                **(context or {}),
                "name": name,
                "value": value,
                "type": type(value).__name__,
            },
        )
        return default

    # Ensure all items are of the expected type
    cleaned_list = []
    had_invalid_items = False

    for i, item in enumerate(value):
        if isinstance(item, expected_type):
            # Item is correct type, now validate if validator is provided
            if validator and not validator(item):
                had_invalid_items = True
                log_warning(
                    f"{name}[{i}] failed validation, " f"skipping item: {item}",
                    {
                        **(context or {}),
                        "name": name,
                        "index": i,
                        "item": item,
                        "expected_type": expected_type.__name__,
                    },
                )
                continue  # Skip invalid items
            else:
                cleaned_list.append(item)
        else:
            # Item is wrong type, try to convert
            had_invalid_items = True
            if converter:
                try:
                    converted_item = converter(item)
                    if isinstance(converted_item, expected_type):
                        # Validate converted item if validator is provided
                        if validator and not validator(converted_item):
                            log_warning(
                                f"{name}[{i}] converted item failed validation, "
                                f"skipping: {converted_item}",
                                {
                                    **(context or {}),
                                    "name": name,
                                    "index": i,
                                    "original": item,
                                    "converted": converted_item,
                                    "expected_type": expected_type.__name__,
                                },
                            )
                            continue
                        cleaned_list.append(converted_item)
                    else:
                        log_warning(
                            f"{name}[{i}] converter returned wrong type, "
                            f"skipping: {item}",
                            {
                                **(context or {}),
                                "name": name,
                                "index": i,
                                "item": item,
                                "expected_type": expected_type.__name__,
                                "converter_result_type": type(converted_item).__name__,
                            },
                        )
                except Exception as e:
                    log_warning(
                        f"{name}[{i}] conversion failed, skipping item: {item}",
                        {
                            **(context or {}),
                            "name": name,
                            "index": i,
                            "item": item,
                            "error": str(e),
                        },
                    )
            else:
                # No converter provided, use default conversion for common types
                try:
                    if expected_type is str:
                        converted = str(item) if item is not None else ""
                    elif expected_type is int:
                        converted = int(item)
                    elif expected_type is float:
                        converted = float(item)
                    else:
                        # Can't convert without explicit converter
                        log_warning(
                            f"{name}[{i}] wrong type and no converter provided, "
                            f"skipping: {item}",
                            {
                                **(context or {}),
                                "name": name,
                                "index": i,
                                "item": item,
                                "expected_type": expected_type.__name__,
                                "actual_type": type(item).__name__,
                            },
                        )
                        continue

                    # Validate converted item if validator is provided
                    if validator and not validator(converted):
                        log_warning(
                            f"{name}[{i}] converted item failed validation, "
                            f"skipping: {converted}",
                            {
                                **(context or {}),
                                "name": name,
                                "index": i,
                                "original": item,
                                "converted": converted,
                            },
                        )
                        continue

                    cleaned_list.append(converted)
                except (ValueError, TypeError) as e:
                    log_warning(
                        f"{name}[{i}] conversion failed, skipping item: {item}",
                        {
                            **(context or {}),
                            "name": name,
                            "index": i,
                            "item": item,
                            "error": str(e),
                        },
                    )

    if had_invalid_items:
        log_warning(
            f"{name} had invalid items, cleaned list created",
            {
                **(context or {}),
                "name": name,
                "original_length": len(value),
                "cleaned_length": len(cleaned_list),
                "expected_type": expected_type.__name__,
            },
        )

    return cleaned_list


def safe_get_attribute(obj: Any, name: str, default: Any = None) -> Any:
    """
    Safely retrieves an attribute from an object, returning a default value if
    not found.

    This function attempts to get the attribute named `name` from `obj`. If
    `obj` is `None` or the attribute does not exist, a warning is logged, and
    the specified `default` value is returned instead.

    Args:
        obj: The object from which to retrieve the attribute.
        name: The name of the attribute to retrieve.
        default: The default value to return if the attribute is not found or
        `obj` is `None`. Defaults to `None`.

    Returns:
        The value of the attribute if found, otherwise the `default` value.
    """
    if obj is None:
        return default

    if hasattr(obj, name):
        return getattr(obj, name)
    else:
        log_warning(
            f"{type(obj).__name__} missing attribute '{name}', using default: {default}",
            {
                "object_type": type(obj).__name__,
                "name": name,
                "default": default,
            },
        )
        return default
