"""
Interactive REPL for plua
Provides a Lua-like interactive prompt with access to plua features
"""

import asyncio
import traceback
from typing import Optional
from .runtime import LuaAsyncRuntime


class PluaREPL:
    """Interactive        # Give the API server a moment to start
        await asyncio.sleep(0.5)L for plua with async support"""

    def __init__(self, runtime):
        self.runtime = runtime
        self.debug = runtime.config.get('debug', False)
        self.running = True
        self.repl_task = None

    async def initialize(self):
        """Initialize the runtime and start callback loop"""
        # Check if runtime is already initialized (for interactive mode)
        if not hasattr(self.runtime, '_initialized') or not self.runtime._initialized:
            self.runtime.initialize_lua()
            await self.runtime.start_callback_loop()
            self.runtime._initialized = True

        # Set debug mode
        if self.debug:
            self.runtime.interpreter.set_debug_mode(True)

    def show_welcome(self):
        """Show welcome message for the REPL"""
        from . import __version__
        import lupa

        try:
            lua = lupa.LuaRuntime()
            lua_version = lua.eval('_VERSION')
        except Exception:
            lua_version = "Lua (version unknown)"

        print(f"Plua v{__version__} Interactive REPL")
        print(f"Running {lua_version} with async runtime support")
        print()
        print("Quick start:")
        print("  help()                           - Show available commands")
        print("  print('Hello, plua!')           - Basic Lua")
        print("  json.encode({name='test'})       - JSON encoding")
        print("  net.HTTPClient()                 - Create HTTP client")
        print("  setTimeout(function() print('Hi!') end, 2000) - Async timer")
        print()
        print("Type 'exit()' or press Ctrl+D to quit")
        print()

    def show_help(self):
        """Show REPL help"""
        print("Plua REPL Commands:")
        print("  exit()          - Exit the REPL")
        print("  help()          - Show this help")
        print("  state()         - Show runtime state")
        print("  clear()         - Clear screen")
        print("  debug(true/false) - Toggle debug mode")
        print()
        print("Lua functions available:")
        print("  setTimeout(fn, ms) - Schedule function execution")
        print("  clearTimeout(id)   - Cancel scheduled timer")
        print("  json.encode(obj)   - Convert to JSON")
        print("  json.decode(str)   - Parse JSON")
        print("  net.HTTPClient()   - Create HTTP client")
        print("  net.HTTPServer()   - Create HTTP server")
        print("  _PY.*             - Python integration functions")
        print()
        print("Tips:")
        print("  - Use Ctrl+C to cancel input, Ctrl+D to exit")
        print("  - Variables persist throughout the session")
        print("  - Async operations run in the background")
        print()

    def show_state(self):
        """Show current runtime state"""
        try:
            state = self.runtime.interpreter.get_runtime_state()
            print("Runtime state:")
            print(f"  Active timers: {state['active_timers']}")
            print(f"  Pending callbacks: {state['pending_callbacks']}")
            print(f"  Total tasks: {state['total_tasks']}")

            # Get asyncio task info
            tasks = [t for t in asyncio.all_tasks() if not t.done()]
            print(f"  Asyncio tasks: {len(tasks)}")
            for task in tasks:
                name = task.get_name() if hasattr(task, 'get_name') else "unnamed"
                print(f"    - {name}")
        except Exception as e:
            print(f"Error getting state: {e}")

    def execute_lua_statement(self, statement: str) -> bool:
        """
        Execute a Lua statement and return True if successful
        Handles special REPL commands
        """
        statement = statement.strip()

        if not statement:
            return True

        # Handle special REPL commands
        if statement in ['exit()', 'quit()']:
            self.running = False
            return True
        elif statement in ['help()']:
            self.show_help()
            return True
        elif statement in ['state()']:
            self.show_state()
            return True
        elif statement in ['clear()']:
            # Clear screen
            print('\033[2J\033[H', end='')
            return True
        elif statement.startswith('debug('):
            try:
                # Simple debug toggle
                if 'true' in statement:
                    self.debug = True
                    self.runtime.interpreter.set_debug_mode(True)
                    print("Debug mode enabled")
                elif 'false' in statement:
                    self.debug = False
                    self.runtime.interpreter.set_debug_mode(False)
                    print("Debug mode disabled")
                else:
                    print(f"Debug mode: {'enabled' if self.debug else 'disabled'}")
            except Exception as e:
                print(f"Error toggling debug: {e}")
            return True

        # Try to execute as Lua code
        try:
            lua = self.runtime.interpreter.get_lua_runtime()
            if not lua:
                print("Error: Lua runtime not available")
                return False

            # Try to execute as expression first (for immediate results)
            try:
                # Wrap in return to get the result
                expr_code = f"return {statement}"
                result = lua.execute(expr_code)
                if result is not None:
                    print(result)
            except Exception:
                # If expression fails, try as statement
                lua.execute(statement)

            return True

        except Exception as e:
            print(f"Lua error: {e}")
            if self.debug:
                traceback.print_exc()
            return False

    async def read_input(self) -> Optional[str]:
        """Read input from user asynchronously"""
        # Use asyncio to read input without blocking the event loop
        loop = asyncio.get_event_loop()
        try:
            # Run input() in a thread pool to avoid blocking
            line = await loop.run_in_executor(None, input, "plua> ")
            return line
        except EOFError:
            return None
        except KeyboardInterrupt:
            print()  # New line after ^C
            return ""  # Empty string to continue

    async def repl_loop(self):
        """Main REPL loop"""
        while self.running:
            try:
                line = await self.read_input()

                if line is None:  # EOF (Ctrl+D)
                    print("\nGoodbye!")
                    break

                if line == "":  # Empty line or Ctrl+C
                    continue

                # Execute the statement
                self.execute_lua_statement(line)

            except KeyboardInterrupt:
                print("\nUse exit() or Ctrl+D to quit")
                continue
            except Exception as e:
                print(f"REPL error: {e}")
                if self.debug:
                    traceback.print_exc()

    async def start(self):
        """Start the REPL"""
        try:
            # Initialize runtime
            await self.initialize()

            # Show welcome message
            self.show_welcome()

            # Start REPL loop
            self.repl_task = asyncio.create_task(self.repl_loop(), name="repl_loop")
            await self.repl_task

        finally:
            # Clean shutdown
            self.runtime.stop()


async def run_repl(runtime=None):
    """Main function to run the REPL, optionally with API server"""
    # Name the main task
    current_task = asyncio.current_task()
    if current_task:
        api_config = runtime.config.get('api_config')
        current_task.set_name("repl_api_main" if api_config else "repl_main")

    if runtime is None:
        # from .runtime import LuaAsyncRuntime
        runtime = LuaAsyncRuntime()
    repl = PluaREPL(runtime)
    api_task = None
    api_config = runtime.config.get('api_config')
    if api_config:
        from .api_server import PlUA2APIServer
        print(f"API server on {api_config['host']}:{api_config['port']}")
        print(f"WebUI on http://127.0.0.1:{api_config['port']}/web")
        api_server = PlUA2APIServer(repl.runtime, api_config['host'], api_config['port'])
        api_task = asyncio.create_task(api_server.start_server(), name="api_server")
        print()
    try:
        await repl.start()
    finally:
        if api_task:
            api_task.cancel()
            try:
                await api_task
            except asyncio.CancelledError:
                pass
