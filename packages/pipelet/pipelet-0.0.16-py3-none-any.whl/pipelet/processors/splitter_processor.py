from typing import Any, Callable, Generator, List, Optional, Type

from pipelet.processors.base import BaseProcessor


class SplitterProcessor(BaseProcessor[Any, Any, None, None]):
    """
    SplitterProcessor splits input data into parts using a provided function and yields them sequentially.

    This processor is useful for breaking down input data into smaller components,
    such as splitting a string into words, dividing a list into sublists, or
    decomposing JSON objects into their individual elements.

    Args:
        splitter (Callable[[Any], List[Any]]):
            A function that takes the input data and returns a list of parts.

    Attributes:
        splitter (Callable[[Any], List[Any]]):
            The function used to split the input data.
    """

    def __init__(
        self,
        splitter: Callable[[Any], List[Any]],
        white_exceptions: Optional[List[Type[Exception]]] = None,
        *args,
        **kwargs
    ):
        """
        Initializes the SplitterProcessor with a splitting function.

        Args:
            splitter (Callable[[Any], List[Any]]):
                The function to use for splitting the input data.
            white_exceptions (Optional[List[Type[Exception]]]):
                A list of exception types that should be caught and ignored (e.g., for logging only).
            *args: Additional positional arguments passed to the BaseProcessor.
            **kwargs: Additional keyword arguments passed to the BaseProcessor.
        """
        super().__init__(white_exceptions, *args, **kwargs)
        self.splitter = splitter

    def _handle(self, input_data: Any) -> Generator[Any, None, None]:
        """
        Core logic to split input data into parts using the splitter function.

        This method is invoked by the `process` method defined in the base class.
        It yields each part one by one.

        Args:
            input_data (Any): The input data to be split.

        Yields:
            Any: Each individual part obtained by splitting the input.
        """
        parts = self.splitter(input_data)

        for part in parts:
            yield part
