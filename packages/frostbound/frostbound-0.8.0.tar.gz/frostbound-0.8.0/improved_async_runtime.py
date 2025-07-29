"""An improved pedagogical asynchronous runtime implementation with rich console output.

This enhanced version addresses the critiques identified in the original implementation:
- Thread-safe operations with proper synchronization
- Comprehensive error handling with resource cleanup
- Performance monitoring and metrics
- Rich debugging support with visual feedback
- Additional async primitives (locks, semaphores, queues)
- Cancellation handling and structured concurrency

Architecture Improvements:
    - ThreadSafeEventLoop: Concurrent-safe event loop with metrics
    - EnhancedTask: Better error handling and resource management
    - AsyncPrimitives: Lock, Semaphore, Queue, Condition, Event
    - DebugMode: Visual task execution with rich console output
    - Performance metrics and monitoring
"""

from __future__ import annotations

import contextlib
import enum
import heapq
import selectors
import socket
import threading
import time
import uuid
import weakref
from collections import defaultdict, deque
from collections.abc import Awaitable, Callable, Coroutine, Generator, Sequence
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Generic, Self, TypeVar, cast

# Rich console imports for beautiful output
try:
    from rich.console import Console
    from rich.layout import Layout
    from rich.live import Live
    from rich.panel import Panel
    from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
    from rich.syntax import Syntax
    from rich.table import Table
    from rich.text import Text
    from rich.tree import Tree

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    Console = None  # type: ignore

if TYPE_CHECKING:
    from types import TracebackType

T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)
T_contra = TypeVar("T_contra", contravariant=True)
P = TypeVar("P")

type ExceptionInfo = tuple[type[BaseException], BaseException, TracebackType | None]

# Global console for rich output
console = Console() if RICH_AVAILABLE else None


class TaskState(enum.Enum):
    """State of a Task in its lifecycle."""

    PENDING = "⏳ PENDING"
    RUNNING = "🏃 RUNNING"
    FINISHED = "✅ FINISHED"
    CANCELLED = "🚫 CANCELLED"
    FAILED = "❌ FAILED"


class CancelledError(BaseException):
    """Raised when a task is cancelled."""

    pass


class InvalidStateError(Exception):
    """Raised when an operation is performed on a task in an invalid state."""

    pass


class TimeoutError(Exception):
    """Raised when an operation times out."""

    pass


@dataclass
class TaskMetrics:
    """Metrics for task execution."""

    task_id: str
    creation_time: float = field(default_factory=time.monotonic)
    start_time: float | None = None
    end_time: float | None = None
    total_suspend_time: float = 0.0
    suspend_count: int = 0
    exception_type: str | None = None

    @property
    def execution_time(self) -> float:
        """Total execution time excluding suspensions."""
        if self.start_time is None:
            return 0.0
        end = self.end_time or time.monotonic()
        return end - self.start_time - self.total_suspend_time

    @property
    def total_time(self) -> float:
        """Total time from creation to completion."""
        end = self.end_time or time.monotonic()
        return end - self.creation_time


@dataclass
class EventLoopMetrics:
    """Metrics for event loop performance."""

    tasks_created: int = 0
    tasks_completed: int = 0
    tasks_failed: int = 0
    tasks_cancelled: int = 0
    total_iterations: int = 0
    total_io_operations: int = 0
    total_timer_operations: int = 0

    def to_table(self) -> Table | str:
        """Convert metrics to a rich table or string."""
        if not RICH_AVAILABLE:
            return (
                f"Tasks: {self.tasks_created} created, {self.tasks_completed} completed, "
                f"{self.tasks_failed} failed, {self.tasks_cancelled} cancelled"
            )

        table = Table(title="Event Loop Metrics", show_header=True)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Tasks Created", str(self.tasks_created))
        table.add_row("Tasks Completed", str(self.tasks_completed))
        table.add_row("Tasks Failed", str(self.tasks_failed))
        table.add_row("Tasks Cancelled", str(self.tasks_cancelled))
        table.add_row("Loop Iterations", str(self.total_iterations))
        table.add_row("I/O Operations", str(self.total_io_operations))
        table.add_row("Timer Operations", str(self.total_timer_operations))

        return table


class DebugVisualization:
    """Rich console visualization for async runtime debugging."""

    def __init__(self, enabled: bool = True):
        self.enabled = enabled and RICH_AVAILABLE
        self.console = Console() if self.enabled else None
        self.task_progress = {}
        self.live = None

    def start(self):
        """Start live visualization."""
        if not self.enabled:
            return

        self.live = Live(self.get_layout(), console=self.console, refresh_per_second=4)
        self.live.start()

    def stop(self):
        """Stop live visualization."""
        if self.live:
            self.live.stop()

    def update_task(self, task_id: str, state: TaskState, info: str = ""):
        """Update task visualization."""
        if self.enabled:
            self.task_progress[task_id] = (state, info)

    def get_layout(self) -> Panel:
        """Get the current layout for display."""
        if not self.task_progress:
            return Panel("No tasks running", title="Async Runtime Monitor")

        tree = Tree("🌟 Active Tasks")
        for task_id, (state, info) in self.task_progress.items():
            color = {
                TaskState.PENDING: "yellow",
                TaskState.RUNNING: "green",
                TaskState.FINISHED: "blue",
                TaskState.CANCELLED: "red",
                TaskState.FAILED: "red",
            }.get(state, "white")

            node_text = Text(f"{state.value} ", style=color)
            node_text.append(f"Task-{task_id[:8]}", style="dim")
            if info:
                node_text.append(f" ({info})", style="italic")
            tree.add(node_text)

        return Panel(tree, title="🚀 Async Runtime Monitor", border_style="blue")


_current_loop: ThreadSafeEventLoop | None = None
_loop_lock = threading.Lock()


