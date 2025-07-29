"""Terminal session management."""

import asyncio
import logging
import os
import sys
import uuid
from asyncio.subprocess import Process
from pathlib import Path
from typing import Any, Dict, Optional, List, TYPE_CHECKING
from collections import deque

if TYPE_CHECKING:
    from ..multiplex import Channel

logger = logging.getLogger(__name__)

_IS_WINDOWS = sys.platform.startswith("win")

# Minimal, safe defaults for interactive shells
_DEFAULT_ENV = {
    "TERM": "xterm-256color",
    "LANG": "C.UTF-8",
    "SHELL": "/bin/bash",
}


def _build_child_env() -> Dict[str, str]:
    """Return a copy of os.environ with sensible fallbacks added."""
    env = os.environ.copy()
    for k, v in _DEFAULT_ENV.items():
        env.setdefault(k, v)
    return env


class TerminalSession:
    """Represents a local shell subprocess bound to a mux channel."""

    def __init__(self, session_id: str, proc: Process, channel: "Channel", project_id: Optional[str] = None, terminal_manager: Optional["TerminalManager"] = None):
        self.id = session_id
        self.proc = proc
        self.channel = channel
        self.project_id = project_id
        self.terminal_manager = terminal_manager
        self._reader_task: Optional[asyncio.Task[None]] = None
        self._buffer: deque[str] = deque(maxlen=400)

    async def start_io_forwarding(self) -> None:
        """Spawn background task that copies stdout/stderr to the channel."""
        assert self.proc.stdout is not None, "stdout pipe not set"

        async def _pump() -> None:
            try:
                while True:
                    data = await self.proc.stdout.read(1024)
                    if not data:
                        break
                    text = data.decode(errors="ignore")
                    logging.getLogger("portacode.terminal").debug(f"[MUX] Terminal {self.id} output: {text!r}")
                    self._buffer.append(text)
                    try:
                        # Send terminal data via control channel with client session targeting
                        if self.terminal_manager:
                            await self.terminal_manager._send_session_aware({
                                "event": "terminal_data",
                                "channel": self.id,
                                "data": text,
                                "project_id": self.project_id
                            }, project_id=self.project_id)
                        else:
                            # Fallback to raw channel for backward compatibility
                            await self.channel.send(text)
                    except Exception as exc:
                        logger.warning("Failed to forward terminal output: %s", exc)
                        await asyncio.sleep(0.5)
                        continue
            finally:
                if self.proc and self.proc.returncode is None:
                    pass  # Keep alive across reconnects

        # Cancel existing reader task if it exists
        if self._reader_task and not self._reader_task.done():
            self._reader_task.cancel()
            
        self._reader_task = asyncio.create_task(_pump())

    async def write(self, data: str) -> None:
        if self.proc.stdin is None:
            logger.warning("stdin pipe closed for terminal %s", self.id)
            return
        try:
            if hasattr(self.proc.stdin, 'write') and hasattr(self.proc.stdin, 'drain'):
                # StreamWriter (pipe fallback)
                self.proc.stdin.write(data.encode())
                await self.proc.stdin.drain()
            else:
                # File object (PTY)
                loop = asyncio.get_running_loop()
                await loop.run_in_executor(None, self.proc.stdin.write, data.encode())
                await loop.run_in_executor(None, self.proc.stdin.flush)
        except Exception as exc:
            logger.warning("Failed to write to terminal %s: %s", self.id, exc)

    async def stop(self) -> None:
        """Stop the terminal session with comprehensive logging."""
        logger.info("session.stop: Starting stop process for session %s (PID: %s)", 
                   self.id, getattr(self.proc, 'pid', 'unknown'))
        
        try:
            # Check if process is still running
            if self.proc.returncode is None:
                logger.info("session.stop: Terminating process for session %s", self.id)
                self.proc.terminate()
            else:
                logger.info("session.stop: Process for session %s already exited (returncode: %s)", 
                           self.id, self.proc.returncode)
            
            # Wait for reader task to complete
            if self._reader_task and not self._reader_task.done():
                logger.info("session.stop: Waiting for reader task to complete for session %s", self.id)
                try:
                    await asyncio.wait_for(self._reader_task, timeout=5.0)
                    logger.info("session.stop: Reader task completed for session %s", self.id)
                except asyncio.TimeoutError:
                    logger.warning("session.stop: Reader task timeout for session %s, cancelling", self.id)
                    self._reader_task.cancel()
                    try:
                        await self._reader_task
                    except asyncio.CancelledError:
                        pass
            
            # Wait for process to exit
            if self.proc.returncode is None:
                logger.info("session.stop: Waiting for process to exit for session %s", self.id)
                await self.proc.wait()
                logger.info("session.stop: Process exited for session %s (returncode: %s)", 
                           self.id, self.proc.returncode)
            else:
                logger.info("session.stop: Process already exited for session %s (returncode: %s)", 
                           self.id, self.proc.returncode)
                
        except Exception as exc:
            logger.exception("session.stop: Error stopping session %s: %s", self.id, exc)
            raise

    def snapshot_buffer(self) -> str:
        """Return concatenated last buffer contents suitable for UI."""
        return "".join(self._buffer)

    async def reattach_channel(self, new_channel: "Channel") -> None:
        """Reattach this session to a new channel after reconnection."""
        logger.info("Reattaching terminal %s to channel %s", self.id, new_channel.id)
        self.channel = new_channel
        # Restart I/O forwarding with new channel
        await self.start_io_forwarding()


