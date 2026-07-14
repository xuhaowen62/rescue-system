"""Tracking interface definitions independent of ROS transport."""

# TODO: Define the model-independent tracking contract.


class Tracker:
    """Base type for multi-object tracking implementations.

    Tracking behavior is intentionally absent.  Future implementations should
    consume detection-layer data through typed interfaces and remain usable in
    non-ROS contexts.
    """

    pass
