"""String parameter validation strategy."""

from typing import Any, Dict

from .base_strategy import ParameterStrategy


class StringParameterStrategy(ParameterStrategy):
    """Strategy for handling string parameters."""

    def validate_and_convert(
        self, param_name: str, param_config: Dict[str, Any], value: Any
    ) -> str:
        """Validate and convert string parameter."""
        if value is None or value == "":
            if param_config.get("required", False):
                raise ValueError(f"Parameter '{param_name}' is required")
            return param_config.get("default", "")

        str_value = str(value)

        # Check choices if specified
        choices = param_config.get("choices")
        if choices and str_value not in choices:
            raise ValueError(
                f"Parameter '{param_name}' must be one of: {', '.join(choices)}"
            )

        return str_value

    def get_type_name(self) -> str:
        return "string"