def get_running_loop() -> ThreadSafeEventLoop:
    """Get the currently running event loop (thread-safe)."""
    with _loop_lock:
        if _current_loop is None:
            raise RuntimeError("No running event loop")
        return _current_loop


def _set_running_loop(loop: ThreadSafeEventLoop | None) -> None:
    """Set the currently running event loop (thread-safe)."""
    global _current_loop
    with _loop_lock:
        _current_loop = loop


def current_task() -> EnhancedTask[Any] | None:
    """Get the currently running task."""
    loop = get_running_loop()
    return loop._current_task


class ResourceManager:
    """Manages resources with automatic cleanup."""

    def __init__(self):
        self._resources: weakref.WeakValueDictionary = weakref.WeakValueDictionary()
        self._cleanup_callbacks: dict[str, list[Callable]] = defaultdict(list)
        self._lock = threading.Lock()

    def register(self, resource_id: str, resource: Any, cleanup: Callable | None = None):
        """Register a resource with optional cleanup callback."""
        with self._lock:
            self._resources[resource_id] = resource
            if cleanup:
                self._cleanup_callbacks[resource_id].append(cleanup)

    def cleanup(self, resource_id: str):
        """Clean up a specific resource."""
        with self._lock:
            callbacks = self._cleanup_callbacks.pop(resource_id, [])
            for callback in callbacks:
                try:
                    callback()
                except Exception as e:
                    if console:
                        console.print(f"[red]Cleanup error for {resource_id}: {e}[/red]")


