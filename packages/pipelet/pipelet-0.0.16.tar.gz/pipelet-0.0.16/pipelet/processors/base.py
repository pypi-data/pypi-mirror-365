"""
BaseProcessor

This class serves as the base implementation for processing units in a pipeline. It provides a flexible and extensible
framework for chaining processors, handling subprocessors (parallel or branched processing), and managing exception
handling. It is designed to work with typed data through Python generics and provides several utility methods for
managing and interacting with processing chains.

Usage:
    - Define a specific processor by subclassing `BaseProcessor` and implementing the `process` method.
    - Use chaining (`>>`) to connect processors sequentially.
    - Use the `*` operator to assign subprocessors for parallel or conditional processing.

Attributes:
    _next (Optional["BaseProcessor"]): The next processor in the chain.
    _sub_processors (Optional[List["BaseProcessor"]]): List of subprocessors for parallel or branched processing.
"""

from abc import abstractmethod
from typing import Any, Generator, Generic, List, Optional, Type

from pipelet.processors import processor_types as p_types
from pipelet.processors.abc import AbstractProcessor
from pipelet.processors.meta import ProcessorMeta
from pipelet.storage.local_storage import LocalStorage
from pipelet.storage.storage_manager import StorageManager


class BaseProcessor(
    AbstractProcessor["BaseProcessor"],
    Generic[
        p_types.INPUT_DATA,
        p_types.YIELD_VALUE,
        p_types.VALUE_TO_SEND,
        p_types.RETURN_VALUE,
    ],
    metaclass=ProcessorMeta,
):
    """
    Base implementation for a processing unit in a pipeline.

    This class serves as the foundational structure for processors in a chain,
    supporting chaining of processing units, handling subprocessors (parallel or branched processing),
    and managing exception handling.

    Attributes:
        _next (Optional[BaseProcessor]): Reference to the next processor in the chain, or None if this is the last processor.
        _sub_processors (Optional[List[BaseProcessor]]): List of subprocessors for parallel or branched processing, or None if there are no subprocessors.
        _storage: Object of some storage for processors
    """

    _next: Optional["BaseProcessor[Any, Any, Any, Any]"] = None
    """Reference to the next processor in the chain, or None if this is the last processor."""

    _sub_next: Optional["BaseProcessor[Any, Any, Any, Any]"] = None
    """Reference to the sub next processor in the chain, or None if this is the last sub processor."""

    _sub_processors: Optional[List["BaseProcessor[Any, Any, Any, Any]"]] = None
    """List of subprocessors for parallel or branched processing, or None if there are no subprocessors."""

    # _storage: StorageManager
    # """Object of some storage for processors"""

    def __init__(
        self,
        white_exceptions: Optional[List[Type[Exception]]] = None,
    ) -> None:
        """
        Initializes the base processor.

        Args:
            white_exceptions (Optional[List[Type[BaseProcessorException]]]):
                A list of exception types that should be gracefully handled during processing.
        """
        self._white_exceptions: List[Type[Exception]] = white_exceptions or []
        # self._storage = StorageManager(storage=LocalStorage())

    # @property
    # def storage(
    #     self,
    # ) -> StorageManager:
    #     """
    #     Retrives the object of storage for processors

    #     Returns:
    #         StorageManager: object of storage for processors.
    #     """
    #     return self._storage

    @property
    def next(
        self,
    ) -> Optional["BaseProcessor[Any, Any, Any, Any]"]:
        """
        Retrieves the next processor in the chain.

        Returns:
            Optional["BaseProcessor"]: The next processor in the chain or None if this is the last processor.
        """
        return self._next

    @property
    def sub_next(
        self,
    ) -> Optional["BaseProcessor[Any, Any, Any, Any]"]:
        """
        Retrieves the next sub processor in the sub chain.

        Returns:
            Optional["BaseProcessor"]: The next sub processor in the sub chain or None if this is the last processor.
        """
        return self._sub_next

    @property
    def sub_processors(
        self,
    ) -> Optional[List["BaseProcessor[Any, Any, Any, Any]"]]:
        """
        Retrieves the list of subprocessors.

        Returns:
            Optional[List["BaseProcessor"]]: The list of sub-processors or None if no subprocessors are set.
        """
        return self._sub_processors

    @property
    def last_processor(
        self,
    ) -> "BaseProcessor[Any, Any, Any, Any]":
        """
        Retrieves the last processor in the chain.

        Returns:
            "BaseProcessor": The last processor in the chain.
        """
        return self._get_last_processor()

    def _get_last_processor(self) -> "BaseProcessor[Any, Any, Any, Any]":
        """
        Finds the last processor in the chain.

        Returns:
            BaseProcessor: The last processor in the chain.
        """
        last = self
        next_ = last._next
        while next_:
            last = next_
            next_ = last._next
        return last

    def set_next(
        self,
        next_: "BaseProcessor[Any, Any, Any, Any]",
    ) -> "BaseProcessor[p_types.INPUT_DATA, p_types.YIELD_VALUE, p_types.VALUE_TO_SEND, p_types.RETURN_VALUE]":
        """
        Sets the next processor in the chain.

        Args:
            next_ ("BaseProcessor"): The processor to add to the chain.

        Returns:
            "BaseProcessor": The current processor instance to allow chaining.
        """
        self.last_processor._next = next_
        return self

    def set_subnext(
        self,
        subnext_: "BaseProcessor[Any, Any, Any, Any]",
    ) -> "BaseProcessor[p_types.INPUT_DATA, p_types.YIELD_VALUE, p_types.VALUE_TO_SEND, p_types.RETURN_VALUE]":
        """
        Sets the subnext processor in the chain.

        Args:
            next_ ("BaseProcessor"): The processor to add to the sub chain.

        Returns:
            "BaseProcessor": The current processor instance to allow chaining.
        """
        self._sub_next = subnext_
        return self

    def set_subprocessors(
        self,
        sub_processors: List["BaseProcessor[Any, Any, Any, Any]"],
    ) -> "BaseProcessor[p_types.INPUT_DATA, p_types.YIELD_VALUE, p_types.VALUE_TO_SEND, p_types.RETURN_VALUE]":
        """
        Assigns a list of subprocessors for parallel processing or branching.

        Args:
            sub_processors (List["BaseProcessor"]): A list of subprocessors to assign.

        Returns:
            "BaseProcessor": The current processor instance to allow chaining.
        """
        self._sub_processors = sub_processors
        for i in range(len(sub_processors) - 1):
            sub_processors[i].set_subnext(sub_processors[i + 1])
        return self

    @abstractmethod
    def _handle(
        self, input_data: p_types.INPUT_DATA
    ) -> Generator[p_types.YIELD_VALUE, p_types.VALUE_TO_SEND, None]:
        """
        Core processing logic for a single processor stage.

        This method must be implemented by subclasses to define custom transformation or
        computation logic. It is called by the `process()` method and is expected to yield
        intermediate results that may be passed to the next processor in the chain.

        Args:
            input_data (p_types.INPUT_DATA): The input data specific to this processor stage.

        Yields:
            p_types.YIELD_VALUE: The intermediate result(s) of processing. These will be passed
                                to the next processor if defined.

        Returns:
            None: This generator should not return a value directly; `process()` handles full-chain return logic.

        Example:
            def _handle(self, input_data: str) -> Generator[str, None, None]:
                yield input_data.upper()
        """
        ...

    def process(
        self, input_data: p_types.INPUT_DATA
    ) -> Generator[
        p_types.YIELD_VALUE, p_types.VALUE_TO_SEND, p_types.RETURN_VALUE
    ]:
        """
        Executes the processing logic for the given input data.

        This is the default pipeline execution method that:
        1. Calls the internal `_handle()` method for custom processing logic.
        2. Forwards each output to the next processor in the chain (`_next`), if any.
        3. Runs any defined `sub_processors` in parallel, each receiving the original input data.
        4. Handles white-listed exceptions gracefully, while re-raising others.

        Args:
            input_data (p_types.INPUT_DATA): The input data to process.

        Yields:
            p_types.YIELD_VALUE: Intermediate results produced during processing.

        Returns:
            p_types.RETURN_VALUE: The return value is expected from the last generator stage (if any).

        Raises:
            Exception: Any exception not listed in `_white_exceptions` will be raised.
        """
        # Step 1: Perform main processor's logic via `_handle`
        for output in self._handle(input_data):
            # Step 2: Forward output to the next processor in the chain
            if self._next:
                yield from self._next.process(output)
            else:
                yield output

    def read_full_result(
        self, input_data: p_types.INPUT_DATA
    ) -> List[p_types.YIELD_VALUE]:
        """
        Processes the input data fully and collects all results in a list.

        This method executes the `process` method of the processor and collects all the results
        yielded by the generator into a list. It is useful when you need to gather all processed
        results at once instead of processing them lazily through iteration.

        Args:
            input_data (p_types.INPUT_DATA): The input data to process, which will be passed to
                                            the processor's `process` method.

        Returns:
            List[p_types.YIELD_VALUE]: A list containing all the results yielded by the processor's
                                        `process` method.

        Example:
            processor = SomeProcessor()
            results = processor.read_full_result(input_data)
            print(results)  # Outputs: ["Processed by SomeProcessor: input_data"]
        """

        gen = self.process(input_data)
        return [result for result in gen]

    def __len__(self) -> int:
        """
        Returns the total number of processors in the chain.

        Returns:
            int: The total number of processors in the chain.
        """
        length = 1
        current = self._next
        while current:
            length += 1
            current = current._next
        return length

    def __getitem__(self, index: int) -> "BaseProcessor[Any, Any, Any, Any]":
        """
        Retrieves the processor at the specified index in the chain.

        Args:
            index (int): The index of the processor to retrieve.

        Returns:
            "BaseProcessor": The processor at the given index.

        Raises:
            IndexError: If the index is out of range.
        """
        length = len(self)
        if index < 0:
            index += length
        if index < 0 or index >= length:
            raise IndexError("Index out of range")

        current = self
        for _ in range(index):
            if current._next is None:
                raise IndexError("Index out of range")
            current = current._next
        return current

    def __contains__(
        self,
        processor: "BaseProcessor[Any, Any, Any, Any]",
    ) -> bool:
        """
        Checks if a processor is present in the chain.

        Args:
            processor (BaseProcessor): The processor to check for.

        Returns:
            bool: True if the processor is in the chain, False otherwise.
        """
        current = self
        while current:
            if current is processor:
                return True
            current = current._next
        return False

    def __rshift__(
        self,
        next_: "BaseProcessor[Any, Any, Any, Any]",
    ) -> "BaseProcessor[p_types.INPUT_DATA, p_types.YIELD_VALUE, p_types.VALUE_TO_SEND, p_types.RETURN_VALUE]":
        """
        Adds a processor to the end of the chain using the `>>` operator.

        Args:
            next_ ("BaseProcessor"): The processor to append to the chain.

        Returns:
            "BaseProcessor": The current processor instance for further chaining.
        """
        self.last_processor.set_next(next_)
        return self

    def __mul__(
        self,
        subprocessors: List["BaseProcessor[Any, Any, Any, Any]"],
    ) -> "BaseProcessor[p_types.INPUT_DATA, p_types.YIELD_VALUE, p_types.VALUE_TO_SEND, p_types.RETURN_VALUE]":
        """
        Assigns subprocessors to the last processor in the chain using the `*` operator.

        Args:
            subprocessors (List["BaseProcessor"]): The list of subprocessors to assign.

        Returns:
            "BaseProcessor": The current processor instance for further chaining.
        """
        self.last_processor.set_subprocessors(subprocessors)
        return self

    def __repr__(self) -> str:
        """
        Returns a string representation of the processor chain.

        Returns:
            str: A formatted string that represents the processor chain and its subprocessors.
        """

        def format_processor(processor, level=0, is_subprocessor=False):
            """
            Formats a processor for string representation.

            Args:
                processor: The processor to format.
                level (int): The current indentation level (used for subprocessors).
                is_subprocessor (bool): Whether this processor is part of a subprocessor list.

            Returns:
                str: A formatted string representing the processor.
            """
            indent = "    " * level if is_subprocessor else ""
            connector = "->" if is_subprocessor else "-->"

            sub_processor_repr = ""
            if processor._sub_processors:
                sub_processor_repr = (
                    " -> [\n"
                    + ",\n".join(
                        (
                            format_processor(
                                sub_processor, level + 1, is_subprocessor=True
                            )
                            + f" -> \n {format_processor(sub_processor._next, level + 2, is_subprocessor=True)}"
                            if sub_processor._next is not None
                            else ""
                        )
                        for sub_processor in processor._sub_processors
                    )
                    + f"\n{indent}]"
                )

            return f"{indent}{connector} {processor}{sub_processor_repr}"

        # Build the main chain of processors.
        processors = []
        current = self
        while current:
            processors.append(format_processor(current))
            current = current._next

        # Combine the chain into a single string.
        chain_repr = "\n".join(processors)
        return f"Input data\n{chain_repr}\nResult"

    def __str__(self) -> str:
        """
        Returns a string representing the processor.

        Returns:
            str: The class name of the processor.
        """
        return self.__class__.__name__
