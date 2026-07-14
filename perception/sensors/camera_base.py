"""Abstract scaffolding for camera sensor integrations."""

# TODO: Define the common camera lifecycle and frame interface.


class CameraBase:
    """Base type for visible, depth, thermal, and other camera sensors.

    The class intentionally contains no sensor access or frame-processing logic.
    Future concrete camera adapters should share a stable interface through this
    type without coupling sensor drivers to detection, tracking, or ROS code.
    """

    pass
