"""
Async runtime for managing Python-Lua timer integration
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from .interpreter import LuaInterpreter


@dataclass
class CallbackData:
    """Data structure for callbacks in the callback queue"""
    type: str  # "timer" or "lua_callback"
    callback_id: int
    data: Any = None


class LuaAsyncRuntime:
    """
    Manages Lua runtime with async timer support and MobDebug integration (handled in init.lua).
    """

    def __init__(self, config=None):
        self.config = config or {}
        self.interpreter = LuaInterpreter(config=self.config)
        self.timer_semaphore = asyncio.Semaphore(0)
        self.callback_task: Optional[asyncio.Task] = None
        self.lua_timer_counter = 0
        self.task_states: Dict[str, str] = {}

        # Queue to store callbacks (both timers and general callbacks)
        self.callback_queue: asyncio.Queue[CallbackData] = asyncio.Queue()

        # Track running timer tasks for cancellation
        self.timer_tasks: Dict[int, asyncio.Task] = {}

        # Optionally, make config available to Lua
        if hasattr(self.interpreter, 'lua') and self.interpreter.lua:
            self.interpreter.lua.globals()['_PY'].config = self.config

    def set_config(self, config):
        self.config = config or {}
        if hasattr(self.interpreter, 'lua') and self.interpreter.lua:
            self.interpreter.lua.globals()['_PY'].config = self.config

    def curr_time(self) -> str:
        """Get current time formatted as HH:MM:SS.mmm"""
        return datetime.now().strftime("%H:%M:%S.%f")[:-3]

    def create_timer(self, timer_id: int, delay_ms: int) -> asyncio.Task:
        """Create a timer that will signal the run_timer_callbacks_loop"""

        async def timer_task() -> None:
            """Async task that waits and then queues the timer for execution"""
            try:
                # Wait for the delay
                await asyncio.sleep(delay_ms / 1000.0)

                current_time = self.curr_time()

                # Check if this timer was cancelled while sleeping
                if timer_id not in self.timer_tasks:
                    # Timer was cancelled - this is normal behavior, don't print unless debugging
                    return

                # Put the timer callback data in the queue for the callback loop to process
                callback_data = CallbackData("timer", timer_id)
                await self.callback_queue.put(callback_data)

                # Release the semaphore to signal the callback loop
                self.timer_semaphore.release()

            except asyncio.CancelledError:
                current_time = self.curr_time()
                self.interpreter.debug_print(f"[{current_time}] Timer {timer_id} task was cancelled")
                raise
            except Exception as e:
                error_time = self.curr_time()
                print(f"[{error_time}] Timer task error: {e}")  # Keep as regular print since this is an error
                import traceback
                traceback.print_exc()
            finally:
                # Clean up the task reference
                if timer_id in self.timer_tasks:
                    del self.timer_tasks[timer_id]

        # Create a named task for the timer
        timer_task_name = f"lua_timer_{timer_id}_{delay_ms}ms"

        # Create and store the named asyncio task
        task = asyncio.create_task(timer_task(), name=timer_task_name)
        self.timer_tasks[timer_id] = task

        return task

    def python_timer(self, timer_id: int, delay_ms: int) -> asyncio.Task:
        """Wrapper function for creating timers from Lua"""
        # Auto-start callback loop if not running
        self._ensure_callback_loop_running()
        return self.create_timer(timer_id, delay_ms)

    def python_cancel_timer(self, timer_id: int) -> bool:
        """Cancel a timer task from Lua"""
        if timer_id in self.timer_tasks:
            task = self.timer_tasks[timer_id]
            if not task.done():
                task.cancel()
                current_time = self.curr_time()
                self.interpreter.debug_print(f"[{current_time}] Python cancelled timer {timer_id}")
            del self.timer_tasks[timer_id]
            return True
        else:
            current_time = self.curr_time()
            self.interpreter.debug_print(f"[{current_time}] Timer {timer_id} not found for cancellation")
            return False

    def get_task_info(self) -> List[str]:
        """Get information about all running tasks with suspension indicators"""
        tasks = asyncio.all_tasks()
        task_info = []
        current_task = asyncio.current_task()

        for task in tasks:
            if not task.done():
                name = task.get_name() if hasattr(task, 'get_name') else "unnamed"

                # Check if this task is marked as suspended in our tracking
                is_suspended = name in self.task_states and self.task_states[name] == "suspended"

                # Or simply mark all non-current tasks as suspended
                if not is_suspended:
                    is_suspended = task != current_task

                prefix = "*" if is_suspended else ""
                task_info.append(f"{prefix}{name}")

        return task_info

    async def run_timer_callbacks_loop(self) -> None:
        """Continuous loop that waits on semaphore for timer callbacks and executes them in the same context"""
        counter = 0
        while True:
            # current_time = self.curr_time()
            isLocked = self.timer_semaphore.locked()
            if isLocked:
                self.interpreter.debug_print("Callback loop suspended...")

            # Mark as suspended before waiting
            self.task_states["callback_loop"] = "suspended"

            await self.timer_semaphore.acquire()

            # Capture timestamp immediately after waking up
            wake_time = self.curr_time()
            if isLocked:
                self.interpreter.debug_print(f"[{wake_time}] Callback loop awakened...")

            # Mark as active after resuming
            self.task_states["callback_loop"] = "active"

            # Get the callback data from the queue
            callback_data = await self.callback_queue.get()

            try:
                self.interpreter.execute_lua_callback(callback_data.callback_id, callback_data.data or None)
                completion_time = self.curr_time()
                self.interpreter.debug_print(f"[{completion_time}] Callback {callback_data.callback_id} executed successfully")
            except Exception as e:
                error_time = self.curr_time()
                print(f"[{error_time}] Callback {callback_data.callback_id} execution error: {e}")
                import traceback
                traceback.print_exc()

            counter += 1

    def initialize_lua(self) -> None:
        """Initialize the Lua runtime and set up environment"""
        self.interpreter.initialize(
            python_timer_func=self.python_timer,
            python_cancel_timer_func=self.python_cancel_timer
        )

        # Set runtime reference for HTTP callbacks AFTER interpreter is initialized
        from . import network
        network.set_current_runtime(self)

    def execute_script(self, script: str, source_name: str = None, debugging: bool = False, debug: bool = False) -> None:
        """Execute a Lua script"""
        self.interpreter.execute_script(script, source_name, debugging, debug)

    def execute_file(self, filepath: str, debugging: bool = False, debug: bool = False) -> None:
        """Execute a Lua file using the main_file_hook"""
        self.interpreter.execute_file(filepath, debugging, debug)

    def _ensure_callback_loop_running(self) -> None:
        """Ensure the callback loop is running, start it if needed"""
        if not hasattr(self, 'callback_task') or self.callback_task is None or self.callback_task.done():
            # Create the callback loop task but don't await it (non-blocking start)
            self.callback_task = asyncio.create_task(
                self.run_timer_callbacks_loop(),
                name="callback_loop"
            )
            # execution_time = self.curr_time()
            self.interpreter.debug_print("Auto-started callback loop as background task")
            self.interpreter.debug_print("[DEBUG] Auto-started callback loop task")
        else:
            self.interpreter.debug_print("[DEBUG] Callback loop already running")

    async def start_callback_loop(self) -> None:
        """Start the callback loop as a background task"""
        self.callback_task = asyncio.create_task(
            self.run_timer_callbacks_loop(),
            name="callback_loop"
        )
        # execution_time = self.curr_time()
        self.interpreter.debug_print("Callback loop started as background task")

    async def run_for_duration(self, duration_seconds: int = 30) -> None:
        """Run the system for a specified duration with periodic status checks"""
        # execution_time = self.curr_time()
        self.interpreter.debug_print(f"Running for {duration_seconds} seconds...")

        # Start the callback loop if it's not already running
        if not hasattr(self, 'callback_task') or self.callback_task is None or self.callback_task.done():
            await self.start_callback_loop()

        # Add periodic status checks
        for i in range(duration_seconds):
            await asyncio.sleep(1)
            # current_time = self.curr_time()

            # Check user-defined isRunning hook
            if not self.interpreter.check_is_running_hook():
                self.interpreter.debug_print(f"Script terminated by _PY.isRunning hook at second {i+1}")
                break

            # Get task information
            task_names = self.get_task_info()
            pending_count = len(task_names)
            task_list = ", ".join(task_names) if task_names else "none"

            # Get runtime state for debugging
            runtime_state = self.interpreter.get_runtime_state()

            self.interpreter.debug_print(f"Second {i+1}/{duration_seconds} - Tasks: {pending_count} ({task_list}) - \
                                         Timers: {runtime_state['active_timers']}, Callbacks: {runtime_state['pending_callbacks']}")

    async def run_forever(self) -> None:
        """Run the system forever with periodic status updates"""
        # execution_time = self.curr_time()
        self.interpreter.debug_print("Running forever...")

        counter = 0
        while True:
            await asyncio.sleep(10)
            # current_time = self.curr_time()

            # Check user-defined isRunning hook
            if not self.interpreter.check_is_running_hook():
                self.interpreter.debug_print(f"Script terminated by _PY.isRunning hook after {counter * 10} seconds")
                break

            # Get task information
            task_names = self.get_task_info()
            pending_count = len(task_names)
            task_list = ", ".join(task_names) if task_names else "none"

            # Get runtime state for debugging
            runtime_state = self.interpreter.get_runtime_state()

            self.interpreter.debug_print(f"Status check {counter} - Tasks: {pending_count} ({task_list}) \
                                         - Timers: {runtime_state['active_timers']}, Callbacks: {runtime_state['pending_callbacks']}")
            counter += 1

    def stop(self) -> None:
        """Stop the callback loop and cleanup"""
        end_time = self.curr_time()
        print(f"[{end_time}] Stopping Lua runtime...")
        
        # 1. Stop mobdebug if running
        try:
            if hasattr(self.interpreter, 'lua') and self.interpreter.lua:
                lua_globals = self.interpreter.lua.globals()
                if '_PY' in lua_globals and 'mobdebug' in lua_globals['_PY']:
                    mobdebug = lua_globals['_PY']['mobdebug']
                    if hasattr(mobdebug, 'done'):
                        mobdebug.done()
                        print(f"[{end_time}] Mobdebug stopped")
        except Exception as e:
            print(f"Warning: Failed to stop mobdebug: {e}")
        
        # 2. Cancel all running timer tasks
        try:
            cancelled_count = 0
            for timer_id, task in list(self.timer_tasks.items()):
                if not task.done():
                    task.cancel()
                    cancelled_count += 1
                del self.timer_tasks[timer_id]
            if cancelled_count > 0:
                print(f"[{end_time}] Cancelled {cancelled_count} timer tasks")
        except Exception as e:
            print(f"Warning: Failed to cancel timer tasks: {e}")
        
        # 3. Stop callback loop
        try:
            if self.callback_task and not self.callback_task.done():
                self.callback_task.cancel()
                print(f"[{end_time}] Callback loop stopped")
        except Exception as e:
            print(f"Warning: Failed to stop callback loop: {e}")
        
        # 4. Cleanup QuickApp windows
        try:
            from .luafuns_lib import close_all_quickapp_windows
            result = close_all_quickapp_windows()
            if result.get('closed_count', 0) > 0:
                print(f"[{end_time}] Closed {result['closed_count']} QuickApp windows")
        except Exception as e:
            print(f"Warning: Failed to cleanup QuickApp windows: {e}")
        
        # 5. Clear queue and release semaphores
        try:
            # Clear any pending callbacks
            while not self.callback_queue.empty():
                try:
                    self.callback_queue.get_nowait()
                except:
                    break
                    
            # Release any waiting semaphores
            while self.timer_semaphore.locked():
                self.timer_semaphore.release()
        except Exception as e:
            print(f"Warning: Failed to clear queue/semaphores: {e}")
            
        print(f"[{end_time}] Lua runtime stopped")

    def queue_lua_callback(self, callback_id: int, result_data: Any) -> None:
        """Queue a Lua callback for execution in the main callback loop"""
        self.interpreter.debug_print(f"[DEBUG] queue_lua_callback called with callback_id={callback_id}")

        # Auto-start callback loop if not running
        self._ensure_callback_loop_running()

        callback_data = CallbackData("lua_callback", callback_id, result_data)

        # Queue the callback using asyncio.run_coroutine_threadsafe for thread safety
        # and to handle cross-thread queuing better
        try:
            loop = asyncio.get_running_loop()
            # Schedule the coroutine to run in the current event loop
            asyncio.ensure_future(self._queue_callback(callback_data), loop=loop)
            self.interpreter.debug_print(f"[DEBUG] Queued callback {callback_id} in event loop")
        except RuntimeError:
            # If there's no running loop, try to queue directly
            self.interpreter.debug_print(f"[DEBUG] No running loop, trying direct queue for callback {callback_id}")
            # This is a fallback - queue synchronously if possible
            try:
                asyncio.create_task(self._queue_callback(callback_data))
            except Exception as e:
                self.interpreter.debug_print(f"[DEBUG] Failed to queue callback {callback_id}: {e}")

    async def _queue_callback(self, callback_data: CallbackData) -> None:
        """Helper to queue callback and signal the loop"""
        await self.callback_queue.put(callback_data)
        self.timer_semaphore.release()  # Wake up the callback loop

    async def start(self, script_fragments: list = None, main_script: str = None, main_file: str = None,
                    duration: Optional[int] = None, debugger_config: Optional[dict] = None,
                    source_name: Optional[str] = None, debug: bool = False, api_server=None) -> None:
        """
        Main method to start the Lua async runtime system
        Args:
            script_fragments: List of -e script fragments to execute first (preserves main script line numbers)
            main_script: The main Lua script to execute (or None)
            main_file: The main Lua file to execute (or None) - takes precedence over main_script
            duration: Duration in seconds to run (None for forever)
            debugger_config: Optional debugger configuration dict with host/port (passed to init.lua)
            source_name: Optional source file name for debugging
            debug: Enable debug logging
            api_server: Optional API server instance
        """
        try:
            # Check if we have anything to execute
            if not script_fragments and not main_script and not main_file:
                print("No script provided to execute")
                return

            # Set debug mode on interpreter
            self.interpreter.set_debug_mode(debug)

            # Initialize Lua runtime
            self.initialize_lua()

            # Start callback loop
            await self.start_callback_loop()

            # Execute script fragments first (without debugging to preserve main script line numbers)
            if script_fragments:
                for i, fragment in enumerate(script_fragments, 1):
                    if debug:
                        print(f"[{self.curr_time()}] Executing script fragment {i}/{len(script_fragments)}...")
                    self.execute_script(fragment, f"fragment_{i}", debugging=False, debug=debug)

            # Check for and register Fibaro API endpoints if api_server is available
            # This must happen before executing user scripts so endpoints are available
            if api_server:
                api_server.check_and_register_fibaro_api()

            # Load and execute the main script/file
            if main_file:
                if debug:
                    print(f"[{self.curr_time()}] Loading main file...")
                self.execute_file(main_file, debugging=False, debug=debug)
            elif main_script:
                if debug:
                    print(f"[{self.curr_time()}] Loading main script...")
                self.execute_script(main_script, source_name, debugging=False, debug=debug)

            # Run for specified duration or forever
            if duration:
                duration_task = asyncio.create_task(
                    self.run_for_duration(duration),
                    name="duration_monitor"
                )
                await duration_task
            else:
                forever_task = asyncio.create_task(
                    self.run_forever(),
                    name="forever_monitor"
                )
                await forever_task

        finally:
            self.stop()

    async def start_script_only(self, script_fragments: list = None, main_script: str = None, main_file: str = None,
                                debugger_config: Optional[dict] = None, source_name: Optional[str] = None, 
                                debug: bool = False, api_server=None) -> None:
        """
        Execute script content without entering the main event loop (for interactive mode)
        """
        try:
            # Check if we have anything to execute
            if not script_fragments and not main_script and not main_file:
                return

            # Set debug mode on interpreter
            self.interpreter.set_debug_mode(debug)

            # Initialize Lua runtime
            self.initialize_lua()
            self._initialized = True

            # Start callback loop (but don't await it)
            asyncio.create_task(self.start_callback_loop(), name="callback_loop")

            # Execute script fragments first
            if script_fragments:
                for i, fragment in enumerate(script_fragments, 1):
                    if debug:
                        print(f"[{self.curr_time()}] Executing script fragment {i}/{len(script_fragments)}...")
                    self.execute_script(fragment, f"fragment_{i}", debugging=False, debug=debug)

            # Check for and register Fibaro API endpoints if api_server is available
            if api_server:
                api_server.check_and_register_fibaro_api()

            # Load and execute the main script/file
            if main_file:
                if debug:
                    print(f"[{self.curr_time()}] Loading main file...")
                self.execute_file(main_file, debugging=False, debug=debug)
            elif main_script:
                if debug:
                    print(f"[{self.curr_time()}] Loading main script...")
                self.execute_script(main_script, source_name, debugging=False, debug=debug)

            # Allow some time for any immediate callbacks to execute
            await asyncio.sleep(0.1)

        except Exception as e:
            print(f"Error in script execution: {e}")
            raise

    async def initialize(self, debugger_config: Optional[dict] = None, debug: bool = False, api_server=None) -> None:
        """
        Initialize the runtime for REPL mode without executing any scripts
        """
        try:
            # Set debug mode on interpreter
            self.interpreter.set_debug_mode(debug)

            # Initialize Lua runtime
            self.initialize_lua()
            self._initialized = True

            # Start callback loop (but don't await it)
            asyncio.create_task(self.start_callback_loop(), name="callback_loop")

            # Check for and register Fibaro API endpoints if api_server is available
            if api_server:
                api_server.check_and_register_fibaro_api()

            # Allow some time for initialization to complete
            await asyncio.sleep(0.1)

        except Exception as e:
            print(f"Error in runtime initialization: {e}")
            raise
