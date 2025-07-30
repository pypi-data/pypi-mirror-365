"""Action command implementation."""

import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

from utils.parameter_utils import (parse_action_parameters,
                                   substitute_parameters)

from .base_command import Command, CommandContext


class ActionCommand(Command):
    """Command for executing specific application actions."""

    def __init__(self, app_name: str, action_name: str, context: CommandContext):
        super().__init__(
            f"action:{app_name}:{action_name}",
            f"Execute {action_name} action for {app_name}",
        )
        self.app_name = app_name
        self.action_name = action_name
        self.context = context

    def validate(self) -> bool:
        """Validate the action exists and has valid configuration."""
        app_config = self.context.config["applications"].get(self.app_name, {})
        action_config = app_config.get("actions", {}).get(self.action_name)

        if not action_config:
            available_actions = list(app_config.get("actions", {}).keys())
            self.logger.error("Invalid %s action: %s", self.app_name, self.action_name)
            print(f"Available actions: {', '.join(available_actions)}")
            return False

        cmd = action_config.get("command")
        if not cmd:
            self.logger.error(
                "No command defined for %s action %s", self.app_name, self.action_name
            )
            return False

        return True

    def execute(self) -> Any:
        """Execute the action command."""
        if not self.validate():
            sys.exit(1)

        app_config = self.context.config["applications"][self.app_name]
        action_config = app_config["actions"][self.action_name]

        # Parse and validate parameters
        self._parse_parameters(action_config)

        # Get and process command
        cmd = action_config["command"]
        if self.context.parameters:
            cmd = self._substitute_parameters(cmd, self.context.parameters)
            self.logger.debug("Command after parameter substitution: %s", cmd)

        # Setup environment
        self._setup_environment(app_config)

        # Execute command
        self._run_command(cmd)

        self._executed = True
        return True

    def _parse_parameters(self, action_config: Dict[str, Any]) -> None:
        """Parse and validate action parameters."""
        if action_config.get("parameters"):
            self.context.parameters = parse_action_parameters(
                action_config, self.context.args
            )
            self.logger.debug("Parsed parameters: %s", self.context.parameters)

    def _substitute_parameters(
        self, command: List[str], parameters: Dict[str, Any]
    ) -> List[str]:
        """Substitute parameters in command."""
        return substitute_parameters(command, parameters)

    def _setup_environment(self, app_config: Dict[str, Any]) -> None:
        """Setup working directory and environment variables."""
        # Handle working directory
        if app_config.get("directory"):
            self._change_directory(app_config["directory"])

        # Handle virtual environment
        if app_config.get("venv"):
            self.context.env = self._activate_venv(app_config["venv"])

        # Handle environment variables
        if app_config.get("env_vars"):
            self.context.env.update(self._substitute_env_vars(app_config["env_vars"]))

    def _change_directory(self, directory: str) -> None:
        """Change to the specified directory."""
        directory = Path(directory).expanduser()
        if not directory.is_dir():
            self.logger.error("Directory %s not found", directory)
            sys.exit(1)
        os.chdir(directory)
        self.context.working_directory = str(directory)
        self.logger.debug("Changed directory to %s", directory)

    def _activate_venv(self, venv_path: str) -> Dict[str, str]:
        """Activate a virtual environment and return the updated environment."""
        venv_path = Path(venv_path).expanduser()
        if not (venv_path / "bin" / "activate").exists():
            self.logger.error("Virtual environment %s not found", venv_path)
            sys.exit(1)

        env = self.context.env.copy()
        env["VIRTUAL_ENV"] = str(venv_path)
        env["PATH"] = f"{venv_path}/bin:{env.get('PATH', '')}"
        self.context.virtual_env = str(venv_path)
        self.logger.info("Activated virtual environment: %s", venv_path)
        return env

    def _substitute_env_vars(self, env_vars: Dict[str, str]) -> Dict[str, str]:
        """Substitute environment variables in the config."""
        result = {}
        for key, value in env_vars.items():
            if (
                isinstance(value, str)
                and value.startswith("${")
                and value.endswith("}")
            ):
                env_key = value[2:-1]
                result[key] = os.environ.get(env_key, "")
                if not result[key]:
                    self.logger.warning("Environment variable %s not set", env_key)
            else:
                result[key] = value
        return result

    def _run_command(self, cmd: List[str]) -> subprocess.CompletedProcess:
        """Run the command with the configured environment."""
        try:
            cmd = [str(c) for c in cmd]
            self.logger.debug("Running command: %s", " ".join(cmd))
            return subprocess.run(cmd, check=True, shell=False, env=self.context.env)
        except subprocess.CalledProcessError as e:
            self.logger.error(
                "Command %s failed with exit code %s", " ".join(cmd), e.returncode
            )
            sys.exit(1)
        except FileNotFoundError:
            self.logger.error("Command %s not found", cmd[0])
            sys.exit(1)

    @property
    def logger(self):
        """Get logger instance."""
        return logging.getLogger("pp")
