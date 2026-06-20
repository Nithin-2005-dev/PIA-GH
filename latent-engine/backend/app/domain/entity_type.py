from enum import Enum


class EventType(Enum):
    COMMIT = "COMMIT"
    PULL_REQUEST = "PULL_REQUEST"
    REVIEW = "REVIEW"
    ISSUE = "ISSUE"
    RELEASE = "RELEASE"
    COMMENT = "COMMENT"