from pydantic import BaseModel
from enum import Enum
from datetime import date, time
from cat.mad_hatter.decorators import plugin


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