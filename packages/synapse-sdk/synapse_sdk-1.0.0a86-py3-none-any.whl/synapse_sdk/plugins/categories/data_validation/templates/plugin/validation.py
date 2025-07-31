from typing import Any, Dict, List, Optional

from synapse_sdk.plugins.categories.data_validation.actions.validation import ValidationDataStatus, ValidationResult


def validate(data: Optional[Dict[str, Any]] = None, **kwargs: Any) -> ValidationResult:
    """Validate data with assignment data.

    * Custom validation logic can be added here.
    * Error messages can be added to the errors list if errors exist in data.
    * The validation result will be returned as a dict with ValidationResult structure.

    Args:
        data: The data to validate.
        **kwargs: Additional arguments.

    Returns:
        ValidationResult: The validation result with status and errors.
    """
    errors: List[str] = []

    # Add custom validation logic here

    # Add error messages into errors list if errors exist in data

    # Determine status based on errors
    status = ValidationDataStatus.FAILED if errors else ValidationDataStatus.SUCCESS

    return ValidationResult(status=status, errors=errors)