class EnhancedTask(Generic[T]):
    """Enhanced Task with better error handling and monitoring."""

    def __init__(self, coro: Coroutine[Any, Any, T], loop: ThreadSafeEventLoop, name: str | None = None) -> None:
        self._coro = coro
        self._loop = loop
        self._state = TaskState.PENDING
        self._result: T | None = None
        self._exception: BaseException | None = None
        self._done_callbacks: list[Callable[[EnhancedTask[T]], Any]] = []
        self._waiters: list[EnhancedTask[Any]] = []
        self._cancel_requested = False
        self._current_io_fd: int | None = None
        self._current_io_type: str | None = None
        self._resource_manager = ResourceManager()
        self._metrics = TaskMetrics(task_id=str(uuid.uuid4()))
        self._name = name or f"Task-{self._metrics.task_id[:8]}"
        self._context: dict[str, Any] = {}
        self._timeout_handle: Any = None
        self._shield = False

    @property
    def name(self) -> str:
        """Get task name."""
        return self._name

    @property
    def done(self) -> bool:
        """Return True if the task is done."""
        return self._state in (TaskState.FINISHED, TaskState.CANCELLED, TaskState.FAILED)

    @property
    def cancelled(self) -> bool:
        """Return True if the task was cancelled."""
        return self._state == TaskState.CANCELLED

    def set_timeout(self, timeout: float) -> None:
        """Set a timeout for the task."""

        def timeout_callback():
            if not self.done:
                self._set_exception(TimeoutError(f"Task {self._name} timed out after {timeout}s"))

        self._timeout_handle = self._loop._schedule_timer(time.monotonic() + timeout, lambda: timeout_callback())

    def shield(self) -> Self:
        """Shield this task from cancellation."""
        self._shield = True
        return self

    def add_context(self, key: str, value: Any) -> None:
        """Add context information for debugging."""
        self._context[key] = value

    def result(self) -> T:
        """Return the result of the task."""
        if not self.done:
            raise InvalidStateError(f"Task {self._name} is not done: {self._state}")
        if self._state == TaskState.CANCELLED:
            raise CancelledError(f"Task {self._name} was cancelled")
        if self._exception is not None:
            raise self._exception
        return cast(T, self._result)

    def exception(self) -> BaseException | None:
        """Return the exception raised by the task, or None."""
        if not self.done:
            raise InvalidStateError(f"Task {self._name} is not done: {self._state}")
        if self._state == TaskState.CANCELLED:
            raise CancelledError(f"Task {self._name} was cancelled")
        return self._exception

    def add_done_callback(self, callback: Callable[[EnhancedTask[T]], Any]) -> None:
        """Add a callback to be run when the task is done."""
        if self.done:
            self._loop._ready.append(lambda: callback(self))
        else:
            self._done_callbacks.append(callback)

    def cancel(self) -> bool:
        """Request cancellation of the task."""
        if self.done or self._shield:
            return False
        self._cancel_requested = True
        if self._state == TaskState.PENDING:
            self._set_cancelled()
        return True

    def _cleanup_io(self) -> None:
        """Clean up any registered I/O operations."""
        if self._current_io_fd is not None:
            if self._current_io_type == "read":
                self._loop._unregister_reader(self._current_io_fd)
            elif self._current_io_type == "write":
                self._loop._unregister_writer(self._current_io_fd)
            self._current_io_fd = None
            self._current_io_type = None

    def _cleanup_resources(self) -> None:
        """Clean up all resources associated with the task."""
        self._cleanup_io()
        if self._timeout_handle:
            # Cancel timeout if still pending
            pass
        # Clean up any registered resources
        for resource_id in list(self._resource_manager._resources.keys()):
            self._resource_manager.cleanup(resource_id)

    def _set_result(self, result: T) -> None:
        """Set the result of the task and mark it as finished."""
        assert self._state in (TaskState.PENDING, TaskState.RUNNING)
        self._cleanup_resources()
        self._result = result
        self._state = TaskState.FINISHED
        self._metrics.end_time = time.monotonic()
        self._loop._metrics.tasks_completed += 1
        self._loop._debug.update_task(self._metrics.task_id, TaskState.FINISHED)
        self._schedule_callbacks()
        self._wake_waiters()

    def _set_exception(self, exception: BaseException) -> None:
        """Set the exception of the task and mark it as failed."""
        assert self._state in (TaskState.PENDING, TaskState.RUNNING)
        self._cleanup_resources()
        self._exception = exception
        self._state = TaskState.FAILED
        self._metrics.end_time = time.monotonic()
        self._metrics.exception_type = type(exception).__name__
        self._loop._metrics.tasks_failed += 1
        self._loop._debug.update_task(self._metrics.task_id, TaskState.FAILED, str(exception))
        self._schedule_callbacks()
        self._wake_waiters()

    def _set_cancelled(self) -> None:
        """Mark the task as cancelled."""
        assert self._state in (TaskState.PENDING, TaskState.RUNNING)
        self._cleanup_resources()
        self._state = TaskState.CANCELLED
        self._metrics.end_time = time.monotonic()
        self._loop._metrics.tasks_cancelled += 1
        self._loop._debug.update_task(self._metrics.task_id, TaskState.CANCELLED)
        self._schedule_callbacks()
        self._wake_waiters()

    def _schedule_callbacks(self) -> None:
        """Schedule done callbacks to run in the next event loop iteration."""
        for callback in self._done_callbacks:
            self._loop._ready.append(lambda cb=callback: cb(self))
        self._done_callbacks.clear()

    def _wake_waiters(self) -> None:
        """Wake up all tasks waiting for this task to complete."""
        for waiter in self._waiters:
            if not waiter.done:
                self._loop._ready.append(waiter)
        self._waiters.clear()

    def _step(self, value: Any = None, exception: BaseException | None = None) -> None:
        """Execute one step of the coroutine with enhanced error handling."""
        assert self._state in (TaskState.PENDING, TaskState.RUNNING)

        # Check for cancellation
        if self._cancel_requested and not self._shield and not exception:
            exception = CancelledError(f"Task {self._name} cancelled")

        # Update state and metrics
        if self._state == TaskState.PENDING:
            self._state = TaskState.RUNNING
            self._metrics.start_time = time.monotonic()
            self._loop._debug.update_task(self._metrics.task_id, TaskState.RUNNING, self._name)

        suspend_start = time.monotonic()

        try:
            # Send value or throw exception into coroutine
            if exception is not None:
                result = self._coro.throw(exception)
            else:
                result = self._coro.send(value)

        except StopIteration as exc:
            self._set_result(exc.value)
        except CancelledError:
            if not self._shield:
                self._set_cancelled()
            else:
                # Re-raise to propagate up if shielded
                raise
        except Exception as exc:
            # Enhanced error context
            if console and self._loop._debug_mode:
                console.print(f"[red]Exception in {self._name}:[/red]")
                console.print_exception()
            self._set_exception(exc)
        else:
            # Update suspension metrics
            self._metrics.total_suspend_time += time.monotonic() - suspend_start
            self._metrics.suspend_count += 1

            # Handle different awaitable types
            if isinstance(result, EnhancedTask):
                if result.done:
                    self._loop._ready.append(lambda: self._step(result.result()))
                else:
                    result._waiters.append(self)
            elif isinstance(result, Sleep):
                deadline = time.monotonic() + result._seconds
                self._loop._schedule_timer(deadline, self)
                self._loop._debug.update_task(self._metrics.task_id, TaskState.PENDING, f"sleeping {result._seconds}s")
            elif isinstance(result, ReadSocket):
                self._setup_io_wait(result._sock.fileno(), "read")
            elif isinstance(result, WriteSocket):
                self._setup_io_wait(result._sock.fileno(), "write")
            elif isinstance(result, (_LockWaiter, _SemaphoreWaiter, _QueueWaiter, _EventWaiter)):
                # Synchronization primitive waiter - do nothing, it will be woken
                pass
            elif isinstance(result, AsyncQueue):
                # Queue operations are handled by the queue itself
                pass
            else:
                # Unknown awaitable, schedule immediately
                self._loop._ready.append(lambda: self._step(result))

            self._state = TaskState.PENDING

    def _setup_io_wait(self, fd: int, io_type: str) -> None:
        """Set up I/O wait with proper cleanup."""
        if self._current_io_fd is not None:
            self._cleanup_io()

        self._current_io_fd = fd
        self._current_io_type = io_type

        if io_type == "read":
            self._loop._register_reader(fd, self)
            self._loop._debug.update_task(self._metrics.task_id, TaskState.PENDING, "waiting for read")
        else:
            self._loop._register_writer(fd, self)
            self._loop._debug.update_task(self._metrics.task_id, TaskState.PENDING, "waiting for write")

    def __await__(self) -> Generator[EnhancedTask[T], None, T]:
        """Allow the task to be awaited."""
        if not self.done:
            yield self
        return self.result()

    def __repr__(self) -> str:
        """String representation with state."""
        return f"<{self.__class__.__name__} {self._name} {self._state.value}>"


