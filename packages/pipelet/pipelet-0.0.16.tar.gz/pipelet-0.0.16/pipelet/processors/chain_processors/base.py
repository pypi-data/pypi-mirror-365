"""
Processor Classes for ETL Chain Operations

This module contains two key processor classes used in the ETL chain-of-responsibility pattern:
`ChainAnyProcessor` and `ChainAllProcessor`.

1. ChainAnyProcessor:
   - Processes data through a sequence of sub-processors, one at a time.
   - The first sub-processor to handle the data is used.
   - Optionally moves the successful processor to the front of the list for optimization.

2. ChainAllProcessor:
   - Runs all sub-processors in parallel (multi-threaded or multi-process).
   - Yields results as they become available.
   - Logs exceptions if any processor fails.

Both processors inherit from `BaseProcessor` and are designed for flexible ETL pipelines.
"""

import concurrent.futures
from typing import Any, Generator, List, Optional, Type

from pipelet.exceptions.base import ProcessorStopIteration
from pipelet.log import logger_factory
from pipelet.processors.base import BaseProcessor

logger = logger_factory()


class ChainAnyProcessor(BaseProcessor[Any, Any, None, None]):
    """
    A processor that processes input data through a list of sub-processors in sequence.

    The first processor that successfully yields results is used.
    Optionally, the successful processor is moved to the front of the list
    to optimize future processing.
    """

    _last_success_processor: Optional[BaseProcessor[Any, Any, None, None]] = (
        None
    )

    def __init__(
        self,
        white_exceptions: Optional[List[Type[Exception]]] = None,
        success_processor_to_front: bool = True,
    ) -> None:
        super().__init__(white_exceptions)
        self._success_processor_to_front = success_processor_to_front

    def _move_processor_to_front(self, index: int) -> None:
        """
        Move the sub-processor at the specified index to the front of the list.

        Args:
            index (int): Index of the processor to move.
        """
        if self._sub_processors:
            self._sub_processors.insert(0, self._sub_processors.pop(index))

    def _handle(self, input_data: Any) -> Generator[Any, None, None]:
        """
        Try to handle the input data using sub-processors in order.

        Each processor is attempted until one yields a result.
        If successful, its results are yielded and optionally passed to the next processor.

        Args:
            input_data (Any): The input data to process.

        Yields:
            Any: The output from a successful processor.
        """
        if not self._sub_processors:
            raise ValueError(
                f"{self.__class__.__name__} must have at least one subprocessor."
            )

        for index, processor in enumerate(self._sub_processors):
            try:
                # Attempt to process input
                generator = processor.process(input_data)
                for result in generator:
                    yield result
                    if self._success_processor_to_front and index > 0:
                        self._move_processor_to_front(index)
                break  # Stop after first successful processor
            except ProcessorStopIteration:
                logger.warning(
                    f"Processor '{processor}' could not handle data."
                )
        else:
            logger.error(
                "All processors in the chain failed to handle the data."
            )


class ChainAllProcessor(BaseProcessor[Any, Any, None, None]):
    """
    A processor that runs all sub-processors in parallel using threads or processes.

    Results are yielded as soon as any processor produces output.
    Exceptions are logged without interrupting the pipeline.
    """

    def __init__(
        self,
        white_exceptions: Optional[List[Type[Exception]]] = None,
        use_threads: bool = False,
        result_timeout: Optional[int] = None,
    ) -> None:
        super().__init__(white_exceptions)
        self._executor = (
            concurrent.futures.ThreadPoolExecutor
            if use_threads
            else concurrent.futures.ProcessPoolExecutor
        )
        self._result_timeout = result_timeout

    def _handle(self, input_data: Any) -> Generator[Any, None, None]:
        """
        Process input data by executing all sub-processors in parallel.

        Each sub-processor runs in its own thread or process. Partial results
        are yielded as soon as they are ready. Any exceptions are logged.

        Args:
            input_data (Any): The data to be processed.

        Yields:
            Any: Partial results from any sub-processor.
        """
        if not self._sub_processors:
            raise ValueError(
                f"{self.__class__.__name__} must have at least one subprocessor."
            )

        with self._executor() as executor:
            futures = {
                executor.submit(
                    (
                        processor.read_full_result  # safer in thread mode
                        if self._executor
                        is concurrent.futures.ThreadPoolExecutor
                        else processor.process
                    ),
                    input_data,
                ): processor
                for processor in self._sub_processors
            }

            for future in concurrent.futures.as_completed(
                futures, timeout=self._result_timeout
            ):
                try:
                    result = future.result()
                    for item in result:
                        yield item
                except Exception as exc:
                    processor = futures[future]
                    logger.error(f"Processor '{processor}' failed with: {exc}")
