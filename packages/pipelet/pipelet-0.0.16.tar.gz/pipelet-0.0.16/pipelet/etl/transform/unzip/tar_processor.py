import io
import tarfile
from os import PathLike
from pathlib import Path
from typing import Generator, List, Optional, Type, Union

from pipelet.exceptions.base import ProcessorStopIteration
from pipelet.exceptions.unzip_processor import UnzipError
from pipelet.log import logger_factory
from pipelet.processors.base import BaseProcessor
from pipelet.processors.file_system import (
    AbstractFileSystemManager,
    FileModeEnum,
)

logger = logger_factory()


class TarExtractProcessor(
    BaseProcessor[
        Union[str, PathLike[str]], Union[str, PathLike[str]], None, None
    ],
):
    """
    A processor that handles extracting `.tar` archives (including compressed formats).

    This processor takes a `.tar` file (or compressed `.tar` variants like `.tar.gz`, `.tgz`),
    extracts its contents, and yields the paths of the extracted files and directories.

    Attributes:
        _file_system_manager (AbstractFileSystemManager): File system manager for file operations.
        _white_exceptions (List[Type[Exception]]): List of exceptions to bypass.
        _auto_delete (bool): Flag to delete the tar file after processing.
        _batch_size (Optional[int]): The batch size in bytes for extracting large files.
    """

    def __init__(
        self,
        file_system_manager: AbstractFileSystemManager[
            Union[str, PathLike[str]], Union[str, bytes]
        ],
        white_exceptions: Optional[List[Type[Exception]]] = None,
        auto_delete: bool = True,
        batch_size: Optional[int] = None,
    ) -> None:
        super().__init__(white_exceptions)
        self._file_system_manager = file_system_manager
        self._auto_delete = auto_delete
        self._batch_size = (
            batch_size * 1024 * 1024 if batch_size is not None else None
        )

    def _handle(
        self, input_data: Union[str, PathLike[str]]
    ) -> Generator[Union[str, PathLike[str]], None, None]:
        """
        Internal method for extracting tar file contents.

        This method performs actual file extraction logic. It reads the file,
        opens the tar archive, iterates through its members, and extracts
        them to the filesystem.

        Args:
            input_data (Union[str, PathLike[str]]): Path to the tar file.

        Yields:
            Union[str, PathLike[str]]: Paths to extracted files or directories.

        Raises:
            UnzipError: If archive format is unsupported or extraction fails.
        """
        suffix = Path(input_data).suffix
        if suffix not in [".tar", ".gz", ".bz2", ".xz", ".tgz", ".tbz2"]:
            raise UnzipError(
                input_data,
                f"File has an extension '{suffix}', expected a supported .tar format",
            )

        content = self._file_system_manager.read_file(input_data)

        if isinstance(content, (str, PathLike)):
            archive_source = content  # Path to archive
        elif isinstance(content, (bytes, bytearray, memoryview)):
            archive_source = io.BytesIO(content)  # Archive in memory
        else:
            raise TypeError(
                f"Unsupported content type: {type(content).__name__}. Expected str, bytes, or PathLike."
            )

        extracted_paths: List[Union[str, PathLike[str]]] = []

        try:
            if isinstance(archive_source, io.BytesIO):
                tar = tarfile.open(fileobj=archive_source, mode="r:*")
            else:
                tar = tarfile.open(name=archive_source, mode="r:*")

            with tar:
                for member in tar.getmembers():
                    extracted_path = self._file_system_manager.get_path(
                        member.name
                    )

                    if member.isdir():
                        # Ensure the directory exists
                        Path(extracted_path).mkdir(parents=True, exist_ok=True)
                        logger.info(f"Created directory: {member.name}")
                        extracted_paths.append(extracted_path)

                    elif member.isfile():
                        # Extract files with optional batching
                        source_file = tar.extractfile(member)
                        if source_file is not None:
                            if self._batch_size is not None:
                                while chunk := source_file.read(
                                    self._batch_size
                                ):
                                    self._file_system_manager.append_to_file(
                                        extracted_path, chunk
                                    )
                            else:
                                self._file_system_manager.create_file(
                                    extracted_path, source_file.read()
                                )
                            extracted_paths.append(extracted_path)
                        else:
                            logger.warning(
                                f"Could not extract file: {member.name}"
                            )

                    else:
                        logger.info(
                            f"Skipping unsupported member type: {member.name}"
                        )

        except Exception as e:
            raise UnzipError(input_data, f"Failed to extract tar file: {e}")

        yield from extracted_paths

    def process(
        self,
        input_data: Union[str, PathLike[str]],
    ) -> Generator[Union[str, PathLike[str]], None, None]:
        """
        Public processing method that delegates to `_handle`.

        Passes extracted items to the next processor in the pipeline, if any.

        Args:
            input_data (Union[str, PathLike[str]]): Path to tar file.

        Yields:
            Union[str, PathLike[str]]: Extracted paths.
        """
        items = self._handle(input_data)

        if self.next is not None:
            for item in items:
                try:
                    yield from self.next.process(item)
                except ProcessorStopIteration:
                    pass
        else:
            yield from items

        if self._auto_delete and not self.sub_next:
            self._file_system_manager.delete_file(input_data)

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__}"
            f"(auto_delete={self._auto_delete}, "
            f"batch_size={self._batch_size})"
        )