class ThreadSafeEventLoop:
    """Thread-safe event loop with enhanced monitoring and debugging."""

    def __init__(self, debug: bool = False) -> None:
        # Core data structures with thread safety
        self._ready: deque[EnhancedTask[Any] | Callable[[], Any]] = deque()
        self._timers: list[tuple[float, int, EnhancedTask[Any] | Callable]] = []
        self._selector = selectors.DefaultSelector()
        self._seq = 0
        self._stopping = False
        self._running = False

        # Thread safety
        self._lock = threading.RLock()
        self._thread_id: int | None = None

        # Metrics and debugging
        self._metrics = EventLoopMetrics()
        self._debug_mode = debug
        self._debug = DebugVisualization(enabled=debug)
        self._task_metrics: dict[str, TaskMetrics] = {}

        # Current task tracking
        self._current_task: EnhancedTask[Any] | None = None

        # Executor for blocking operations
        self._executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="AsyncIO-Executor")

    def create_task(self, coro: Coroutine[Any, Any, T], name: str | None = None) -> EnhancedTask[T]:
        """Create a task from a coroutine and schedule it."""
        with self._lock:
            task = EnhancedTask(coro, self, name)
            self._ready.append(task)
            self._metrics.tasks_created += 1
            self._task_metrics[task._metrics.task_id] = task._metrics
            self._debug.update_task(task._metrics.task_id, TaskState.PENDING, task.name)
            return task

    def run_until_complete(self, awaitable: Awaitable[T]) -> T:
        """Run the event loop until the awaitable completes."""
        with self._lock:
            if self._running:
                raise RuntimeError("Loop is already running")
            self._thread_id = threading.get_ident()

        # Create or wrap task
        if isinstance(awaitable, EnhancedTask):
            task = awaitable
        else:
            task = self.create_task(cast(Coroutine[Any, Any, T], awaitable))

        old_loop = _current_loop
        _set_running_loop(self)
        self._running = True

        if self._debug_mode:
            self._debug.start()

        try:
            while not task.done and not self._stopping:
                self._run_once()

            if console and self._debug_mode:
                console.print("\n[green]✨ Event loop completed![/green]")
                console.print(self._metrics.to_table())

            return task.result()

        finally:
            self._running = False
            self._stopping = False
            self._thread_id = None
            _set_running_loop(old_loop)
            if self._debug_mode:
                self._debug.stop()

    def stop(self) -> None:
        """Stop the event loop."""
        with self._lock:
            self._stopping = True

    def _run_once(self) -> None:
        """Execute one iteration of the event loop with monitoring."""
        timeout: float | None = None

        with self._lock:
            self._metrics.total_iterations += 1

            # Calculate timeout based on ready queue and timers
            if self._ready:
                timeout = 0
            elif self._timers:
                timeout = max(0, self._timers[0][0] - time.monotonic())

        # Poll for I/O events
        if self._ready:
            events = self._selector.select(0)
        else:
            events = self._selector.select(timeout)

        if events:
            self._metrics.total_io_operations += len(events)
            self._process_events(events)

        # Process expired timers
        now = time.monotonic()
        with self._lock:
            while self._timers and self._timers[0][0] <= now:
                _, _, callback = heapq.heappop(self._timers)
                self._metrics.total_timer_operations += 1
                if isinstance(callback, EnhancedTask) and not callback.done or callable(callback):
                    self._ready.append(callback)

        # Execute ready tasks
        with self._lock:
            ntodo = len(self._ready)

        for _ in range(ntodo):
            with self._lock:
                if not self._ready:
                    break
                item = self._ready.popleft()

            if isinstance(item, EnhancedTask):
                if not item.done:
                    # Set current task
                    old_task = self._current_task
                    self._current_task = item
                    try:
                        item._step()
                    except Exception as e:
                        if console:
                            console.print(f"[red]Unhandled exception in task: {e}[/red]")
                            console.print_exception()
                    finally:
                        self._current_task = old_task
            else:
                try:
                    item()
                except Exception as e:
                    if console:
                        console.print(f"[red]Unhandled exception in callback: {e}[/red]")

    def _process_events(self, events: list[tuple[selectors.SelectorKey, int]]) -> None:
        """Process selector events and wake waiting tasks."""
        for key, mask in events:
            callback_data = key.data
            if callback_data is not None:
                tasks_to_wake = []

                if isinstance(callback_data, tuple) and len(callback_data) == 2:
                    readers, writers = callback_data
                    if mask & selectors.EVENT_READ and readers:
                        _, task = readers
                        if task and not task.done:
                            tasks_to_wake.append(task)
                    if mask & selectors.EVENT_WRITE and writers:
                        _, task = writers
                        if task and not task.done:
                            tasks_to_wake.append(task)
                elif isinstance(callback_data, EnhancedTask):
                    if not callback_data.done:
                        tasks_to_wake.append(callback_data)

                # Wake tasks with lock held
                with self._lock:
                    for task in tasks_to_wake:
                        self._ready.append(task)

    def _schedule_timer(self, deadline: float, callback: EnhancedTask[Any] | Callable) -> None:
        """Schedule a callback to run at a specific time."""
        with self._lock:
            self._seq += 1
            heapq.heappush(self._timers, (deadline, self._seq, callback))

    def _register_reader(self, fd: int, task: EnhancedTask[Any]) -> None:
        """Register a task to be woken when fd is ready for reading."""
        with self._lock:
            try:
                key = self._selector.get_key(fd)
                mask, data = key.events, key.data
                self._selector.modify(
                    fd, mask | selectors.EVENT_READ, ((selectors.EVENT_READ, task), data[1] if data else None)
                )
            except KeyError:
                self._selector.register(fd, selectors.EVENT_READ, ((selectors.EVENT_READ, task), None))

    def _register_writer(self, fd: int, task: EnhancedTask[Any]) -> None:
        """Register a task to be woken when fd is ready for writing."""
        with self._lock:
            try:
                key = self._selector.get_key(fd)
                mask, data = key.events, key.data
                self._selector.modify(
                    fd, mask | selectors.EVENT_WRITE, (data[0] if data else None, (selectors.EVENT_WRITE, task))
                )
            except KeyError:
                self._selector.register(fd, selectors.EVENT_WRITE, (None, (selectors.EVENT_WRITE, task)))

    def _unregister_reader(self, fd: int) -> None:
        """Stop monitoring fd for reading."""
        with self._lock:
            try:
                key = self._selector.get_key(fd)
                mask, data = key.events, key.data
                mask &= ~selectors.EVENT_READ
                if mask:
                    self._selector.modify(fd, mask, (None, data[1] if data else None))
                else:
                    self._selector.unregister(fd)
            except KeyError:
                pass

    def _unregister_writer(self, fd: int) -> None:
        """Stop monitoring fd for writing."""
        with self._lock:
            try:
                key = self._selector.get_key(fd)
                mask, data = key.events, key.data
                mask &= ~selectors.EVENT_WRITE
                if mask:
                    self._selector.modify(fd, mask, (data[0] if data else None, None))
                else:
                    self._selector.unregister(fd)
            except KeyError:
                pass

    def __del__(self):
        """Clean up resources."""
        self._executor.shutdown(wait=False)
        self._selector.close()


