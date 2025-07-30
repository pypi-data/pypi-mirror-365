from typing import Any, Dict, Sequence, Union

from pipelet.operations.operations import (
    Op,
    OpAll,
    OpAny,
    get_processor_for_operation,
)
from pipelet.processors import processors_to_chain
from pipelet.processors.base import BaseProcessor


class PipelineConverter:
    """
    Converts a list of operations and chains into a unified processor.

    This class takes a sequence of pipeline operations and a configuration dictionary,
    converting them into a single executable processor.

    Attributes:
        _pipeline (Sequence[Op | OpAny | OpAll]):
            A sequence of operations and/or nested chains defined in the pipeline.
        _config (Dict[str, Any] | None = None):
            A dictionary containing pipeline configuration parameters, which can be used
            to modify processor behavior dynamically.
    """

    def __init__(
        self,
        pipeline: Sequence[Union[Op, OpAny, OpAll]],
        config: Dict[str, Any] | None = None,
    ) -> None:
        """
        Initializes the PipelineConverter with a sequence of operations and a configuration.

        Args:
            pipeline (Sequence[Op | OpAny | OpAll]):
                Sequence of operations and/or nested chains forming the pipeline.
            config (Dict[str, Any] | None = None):
                Configuration parameters that may affect the pipeline's behavior.
        """
        self._pipeline = pipeline
        self._config = config or {}

    def convert(self) -> BaseProcessor[Any, Any, Any, Any]:
        """
        Converts the pipeline into a unified processor.

        This method processes each operation or chain, applies the stored configuration,
        and constructs a chained processor structure ready for execution.

        Returns:
            BaseProcessor[Any, Any, Any, Any]:
                A unified processor for the entire pipeline, which can be executed
                as part of the Pipelet framework.

        Raises:
            ValueError: If any operation or chain is invalid or cannot be converted.
        """
        processors = [get_processor_for_operation(op) for op in self._pipeline]
        processor = processors_to_chain(processors)
        return processor
