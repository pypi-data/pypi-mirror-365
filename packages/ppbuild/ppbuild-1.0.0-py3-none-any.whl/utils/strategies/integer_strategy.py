"""Integer parameter validation strategy."""

from typing import Any, Dict

from .base_strategy import ParameterStrategy


class IntegerParameterStrategy(ParameterStrategy):
    """Strategy for handling integer parameters."""

    def validate_and_convert(
        self, param_name: str, param_config: Dict[str, Any], value: Any
    ) -> int:
        """Validate and convert integer parameter."""
        if value is None or value == "":
            if param_config.get("required", False):
                raise ValueError(f"Parameter '{param_name}' is required")
            return param_config.get("default", 0)

        try:
            int_value = int(value)
        except (ValueError, TypeError):
            raise ValueError(
                f"Invalid value for parameter '{param_name}': expected integer"
            )

        # Check bounds
        min_val = param_config.get("min")
        max_val = param_config.get("max")

        if min_val is not None and int_value < min_val:
            raise ValueError(f"Parameter '{param_name}' must be >= {min_val}")

        if max_val is not None and int_value > max_val:
            raise ValueError(f"Parameter '{param_name}' must be <= {max_val}")

        return int_value

    def get_type_name(self) -> str:
        return "integer"
