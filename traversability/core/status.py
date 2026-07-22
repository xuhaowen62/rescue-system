"""Traversability ?????"""

from enum import Enum


class TraversabilityStatus(str, Enum):
    """?? Provider ? Analyzer ???????"""

    CREATED = "CREATED"
    INITIALIZED = "INITIALIZED"
    IDLE = "IDLE"
    READY = "READY"
    RUNNING = "RUNNING"
    STOPPED = "STOPPED"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    RECOVERING = "RECOVERING"
    ERROR = "ERROR"
