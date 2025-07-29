import asyncio
import inspect
import traceback
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, List

import aiofiles
from aioconsole import aprint


@dataclass
class LogEntry:
    context: List[str]


@dataclass
class MessageEntry(LogEntry):
    message: str
    caller: str
    metadata: dict[str, Any] | None = None


@dataclass
class ErrorEntry(LogEntry):
    error: Exception


class Writer(ABC):
    @abstractmethod
    async def write(self, entry: LogEntry): ...

    def format(self, entry: LogEntry):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        context_str = " / ".join(entry.context)

        match entry:
            case MessageEntry(message=message, caller=caller, metadata=metadata):
                header = f"{current_time} - {caller} - {context_str}"
                if metadata:
                    metadata_str = ", ".join(f"{k}={v}" for k, v in metadata.items())
                    header = f"{header} ({metadata_str})"
                payload = message
            case ErrorEntry(error=e):
                header = f"{current_time} - {context_str}"
                payload = "".join(traceback.format_exception(e))

        return f"{header}\n{payload}\n"


class FileWriter(Writer):
    def __init__(self, file: Path | str):
        self.file = Path(file) if isinstance(file, str) else file
        self.file.parent.mkdir(parents=True, exist_ok=True)

    async def write(self, entry: LogEntry):
        async with aiofiles.open(self.file, "a") as f:
            await f.write(self.format(entry))


class StdoutWriter(Writer):
    async def write(self, entry: LogEntry):
        await aprint(self.format(entry))


class Logger:
    def __init__(self, file: str | Path | None = None):
        self.writer = FileWriter(file) if file else StdoutWriter()
        self.stack = ContextVar[List[str]]("context", default=[])
        self.queue = asyncio.Queue()  # type: ignore
        self.runner = asyncio.create_task(self._run())

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc_info):
        await self.aclose()

    async def aclose(self):
        # first process all queued entries
        await self.queue.join()
        # then cancel the queue consumer
        self.runner.cancel()

    async def log(self, message: str, metadata: dict[str, Any] | None = None):
        """Log a message with optional metadata.

        Args:
            message: The message to log
            metadata: Dictionary of additional data to include
        """
        entry = MessageEntry(
            context=self.stack.get(),
            message=message,
            caller=self._get_caller_module_name(),
            metadata=metadata,
        )
        await self.queue.put(entry)

    async def log_error(self, e: Exception):
        """Log an exception with its full stack trace.

        Args:
            e: The exception to log.
        """
        entry = ErrorEntry(
            context=self.stack.get(),
            error=e,
        )
        await self.queue.put(entry)

    @asynccontextmanager
    async def context(self, frame: str):
        """A context manager that puts an additional context frame onto the current context stack.

        Example:
            ```python
            async with logger.context("User Login"):
                await logger.log("Attempting login")  # Logs with "User Login" context
                await db.query(...)
                await logger.log("Login successful")  # Logs with "User Login" context

                # Contexts can be nested
                async with logger.context("Profile"):
                    # Logs with "User Login / Profile" context
                    await logger.log("Loading user profile")
            ```

        Args:
            frame: The context frame to add

        Raises:
            Exception: Re-raises any exception that occurs within the context after logging it.
        """
        context = self.stack.get().copy()
        context.append(frame)
        token = self.stack.set(context)

        try:
            yield self
        except Exception as e:
            await self.log_error(e)
            raise
        finally:
            self.stack.reset(token)

    async def _run(self):
        while True:
            entry = await self.queue.get()
            await self.writer.write(entry)
            self.queue.task_done()

    def _get_caller_module_name(self):
        caller_frame = inspect.stack()[2]
        caller_module = inspect.getmodule(caller_frame[0])
        return caller_module.__name__  # type: ignore
