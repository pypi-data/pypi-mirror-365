"""Boolean parameter validation strategy."""

from typing import Any, Dict

from .base_strategy import ParameterStrategy


class BooleanParameterStrategy(ParameterStrategy):
    """Strategy for handling boolean parameters."""

    def validate_and_convert(
        self, param_name: str, param_config: Dict[str, Any], value: Any
    ) -> bool:
        """Validate and convert boolean parameter."""
        if value is None:
            if param_config.get("required", False):
                raise ValueError(f"Parameter '{param_name}' is required")
            return param_config.get("default", False)

        # Handle various boolean representations
        if isinstance(value, bool):
            return value

        if isinstance(value, str):
            lower_value = value.lower()
            if lower_value in ("true", "yes", "1", "on"):
                return True
            elif lower_value in ("false", "no", "0", "off", ""):
                return False
            else:
                raise ValueError(
                    f"Invalid boolean value for parameter '{param_name}': '{value}'"
                )

        # Handle numeric values
        try:
            return bool(int(value))
        except (ValueError, TypeError):
            raise ValueError(
                f"Invalid boolean value for parameter '{param_name}': '{value}'"
            )

    def get_type_name(self) -> str:
        return "boolean"
