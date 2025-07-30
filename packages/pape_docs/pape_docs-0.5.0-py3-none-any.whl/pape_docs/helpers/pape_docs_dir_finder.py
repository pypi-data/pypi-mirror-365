# # # # # # # # # # # # # # # # # # # #
# Pape Docs
# Copyright 2025 Carter Pape
#
# See file LICENSE for licensing terms.
# # # # # # # # # # # # # # # # # # # #

"""A module that provides the `PapeDocsDirectoryFinder` class."""

import logging
import pathlib
import tomllib

import dotenv

_logger = logging.getLogger(__name__)


class PapeDocsDirectoryFinder:
    """
    A class that facilitates the search for a pape-docs, based on a starting location.

    If there is no explicit or implicit definition, the function returns `None`.
    """

    def find_from_explicit_definition(
        self,
        *,
        for_directory: pathlib.Path,
        or_any_parent: bool = True,
    ) -> pathlib.Path | None:
        """
        Perform a search for an explicit pape-docs definition, starting at the specified directory.

        The search for an explicit definition starts at the `for_directory`, looking in the
        following files (in order, stopping when an explicit definition is found):

        1. `.env`
        2. `.pape-docs`
        3. `pyproject.toml`

        If there is no explicit definition in `for_directory`, and `or_any_parent == True`, then the
        search continues in the parent and (if necessary) goes until hitting the system root.

        Returns `None` if no explicit definition is found.
        """
        self._current_directory = for_directory
        search_parents = or_any_parent

        if search_parents:
            explicit_value = self._explicit_value_from_current_directory()

            while (
                explicit_value is None and self._current_directory != self._current_directory.parent
            ):
                self._current_directory = self._current_directory.parent
                explicit_value = self._explicit_value_from_current_directory()

            return explicit_value

        return self._explicit_value_from_current_directory()

    def find_from_implicit_definition(
        self,
        *,
        for_directory: pathlib.Path,
    ) -> pathlib.Path | None:
        """
        Return the pape-docs directory path from an implicit definition.

        If there is a `pape-docs` directory in the `search_start_dir_path`, that is the value that
        this function returns. Otherwise, the search continues in the parent, and so on until the
        system root.

        If no `pape-docs` directories are found, returns `None`.
        """
        self._current_directory = for_directory
        for directory in [
            self._current_directory,
            *list(self._current_directory.parents),
        ]:
            potential_docs_dir = directory / "pape-docs"
            if potential_docs_dir.is_dir():
                return potential_docs_dir

        return None

    def _explicit_value_from_current_directory(self) -> pathlib.Path | None:
        return (
            self.value_from_dot_env(self._current_directory / ".env")
            or self.value_from_dot_pape_docs(self._current_directory / ".pape-docs")
            or self.value_from_pyproject_toml(self._current_directory / "pyproject.toml")
        )

    @staticmethod
    def value_from_dot_env(potential_dot_env_path: pathlib.Path) -> pathlib.Path | None:
        """
        Given a path to .env, provide the pape-docs directory definition provided in the file.

        If the file doesn't exist, or there is no definition for the pape-docs directory in the
        file, returns None.
        """
        if not potential_dot_env_path.exists():
            return None

        dotenv_value = dotenv.main.DotEnv(potential_dot_env_path).get("PAPE_DOCS_DIR")
        if dotenv_value:
            return potential_dot_env_path.parent / dotenv_value

        _logger.info(
            "Found %s, but it didn't contain a PAPE_DOCS_DIR value. Skipping.",
            potential_dot_env_path,
        )
        return None

    @staticmethod
    def value_from_dot_pape_docs(
        potential_dot_pape_docs_path: pathlib.Path,
    ) -> pathlib.Path | None:
        """
        Given a path to .pape-docs, provide the pape-docs directory definition provided in the file.

        If the file doesn't exist, or there is no definition for the pape-docs directory in the
        file, returns None.
        """
        if not potential_dot_pape_docs_path.exists():
            return None

        dot_pape_docs_contents = potential_dot_pape_docs_path.read_text().strip()
        if dot_pape_docs_contents:
            return potential_dot_pape_docs_path.parent / dot_pape_docs_contents

        _logger.info(
            "Found %s, but it was empty. Skipping.",
            potential_dot_pape_docs_path,
        )
        return None

    @staticmethod
    def value_from_pyproject_toml(
        potential_pyproject_toml_path: pathlib.Path,
    ) -> pathlib.Path | None:
        """
        Given a pyprojec.toml, provide the `pape-docs` directory path provided in the file.

        If the file doesn't exist, or there is no definition for the pape-docs directory in the
        file, returns None.
        """
        if not potential_pyproject_toml_path.exists():
            return None

        with potential_pyproject_toml_path.open("r", encoding="utf-8") as f:
            pyproject_content = tomllib.loads(f.read())

        tool_config = pyproject_content.get("tool", {}).get("pape-docs", {})
        if "docs-dir" in tool_config:
            return potential_pyproject_toml_path.parent / tool_config["docs-dir"]

        _logger.info(
            "Found %s, but it didn't contain [tool.pape-docs].docs-dir. Skipping.",
            potential_pyproject_toml_path,
        )
        return None

    def search(
        self,
        *,
        starting_at_directory: pathlib.Path,
    ) -> pathlib.Path | None:
        """
        Search for an explicit definition then, if necessary, an implicit definition.

        If the function finds neither an explicit nor implicit definition, it returns `None`.
        """
        return self.find_from_explicit_definition(
            for_directory=starting_at_directory,
        ) or self.find_from_implicit_definition(
            for_directory=starting_at_directory,
        )
