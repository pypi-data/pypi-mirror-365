import logging
import re
from pathlib import Path
from typing import Any, Optional, Self

from aa_psycopg.utils import read_yaml, read_file

try:
    from pydantic import BaseModel, Field, model_validator
    from pydantic.config import ConfigDict
except ImportError as e:
    raise ImportError(
        "The 'QueryConfig' feature requires extra dependencies.\n"
        "Install them with:\n\n"
        "    pip install aa-psycopg[pydantic]\n"
    ) from e


logger = logging.getLogger(__name__)


class QueryConfig(BaseModel):
    """Configuration for the query."""

    # Attributes
    path_query: Path | None = Field(
        default=None,
        exclude=True,  # Exclude path_query from model_dump
        description=(
            "Path to the '.sql' file containing the SQL query, "
            "either path_query or query must be provided, but not both. "
        ),
    )
    query: str | None = Field(
        default=None,
        description=(
            "SQL query as a string, either query or path_query must be provided, but not both. "
        ),
    )
    params: Optional[dict[str, Any]] = Field(
        default_factory=dict,
        description="Parameters for the SQL query as a dictionary.",
    )

    # Pydantic model configuration
    model_config: ConfigDict = ConfigDict(
        extra="forbid", frozen=True, arbitrary_types_allowed=True
    )

    @model_validator(mode="before")
    def _check_query(cls, values: dict) -> dict:
        """Check if the query file exists and read the query from it.

        Args:
            values (dict): The values to validate.
        Returns:
            dict: The validated values.
        Raises:
            AssertionError: If neither 'path_query' nor 'query' is provided, or if both are provided.
            AssertionError: If the query file does not exist or is not a SQL file.
        """
        path_query = values.get("path_query")
        query = values.get("query")
        assert bool(path_query) ^ bool(query), (
            "Either 'path_query' or 'query' must be provided, but not both."
        )
        if path_query:
            path_query = Path(path_query)
            assert path_query.exists(), f"Query file does not exist: {path_query}"
            assert path_query.suffix == ".sql", f"File is not a SQL file: {path_query}"
            values.update({"query": read_file(query)})
        return values

    @model_validator(mode="after")
    def _check_corresponding_query_and_params(cls, values: Self) -> Self:
        """Check if the parameters in the query and the params dictionary match.

        Args:
            values (Self): The current instance of QueryConfig.
        Returns:
            Self: The current instance of QueryConfig.
        Raises:
            ValueError: If the parameters in the query and the params dictionary do not match.

        """
        params_keys = set(values.params.keys())
        query_params = set(re.findall(r"%\((\w+)\)s", values.query, re.DOTALL))
        diff = params_keys.symmetric_difference(query_params)
        if diff:
            msg = (
                "The parameters in the query and the params dictionary do not match. \n"
                f"Params: {params_keys}\n"
                f"QueryParams: {query_params}\n"
                f"Query: {values.query}"
            )
            logger.error(msg)
            raise ValueError(msg)
        return values

    @classmethod
    def from_yaml(cls, yaml_path: str | Path) -> Self:
        """Load the report configuration from a YAML file.

        Args:
            yaml_path (str | Path): Path to the YAML file.
        Returns:
            QueryConfig: An instance of QueryConfig with the loaded data.
        Raises:
            AssertionError: If the YAML file does not exist or is not a valid YAML file.
        """
        yaml_path = Path(yaml_path)
        assert yaml_path.exists(), f"YAML file does not exist: {yaml_path}!"
        assert yaml_path.suffix in [".yaml", ".yml"], (
            f"File is not a YAML file: {yaml_path}"
        )
        data = read_yaml(yaml_path)
        return cls(**data)
