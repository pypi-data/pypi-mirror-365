"""Application command implementation."""

import logging
import sys
from typing import Any

from .action_command import ActionCommand
from .base_command import Command, CommandContext


class AppCommand(Command):
    """Command for executing application actions."""

    def __init__(self, app_name: str, context: CommandContext):
        super().__init__(f"app:{app_name}", f"Execute {app_name} application")
        self.app_name = app_name
        self.context = context
        self.action_command: ActionCommand = None

    def validate(self) -> bool:
        """Validate the application exists and has valid configuration."""
        app_config = self.context.config["applications"].get(self.app_name)
        if not app_config:
            self.logger.error("Application %s not found in config", self.app_name)
            return False

        if "actions" not in app_config:
            self.logger.error("Application %s must define 'actions'", self.app_name)
            return False

        return True

    def execute(self) -> Any:
        """Execute the application command."""
        if not self.validate():
            sys.exit(1)

        # todo: fix circular import at top-level import
        from utils.builders import FluentCommandBuilder

        builder = FluentCommandBuilder.for_action(
            self.app_name,
            self.get_action_name(),
            self.context.config,
            self.context.args,
        )

        self.action_command = builder.build_action_command()
        result = self.action_command.execute()
        self._executed = True
        self._result = result
        return result

    def get_action_name(self) -> str:
        """Get action name from args or use default action."""
        app_config = self.context.config["applications"][self.app_name]
        action_name = getattr(self.context.args, "action", None)

        if action_name:
            return action_name

        default_action = app_config.get("default_action")
        if default_action:
            return default_action

        self.logger.error(
            "No action specified and no default action defined for application %s",
            self.app_name,
        )
        sys.exit(1)

    @property
    def logger(self):
        """Get logger instance."""
        return logging.getLogger("pp")
