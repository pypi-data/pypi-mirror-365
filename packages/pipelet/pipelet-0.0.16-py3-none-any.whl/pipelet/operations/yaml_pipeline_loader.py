"""
YAMLPipelineLoader

This module provides a class for loading and converting pipeline definitions from YAML files
into the Pipelet framework format. It supports parsing simple and nested operations (`any`, `all`)
and applies transformations to specific keyword arguments, such as resolving exception names
into actual exception classes.

## Example YAML Pipeline Template:
```yaml
pipeline:
  - operation: path.to.ProcessorClass1
    kwargs:
      param1: value1
      param2: value2
      nested_param:
        path: path.to.NestedClass
        kwargs:
          nested_key: nested_value
      white_exceptions:
        - BuiltinException
        - path.to.CustomException

  - operation: path.to.ProcessorClass2
    kwargs:
      paramA: valueA
      retry_args:
        max_retries: 3
        delay: 2
        delay_step: 1
        retry_with_white_exc: true

  - operation: any
    operations:
      - operation: path.to.ProcessorClass3
        kwargs:
          option: setting
      - operation: path.to.ProcessorClass4
        kwargs:
          option: alternative_setting
```

## Usage Example:
```python
from yaml_pipeline_loader import YAMLPipelineLoader

loader = YAMLPipelineLoader("pipeline.yaml")
pipeline = loader.build_pipeline()

for result in pipeline.process(input_data):
    print(result)
```

## Features:
- **Parses YAML pipeline definitions** into `Op`, `OpAny`, or `OpAll` operations.
- **Handles nested operations (`any`, `all`)**, allowing flexible pipeline structures.
- **Processes keyword arguments**, applying transformations (e.g., resolving exception names).
- **Supports custom exception handling** via `custom_exceptions_factory`.
"""

from typing import Any, Dict, List, Type

import yaml

from pipelet.factories.exceptions_factory import custom_exceptions_factory
from pipelet.operations import Op, OpAll, OpAny, PipelineConverter
from pipelet.processors.base import BaseProcessor


class YAMLPipelineLoader:
    """
    A class responsible for loading and converting pipeline definitions
    from a YAML file into a format compatible with the Pipelet framework.

    This class parses YAML pipeline definitions, supports nested operations,
    and applies specific transformations to keyword arguments, such as
    converting exception names from strings into actual exception classes.
    """

    def __init__(self, yaml_path: str) -> None:
        """
        Initializes the pipeline loader with a YAML configuration file.

        :param yaml_path: Path to the YAML file containing the pipeline definition.
        """
        self.yaml_path: str = yaml_path
        self._config: Dict[str, Any] = self._load_yaml()

    def _load_yaml(self) -> Dict[str, Any]:
        """
        Loads and parses the YAML file containing the pipeline configuration.

        :return: A dictionary representing the parsed YAML content.
        :raises FileNotFoundError: If the specified YAML file does not exist.
        :raises ValueError: If there is an error parsing the YAML file.
        """
        try:
            with open(self.yaml_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except FileNotFoundError as e:
            raise FileNotFoundError(
                f"YAML file not found: {self.yaml_path}"
            ) from e
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML file: {e}") from e

    def _parse_simple_operation(self, op: str, kwargs: Dict[str, Any]) -> Op:
        """
        Parses a simple operation without nested operations.

        :param op: The operation name as a string.
        :param kwargs: A dictionary of keyword arguments for the operation.
        :return: An instance of Op.
        """
        return Op(operation=op, kwargs=self._process_op_kwargs(kwargs))

    def _parse_operation(self, step: Dict[str, Any]) -> Op | OpAny | OpAll:
        """
        Parses an operation from a YAML step configuration, supporting nested operations ('any' and 'all').

        :param step: A dictionary representing a step in the pipeline.
        :return: An operation instance (Op, OpAny, or OpAll).
        """
        operation_type: str = step["operation"]
        kwargs: Dict[str, Any] = step.get("kwargs", {})

        if operation_type in ("any", "all"):
            operations: List[Op | OpAny | OpAll] = [
                (
                    self._parse_operation(op)
                    if op["operation"] in ("any", "all")
                    else self._parse_simple_operation(
                        op["operation"], op.get("kwargs", {})
                    )
                )
                for op in step["operations"]
            ]
            return (
                OpAny(operations=operations, kwargs=kwargs)
                if operation_type == "any"
                else OpAll(operations=operations, kwargs=kwargs)
            )

        return self._parse_simple_operation(operation_type, kwargs)

    def _process_exceptions(
        self, exceptions: List[str]
    ) -> List[Type[Exception]]:
        """
        Converts a list of exception names from strings into actual Python exception classes.

        :param exceptions: A list of exception names as strings.
        :return: A list of corresponding exception classes.
        :raises ValueError: If an exception name cannot be resolved.
        """
        python_exceptions: List[Type[Exception]] = []
        for exc in exceptions:
            try:
                to_extend = custom_exceptions_factory([exc])
            except ValueError:
                try:
                    to_extend = [getattr(__import__("builtins"), exc)]
                except AttributeError:
                    raise ValueError(f"Unknown exception: {exc}")
            python_exceptions.extend(to_extend)
        return python_exceptions

    KWARG_PROCESSORS: Dict[str, Any] = {
        "white_exceptions": _process_exceptions,
    }

    def _process_op_kwargs(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes the keyword arguments for an operation, applying transformations
        based on predefined processors.

        :param kwargs: A dictionary of keyword arguments.
        :return: A processed dictionary with transformed values where applicable.
        """
        processed_kwargs: Dict[str, Any] = {}
        for key, value in kwargs.items():
            if key in self.KWARG_PROCESSORS:
                processed_kwargs[key] = self.KWARG_PROCESSORS[key](self, value)
            else:
                processed_kwargs[key] = value
        return processed_kwargs

    def build_pipeline(self) -> BaseProcessor:
        """
        Builds a pipeline based on the loaded YAML configuration.

        :return: A converted BaseProcessor instance representing the pipeline.
        :raises KeyError: If the YAML structure is invalid or missing required keys.
        """
        if "pipeline" not in self._config:
            raise KeyError("YAML file must contain a 'pipeline' key.")

        pipeline: List[Op | OpAny | OpAll] = [
            self._parse_operation(step) for step in self._config["pipeline"]
        ]
        return PipelineConverter(
            pipeline=pipeline, config=self._config
        ).convert()