class WindowsTerminalSession(TerminalSession):
    """Terminal session backed by a Windows ConPTY."""

    def __init__(self, session_id: str, pty, channel: "Channel", project_id: Optional[str] = None, terminal_manager: Optional["TerminalManager"] = None):
        # Create a proxy for the PTY process
        class _WinPTYProxy:
            def __init__(self, pty):
                self._pty = pty

            @property
            def pid(self):
                return self._pty.pid

            @property
            def returncode(self):
                return None if self._pty.isalive() else self._pty.exitstatus

            async def wait(self):
                loop = asyncio.get_running_loop()
                await loop.run_in_executor(None, self._pty.wait)

        super().__init__(session_id, _WinPTYProxy(pty), channel, project_id, terminal_manager)
        self._pty = pty

    async def start_io_forwarding(self) -> None:
        """Spawn background task that copies stdout/stderr to the channel."""
        loop = asyncio.get_running_loop()

        async def _pump() -> None:
            try:
                while True:
                    data = await loop.run_in_executor(None, self._pty.read, 1024)
                    if not data:
                        if not self._pty.isalive():
                            break
                        await asyncio.sleep(0.05)
                        continue
                    if isinstance(data, bytes):
                        text = data.decode(errors="ignore")
                    else:
                        text = data
                    logging.getLogger("portacode.terminal").debug(f"[MUX] Terminal {self.id} output: {text!r}")
                    self._buffer.append(text)
                    try:
                        # Send terminal data via control channel with client session targeting
                        if self.terminal_manager:
                            await self.terminal_manager._send_session_aware({
                                "event": "terminal_data",
                                "channel": self.id,
                                "data": text,
                                "project_id": self.project_id
                            }, project_id=self.project_id)
                        else:
                            # Fallback to raw channel for backward compatibility
                            await self.channel.send(text)
                    except Exception as exc:
                        logger.warning("Failed to forward terminal output: %s", exc)
                        await asyncio.sleep(0.5)
                        continue
            finally:
                if self._pty and self._pty.isalive():
                    self._pty.kill()

        # Cancel existing reader task if it exists
        if self._reader_task and not self._reader_task.done():
            self._reader_task.cancel()
            
        self._reader_task = asyncio.create_task(_pump())

    async def write(self, data: str) -> None:
        loop = asyncio.get_running_loop()
        try:
            await loop.run_in_executor(None, self._pty.write, data)
        except Exception as exc:
            logger.warning("Failed to write to terminal %s: %s", self.id, exc)

    async def stop(self) -> None:
        """Stop the Windows terminal session with comprehensive logging."""
        logger.info("session.stop: Starting stop process for Windows session %s (PID: %s)", 
                   self.id, getattr(self._pty, 'pid', 'unknown'))
        
        try:
            # Check if PTY is still alive
            if self._pty.isalive():
                logger.info("session.stop: Killing PTY process for session %s", self.id)
                self._pty.kill()
            else:
                logger.info("session.stop: PTY process for session %s already exited", self.id)
            
            # Wait for reader task to complete
            if self._reader_task and not self._reader_task.done():
                logger.info("session.stop: Waiting for reader task to complete for Windows session %s", self.id)
                try:
                    await asyncio.wait_for(self._reader_task, timeout=5.0)
                    logger.info("session.stop: Reader task completed for Windows session %s", self.id)
                except asyncio.TimeoutError:
                    logger.warning("session.stop: Reader task timeout for Windows session %s, cancelling", self.id)
                    self._reader_task.cancel()
                    try:
                        await self._reader_task
                    except asyncio.CancelledError:
                        pass
            
            logger.info("session.stop: Successfully stopped Windows session %s", self.id)
                
        except Exception as exc:
            logger.exception("session.stop: Error stopping Windows session %s: %s", self.id, exc)
            raise