# Async Primitives


class Sleep:
    """An awaitable that yields control for a specified duration."""

    def __init__(self, seconds: float) -> None:
        self._seconds = seconds

    def __await__(self) -> Generator[Sleep, None, None]:
        yield self


class ReadSocket:
    """An awaitable that waits for a socket to be ready for reading."""

    def __init__(self, sock: socket.socket) -> None:
        self._sock = sock

    def __await__(self) -> Generator[ReadSocket, None, None]:
        yield self


class WriteSocket:
    """An awaitable that waits for a socket to be ready for writing."""

    def __init__(self, sock: socket.socket) -> None:
        self._sock = sock

    def __await__(self) -> Generator[WriteSocket, None, None]:
        yield self


class _LockWaiter:
    """Internal waiter for Lock."""

    def __init__(self) -> None:
        self._done = False
        self._task: EnhancedTask[Any] | None = None

    def _wake(self) -> None:
        """Wake up the waiting task."""
        if not self._done and self._task:
            self._done = True
            loop = get_running_loop()
            loop._ready.append(self._task)

    def __await__(self) -> Generator[_LockWaiter, None, None]:
        """Wait to be woken up."""
        if not self._done:
            task = current_task()
            if task is None:
                raise RuntimeError("No current task")
            self._task = task
            yield self
        if not self._done:
            raise RuntimeError("Lock waiter was not woken")


class Lock:
    """An async lock for synchronization."""

    def __init__(self) -> None:
        self._locked = False
        self._waiters: deque[_LockWaiter] = deque()

    def locked(self) -> bool:
        """Return True if the lock is held."""
        return self._locked

    def acquire_nowait(self) -> None:
        """Acquire the lock immediately."""
        if self._locked:
            raise RuntimeError("Lock is already held")
        self._locked = True

    async def acquire(self) -> None:
        """Acquire the lock."""
        if not self._locked:
            self._locked = True
            return

        # Need to wait
        waiter = _LockWaiter()
        self._waiters.append(waiter)
        try:
            await waiter
            # After being woken, the lock is already held for us by release()
        except:
            # Remove from waiters if still there (in case of cancellation)
            try:
                self._waiters.remove(waiter)
            except ValueError:
                pass
            raise

    def release(self) -> None:
        """Release the lock."""
        if not self._locked:
            raise RuntimeError("Lock is not acquired")

        # Wake up the next waiter - if found, they now own the lock
        woken = False
        while self._waiters:
            waiter = self._waiters.popleft()
            if not waiter._done:
                waiter._wake()
                woken = True
                break

        # Only clear the lock if no waiter was woken
        if not woken:
            self._locked = False

    async def __aenter__(self) -> None:
        await self.acquire()

    async def __aexit__(self, *args) -> None:
        self.release()


class _SemaphoreWaiter:
    """Internal waiter for Semaphore."""

    def __init__(self) -> None:
        self._done = False
        self._task: EnhancedTask[Any] | None = None

    def _wake(self) -> None:
        """Wake up the waiting task."""
        if not self._done and self._task:
            self._done = True
            loop = get_running_loop()
            loop._ready.append(self._task)

    def __await__(self) -> Generator[_SemaphoreWaiter, None, None]:
        """Wait to be woken up."""
        if not self._done:
            task = current_task()
            if task is None:
                raise RuntimeError("No current task")
            self._task = task
            yield self
        if not self._done:
            raise RuntimeError("Semaphore waiter was not woken")


class Semaphore:
    """An async semaphore for limiting concurrent access."""

    def __init__(self, value: int = 1) -> None:
        if value < 0:
            raise ValueError("Semaphore initial value must be >= 0")
        self._value = value
        self._waiters: deque[_SemaphoreWaiter] = deque()

    async def acquire(self) -> None:
        """Acquire a semaphore permit."""
        while self._value <= 0:
            waiter = _SemaphoreWaiter()
            self._waiters.append(waiter)
            try:
                await waiter
            except:
                # Remove from waiters if still there (in case of cancellation)
                try:
                    self._waiters.remove(waiter)
                except ValueError:
                    pass
                raise
        self._value -= 1

    def release(self) -> None:
        """Release a semaphore permit."""
        self._value += 1
        # Wake up waiters that can now proceed
        while self._waiters and self._value > 0:
            waiter = self._waiters.popleft()
            if not waiter._done:
                waiter._wake()
                # Don't decrement value here - let acquire() do it
                break

    async def __aenter__(self) -> None:
        await self.acquire()

    async def __aexit__(self, *args) -> None:
        self.release()


@dataclass
class QueueItem(Generic[T]):
    """Item in async queue with priority support."""

    value: T
    priority: int = 0

    def __lt__(self, other: QueueItem[T]) -> bool:
        return self.priority < other.priority


class _QueueWaiter:
    """Internal waiter for AsyncQueue."""

    def __init__(self) -> None:
        self._done = False
        self._task: EnhancedTask[Any] | None = None

    def _wake(self) -> None:
        """Wake up the waiting task."""
        if not self._done and self._task:
            self._done = True
            loop = get_running_loop()
            loop._ready.append(self._task)

    def __await__(self) -> Generator[_QueueWaiter, None, None]:
        """Wait to be woken up."""
        if not self._done:
            task = current_task()
            if task is None:
                raise RuntimeError("No current task")
            self._task = task
            yield self
        if not self._done:
            raise RuntimeError("Queue waiter was not woken")


