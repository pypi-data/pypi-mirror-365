"""GraspSession class for session management."""

import asyncio
import websockets
from typing import Optional
from .browser import GraspBrowser
from ..services.terminal import TerminalService
from ..services.browser import CDPConnection
from ..services.filesystem import FileSystemService
from ..utils.logger import get_logger


class GraspSession:
    """Main session interface providing access to browser, terminal, and files."""
    
    def __init__(self, connection: CDPConnection):
        """Initialize GraspSession.
        
        Args:
            connection: CDP connection instance
        """
        self.connection = connection
        self.browser = GraspBrowser(connection, self)
        
        # Create files service
        connection_id = connection.id
        try:
            from .utils import _servers
            server = _servers[connection_id]
            if server.sandbox is None:
                raise RuntimeError('Sandbox is not available for file system service')
            self.files = FileSystemService(server.sandbox, connection)
            self.terminal = TerminalService(server.sandbox, connection)
        except (ImportError, KeyError) as e:
            # In test environment or when server is not available, create a mock files service
            self.logger.debug(f"Warning: Files service not available: {e}")
            raise e
        
        # WebSocket connection for keep-alive
        self._ws = None
        self._is_closed = False

        self.logger = get_logger().child('GraspSession')
        
        # Initialize WebSocket connection and start keep-alive
        # self.logger.debug('create session...')
        asyncio.create_task(self._initialize_websocket())
    
    async def _initialize_websocket(self) -> None:
        """Initialize WebSocket connection and start keep-alive."""
        try:
            self._ws = await websockets.connect(self.connection.ws_url)
            if not self._is_closed:
                await self._keep_alive()
            else:
                await self._ws.close()
        except Exception as e:
            self.logger.debug(f"Failed to initialize WebSocket connection: {e}")
    
    async def _keep_alive(self) -> None:
        """Keep WebSocket connection alive with periodic ping."""
        ws = self._ws
        await asyncio.sleep(10)  # 10 seconds interval, same as TypeScript version
        if ws and ws.close_code is None:
            try:
                # Send ping and wait for pong response
                pong_waiter = ws.ping()
                await pong_waiter
                # Recursively call keep_alive after receiving pong
                await self._keep_alive()
            except Exception as e:
                self.logger.debug(f"Keep-alive ping failed: {e}")
    
    @property
    def id(self) -> str:
        """Get session ID.
        
        Returns:
            Session ID
        """
        return self.connection.id
    
    def is_running(self) -> bool:
        """Check if the session is currently running.
        
        Returns:
            True if the session is running, False otherwise
        """
        try:
            from .utils import _servers
            from ..models import SandboxStatus
            server = _servers[self.id]
            if server.sandbox is None:
                return False
            status = server.sandbox.get_status()
            return status == SandboxStatus.RUNNING
        except (ImportError, KeyError) as e:
            self.logger.error(f"Failed to check running status: {e}")
            return False
    
    def get_host(self, port: int) -> Optional[str]:
        """Get the external host address for a specific port.
        
        Args:
            port: Port number to get host for
            
        Returns:
            External host address or None if sandbox not available
        """
        try:
            from .utils import _servers
            server = _servers[self.id]
            if server.sandbox is None:
                self.logger.warn('Cannot get host: sandbox not available')
                return None
            return server.sandbox.get_sandbox_host(port)
        except (ImportError, KeyError) as e:
            self.logger.error(f"Failed to get host: {e}")
            return None
    
    async def close(self) -> None:
        """Close the session and cleanup resources."""
        # Set closed flag to prevent new keep-alive cycles
        self._is_closed = True
        
        # Close WebSocket connection with timeout
        if self._ws and self._ws.close_code is None:
            try:
                # Add timeout to prevent hanging on close
                await asyncio.wait_for(self._ws.close(), timeout=5.0)
                self.logger.debug('✅ WebSocket closed successfully')
            except asyncio.TimeoutError:
                self.logger.debug('⚠️ WebSocket close timeout, forcing termination')
                # Force close if timeout
                if hasattr(self._ws, 'transport') and self._ws.transport:
                    self._ws.transport.close()
            except Exception as e:
                self.logger.error(f"Failed to close WebSocket connection: {e}")
        
        # Cleanup server resources
        try:
            from .utils import _servers
            await _servers[self.id].cleanup()
        except (ImportError, KeyError) as e:
            # In test environment or when server is not available, skip cleanup
            self.logger.error(f"Warning: Server cleanup not available: {e}")