class SessionManager:
    """Manages terminal sessions."""

    def __init__(self, mux, terminal_manager=None):
        self.mux = mux
        self.terminal_manager = terminal_manager
        self._sessions: Dict[str, TerminalSession] = {}

    def _allocate_channel_id(self) -> str:
        """Allocate a new unique channel ID for a terminal session using UUID."""
        return uuid.uuid4().hex

    async def create_session(self, shell: Optional[str] = None, cwd: Optional[str] = None, project_id: Optional[str] = None) -> Dict[str, Any]:
        """Create a new terminal session."""
        # Use the same UUID for both terminal_id and channel_id to ensure consistency
        session_uuid = uuid.uuid4().hex
        term_id = session_uuid
        channel_id = session_uuid
        channel = self.mux.get_channel(channel_id)

        # Choose shell - prefer bash over sh for better terminal compatibility
        if shell is None:
            if not _IS_WINDOWS:
                shell = os.getenv("SHELL")
                # If the default shell is /bin/sh, try to use bash instead for better terminal support
                if shell == "/bin/sh":
                    for bash_path in ["/bin/bash", "/usr/bin/bash", "/usr/local/bin/bash"]:
                        if os.path.exists(bash_path):
                            shell = bash_path
                            logger.info("Switching from /bin/sh to %s for better terminal compatibility", shell)
                            break
            else:
                shell = os.getenv("COMSPEC", "cmd.exe")

        logger.info("Launching terminal %s using shell=%s on channel=%s", term_id, shell, channel_id)

        if _IS_WINDOWS:
            try:
                from winpty import PtyProcess
            except ImportError as exc:
                logger.error("winpty (pywinpty) not found: %s", exc)
                raise RuntimeError("pywinpty not installed on client")

            pty_proc = PtyProcess.spawn(shell, cwd=cwd or None, env=_build_child_env())
            session = WindowsTerminalSession(term_id, pty_proc, channel, project_id, self.terminal_manager)
        else:
            # Unix: try real PTY for proper TTY semantics
            try:
                import pty
                master_fd, slave_fd = pty.openpty()
                proc = await asyncio.create_subprocess_exec(
                    shell,
                    stdin=slave_fd,
                    stdout=slave_fd,
                    stderr=slave_fd,
                    preexec_fn=os.setsid,
                    cwd=cwd,
                    env=_build_child_env(),
                )
                # Wrap master_fd into a StreamReader
                loop = asyncio.get_running_loop()
                reader = asyncio.StreamReader()
                protocol = asyncio.StreamReaderProtocol(reader)
                await loop.connect_read_pipe(lambda: protocol, os.fdopen(master_fd, "rb", buffering=0))
                proc.stdout = reader
                # Use writer for stdin - create a simple file-like wrapper
                proc.stdin = os.fdopen(master_fd, "wb", buffering=0)
            except Exception:
                logger.warning("Failed to allocate PTY, falling back to pipes")
                proc = await asyncio.create_subprocess_exec(
                    shell,
                    stdin=asyncio.subprocess.PIPE,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.STDOUT,
                    cwd=cwd,
                    env=_build_child_env(),
                )
            session = TerminalSession(term_id, proc, channel, project_id, self.terminal_manager)

        self._sessions[term_id] = session
        await session.start_io_forwarding()

        return {
            "terminal_id": term_id,
            "channel": channel_id,
            "pid": session.proc.pid,
            "shell": shell,
            "cwd": cwd,
            "project_id": project_id,
        }

    def get_session(self, terminal_id: str) -> Optional[TerminalSession]:
        """Get a terminal session by ID."""
        return self._sessions.get(terminal_id)

    def remove_session(self, terminal_id: str) -> Optional[TerminalSession]:
        """Remove and return a terminal session."""
        session = self._sessions.pop(terminal_id, None)
        if session:
            logger.info("session_manager: Removed session %s (PID: %s) from session manager", 
                       terminal_id, getattr(session.proc, 'pid', 'unknown'))
        else:
            logger.warning("session_manager: Attempted to remove non-existent session %s", terminal_id)
        return session

    def list_sessions(self, project_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all terminal sessions, optionally filtered by project_id."""
        filtered_sessions = []
        for s in self._sessions.values():
            if project_id == "all":
                filtered_sessions.append(s)
            elif project_id is None:
                if s.project_id is None:
                    filtered_sessions.append(s)
            else:
                if s.project_id == project_id:
                    filtered_sessions.append(s)

        return [
            {
                "terminal_id": s.id,
                "channel": s.channel.id,
                "pid": s.proc.pid,
                "returncode": s.proc.returncode,
                "buffer": s.snapshot_buffer(),
                "status": "active" if s.proc.returncode is None else "exited",
                "created_at": None,  # Could add timestamp if needed
                "shell": None,  # Could store shell info if needed
                "cwd": None,    # Could store cwd info if needed
                "project_id": s.project_id,
            }
            for s in filtered_sessions
        ]

    async def reattach_sessions(self, mux):
        """Reattach sessions to a new multiplexer after reconnection."""
        self.mux = mux
        logger.info("Reattaching %d terminal sessions to new multiplexer", len(self._sessions))
        
        # Clean up any sessions with dead processes first
        dead_sessions = []
        for term_id, sess in list(self._sessions.items()):
            if sess.proc.returncode is not None:
                logger.info("Cleaning up dead terminal session %s (exit code: %s)", term_id, sess.proc.returncode)
                dead_sessions.append(term_id)
        
        for term_id in dead_sessions:
            self._sessions.pop(term_id, None)
        
        # Reattach remaining live sessions
        for sess in self._sessions.values():
            try:
                # Get the existing channel ID (UUID string)
                channel_id = sess.channel.id
                new_channel = self.mux.get_channel(channel_id)
                await sess.reattach_channel(new_channel)
                logger.info("Successfully reattached terminal %s", sess.id)
            except Exception as exc:
                logger.error("Failed to reattach terminal %s: %s", sess.id, exc) 