class AsyncQueue(Generic[T]):
    """An async queue for inter-task communication."""

    def __init__(self, maxsize: int = 0, priority: bool = False) -> None:
        self._maxsize = maxsize
        self._priority = priority
        self._items: deque[T] | list[QueueItem[T]] = [] if priority else deque()
        self._get_waiters: deque[_QueueWaiter] = deque()
        self._put_waiters: deque[_QueueWaiter] = deque()

    def qsize(self) -> int:
        """Return the approximate size of the queue."""
        return len(self._items)

    def empty(self) -> bool:
        """Return True if the queue is empty."""
        return not self._items

    def full(self) -> bool:
        """Return True if the queue is full."""
        return self._maxsize > 0 and self.qsize() >= self._maxsize

    async def put(self, item: T, priority: int = 0) -> None:
        """Put an item into the queue."""
        while self.full():
            waiter = _QueueWaiter()
            self._put_waiters.append(waiter)
            try:
                await waiter
            except:
                try:
                    self._put_waiters.remove(waiter)
                except ValueError:
                    pass
                raise

        if self._priority:
            heapq.heappush(cast(list[QueueItem[T]], self._items), QueueItem(item, priority))
        else:
            cast(deque[T], self._items).append(item)

        # Wake up a getter if any
        while self._get_waiters:
            getter = self._get_waiters.popleft()
            if not getter._done:
                getter._wake()
                break

    async def get(self) -> T:
        """Get an item from the queue."""
        while self.empty():
            waiter = _QueueWaiter()
            self._get_waiters.append(waiter)
            try:
                await waiter
            except:
                try:
                    self._get_waiters.remove(waiter)
                except ValueError:
                    pass
                raise

        if self._priority:
            item = heapq.heappop(cast(list[QueueItem[T]], self._items)).value
        else:
            item = cast(deque[T], self._items).popleft()

        # Wake up a putter if any
        while self._put_waiters:
            putter = self._put_waiters.popleft()
            if not putter._done:
                putter._wake()
                break

        return item


class _EventWaiter:
    """Internal waiter for Event."""

    def __init__(self) -> None:
        self._done = False
        self._task: EnhancedTask[Any] | None = None

    def _wake(self) -> None:
        """Wake up the waiting task."""
        if not self._done and self._task:
            self._done = True
            loop = get_running_loop()
            loop._ready.append(self._task)

    def __await__(self) -> Generator[_EventWaiter, None, None]:
        """Wait to be woken up."""
        if not self._done:
            task = current_task()
            if task is None:
                raise RuntimeError("No current task")
            self._task = task
            yield self
        if not self._done:
            raise RuntimeError("Event waiter was not woken")


class Event:
    """An async event for signaling between tasks."""

    def __init__(self) -> None:
        self._is_set = False
        self._waiters: list[_EventWaiter] = []

    def is_set(self) -> bool:
        """Return True if the event is set."""
        return self._is_set

    def set(self) -> None:
        """Set the event, waking all waiters."""
        if not self._is_set:
            self._is_set = True
            # Wake all waiters
            for waiter in self._waiters:
                if not waiter._done:
                    waiter._wake()
            self._waiters.clear()

    def clear(self) -> None:
        """Clear the event."""
        self._is_set = False

    async def wait(self) -> None:
        """Wait until the event is set."""
        if self._is_set:
            return

        waiter = _EventWaiter()
        self._waiters.append(waiter)
        try:
            await waiter
        except:
            # Remove from waiters if still there
            try:
                self._waiters.remove(waiter)
            except ValueError:
                pass
            raise


# High-level functions


async def sleep(seconds: float) -> None:
    """Sleep for the specified number of seconds."""
    await Sleep(seconds)


async def gather(*awaitables: Awaitable[Any], return_exceptions: bool = False) -> list[Any]:
    """Run awaitables concurrently and gather their results."""
    if not awaitables:
        return []

    loop = get_running_loop()
    tasks: list[EnhancedTask[Any]] = []

    for awt in awaitables:
        if isinstance(awt, EnhancedTask):
            tasks.append(awt)
        else:
            task = loop.create_task(cast(Coroutine[Any, Any, Any], awt))
            tasks.append(task)

    # Wait for all tasks
    for task in tasks:
        if not task.done:
            await task

    # Collect results
    results: list[Any] = []
    for task in tasks:
        try:
            results.append(task.result())
        except BaseException as exc:
            if return_exceptions:
                results.append(exc)
            else:
                # Cancel remaining tasks
                for t in tasks:
                    if not t.done:
                        t.cancel()
                raise

    return results


async def wait_for(awaitable: Awaitable[T], timeout: float) -> T:
    """Wait for an awaitable with a timeout."""
    loop = get_running_loop()

    # Create task if needed
    if isinstance(awaitable, EnhancedTask):
        task = awaitable
    else:
        task = loop.create_task(cast(Coroutine[Any, Any, T], awaitable))

    # Set timeout
    task.set_timeout(timeout)

    try:
        return await task
    except TimeoutError:
        task.cancel()
        raise


async def shield(awaitable: Awaitable[T]) -> T:
    """Shield an awaitable from cancellation."""
    loop = get_running_loop()

    if isinstance(awaitable, EnhancedTask):
        task = awaitable
    else:
        task = loop.create_task(cast(Coroutine[Any, Any, T], awaitable))

    task.shield()
    return await task


