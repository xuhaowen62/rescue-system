"""Feature-fusion interface definitions for multimodal perception."""

# TODO: Define typed feature inputs and fused-feature outputs.


class FeatureFusion:
    """Base type for combining features from heterogeneous sensors.

    No feature alignment, projection, weighting, or fusion logic is included.
    The future implementation should remain independent of ROS and sensor
    driver details.
    """

    pass
