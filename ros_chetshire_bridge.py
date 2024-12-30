from roslibpy import Ros
import logging
from typing import Optional
from enum import Enum

from cat.mad_hatter.decorators import tool, hook

class ConnectionState(Enum):
    DISCONNECTED = "disconnected"
    CONNECTED = "connected"
    ERROR = "error"

class RosClient:
    def __init__(self, host: str, port: int):
        """
        Initialize ROS client using roslibpy.
        
        Args:
            host: ROS server host
            port: ROS server port
        """
        self.host = host
        self.port = port
        self.client: Optional[Ros] = None
        self.state = ConnectionState.DISCONNECTED
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Configure logging."""
        self.logger = logging.getLogger(__name__)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    @tool
    def connect(self, cat) -> bool:
        """
        Establish connection to ROS server.
        
        Returns:
            bool: True if connection successful
        """
        try:
            self.client = Ros(host=self.host, port=self.port)
            self.client.on_ready(self._on_connect)
            self.client.on_error(self._on_error)
            self.client.run()
            return True
        except Exception as e:
            self.logger.error(f"Connection failed: {str(e)}")
            self.state = ConnectionState.ERROR
            return False
        
    @tool
    def disconnect(self, cat) -> None:
        """Close connection to ROS server."""
        if self.client and self.client.is_connected:
            self.client.close()
            self.state = ConnectionState.DISCONNECTED
            self.logger.info("Disconnected from ROS server")

    def _on_connect(self) -> None:
        """Handle successful connection."""
        self.state = ConnectionState.CONNECTED
        self.logger.info(f"Connected to ROS server at {self.host}:{self.port}")

    def _on_error(self, error: str) -> None:
        """Handle connection error."""
        self.state = ConnectionState.ERROR
        self.logger.error(f"ROS connection error: {error}")

    @property
    def is_connected(self) -> bool:
        """Check if client is connected."""
        return self.client is not None and self.client.is_connected