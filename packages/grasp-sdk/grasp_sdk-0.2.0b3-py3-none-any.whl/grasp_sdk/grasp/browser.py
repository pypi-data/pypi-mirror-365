"""GraspBrowser class for browser interface."""

import aiohttp
import os
from typing import Optional, Dict, Any, TYPE_CHECKING

from ..services.browser import CDPConnection

if TYPE_CHECKING:
    from .session import GraspSession


class GraspBrowser:
    """Browser interface for Grasp session."""
    
    def __init__(self, connection: CDPConnection, session: Optional['GraspSession'] = None):
        """Initialize GraspBrowser.
        
        Args:
            connection: CDP connection instance
            session: GraspSession instance for accessing terminal and files services
        """
        self.connection = connection
        self.session = session
    
    def get_host(self) -> str:
        """Get browser host.
        
        Returns:
            Host for browser connection
        """
        from urllib.parse import urlparse
        return urlparse(self.connection.http_url).netloc
    
    def get_endpoint(self) -> str:
        """Get browser WebSocket endpoint URL.
        
        Returns:
            WebSocket URL for browser connection
        """
        return self.connection.ws_url
    
    async def get_current_page_target_info(self) -> Optional[Dict[str, Any]]:
        """Get current page target information.
        
        Warning:
            This method is experimental and may change or be removed in future versions.
            Use with caution in production environments.
        
        Returns:
            Dictionary containing target info and last screenshot, or None if failed
        """
        host = self.connection.http_url
        api = f"{host}/api/page/info"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(api) as response:
                    if not response.ok:
                        return None
                    
                    data = await response.json()
                    page_info = data.get('pageInfo', {})
                    last_screenshot = page_info.get('lastScreenshot')
                    session_id = page_info.get('sessionId')
                    targets = page_info.get('targets', {})
                    target_id = page_info.get('targetId')
                    page_loaded = page_info.get('pageLoaded')
                    
                    current_target = {}
                    for target in targets.values():
                        if target.get('targetId') == target_id:
                            current_target = target
                            break
                    
                    return {
                        'targetId': target_id,
                        'sessionId': session_id,
                        'pageLoaded': page_loaded,
                        **current_target,
                        'lastScreenshot': last_screenshot,
                        'targets': targets,
                    }
        except Exception:
             return None
    
    async def download_replay_video(self, local_path: str) -> None:
        """Download replay video from screenshots.
        
        Args:
            local_path: Local path to save the video file
            
        Raises:
            RuntimeError: If session is not available or video generation fails
        """
        if not self.session:
            raise RuntimeError("Session is required for download_replay_video")
        
        # Create terminal instance
        terminal = self.session.terminal
        
        # Generate file list for ffmpeg
        command1 = await terminal.run_command(
            "cd /home/user/downloads/grasp-screenshots && ls -1 | grep -v '^filelist.txt$' | sort | awk '{print \"file '\''\" $0 \"'\''\"}'> filelist.txt"
        )
        await command1.end()
        
        # Generate video using ffmpeg
        command2 = await terminal.run_command(
            "cd /home/user/downloads/grasp-screenshots && ffmpeg -r 25 -f concat -safe 0 -i filelist.txt -vsync vfr -pix_fmt yuv420p output.mp4"
        )
        await command2.end()
        
        # Determine final local path
        if not local_path.endswith('.mp4'):
            local_path = os.path.join(local_path, 'output.mp4')
        
        # Download the generated video file
        await self.session.files.download_file(
            '/home/user/downloads/grasp-screenshots/output.mp4',
            local_path
        )
    
    async def get_liveview_streaming_url(self) -> Optional[str]:
        """Get liveview streaming URL.
        
        Returns:
            Liveview streaming URL or None if not ready
        """
        host = self.connection.http_url
        api = f"{host}/api/session/liveview/stream"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(api) as response:
                    if not response.ok:
                        return None
                    return api
        except Exception:
            return None
    
    async def get_liveview_page_url(self) -> Optional[str]:
        """Get liveview page URL.
        
        Warning:
            This method is experimental and may change or be removed in future versions.
            Use with caution in production environments.
        
        Returns:
            Liveview page URL or None if not ready
        """
        host = self.connection.http_url
        api = f"{host}/api/session/liveview/preview"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(api) as response:
                    if not response.ok:
                        return None
                    return api
        except Exception:
            return None