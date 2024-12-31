from cat.mad_hatter.decorators import tool, hook, plugin
from pydantic import BaseModel
from roslibpy import Ros
import logging
from pydantic import BaseModel
from enum import Enum
from datetime import date, time

# select box options
class ROSVersion(Enum):
    a: str = 'ROS1'
    b: str = 'ROS2'


# settings
class PlugInSettings(BaseModel):

    # ROS server host
    host: str = 'localhost'

    # ROS server port
    port: int = 9090

    # ROS version
    version: ROSVersion = ROSVersion.a


# Give your settings model to the Cat.
@plugin
def settings_model():
    return PlugInSettings

@hook(priority=0) 
def agent_prompt_prefix(prefix, cat):
    prefix = """Your are ROSA (Robot Operating System Agent), an AI agent that can use ROS tools to answer questions 
        about robotics systems. You have a subset of the ROS tools available to you, and you can use them to 
        interact with the robotic system you are integrated with. Your responses should be grounded in real-time 
        information whenever possible using the tools available to you."""
    return prefix

# Configurazione logging
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

ros_client = None
connection_state = "disconnected"

@tool(
    examples=["I would like to connect to a ROS server"]
)
def connect_to_ros(cat):
    """Connect to ROS server to control the robot"""
    global ros_client, connection_state

    settings = cat.mad_hatter.get_plugin().load_settings()
    host = settings.get("host")
    port = settings.get("port")

    print("Trying connection to ROS server")
    
    try:
        ros_client = Ros(host=host, port=port)
        ros_client.on_ready(lambda: _on_connect())
        ros_client.on_error(lambda e: _on_error(str(e)))
        ros_client.run()
        return "Connection initiated"
    except Exception as e:
        logger.error(f"Connection failed: {str(e)}")
        connection_state = "error"
        return f"Connection failed: {str(e)}"

@tool
def disconnect_from_ros(cat):
    """Disconnect from ROS server"""
    global ros_client, connection_state
    
    if ros_client and ros_client.is_connected:
        ros_client.close()
        connection_state = "disconnected"
        logger.info("Disconnected from ROS server")
        return "Disconnected successfully"
    return "Not connected"

def _on_connect():
    """Internal callback for successful connection"""
    global connection_state
    connection_state = "connected"
    logger.info("Connected to ROS server")

def _on_error(error: str):
    """Internal callback for connection error"""
    global connection_state
    connection_state = "error"
    logger.error(f"ROS connection error: {error}")