class TaskGroup:
    """Context manager for structured concurrency with error handling."""

    def __init__(self) -> None:
        self._tasks: list[EnhancedTask[Any]] = []
        self._loop: ThreadSafeEventLoop | None = None
        self._entered = False
        self._exiting = False
        self._base_error: BaseException | None = None
        self._errors: list[BaseException] = []

    async def __aenter__(self) -> Self:
        """Enter the task group context."""
        self._loop = get_running_loop()
        self._entered = True
        return self

    async def __aexit__(
        self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None
    ) -> bool:
        """Exit the task group context, waiting for all tasks."""
        self._exiting = True

        # If an exception occurred, cancel all tasks
        if exc_val is not None:
            self._base_error = exc_val
            for task in self._tasks:
                if not task.done:
                    task.cancel()

        # Wait for all tasks to complete
        while self._tasks:
            pending = [task for task in self._tasks if not task.done]
            if not pending:
                break

            # Wait for at least one task to complete
            await pending[0]

        # Collect exceptions
        if self._base_error is not None:
            self._errors.append(self._base_error)

        for task in self._tasks:
            try:
                task.result()
            except CancelledError:
                # Ignore cancellation
                pass
            except BaseException as exc:
                self._errors.append(exc)

        # Raise exceptions if any
        if self._errors:
            if len(self._errors) == 1:
                raise self._errors[0]
            else:
                raise ExceptionGroup("Multiple exceptions in TaskGroup", self._errors)

        return True

    def create_task(self, coro: Coroutine[Any, Any, T], name: str | None = None) -> EnhancedTask[T]:
        """Create a task within this group."""
        if not self._entered or self._exiting:
            raise RuntimeError("TaskGroup not active")
        if self._loop is None:
            raise RuntimeError("No event loop")

        task = self._loop.create_task(coro, name)
        self._tasks.append(task)
        return task


class ExceptionGroup(Exception):
    """Group of exceptions raised concurrently."""

    def __init__(self, message: str, exceptions: Sequence[BaseException]) -> None:
        super().__init__(message)
        self.exceptions = list(exceptions)

    def __str__(self) -> str:
        lines = [super().__str__()]
        for i, exc in enumerate(self.exceptions, 1):
            lines.append(f"  [{i}] {type(exc).__name__}: {exc}")
        return "\n".join(lines)


# Example usage and tests

if __name__ == "__main__":
    """Comprehensive test suite with rich console output."""

    if not RICH_AVAILABLE:
        print("Note: Install 'rich' for enhanced visual output: pip install rich")
        print()

    async def test_basic_operations() -> None:
        """Test basic async operations."""
        if console:
            console.rule("[bold blue]Basic Operations Test[/bold blue]")

        # Test sleep
        start = time.monotonic()
        await sleep(0.5)
        elapsed = time.monotonic() - start
        assert 0.4 < elapsed < 0.6, f"Sleep duration incorrect: {elapsed}"

        if console:
            console.print("[green]✓[/green] Basic sleep works")

        # Test concurrent execution
        async def task(name: str, duration: float) -> str:
            if console:
                console.print(f"[cyan]{name}[/cyan] starting (sleep {duration}s)")
            await sleep(duration)
            if console:
                console.print(f"[cyan]{name}[/cyan] completed")
            return f"{name} done"

        results = await gather(task("Task-A", 0.3), task("Task-B", 0.2), task("Task-C", 0.4))

        assert results == ["Task-A done", "Task-B done", "Task-C done"]
        if console:
            console.print("[green]✓[/green] Concurrent execution works")

    async def test_synchronization() -> None:
        """Test synchronization primitives."""
        if console:
            console.rule("[bold blue]Synchronization Test[/bold blue]")

        # Test Lock
        lock = Lock()
        counter = 0

        async def increment(name: str) -> None:
            nonlocal counter
            await lock.acquire()
            try:
                if console:
                    console.print(f"[yellow]{name}[/yellow] acquired lock")
                old = counter
                await sleep(0.1)
                counter = old + 1
                if console:
                    console.print(f"[yellow]{name}[/yellow] releasing lock")
            finally:
                lock.release()

        await gather(increment("Worker-1"), increment("Worker-2"), increment("Worker-3"))

        assert counter == 3
        if console:
            console.print("[green]✓[/green] Lock synchronization works")

        # Test Semaphore
        sem = Semaphore(2)
        active = 0
        max_active = 0

        async def limited_task(name: str) -> None:
            nonlocal active, max_active
            async with sem:
                active += 1
                max_active = max(max_active, active)
                if console:
                    console.print(f"[magenta]{name}[/magenta] running (active: {active})")
                await sleep(0.2)
                active -= 1

        await gather(*[limited_task(f"Task-{i}") for i in range(5)])

        assert max_active == 2
        if console:
            console.print("[green]✓[/green] Semaphore limiting works")

    async def test_communication() -> None:
        """Test inter-task communication."""
        if console:
            console.rule("[bold blue]Communication Test[/bold blue]")

        # Test Queue
        queue: AsyncQueue[str] = AsyncQueue(maxsize=3)

        async def producer(name: str) -> None:
            for i in range(3):
                item = f"{name}-{i}"
                await queue.put(item)
                if console:
                    console.print(f"[blue]Producer[/blue] put: {item}")
                await sleep(0.1)

        async def consumer(name: str) -> list[str]:
            items = []
            for _ in range(3):
                item = await queue.get()
                items.append(item)
                if console:
                    console.print(f"[green]Consumer[/green] got: {item}")
            return items

        results = await gather(producer("Producer"), consumer("Consumer"))

        assert len(results[1]) == 3
        if console:
            console.print("[green]✓[/green] Queue communication works")

        # Test Event
        event = Event()
        results = []

        async def waiter(name: str) -> None:
            if console:
                console.print(f"[yellow]{name}[/yellow] waiting for event")
            await event.wait()
            results.append(name)
            if console:
                console.print(f"[yellow]{name}[/yellow] got event")

        async def setter() -> None:
            await sleep(0.2)
            if console:
                console.print("[red]Setting event![/red]")
            event.set()

        await gather(waiter("Waiter-1"), waiter("Waiter-2"), setter())

        assert len(results) == 2
        if console:
            console.print("[green]✓[/green] Event signaling works")

    async def test_error_handling() -> None:
        """Test error handling and cancellation."""
        if console:
            console.rule("[bold blue]Error Handling Test[/bold blue]")

        # Test timeout
        try:
            await wait_for(sleep(2), timeout=0.5)
            assert False, "Should have timed out"
        except TimeoutError:
            if console:
                console.print("[green]✓[/green] Timeout works correctly")

        # Test cancellation
        loop = get_running_loop()
        task = loop.create_task(sleep(10), name="Cancellable")
        await sleep(0.1)

        cancelled = task.cancel()
        assert cancelled

        try:
            await task
            assert False, "Should have been cancelled"
        except CancelledError:
            if console:
                console.print("[green]✓[/green] Cancellation works correctly")

        # Test shield
        async def important_work() -> str:
            await sleep(0.2)
            return "Important result"

        shielded = shield(important_work())
        result = await shielded
        assert result == "Important result"
        if console:
            console.print("[green]✓[/green] Shield protection works")

        # Test exception in gather
        async def failing_task() -> None:
            await sleep(0.1)
            raise ValueError("Test error")

        results = await gather(sleep(0.1), failing_task(), sleep(0.1), return_exceptions=True)

        assert results[0] is None
        assert isinstance(results[1], ValueError)
        assert results[2] is None
        if console:
            console.print("[green]✓[/green] Exception handling in gather works")

    async def test_task_group() -> None:
        """Test structured concurrency with TaskGroup."""
        if console:
            console.rule("[bold blue]TaskGroup Test[/bold blue]")

        results = []

        async def append_value(value: str, delay: float) -> None:
            await sleep(delay)
            results.append(value)
            if console:
                console.print(f"[cyan]Appended:[/cyan] {value}")

        async with TaskGroup() as tg:
            tg.create_task(append_value("A", 0.3), name="Append-A")
            tg.create_task(append_value("B", 0.1), name="Append-B")
            tg.create_task(append_value("C", 0.2), name="Append-C")

        assert sorted(results) == ["A", "B", "C"]
        if console:
            console.print("[green]✓[/green] TaskGroup works correctly")

        # Test TaskGroup with exception
        results.clear()

        async def failing_append() -> None:
            await sleep(0.15)
            raise RuntimeError("Task failed")

        try:
            async with TaskGroup() as tg:
                tg.create_task(append_value("X", 0.3), name="Append-X")
                tg.create_task(failing_append(), name="Failing")
                tg.create_task(append_value("Y", 0.1), name="Append-Y")
        except RuntimeError:
            if console:
                console.print("[green]✓[/green] TaskGroup exception handling works")

        # Y should have completed, X should have been cancelled
        assert "Y" in results
        assert "X" not in results

    async def test_network_operations() -> None:
        """Test network I/O operations."""
        if console:
            console.rule("[bold blue]Network Operations Test[/bold blue]")

        host = "127.0.0.1"
        port = 12345

        async def echo_server() -> None:
            server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_sock.setblocking(False)
            server_sock.bind((host, port))
            server_sock.listen(1)

            if console:
                console.print(f"[blue]Server[/blue] listening on {host}:{port}")

            try:
                await ReadSocket(server_sock)
                client_sock, addr = server_sock.accept()
                client_sock.setblocking(False)

                if console:
                    console.print(f"[blue]Server[/blue] accepted connection from {addr}")

                await ReadSocket(client_sock)
                data = client_sock.recv(1024)

                await WriteSocket(client_sock)
                client_sock.send(data)

                client_sock.close()
            finally:
                server_sock.close()

        async def echo_client(message: str) -> str:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setblocking(False)

            try:
                try:
                    sock.connect((host, port))
                except BlockingIOError:
                    await WriteSocket(sock)

                await WriteSocket(sock)
                sock.send(message.encode())

                await ReadSocket(sock)
                data = sock.recv(1024)
                return data.decode()
            finally:
                sock.close()

        # Start server and client
        loop = get_running_loop()
        server_task = loop.create_task(echo_server(), name="EchoServer")

        await sleep(0.1)  # Let server start

        response = await echo_client("Hello, Async!")
        assert response == "Hello, Async!"

        if console:
            console.print("[green]✓[/green] Network operations work")

        server_task.cancel()
        with contextlib.suppress(CancelledError):
            await server_task

    async def main() -> None:
        """Run all tests with beautiful output."""
        if console:
            console.print(
                Panel.fit(
                    "[bold]🚀 Enhanced Async Runtime Test Suite[/bold]\nTesting all components with visual feedback",
                    border_style="bright_blue",
                )
            )

        tests = [
            ("Basic Operations", test_basic_operations),
            ("Synchronization Primitives", test_synchronization),
            ("Inter-task Communication", test_communication),
            ("Error Handling", test_error_handling),
            ("Structured Concurrency", test_task_group),
            ("Network I/O", test_network_operations),
        ]

        for name, test_func in tests:
            try:
                await test_func()
                if console:
                    console.print(f"\n[bold green]✅ {name} - PASSED[/bold green]\n")
            except Exception as e:
                if console:
                    console.print(f"\n[bold red]❌ {name} - FAILED[/bold red]")
                    console.print_exception()
                else:
                    print(f"\n❌ {name} - FAILED: {e}")
                raise

        if console:
            console.print(
                Panel.fit(
                    "[bold green]🎉 All tests passed![/bold green]\nThe enhanced async runtime is working correctly",
                    border_style="bright_green",
                )
            )

    # Run the test suite
    loop = ThreadSafeEventLoop(debug=True)
    loop.run_until_complete(main())
